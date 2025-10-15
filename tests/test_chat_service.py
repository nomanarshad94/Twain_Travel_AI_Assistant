"""
Unit tests for Chat Service - Core business logic
"""
import pytest
from unittest.mock import Mock, patch
from src.services.chat_service import ChatService


class TestChatService:
    """Test suite for Chat Service core functionality"""

    @pytest.fixture
    def chat_service(self):
        """Create chat service instance"""
        return ChatService()

    @pytest.fixture
    def mock_db_cursor(self):
        """Mock database cursor"""
        cursor = Mock()
        return cursor

    @pytest.fixture
    def mock_db_connection(self, mock_db_cursor):
        """Mock database connection"""
        conn = Mock()
        conn.cursor.return_value = mock_db_cursor
        conn.commit = Mock()
        return conn

    def test_create_conversation(self, chat_service, mock_db_connection, mock_db_cursor):
        """Test creating a new conversation"""
        mock_db_cursor.fetchone.return_value = (1,)

        with patch('src.services.chat_service.get_db_connection', return_value=mock_db_connection):
            with patch('src.services.chat_service.release_db_connection'):
                conversation_id = chat_service.create_conversation("Test Conversation")

                assert conversation_id == 1
                mock_db_cursor.execute.assert_called_once()
                mock_db_connection.commit.assert_called_once()

    def test_add_message(self, chat_service, mock_db_connection, mock_db_cursor):
        """Test adding a message to a conversation"""
        mock_db_cursor.fetchone.return_value = (42,)

        with patch('src.services.chat_service.get_db_connection', return_value=mock_db_connection):
            with patch('src.services.chat_service.release_db_connection'):
                message_id = chat_service.add_message(
                    conversation_id=1,
                    content="Test message",
                    is_user=True
                )

                assert message_id == 42
                assert mock_db_cursor.execute.call_count == 2  # Insert message + Update conversation
                mock_db_connection.commit.assert_called_once()

    def test_get_conversation_history(self, chat_service, mock_db_connection, mock_db_cursor):
        """Test retrieving conversation message history"""
        mock_db_cursor.fetchall.return_value = [
            (1, "Hello", True, "2025-01-15 10:00:00"),
            (2, "Hi there!", False, "2025-01-15 10:00:05")
        ]

        with patch('src.services.chat_service.get_db_connection', return_value=mock_db_connection):
            with patch('src.services.chat_service.release_db_connection'):
                messages = chat_service.get_conversation_history(1)

                assert len(messages) == 2
                assert messages[0]['content'] == "Hello"
                assert messages[0]['is_user'] is True
                assert messages[1]['is_user'] is False

    def test_delete_conversation(self, chat_service, mock_db_connection, mock_db_cursor):
        """Test deleting a conversation"""
        with patch('src.services.chat_service.get_db_connection', return_value=mock_db_connection):
            with patch('src.services.chat_service.release_db_connection'):
                result = chat_service.delete_conversation(1)

                assert result is True
                mock_db_cursor.execute.assert_called_once()
                mock_db_connection.commit.assert_called_once()
