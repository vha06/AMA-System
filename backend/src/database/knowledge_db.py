import os
import json
import logging
from typing import List, Dict, Any, Optional

import chromadb
import networkx as nx
from google import genai
from google.genai import types
from google.genai.errors import APIError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# LlamaIndex Imports
from llama_index.core import PropertyGraphIndex, Document, Settings
from llama_index.core.graph_stores import SimplePropertyGraphStore
from llama_index.core.graph_stores.types import EntityNode, Relation
from llama_index.core.embeddings import MockEmbedding
from llama_index.core.llms import MockLLM
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.llms.gemini import Gemini
from llama_index.embeddings.gemini import GeminiEmbedding

from src.core.config import settings
from src.core.models import (
    Triplet,
    TripletExtractionResponse,
    KnowledgeQueryResponse,
)

logger = logging.getLogger(__name__)

TRIPLET_EXTRACTION_PROMPT = """Bạn là một chuyên gia phân tích dữ liệu và trích xuất Knowledge Graph.
Nhiệm vụ của bạn là đọc đoạn văn bản được cung cấp và trích xuất các bộ ba Triplet (Subject - Predicate - Object) thể hiện các mối quan hệ quan trọng.

Quy tắc:
1. Subject và Object phải là các thực thể (Entity), khái niệm, sản phẩm, đối thủ, phân khúc khách hàng, rủi ro, hoặc từ khóa chính.
2. Predicate phải mô tả ngắn gọn mối quan hệ (ví dụ: "thuộc ngách", "rủi ro chính là", "đối thủ của", "giá trung bình", "khách hàng mục tiêu", "có đặc điểm").
3. Trích xuất chính xác, cô đọng, tránh mơ hồ.
4. Trả về dưới dạng JSON khớp với cấu trúc TripletExtractionResponse.
"""


