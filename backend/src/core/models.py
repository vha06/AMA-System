from pydantic import BaseModel, Field
from typing import List, Optional

class Triplet(BaseModel):
    """Represents a Knowledge Graph Triplet (Subject - Predicate - Object)."""
    subject: str = Field(..., description="Entity name or subject")
    predicate: str = Field(..., description="Relationship or property connecting subject and object")
    object: str = Field(..., description="Target entity or object value")

class TripletExtractionResponse(BaseModel):
    """Container for a list of extracted Triplets from text."""
    triplets: List[Triplet] = Field(default_factory=list, description="List of extracted Triplets")

class KnowledgeAddRequest(BaseModel):
    """Request schema for adding text knowledge to GraphRAG."""
    text: str = Field(..., description="Raw text to extract knowledge from and index")

class KnowledgeQueryRequest(BaseModel):
    """Request schema for querying GraphRAG knowledge base."""
    query: str = Field(..., description="Search query string")
    top_k: int = Field(default=5, description="Number of vector search results to retrieve")

class KnowledgeQueryResponse(BaseModel):
    """Response schema containing retrieved graph context for GraphRAG."""
    query: str
    vector_results: List[str] = Field(default_factory=list)
    graph_triplets: List[Triplet] = Field(default_factory=list)
    combined_context: str = ""
