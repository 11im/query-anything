from typing import List
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from sentence_transformers import SentenceTransformer
import os
import torch
import numpy as np

class KeywordVectorStore:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize the Vector Store with HuggingFace embeddings.
        
        Args:
            model_name: Name of the HuggingFace model to use for embeddings
        """
        self.embedding_model = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={'device': 'cpu'}
        )
        self.vector_store = None
        
    def create_vector_store(self, keywords: List[str], store_name: str = "keyword_store") -> FAISS:
        """
        Create a FAISS vector store from a list of keywords.
        
        Args:
            keywords: List of keywords to store
            store_name: Name of the store for saving/loading
            
        Returns:
            FAISS vector store instance
        """
        # Create the vector store
        print(f"Creating vector store with {len(keywords)} keywords...")
        self.vector_store = FAISS.from_texts(
            texts=keywords,
            embedding=self.embedding_model
        )
        
        # Save the vector store
        self.vector_store.save_local(store_name)
        print(f"Vector store saved to {store_name}")
        
        return self.vector_store
    
    def load_vector_store(self, store_name: str = "keyword_store") -> FAISS:
        """
        Load a saved FAISS vector store.
        
        Args:
            store_name: Name of the store to load
            
        Returns:
            Loaded FAISS vector store instance
        """
        if os.path.exists(store_name):
            self.vector_store = FAISS.load_local(
                store_name,
                self.embedding_model
            )
            print(f"Vector store loaded from {store_name}")
            return self.vector_store
        else:
            raise FileNotFoundError(f"No vector store found at {store_name}")
    
    def search_similar_keywords(self, query: str, k: int = 5) -> List[tuple]:
        """
        Search for similar keywords in the vector store.
        
        Args:
            query: Search query
            k: Number of results to return
            
        Returns:
            List of (keyword, score) tuples
        """
        if self.vector_store is None:
            raise ValueError("Vector store not initialized. Create or load a store first.")
            
        results = self.vector_store.similarity_search_with_score(query, k=k)
        return [(doc.page_content, score) for doc, score in results]

    def add_keywords(self, new_keywords: List[str]):
        """
        Add new keywords to the existing vector store.
        
        Args:
            new_keywords: List of new keywords to add
        """
        if self.vector_store is None:
            raise ValueError("Vector store not initialized. Create or load a store first.")
            
        print(f"Adding {len(new_keywords)} new keywords to the store...")
        self.vector_store.add_texts(new_keywords)
        print("Keywords added successfully")

    def get_total_keywords(self) -> int:
        """
        Get the total number of keywords in the store.
        
        Returns:
            Total number of keywords
        """
        if self.vector_store is None:
            return 0
        return len(self.vector_store.docstore._dict)
    
    
def load_vector_store(store_path: str = "keyword_store"):
    """
    Load a saved FAISS vector store.
    
    Args:
        store_path: Path to the stored FAISS index
        
    Returns:
        Loaded FAISS vector store instance
    """
    # Initialize the embedding model (must match the one used for creation)
    embedding_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': 'cuda' if torch.cuda.is_available() else 'cpu'}
    )
    
    # Load the vector store
    vector_store = FAISS.load_local(store_path, embedding_model,allow_dangerous_deserialization=True)
    return vector_store

def search_keywords(vector_store, query: str, k: int = 5):
    """
    Search for similar keywords in the loaded vector store.
    
    Args:
        vector_store: Loaded FAISS vector store
        query: Search query
        k: Number of results to return
    """
    results = vector_store.similarity_search_with_score(query, k=k)
    
    print(f"\nSearch results for '{query}':")
    for doc, score in results:
        similarity = 1 - score  # Convert distance to similarity
        print(f"- {doc.page_content} (similarity: {similarity:.3f})")
    
    return results