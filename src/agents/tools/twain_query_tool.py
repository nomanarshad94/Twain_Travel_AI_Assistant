import logging
from langchain_core.tools import tool
from src.services.book_vectorstore_service import BookVectorStoreService
from src.config import TOP_K_RESULTS

logger = logging.getLogger(__name__)

# Initialize book vector store service (singleton)
book_service = BookVectorStoreService()


@tool
def query_twain_book(query: str) -> str:
    """
    Search Mark Twain's 'The Innocents Abroad' for information about locations, experiences, and insights.

    Use this tool when the user asks about:
    - What Mark Twain said or thought about a specific place or topic
    - Twain's experiences and observations from his travels
    - Descriptions of locations Twain visited
    - Twain's opinions, humor, or commentary about cultures and places

    Args:
        query: A natural language query about Twain's book
               (e.g., "What did Twain say about the Sphinx?", "Twain's visit to Italy")

    Returns:
        Relevant passages from 'The Innocents Abroad' with chapter information
        that answer the query.

    Example:
        query_twain_book("What did Twain think about the Sphinx?")
        -> Returns passages where Twain describes the Sphinx with chapter references
    """
    try:
        logger.info(f"Searching Twain's book for: {query}")

        # Perform similarity search (get top 3 most relevant passages)
        results = book_service.similarity_search(query, k=TOP_K_RESULTS)

        if not results:
            return (
                f"I couldn't find specific information about '{query}' in 'The Innocents Abroad'. "
                "This might be outside the scope of Twain's travel memoir."
            )

        # Format the results with chapter information
        response_parts = [f"Here's what Mark Twain wrote about that in 'The Innocents Abroad':\n"]

        for i, doc in enumerate(results, 1):
            chapter_num = doc.metadata.get('chapter_number', 'Unknown')
            chapter_title = doc.metadata.get('chapter_title', '')

            chapter_ref = f"Chapter {chapter_num}"
            if chapter_title:
                chapter_ref += f" - {chapter_title}"

            passage = doc.page_content.strip()

            response_parts.append(f"\n\n**[{chapter_ref}]**")
            response_parts.append(f"{passage}\n\n")

        response = "\n\n".join(response_parts)
        return response

    except Exception as e:
        logger.error(f"Error in query_twain_book tool: {e}")
        return (
            f"I encountered an error while searching for information about '{query}' "
            "in Twain's book. Please try rephrasing your question."
        )


@tool
def extract_locations_from_twain(region: str) -> str:
    """
    Extract specific locations that Mark Twain visited in a given region from 'The Innocents Abroad'.

    Use this tool when the user wants to know which specific cities or places Twain visited
    in a particular country or region.

    Args:
        region: The country or region name (e.g., "Italy", "France")

    Returns:
        A list of specific locations/cities that Twain visited in that region, extracted from the book.

    Example:
        extract_locations_from_twain("Italy") -> Returns relevant passages with cities like Venice, Milan,
        Rome that Twain visited
    """
    try:
        logger.info(f"Extracting locations Twain visited in: {region}")

        # Search for passages mentioning the region
        query = f"places cities locations Twain visited in {region}"
        results = book_service.similarity_search(query, k=TOP_K_RESULTS)

        if not results:
            return f"I couldn't find specific information about places Twain visited in {region}."

        # Combine passages to extract location names
        combined_text = "\n\n".join([doc.page_content for doc in results])

        # For now, return the relevant passages
        # TODO: extract NER based location names from combined_text for accurate listing
        response_parts = [f"Based on 'The Innocents Abroad', here are references to Twain's travels in {region}:\n\n"]

        for i, doc in enumerate(results, 1):
            chapter_num = doc.metadata.get('chapter_number', 'Unknown')
            passage = doc.page_content.strip()  # [:200] + "..."  # Shortened excerpt to save tokens

            response_parts.append(f"\n\n{i}. [Chapter {chapter_num}] {passage}")

        response = "\n\n".join(response_parts)
        return response

    except Exception as e:
        logger.error(f"Error in extract_locations_from_twain tool: {e}")
        return f"I encountered an error while extracting locations from {region}."
