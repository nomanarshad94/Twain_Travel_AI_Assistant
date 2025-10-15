"""
Integration tests for Database Operations - Tests actual database queries
Requires a test PostgreSQL database to be running
"""
import pytest
import psycopg2
import os
from src.services.chat_service import ChatService
from src.utils.database import init_connection_pool, init_db, get_db_connection, release_db_connection


@pytest.fixture(scope='session')
def test_db_config():
    """Configure test database connection"""
    return {
        'host': os.getenv('TEST_DB_HOST', 'localhost'),
        'port': os.getenv('TEST_DB_PORT', '5432'),
        'database': os.getenv('TEST_DB_NAME', 'test_travel_advisor_db'),
        'user': os.getenv('TEST_DB_USER', 'postgres'),
        'password': os.getenv('TEST_DB_PASSWORD', 'postgres')
    }


@pytest.fixture(scope='session')
def test_database(test_db_config):
    """
    Set up test database for the session.
    Creates a fresh test database before tests and drops it after.
    """
    # Connect to default postgres database to create test db
    conn = psycopg2.connect(
        host=test_db_config['host'],
        port=test_db_config['port'],
        database='postgres',
        user=test_db_config['user'],
        password=test_db_config['password']
    )
    conn.autocommit = True
    cursor = conn.cursor()

    # Drop test database if exists and create fresh one
    cursor.execute(f"DROP DATABASE IF EXISTS {test_db_config['database']}")
    cursor.execute(f"CREATE DATABASE {test_db_config['database']}")

    cursor.close()
    conn.close()

    # Set environment variables for test database
    os.environ['DB_HOST'] = test_db_config['host']
    os.environ['DB_PORT'] = test_db_config['port']
    os.environ['DB_NAME'] = test_db_config['database']
    os.environ['DB_USER'] = test_db_config['user']
    os.environ['DB_PASSWORD'] = test_db_config['password']

    # Initialize connection pool and tables
    init_connection_pool()
    init_db()

    yield test_db_config

    # Teardown: Drop test database after all tests
    conn = psycopg2.connect(
        host=test_db_config['host'],
        port=test_db_config['port'],
        database='postgres',
        user=test_db_config['user'],
        password=test_db_config['password']
    )
    conn.autocommit = True
    cursor = conn.cursor()
    cursor.execute(f"DROP DATABASE IF EXISTS {test_db_config['database']}")
    cursor.close()
    conn.close()


@pytest.fixture
def clean_database(test_database):
    """
    Clean database before each test.
    Deletes all data but keeps the schema.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Delete all data (CASCADE will handle messages)
    cursor.execute("DELETE FROM conversations")

    conn.commit()
    cursor.close()
    release_db_connection(conn)

    yield

    # Clean up after test
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM conversations")
    conn.commit()
    cursor.close()
    release_db_connection(conn)


class TestDatabaseIntegration:
    """Integration tests for essential database operations"""

    def test_create_conversation_and_retrieve(self, clean_database):
        """Test creating and retrieving a conversation"""
        chat_service = ChatService()

        # Create conversation
        conv_id = chat_service.create_conversation("Test Conversation")
        assert conv_id is not None

        # Retrieve all conversations
        conversations = chat_service.get_all_conversations()
        assert len(conversations) == 1
        assert conversations[0]['title'] == "Test Conversation"

    def test_add_messages_and_get_history(self, clean_database):
        """Test adding messages and retrieving conversation history"""
        chat_service = ChatService()

        conv_id = chat_service.create_conversation("Test")

        # Add messages
        chat_service.add_message(conv_id, "User message", True)
        chat_service.add_message(conv_id, "AI response", False)

        # Get history
        messages = chat_service.get_conversation_history(conv_id)

        assert len(messages) == 2
        assert messages[0]['content'] == "User message"
        assert messages[0]['is_user'] is True
        assert messages[1]['content'] == "AI response"
        assert messages[1]['is_user'] is False

    def test_delete_conversation_cascade(self, clean_database):
        """Test that deleting a conversation also deletes its messages (CASCADE)"""
        chat_service = ChatService()

        conv_id = chat_service.create_conversation("Test")
        chat_service.add_message(conv_id, "Message 1", True)
        chat_service.add_message(conv_id, "Message 2", False)

        # Delete conversation
        result = chat_service.delete_conversation(conv_id)
        assert result is True

        # Verify conversation is deleted
        conversations = chat_service.get_all_conversations()
        assert len(conversations) == 0

        # Verify messages were also deleted (CASCADE)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM messages WHERE conversation_id = %s", (conv_id,))
        count = cursor.fetchone()[0]
        cursor.close()
        release_db_connection(conn)

        assert count == 0

    def test_multiple_conversations_ordering(self, clean_database):
        """Test that conversations are ordered by most recent update"""
        chat_service = ChatService()

        conv_id_1 = chat_service.create_conversation("First")
        conv_id_2 = chat_service.create_conversation("Second")

        # Add message to first conversation (updates its updated_at)
        chat_service.add_message(conv_id_1, "New message", True)

        # Get all conversations
        conversations = chat_service.get_all_conversations()

        # First conversation should now be at the top (most recent update)
        assert len(conversations) == 2
        assert conversations[0]['id'] == conv_id_1
