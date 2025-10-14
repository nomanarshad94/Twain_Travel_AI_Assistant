from src.utils.database import get_db_connection, release_db_connection
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class ChatService:
    """Service for managing conversations and messages"""

    def create_conversation(self, title: str) -> int:
        """
        Create a new conversation

        Args:
            title: Title for the conversation

        Returns:
            conversation_id
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute(
                "INSERT INTO conversations (title) VALUES (%s) RETURNING id",
                (title,)
            )
            conversation_id = cursor.fetchone()[0]

            conn.commit()
            cursor.close()
            release_db_connection(conn)

            logger.info(f"Created conversation: {conversation_id}")
            return conversation_id

        except Exception as e:
            logger.error(f"Error creating conversation: {e}")
            raise

    def get_all_conversations(self) -> List[Dict]:
        """
        Get all conversations ordered by updated_at

        Returns:
            List of conversation dictionaries
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute(
                "SELECT id, title, created_at, updated_at FROM conversations ORDER BY updated_at DESC"
            )
            rows = cursor.fetchall()

            conversations = []
            for row in rows:
                conversations.append({
                    'id': row[0],
                    'title': row[1],
                    'created_at': row[2],
                    'updated_at': row[3]
                })

            cursor.close()
            release_db_connection(conn)

            return conversations

        except Exception as e:
            logger.error(f"Error getting conversations: {e}")
            return []

    def get_conversation_history(self, conversation_id: int) -> List[Dict]:
        """
        Get all messages for a conversation

        Args:
            conversation_id: ID of the conversation

        Returns:
            List of message dictionaries
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute(
                """SELECT id, content, is_user, timestamp
                   FROM messages
                   WHERE conversation_id = %s
                   ORDER BY timestamp ASC""",
                (conversation_id,)
            )
            rows = cursor.fetchall()

            messages = []
            for row in rows:
                messages.append({
                    'id': row[0],
                    'content': row[1],
                    'is_user': row[2],
                    'timestamp': row[3]
                })

            cursor.close()
            release_db_connection(conn)

            return messages

        except Exception as e:
            logger.error(f"Error getting conversation history: {e}")
            return []

    def add_message(self, conversation_id: int, content: str, is_user: bool) -> int:
        """
        Add a message to a conversation

        Args:
            conversation_id: ID of the conversation
            content: Message content
            is_user: True if message is from user, False if from AI

        Returns:
            message_id
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Insert message
            cursor.execute(
                "INSERT INTO messages (conversation_id, content, is_user) VALUES (%s, %s, %s) RETURNING id",
                (conversation_id, content, is_user)
            )
            message_id = cursor.fetchone()[0]

            # Update conversation updated_at timestamp
            cursor.execute(
                "UPDATE conversations SET updated_at = CURRENT_TIMESTAMP WHERE id = %s",
                (conversation_id,)
            )

            conn.commit()
            cursor.close()
            release_db_connection(conn)

            return message_id

        except Exception as e:
            logger.error(f"Error adding message: {e}")
            raise

    def delete_conversation(self, conversation_id: int) -> bool:
        """
        Delete a conversation and all its messages

        Args:
            conversation_id: ID of the conversation

        Returns:
            True if successful
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("DELETE FROM conversations WHERE id = %s", (conversation_id,))

            conn.commit()
            cursor.close()
            release_db_connection(conn)

            logger.info(f"Deleted conversation: {conversation_id}")
            return True

        except Exception as e:
            logger.error(f"Error deleting conversation: {e}")
            return False
