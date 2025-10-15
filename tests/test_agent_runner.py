"""
Unit tests for Agent Runner - Message handling logic
"""
import pytest
from unittest.mock import Mock, patch
from langchain_core.messages import HumanMessage, AIMessage
from src.agents.agent_run import AgentRunner


class TestAgentRunner:
    """Test suite for Agent Runner message handling"""

    @pytest.fixture
    def agent_runner(self):
        """Create agent runner instance"""
        with patch('src.agents.agent_run.travel_agent'):
            return AgentRunner()

    def test_convert_history_to_messages(self, agent_runner):
        """Test converting database history to LangChain messages"""
        history = [
            {'content': 'Hello', 'is_user': True, 'timestamp': '2025-01-15', 'id': 1},
            {'content': 'Hi there!', 'is_user': False, 'timestamp': '2025-01-15', 'id': 2}
        ]

        messages = agent_runner._convert_history_to_messages(history)

        assert len(messages) == 2
        assert isinstance(messages[0], HumanMessage)
        assert isinstance(messages[1], AIMessage)
        assert messages[0].content == 'Hello'
        assert messages[1].content == 'Hi there!'

    def test_run_with_conversation_history(self, agent_runner):
        """Test running agent with conversation history"""
        history = [
            {'content': 'Previous question', 'is_user': True, 'timestamp': '2025-01-15', 'id': 1}
        ]

        config = {
            'configurable': {'conversation_history': history}
        }

        mock_response = {
            'messages': [Mock(content='New response')]
        }

        with patch.object(agent_runner.agent, 'invoke', return_value=mock_response) as mock_invoke:
            response = agent_runner.run('New question', config)

            assert response == 'New response'
            # Verify history + new query were passed
            call_inputs = mock_invoke.call_args[0][0]
            assert len(call_inputs['messages']) == 2  # 1 history + 1 new

    def test_run_handles_agent_error(self, agent_runner):
        """Test handling of agent execution errors"""
        with patch.object(agent_runner.agent, 'invoke', side_effect=Exception("Agent error")):
            response = agent_runner.run('Test query')

            assert "error" in response.lower()
            assert "try again" in response.lower()
