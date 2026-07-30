import os
import shutil
import pytest
from unittest.mock import MagicMock, patch
import networkx as nx

from src.core.models import Triplet, KnowledgeQueryResponse
from src.database.knowledge_db import GraphRAGKnowledgeBase


@pytest.fixture
def temp_kb(tmp_path):
    """Fixture providing a temporary GraphRAGKnowledgeBase with isolated temp directories."""
    graph_file = tmp_path / "test_graph.json"
    chroma_dir = tmp_path / "test_chroma"
    kb = GraphRAGKnowledgeBase(
        api_key=None,
        graph_path=str(graph_file),
        chroma_path=str(chroma_dir),
    )
    yield kb
    if os.path.exists(chroma_dir):
        shutil.rmtree(chroma_dir, ignore_errors=True)


def test_load_and_save_graph(temp_kb):
    """Test saving graph to JSON and reloading it."""
    temp_kb.graph.add_node("Shopee", type="entity")
    temp_kb.graph.add_node("Thương mại điện tử", type="entity")
    temp_kb.graph.add_edge("Shopee", "Thương mại điện tử", relation="thuộc lĩnh vực")
    
    temp_kb._save_graph()
    assert os.path.exists(temp_kb.graph_path)

    # Load into new instance
    new_kb = GraphRAGKnowledgeBase(
        api_key=None,
        graph_path=temp_kb.graph_path,
        chroma_path=temp_kb.chroma_path,
    )
    assert new_kb.graph.number_of_nodes() == 2
    assert new_kb.graph.number_of_edges() == 1
    assert new_kb.graph.has_edge("Shopee", "Thương mại điện tử")


def test_add_knowledge_with_mock(temp_kb):
    """Test adding knowledge with mocked Gemini LLM extraction."""
    sample_triplets = [
        Triplet(subject="Dầu gội bưởi", predicate="giá trung bình", object="150.000 VNĐ"),
        Triplet(subject="Dầu gội bưởi", predicate="thuộc ngách", object="Mỹ phẩm thiên nhiên"),
    ]

    with patch.object(temp_kb, "extract_triplets", return_value=sample_triplets):
        with patch.object(temp_kb, "_get_embedding", return_value=[0.1] * 768):
            result = temp_kb.add_knowledge("Dầu gội bưởi có giá trung bình 150k thuộc ngách Mỹ phẩm thiên nhiên.")
            
            assert len(result) == 2
            assert temp_kb.graph.number_of_nodes() == 3
            assert temp_kb.graph.number_of_edges() == 2
            assert temp_kb.collection.count() == 1


def test_query_knowledge(temp_kb):
    """Test hybrid query retrieving vector docs and graph triplets."""
    sample_triplets = [
        Triplet(subject="Kem chống nắng", predicate="đối thủ chính", object="Anessa"),
        Triplet(subject="Kem chống nắng", predicate="rủi ro", object="Hàng giả nhiều"),
    ]

    with patch.object(temp_kb, "extract_triplets", return_value=sample_triplets):
        with patch.object(temp_kb, "_get_embedding", return_value=[0.2] * 768):
            temp_kb.add_knowledge("Kem chống nắng Anessa bị cạnh tranh và rủi ro hàng giả nhiều.")

    with patch.object(temp_kb, "_get_embedding", return_value=[0.2] * 768):
        query_response = temp_kb.query_knowledge("Kem chống nắng", top_k=1)
        
        assert isinstance(query_response, KnowledgeQueryResponse)
        assert len(query_response.vector_results) == 1
        assert len(query_response.graph_triplets) == 2
        assert "Kem chống nắng" in query_response.combined_context
        assert "Anessa" in query_response.combined_context
