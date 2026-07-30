import os
import json
import logging
from typing import List, Dict, Any, Optional
import networkx as nx
from networkx.readwrite import json_graph
import chromadb
from google import genai
from google.genai import types
from google.genai.errors import APIError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

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
    """GraphRAG Knowledge Base combining ChromaDB (Vector) and NetworkX (Graph)."""

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

        # Initialize Gemini Client
        self._client = None
        if self.api_key:
            self._client = genai.Client(api_key=self.api_key)
        else:
            logger.warning("GEMINI_API_KEY is missing. GraphRAG will operate in offline/mock mode.")

        # Initialize NetworkX Graph
        self.graph = nx.DiGraph()
        self._load_graph()

        # Initialize ChromaDB Vector Store
        os.makedirs(self.chroma_path, exist_ok=True)
        self.chroma_client = chromadb.PersistentClient(path=self.chroma_path)
        self.collection = self.chroma_client.get_or_create_collection(
            name="graphrag_chunks",
            metadata={"hnsw:space": "cosine"}
        )

    def _load_graph(self) -> None:
        """Load graph from JSON file if exists."""
        if os.path.exists(self.graph_path):
            try:
                with open(self.graph_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.graph = json_graph.node_link_graph(data)
                logger.info(f"Loaded knowledge graph with {self.graph.number_of_nodes()} nodes and {self.graph.number_of_edges()} edges.")
            except Exception as e:
                logger.error(f"Failed to load graph JSON from {self.graph_path}: {e}")
                self.graph = nx.DiGraph()
        else:
            self.graph = nx.DiGraph()

    def _save_graph(self) -> None:
        """Save NetworkX graph to JSON file."""
        os.makedirs(os.path.dirname(self.graph_path) or ".", exist_ok=True)
        try:
            data = json_graph.node_link_data(self.graph)
            with open(self.graph_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved knowledge graph to {self.graph_path}.")
        except Exception as e:
            logger.error(f"Failed to save graph to {self.graph_path}: {e}")

    def _get_embedding(self, text: str) -> List[float]:
        """Generate embedding vector using Google Embedding API."""
        if not self._client:
            # Fallback zero vector if no client
            return [0.0] * 768

        try:
            response = self._client.models.embed_content(
                model=self.embedding_model,
                contents=text,
            )
            if hasattr(response, "embedding") and hasattr(response.embedding, "values"):
                return response.embedding.values
            elif hasattr(response, "embeddings") and len(response.embeddings) > 0:
                return response.embeddings[0].values
            raise ValueError("Unexpected response format from embedding API.")
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return [0.0] * 768

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((APIError, Exception)),
        reraise=False,
    )
    def extract_triplets(self, text: str) -> List[Triplet]:
        """Extract Triplets from text using Gemini 2.5 Pro."""
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
        """Process raw text, extract Triplets, store in NetworkX graph and ChromaDB."""
        if not text or not text.strip():
            return []

        # 1. Extract Triplets
        triplets = []
        try:
            triplets = self.extract_triplets(text)
        except Exception as e:
            logger.error(f"Failed to extract triplets: {e}")

        # 2. Add Triplets to NetworkX Graph
        for t in triplets:
            subj, pred, obj = t.subject.strip(), t.predicate.strip(), t.object.strip()
            self.graph.add_node(subj, type="entity")
            self.graph.add_node(obj, type="entity")
            self.graph.add_edge(subj, obj, relation=pred)

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

        logger.info(f"Added knowledge chunk {chunk_id}: {len(triplets)} triplets extracted.")
        return triplets

    def query_knowledge(self, query: str, top_k: int = 5) -> KnowledgeQueryResponse:
        """Execute GraphRAG hybrid retrieval: Vector search + Graph traversal."""
        query_embedding = self._get_embedding(query)

        # 1. Vector Search in ChromaDB
        vector_docs: List[str] = []
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=min(top_k, max(1, self.collection.count()))
            )
            if results and "documents" in results and results["documents"]:
                vector_docs = results["documents"][0]
        except Exception as e:
            logger.error(f"Vector search failed: {e}")

        # 2. Graph Search in NetworkX
        graph_triplets: List[Triplet] = []
        q_lower = query.lower()

        # Find matching nodes
        matching_nodes = [
            node for node in self.graph.nodes()
            if str(node).lower() in q_lower or q_lower in str(node).lower()
        ]

        # Traversal: get out-edges and in-edges for matched nodes
        visited_edges = set()
        for node in matching_nodes:
            # Outgoing relations
            for neighbor in self.graph.neighbors(node):
                edge_data = self.graph.get_edge_data(node, neighbor)
                rel = edge_data.get("relation", "relates_to") if edge_data else "relates_to"
                edge_key = (node, rel, neighbor)
                if edge_key not in visited_edges:
                    visited_edges.add(edge_key)
                    graph_triplets.append(Triplet(subject=str(node), predicate=rel, object=str(neighbor)))

            # Incoming relations
            for predecessor in self.graph.predecessors(node):
                edge_data = self.graph.get_edge_data(predecessor, node)
                rel = edge_data.get("relation", "relates_to") if edge_data else "relates_to"
                edge_key = (predecessor, rel, node)
                if edge_key not in visited_edges:
                    visited_edges.add(edge_key)
                    graph_triplets.append(Triplet(subject=str(predecessor), predicate=rel, object=str(node)))

        # 3. Combine context
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
