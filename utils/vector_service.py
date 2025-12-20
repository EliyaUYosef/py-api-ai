# utils/vector_service.py
import os
import json
import numpy as np
from typing import List, Dict, Optional, Tuple
from openai import OpenAI
from dotenv import load_dotenv
import chromadb
from chromadb.config import Settings

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize ChromaDB
chroma_client = chromadb.Client(Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory="./chroma_db"
))

# Collection name for storing receipt embeddings
COLLECTION_NAME = "receipt_embeddings"

def get_or_create_collection():
    """Get or create the ChromaDB collection for receipts"""
    try:
        collection = chroma_client.get_collection(name=COLLECTION_NAME)
    except:
        collection = chroma_client.create_collection(
            name=COLLECTION_NAME,
            metadata={"description": "Receipt data embeddings"}
        )
    return collection

def text_to_embedding(text: str, model: str = "text-embedding-3-small") -> List[float]:
    """
    Convert text to vector embedding using OpenAI embeddings API
    
    Args:
        text: The text to convert to embedding
        model: The embedding model to use (default: text-embedding-3-small)
    
    Returns:
        List of floats representing the embedding vector
    """
    try:
        response = client.embeddings.create(
            model=model,
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"🧨 Error creating embedding: {e}")
        raise

def store_embedding(
    text: str,
    metadata: Dict,
    embedding_id: Optional[str] = None
) -> str:
    """
    Store text as embedding in vector database
    
    Args:
        text: The text to store
        metadata: Metadata associated with the text (e.g., timestamp, receipt_id)
        embedding_id: Optional unique ID for the embedding
    
    Returns:
        The ID of the stored embedding
    """
    collection = get_or_create_collection()
    
    # Convert text to embedding
    embedding = text_to_embedding(text)
    
    # Generate ID if not provided
    if not embedding_id:
        embedding_id = f"receipt_{metadata.get('timestamp', 'unknown')}"
    
    # Store in ChromaDB
    collection.add(
        embeddings=[embedding],
        documents=[text],
        metadatas=[metadata],
        ids=[embedding_id]
    )
    
    return embedding_id

def query_similar_embeddings(
    query_text: str,
    n_results: int = 3,
    filter_metadata: Optional[Dict] = None
) -> List[Dict]:
    """
    Query similar embeddings based on text query
    
    Args:
        query_text: The text to find similar embeddings for
        n_results: Number of similar results to return
        filter_metadata: Optional metadata filters
    
    Returns:
        List of dictionaries containing similar documents with their metadata
    """
    collection = get_or_create_collection()
    
    # Convert query text to embedding
    query_embedding = text_to_embedding(query_text)
    
    # Query the collection
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        where=filter_metadata if filter_metadata else None
    )
    
    # Format results
    formatted_results = []
    if results['ids'] and len(results['ids'][0]) > 0:
        for i in range(len(results['ids'][0])):
            formatted_results.append({
                'id': results['ids'][0][i],
                'document': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'distance': results['distances'][0][i] if 'distances' in results else None
            })
    
    return formatted_results

def store_receipt_embedding(
    cleaned_data: dict,
    template_structure: dict,
    timestamp: str
) -> str:
    """
    Store receipt data as embedding
    
    Args:
        cleaned_data: Cleaned Document AI data
        template_structure: Expected JSON structure template
        timestamp: Timestamp for this receipt
    
    Returns:
        The ID of the stored embedding
    """
    # Create a combined text representation
    receipt_text = json.dumps(cleaned_data, ensure_ascii=False)
    structure_text = json.dumps(template_structure, ensure_ascii=False)
    combined_text = f"Receipt data: {receipt_text}\n\nExpected structure: {structure_text}"
    
    metadata = {
        "timestamp": timestamp,
        "type": "receipt",
        "has_structure": True
    }
    
    return store_embedding(combined_text, metadata, f"receipt_{timestamp}")

def get_context_from_vectors(
    cleaned_data: dict,
    template_structure: dict,
    n_similar: int = 2
) -> str:
    """
    Get similar receipt contexts from vector database to use as examples
    
    Args:
        cleaned_data: Current receipt data
        template_structure: Expected JSON structure
        n_similar: Number of similar receipts to retrieve
    
    Returns:
        Context string with similar receipt examples
    """
    # Create query text from current receipt
    query_text = json.dumps(cleaned_data, ensure_ascii=False)
    
    # Find similar receipts
    similar_receipts = query_similar_embeddings(
        query_text,
        n_results=n_similar,
        filter_metadata={"type": "receipt"}
    )
    
    if not similar_receipts:
        return ""
    
    # Build context from similar receipts
    context_parts = ["Similar receipt examples from database:"]
    for i, receipt in enumerate(similar_receipts, 1):
        context_parts.append(f"\nExample {i}:")
        context_parts.append(receipt['document'])
    
    return "\n".join(context_parts)