class GraphRAGKnowledgeBase:
    """Enhanced GraphRAG Knowledge Base utilizing LlamaIndex Property Graph Store and ChromaDB."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
        embedding_model: str = "text-embedding-004",
        graph_path: str = "./data/graph_kb.json",
        chroma_path: str = "./data/chroma_db",
    ):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model_name = model_name or "gemini-2.5-pro"
        self.embedding_model = embedding_model
        self.graph_path = graph_path
        self.chroma_path = chroma_path

        # 1. Gemini GenAI Client for direct structured extraction fallback/verification
        self._client = None
        if self.api_key:
            self._client = genai.Client(api_key=self.api_key)

        # 2. LlamaIndex LLM & Embedding Setup
        if self.api_key:
            try:
                self.llm = Gemini(model=self.model_name, api_key=self.api_key)
                self.embed_model = GeminiEmbedding(model_name=self.embedding_model, api_key=self.api_key)
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini LlamaIndex wrappers: {e}. Falling back to Mock.")
                self.llm = MockLLM()
                self.embed_model = MockEmbedding(embed_dim=768)
        else:
            logger.warning("GEMINI_API_KEY missing. GraphRAG operating in Mock/Offline mode.")
            self.llm = MockLLM()
            self.embed_model = MockEmbedding(embed_dim=768)

        Settings.llm = self.llm
        Settings.embed_model = self.embed_model

        # 3. ChromaDB Vector Store
        os.makedirs(self.chroma_path, exist_ok=True)
        self.chroma_client = chromadb.PersistentClient(path=self.chroma_path)
        self.collection = self.chroma_client.get_or_create_collection(
            name="graphrag_chunks",
            metadata={"hnsw:space": "cosine"}
        )
        self.vector_store = ChromaVectorStore(chroma_collection=self.collection)

        # 4. NetworkX Graph (for compatibility)
        self.graph = nx.DiGraph()

        # 5. LlamaIndex Property Graph Store
        self.graph_store = SimplePropertyGraphStore()
        self._load_graph()

        # 6. Initialize LlamaIndex PropertyGraphIndex
        self.index = PropertyGraphIndex.from_documents(
            [],
            property_graph_store=self.graph_store,
            vector_store=self.vector_store,
            embed_model=self.embed_model,
            llm=self.llm,
        )

    def _sync_networkx_to_property_store(self) -> None:
        """Sync manual edits from self.graph into PropertyGraphStore."""
        nodes = []
        relations = []
        for u, v, data in self.graph.edges(data=True):
            rel_label = data.get("relation", "relates_to")
            e1 = EntityNode(name=str(u), label="ENTITY")
            e2 = EntityNode(name=str(v), label="ENTITY")
            rel = Relation(label=rel_label, source_id=e1.id, target_id=e2.id)
            nodes.extend([e1, e2])
            relations.append(rel)
        if nodes and relations:
            self.graph_store.upsert_nodes(nodes)
            self.graph_store.upsert_relations(relations)

    def _sync_property_store_to_networkx(self) -> None:
        """Sync PropertyGraphStore triplets into self.graph."""
        try:
            if hasattr(self.graph_store, "graph") and hasattr(self.graph_store.graph, "nodes"):
                node_keys = list(self.graph_store.graph.nodes.keys())
                if node_keys:
                    raw_triplets = self.graph_store.get_triplets(entity_names=node_keys)
                    for src, rel, tgt in raw_triplets:
                        s_name = getattr(src, "name", str(src))
                        r_label = getattr(rel, "label", getattr(rel, "relation", "relates_to"))
                        t_name = getattr(tgt, "name", str(tgt))
                        self.graph.add_node(s_name, type="entity")
                        self.graph.add_node(t_name, type="entity")
                        self.graph.add_edge(s_name, t_name, relation=r_label)
        except Exception as e:
            logger.error(f"Error syncing property store to NetworkX: {e}")

    def _load_graph(self) -> None:
        """Load PropertyGraphStore from persisted path if exists."""
        if os.path.exists(self.graph_path):
            try:
                self.graph_store = SimplePropertyGraphStore.from_persist_path(self.graph_path)
                self._sync_property_store_to_networkx()
                logger.info(f"Loaded LlamaIndex PropertyGraphStore from {self.graph_path}.")
            except Exception as e:
                logger.error(f"Failed to load graph from {self.graph_path}: {e}")
                self.graph_store = SimplePropertyGraphStore()

    def _save_graph(self) -> None:
        """Save LlamaIndex PropertyGraphStore to file."""
        self._sync_networkx_to_property_store()
        os.makedirs(os.path.dirname(self.graph_path) or ".", exist_ok=True)
        try:
            self.graph_store.persist(self.graph_path)
            logger.info(f"Saved PropertyGraphStore to {self.graph_path}.")
        except Exception as e:
            logger.error(f"Failed to save graph to {self.graph_path}: {e}")

    def _get_embedding(self, text: str) -> List[float]:
        """Generate embedding vector using LlamaIndex embed model or fallback."""
        try:
            return self.embed_model.get_text_embedding(text)
        except Exception:
            return [0.0] * 768

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((APIError, Exception)),
        reraise=False,
    )
    def extract_triplets(self, text: str) -> List[Triplet]:
        """Extract Triplets from text using Gemini."""
        if not self._client:
            logger.warning("No API key available for triplet extraction.")
            return []

        config = types.GenerateContentConfig(
            system_instruction=TRIPLET_EXTRACTION_PROMPT,
            response_mime_type="application/json",
            response_schema=TripletExtractionResponse,
            temperature=0.1,
        )

        response = self._client.models.generate_content(
            model=self.model_name,
            contents=text,
            config=config,
        )

        if hasattr(response, "parsed") and response.parsed is not None:
            if isinstance(response.parsed, TripletExtractionResponse):
                return response.parsed.triplets
            return TripletExtractionResponse.model_validate(response.parsed).triplets

        if response.text:
            data = json.loads(response.text)
            parsed = TripletExtractionResponse.model_validate(data)
            return parsed.triplets

        return []

    def add_knowledge(self, text: str, doc_id: Optional[str] = None) -> List[Triplet]:
        """Process raw text, extract Triplets, store in Property Graph and ChromaDB."""
        if not text or not text.strip():
            return []

        # 1. Extract Triplets
        triplets = []
        try:
            triplets = self.extract_triplets(text)
        except Exception as e:
            logger.error(f"Failed to extract triplets: {e}")

        # 2. Add Triplets to PropertyGraphStore and NetworkX
        nodes = []
        relations = []
        for t in triplets:
            subj, pred, obj = t.subject.strip(), t.predicate.strip(), t.object.strip()
            self.graph.add_node(subj, type="entity")
            self.graph.add_node(obj, type="entity")
            self.graph.add_edge(subj, obj, relation=pred)

            e1 = EntityNode(name=subj, label="ENTITY")
            e2 = EntityNode(name=obj, label="ENTITY")
            rel = Relation(label=pred, source_id=e1.id, target_id=e2.id)
            nodes.extend([e1, e2])
            relations.append(rel)

        if nodes and relations:
            self.graph_store.upsert_nodes(nodes)
            self.graph_store.upsert_relations(relations)

        self._save_graph()

        # 3. Add Document Chunk to ChromaDB Vector Store
        embedding = self._get_embedding(text)
        chunk_id = doc_id or f"doc_{self.collection.count() + 1}"
        self.collection.add(
            ids=[chunk_id],
            documents=[text],
            embeddings=[embedding],
            metadatas=[{"triplet_count": len(triplets)}]
        )

        # 4. Insert into LlamaIndex PropertyGraphIndex only when using real LLM (not MockLLM)
        if not isinstance(self.llm, MockLLM):
            try:
                doc = Document(text=text, doc_id=chunk_id)
                self.index.insert(doc)
            except Exception as e:
                logger.warning(f"PropertyGraphIndex insertion notice: {e}")

        logger.info(f"Added knowledge chunk {chunk_id}: {len(triplets)} triplets extracted.")
        return triplets

    def query_knowledge(self, query: str, top_k: int = 5) -> KnowledgeQueryResponse:
        """Execute GraphRAG hybrid retrieval using LlamaIndex PropertyGraph & ChromaDB."""
        vector_docs: List[str] = []
        graph_triplets: List[Triplet] = []

        # 1. Vector Search in ChromaDB
        try:
            query_embedding = self._get_embedding(query)
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=min(top_k, max(1, self.collection.count()))
            )
            if results and "documents" in results and results["documents"]:
                vector_docs = results["documents"][0]
        except Exception as e:
            logger.error(f"Vector search failed: {e}")

        # 2. Try LlamaIndex PropertyGraph Retriever to supplement vector docs if not using MockLLM
        if not isinstance(self.llm, MockLLM):
            try:
                retriever = self.index.as_retriever()
                retrieved_nodes = retriever.retrieve(query)
                for n in retrieved_nodes:
                    text_content = getattr(n, 'text', str(n))
                    if text_content and text_content not in vector_docs:
                        vector_docs.append(text_content)
            except Exception as e:
                logger.debug(f"PropertyGraph retriever notice: {e}")

        # Limit vector results to requested top_k
        vector_docs = vector_docs[:top_k]

        # 3. Graph Traversal for Triplets matching query
        q_lower = query.lower()
        visited_edges = set()

        for u, v, data in self.graph.edges(data=True):
            rel = data.get("relation", "relates_to")
            u_str, v_str = str(u), str(v)
            if q_lower in u_str.lower() or q_lower in v_str.lower() or u_str.lower() in q_lower or v_str.lower() in q_lower:
                edge_key = (u_str, rel, v_str)
                if edge_key not in visited_edges:
                    visited_edges.add(edge_key)
                    graph_triplets.append(Triplet(subject=u_str, predicate=rel, object=v_str))

        # 4. Combine context
        context_parts = []
        if vector_docs:
            context_parts.append("--- VECTOR CONTEXT ---")
            for doc in vector_docs:
                context_parts.append(f"- {doc}")

        if graph_triplets:
            context_parts.append("\n--- GRAPH TRIPLETS ---")
            for t in graph_triplets:
                context_parts.append(f"- ({t.subject}) --[{t.predicate}]--> ({t.object})")

        combined_context = "\n".join(context_parts)

        return KnowledgeQueryResponse(
            query=query,
            vector_results=vector_docs,
            graph_triplets=graph_triplets,
            combined_context=combined_context,
        )
