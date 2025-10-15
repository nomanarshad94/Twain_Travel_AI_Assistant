"""
Unit tests for API Routes - Core request validation
"""
import pytest
from unittest.mock import patch
from src.app import create_app


class TestChatRoutes:
    """Test suite for Chat API Routes - Core functionality"""

    @pytest.fixture
    def app(self):
        """Create Flask test app"""
        app = create_app()
        app.config['TESTING'] = True
        return app

    @pytest.fixture
    def client(self, app):
        """Create test client"""
        return app.test_client()

    def test_send_message_missing_message_field(self, client):
        """Test that missing message field returns 400 Bad Request"""
        with patch('src.routes.chat_routes.chat_service'):
            response = client.post('/chat/message', json={
                'conversation_id': '1'
            })

            assert response.status_code == 400
            assert 'error' in response.json

    def test_send_message_success(self, client):
        """Test sending a message successfully"""
        with patch('src.routes.chat_routes.chat_service') as mock_chat:
            with patch('src.routes.chat_routes.agent_runner') as mock_agent:
                mock_chat.create_conversation.return_value = 1
                mock_chat.get_conversation_history.return_value = []
                mock_agent.run.return_value = "AI response"

                response = client.post('/chat/message', json={
                    'message': 'Test message',
                    'conversation_id': 'new'
                })

                assert response.status_code == 200
                assert 'response' in response.json
                assert 'conversation_id' in response.json

    def test_get_conversations(self, client):
        """Test retrieving all conversations"""
        from datetime import datetime

        mock_conversations = [
            {
                'id': 1,
                'title': 'Test conversation',
                'created_at': datetime(2025, 1, 15, 10, 0, 0),
                'updated_at': datetime(2025, 1, 15, 10, 5, 0)
            }
        ]

        with patch('src.routes.chat_routes.chat_service') as mock_chat:
            mock_chat.get_all_conversations.return_value = mock_conversations

            response = client.get('/chat/conversations')

            assert response.status_code == 200
            assert isinstance(response.json, list)
            assert len(response.json) == 1

    def test_delete_conversation_success(self, client):
        """Test successful conversation deletion"""
        with patch('src.routes.chat_routes.chat_service') as mock_chat:
            mock_chat.delete_conversation.return_value = True

            response = client.delete('/chat/conversations/1')

            assert response.status_code == 200
            assert 'message' in response.json
