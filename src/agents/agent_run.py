import logging
from src.agents.travel_agent import app_agent as travel_agent
from src.config import AGENT_RECURSION_LIMIT
from typing import Dict, Any, Optional, List
from langchain_core.messages import HumanMessage, AIMessage

logger = logging.getLogger(__name__)


class AgentRunner:
    """
    Runner class for the Travel Advisor Agent.
    Provides a simple interface to invoke the agent with queries.
    """

    def __init__(self):
        """Initialize the agent runner"""
        self.agent = travel_agent
        logger.info("Agent Runner initialized")

    def _convert_history_to_messages(self, conversation_history: List[Dict]) -> List:
        """
        Convert conversation history from database format to LangChain messages

        Args:
            conversation_history: List of message dictionaries from database
                Format: [{'content': str, 'is_user': bool, 'timestamp': datetime, 'id': int}]

        Returns:
            List of LangChain message objects (HumanMessage, AIMessage)
        """
        messages = []
        for msg in conversation_history:
            if msg['is_user']:
                messages.append(HumanMessage(content=msg['content']))
            else:
                messages.append(AIMessage(content=msg['content']))
        return messages

    def run(self, query: str, config: Optional[Dict[str, Any]] = None) -> str:
        """
        Run the agent with a user query and conversation history.

        Args:
            query: User's question or request
            config: Optional configuration including:
                - configurable.conversation_history: List of previous messages
                - recursion_limit: Max recursion depth

        Returns:
            Response message from the agent
        """

        config = config or {}
        if "recursion_limit" not in config:
            config["recursion_limit"] = AGENT_RECURSION_LIMIT

        # Build message list with conversation history
        messages = []

        # Convert and add conversation history if provided
        if "configurable" in config and "conversation_history" in config["configurable"]:
            conversation_history = config["configurable"]["conversation_history"]
            if conversation_history:
                messages = self._convert_history_to_messages(conversation_history)
                logger.info(f"Loaded {len(messages)} messages from conversation history")

        # Add current user query
        messages.append(HumanMessage(content=query))

        # Create input with full message history
        inputs = {"messages": messages}

        try:
            # Invoke the agent with full conversation context
            response = self.agent.invoke(inputs, config)

            # Extract the final message
            if response and "messages" in response and len(response["messages"]) > 0:
                final_message = response["messages"][-1]
                if hasattr(final_message, "content"):
                    return final_message.content

            return "I'm sorry, I couldn't generate a response. Please try again."

        except Exception as e:
            logger.error(f"Error running agent: {e}", exc_info=True)
            return "I apologize, but I encountered an error while processing your request. Please try again."
