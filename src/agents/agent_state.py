from typing import Literal, List, Dict
from langgraph.graph import MessagesState


class TravelAgentState(MessagesState):
    """
    State definition for the Travel Advisor Agent.

    Extends MessagesState to include conversation history and additional context.
    """
    # Query routing
    query_type: Literal["weather", "twain_book", "combined", "out_of_domain", "unknown"]

    # Extracted information
    locations: List[str]  # Extracted location names from query
    region: str  # Region/country mentioned (for Twain queries)

    # Tool results
    weather_data: Dict  # Weather information from API
    book_passages: str  # Relevant passages from Twain's book

    # Response generation
    final_answer: str  # Generated final response to user

    # Metadata
    conversation_history: str  # Previous conversation context
    requires_both_sources: bool  # Whether query needs both weather and book data
