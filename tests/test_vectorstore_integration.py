"""
Integration tests for Vector Store Operations - Tests actual FAISS operations
Requires the book data and FAISS index to exist
"""
import pytest
from src.services.book_vectorstore_service import BookVectorStoreService
from langchain_core.documents import Document


@pytest.fixture(scope='session')
def vectorstore_service():
    """
    Create vector store service for testing.
    This will use actual embedding model and FAISS index.
    """
    service = BookVectorStoreService()
    yield service


class TestVectorStoreIntegration:
    """Integration tests for essential vector store operations"""

    def test_vectorstore_initializes_successfully(self, vectorstore_service):
        """Test that vector store initializes without errors"""
        assert vectorstore_service is not None
        assert vectorstore_service.vector_store is not None
        assert vectorstore_service.embeddings is not None

    def test_similarity_search_returns_relevant_results(self, vectorstore_service):
        """Test that similarity search returns relevant documents with content"""
        query = "What did Twain think about Rome?"

        results = vectorstore_service.similarity_search(query, k=5)

        assert len(results) > 0
        assert len(results) <= 5

        # Verify documents have content and metadata
        for doc in results:
            assert isinstance(doc, Document)
            assert hasattr(doc, 'page_content')
            assert len(doc.page_content) > 0
            assert hasattr(doc, 'metadata')
            assert isinstance(doc.metadata, dict)

    def test_search_for_specific_locations(self, vectorstore_service):
        """Test searching for locations Twain actually visited"""
        locations = ["Rome", "Paris", "Venice"]

        for location in locations:
            results = vectorstore_service.similarity_search(location, k=3)

            # Should return results for known locations in the book
            assert len(results) > 0, f"No results found for {location}"

    def test_get_retriever_functionality(self, vectorstore_service):
        """Test that retriever can be obtained and works correctly"""
        retriever = vectorstore_service.get_retriever(search_kwargs={'k': 5})

        assert retriever is not None

        # Test retriever actually works
        results = retriever.invoke("Twain's travels in Europe")

        assert isinstance(results, list)
        assert len(results) > 0
        assert len(results) <= 5
