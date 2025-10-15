import logging
from langgraph.graph import START, END, StateGraph
from langgraph.prebuilt import ToolNode
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import SystemMessage
from src.agents.agent_state import TravelAgentState
from src.agents.tools import get_weather, query_twain_book, extract_locations_from_twain
from src.config import (
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_API_VERSION,
    GPT_DEPLOYMENT_NAME,
    AZURE_OPENAI_TEMPERATURE
)
from src.utils.prompts import TRAVEL_AGENT_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

# Define tools
tools = [get_weather, query_twain_book, extract_locations_from_twain]
weather_tools = [get_weather]
# Initialize Azure OpenAI model with tools
llm = AzureChatOpenAI(
    azure_deployment=GPT_DEPLOYMENT_NAME,
    openai_api_version=AZURE_OPENAI_API_VERSION,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_API_KEY,
    temperature=AZURE_OPENAI_TEMPERATURE
)

# Bind tools to the model
llm_with_tools = llm.bind_tools(tools)


def twain_agent(state: TravelAgentState):
    """This agent will act as a main agent to identifyCall the LLM with tools"""
    messages = state["messages"]
    logger.debug(f"Messages state at twain agent call: {messages}")
    # Add system prompt
    system_message = SystemMessage(content=TRAVEL_AGENT_SYSTEM_PROMPT)
    messages_with_system = [system_message] + messages

    # Call model
    response = llm_with_tools.invoke(messages_with_system)

    return {"messages": [response]}


def should_continue(state: TravelAgentState):
    """Determine if we should continue to tools or end"""
    messages = state["messages"]
    last_message = messages[-1]

    # If there are tool calls, continue to tools otherwise end
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return END


# Create the graph
workflow = StateGraph(TravelAgentState)

# Add nodes
workflow.add_node("agent", twain_agent)
workflow.add_node("tools", ToolNode(tools))

# Add edges
workflow.add_edge(START, "agent")
workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "tools": "tools",
        END: END
    }
)
workflow.add_edge("tools", "agent")

# Compile the graph
app_agent = workflow.compile(debug=False)

logger.info("Travel Agent LangGraph workflow compiled successfully")

# Generate graph visualization
try:
    app_agent.get_graph().draw_mermaid_png(output_file_path="src/agents/travel_agent_graph.png")
    logger.info("LangGraph visualization saved to: src/agents/travel_agent_graph.png")
except Exception as e:
    logger.warning(f"Could not generate graph visualization: {e}")
