from langgraph.graph import MessagesState


class TravelAgentState(MessagesState):
    """
    State definition for the Travel Advisor Agent.
    Extends MessagesState which provides:
    - messages: List[BaseMessage] - Automatic conversation history management

    MessagesState automatically handles conversation history, so we don't need additional fields for simple
    tool-based agents.
    """
    pass
