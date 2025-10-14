from typing import List, Dict, Optional
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from src.config import FAISS_INDEX_PATH, EMBEDDING_MODEL_NAME, EMBEDDING_MODEL_DEVICE, TOP_K_RESULTS
from src.data.gutenberg_downloader import GutenbergDownloader
import logging
import os

logger = logging.getLogger(__name__)


class BookVectorStoreService:
    """
    In-memory FAISS vector store service for 'The Innocents Abroad'
    with chapter metadata support using Hugging Face embeddings
    """

    def __init__(self):
        """Initialize the vector store service"""
        self.embeddings = None
        self.vector_store = None
        self.downloader = GutenbergDownloader()

        # Initialize on first use
        self._setup()

    def _setup(self):
        """Set up embeddings and load vector store"""
        try:
            logger.info("Initializing Book Vector Store Service...")

            # Initialize Hugging Face Embeddings with embedding model
            model_name = EMBEDDING_MODEL_NAME
            model_kwargs = {'device': EMBEDDING_MODEL_DEVICE}
            encode_kwargs = {'normalize_embeddings': True}

            self.embeddings = HuggingFaceEmbeddings(
                model_name=model_name,
                model_kwargs=model_kwargs,
                encode_kwargs=encode_kwargs,
                show_progress=True
            )

            logger.info(f"Loaded embedding model: {model_name}")

            # Download book if not already downloaded
            if not self.downloader.is_book_downloaded():
                logger.info("Book not found. Downloading 'The Innocents Abroad'...")
                self.downloader.download_innocents_abroad()

            # Load and index chunks
            self._load_and_index_chunks()

            logger.info("Book Vector Store Service initialized successfully")

        except Exception as e:
            logger.error(f"Error setting up Book Vector Store Service: {e}")
            raise

    def _load_and_index_chunks(self):
        """Load processed chunks and create/load FAISS index"""
        try:
            # Check if FAISS index already exists on disk
            if os.path.exists(FAISS_INDEX_PATH) and os.path.isdir(FAISS_INDEX_PATH):
                logger.info("Loading existing FAISS index from disk...")
                self.vector_store = FAISS.load_local(
                    FAISS_INDEX_PATH,
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                logger.info("FAISS index loaded successfully from disk")
                return

            # If index doesn't exist, create it
            logger.info("FAISS index not found. Creating new index...")

            # Load chunks from JSON
            chunks = self.downloader.load_book_chunks()

            if not chunks:
                raise ValueError("No book chunks found. Please download and process the book first.")

            logger.info(f"Loaded {len(chunks)} chunks from 'The Innocents Abroad'")

            # Convert chunks to LangChain Documents with metadata
            documents = []
            for chunk in chunks:
                doc = Document(
                    page_content=chunk['text'],
                    metadata={
                        'chunk_id': chunk['id'],
                        'chapter_number': chunk.get('chapter_number', 'Unknown'),
                        'chapter_title': chunk.get('chapter_title', 'Unknown'),
                        'chunk_index': chunk['chunk_index'],
                        'chunk_in_chapter': chunk.get('chunk_in_chapter', 0)
                    }
                )
                documents.append(doc)

            # Create FAISS vector store
            logger.info("Creating FAISS index... This may take a moment.")
            self.vector_store = FAISS.from_documents(
                documents=documents,
                embedding=self.embeddings
            )

            # Save to disk for future use
            logger.info(f"Saving FAISS index to disk: {FAISS_INDEX_PATH}")
            self.vector_store.save_local(FAISS_INDEX_PATH)

            logger.info(f"Created and saved FAISS index with {len(documents)} documents")

        except Exception as e:
            logger.error(f"Error loading and indexing chunks: {e}")
            raise

    def similarity_search(
        self,
        query: str,
        k: int = TOP_K_RESULTS,
        filter_chapter: Optional[str] = None
    ) -> List[Document]:
        """
        Perform similarity search on the book

        Args:
            query: Search query
            k: Number of results to return
            filter_chapter: Optional chapter number to filter by

        Returns:
            List of relevant documents with metadata
        """
        if not self.vector_store:
            raise ValueError("Vector store not initialized")

        try:
            # Perform similarity search
            if filter_chapter:
                # Filter by chapter if specified
                results = self.vector_store.similarity_search(
                    query,
                    k=k * 2,  # Get more results to filter
                    filter={"chapter_number": filter_chapter}
                )
                results = results[:k]  # Return only k results
            else:
                results = self.vector_store.similarity_search(query, k=k)

            logger.info(f"Found {len(results)} relevant passages for query: '{query[:50]}...'")
            return results

        except Exception as e:
            logger.error(f"Error during similarity search: {e}")
            return []

    def similarity_search_with_score(
        self,
        query: str,
        k: int = TOP_K_RESULTS
    ) -> List[tuple[Document, float]]:
        """
        Perform similarity search with relevance scores

        Args:
            query: Search query
            k: Number of results to return

        Returns:
            List of tuples (document, score)
        """
        if not self.vector_store:
            raise ValueError("Vector store not initialized")

        try:
            results = self.vector_store.similarity_search_with_score(query, k=k)
            logger.info(f"Found {len(results)} passages with scores for query: '{query[:50]}...'")
            return results

        except Exception as e:
            logger.error(f"Error during similarity search with score: {e}")
            return []

    def get_retriever(self, search_kwargs: Optional[Dict] = None):
        """
        Get a LangChain retriever for the vector store

        Args:
            search_kwargs: Optional search parameters (e.g., {'k': 4})

        Returns:
            LangChain retriever
        """
        if not self.vector_store:
            raise ValueError("Vector store not initialized")

        search_kwargs = search_kwargs or {'k': TOP_K_RESULTS}
        return self.vector_store.as_retriever(search_kwargs=search_kwargs)
