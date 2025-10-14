from flask import Blueprint, request, jsonify, render_template
from src.services.chat_service import ChatService
from src.agents.agent_run import AgentRunner
from src.config import AGENT_RECURSION_LIMIT
from src.utils.constants import (
    HTTP_OK,
    HTTP_BAD_REQUEST,
    HTTP_NOT_FOUND,
    HTTP_INTERNAL_SERVER_ERROR,
    ERROR_NO_MESSAGE,
    ERROR_CONVERSATION_NOT_FOUND,
    ERROR_AGENT_ERROR,
    ERROR_DATABASE_ERROR,
    MSG_NO_MESSAGE,
    MSG_CONVERSATION_NOT_FOUND,
    MSG_CONVERSATION_DELETED,
    MSG_AGENT_ERROR,
    DEFAULT_CONVERSATION_TITLE_LENGTH,
    AGENT_ERROR_RESPONSE
)
import logging

logger = logging.getLogger(__name__)

chat_bp = Blueprint('chat', __name__)
chat_service = ChatService()
agent_runner = AgentRunner()


@chat_bp.route('/', methods=['GET'])
def chat_page():
    """Render the main chat interface"""
    try:
        conversations = chat_service.get_all_conversations()
        conversation_id = request.args.get('conversation_id')

        messages = []
        if conversation_id:
            messages = chat_service.get_conversation_history(int(conversation_id))

        return render_template(
            'chat.html',
            conversations=conversations,
            messages=messages,
            current_conversation_id=conversation_id
        )
    except Exception as e:
        logger.error(f"Error rendering chat page: {e}")
        return jsonify({
            "error": ERROR_DATABASE_ERROR,
            "message": "Failed to load chat interface"
        }), HTTP_INTERNAL_SERVER_ERROR


@chat_bp.route('/message', methods=['POST'])
def send_message():
    """Handle sending a message and getting agent response"""
    try:
        data = request.get_json()
        message = data.get('message')
        conversation_id = data.get('conversation_id')

        if not message:
            return jsonify({
                "error": ERROR_NO_MESSAGE,
                "message": MSG_NO_MESSAGE
            }), HTTP_BAD_REQUEST

        # Create new conversation if needed
        if not conversation_id or conversation_id == 'new':
            title = message[:DEFAULT_CONVERSATION_TITLE_LENGTH]
            if len(message) > DEFAULT_CONVERSATION_TITLE_LENGTH:
                title += "..."
            conversation_id = chat_service.create_conversation(title)

        # Get conversation history for context
        conversation_history = chat_service.get_conversation_history(conversation_id)

        # Save user message
        chat_service.add_message(conversation_id, message, is_user=True)

        # Get agent response
        try:
            response = ""
            for chunk in agent_runner.run(
                message,
                config={
                    "configurable": {"conversation_history": conversation_history},
                    "recursion_limit": AGENT_RECURSION_LIMIT
                }
            ):
                response += chunk

            if not response:
                response = AGENT_ERROR_RESPONSE

        except Exception as agent_error:
            logger.error(f"Agent error: {agent_error}")
            response = AGENT_ERROR_RESPONSE

        # Save AI response
        chat_service.add_message(conversation_id, response, is_user=False)

        return jsonify({
            "response": response,
            "conversation_id": conversation_id
        }), HTTP_OK

    except Exception as e:
        logger.error(f"Error in send_message: {e}")
        return jsonify({
            "error": ERROR_AGENT_ERROR,
            "message": MSG_AGENT_ERROR
        }), HTTP_INTERNAL_SERVER_ERROR


@chat_bp.route('/conversations', methods=['GET'])
def get_conversations():
    """Get all conversations"""
    try:
        conversations = chat_service.get_all_conversations()

        # Format for JSON response
        formatted_conversations = []
        for conv in conversations:
            formatted_conversations.append({
                'id': conv['id'],
                'title': conv['title'],
                'created_at': conv['created_at'].isoformat() if conv['created_at'] else None,
                'updated_at': conv['updated_at'].isoformat() if conv['updated_at'] else None
            })

        return jsonify(formatted_conversations), HTTP_OK

    except Exception as e:
        logger.error(f"Error getting conversations: {e}")
        return jsonify({
            "error": ERROR_DATABASE_ERROR,
            "message": "Failed to retrieve conversations"
        }), HTTP_INTERNAL_SERVER_ERROR


@chat_bp.route('/conversations/<int:conversation_id>', methods=['GET'])
def get_conversation_messages(conversation_id):
    """Get messages for a specific conversation"""
    try:
        messages = chat_service.get_conversation_history(conversation_id)

        if not messages and conversation_id:
            return jsonify({
                "error": ERROR_CONVERSATION_NOT_FOUND,
                "message": MSG_CONVERSATION_NOT_FOUND
            }), HTTP_NOT_FOUND

        # Format for JSON response
        formatted_messages = []
        for msg in messages:
            formatted_messages.append({
                'id': msg['id'],
                'content': msg['content'],
                'is_user': msg['is_user'],
                'timestamp': msg['timestamp'].isoformat() if msg['timestamp'] else None
            })

        return jsonify(formatted_messages), HTTP_OK

    except Exception as e:
        logger.error(f"Error getting conversation messages: {e}")
        return jsonify({
            "error": ERROR_DATABASE_ERROR,
            "message": "Failed to retrieve messages"
        }), HTTP_INTERNAL_SERVER_ERROR


@chat_bp.route('/conversations/<int:conversation_id>', methods=['DELETE'])
def delete_conversation(conversation_id):
    """Delete a conversation"""
    try:
        success = chat_service.delete_conversation(conversation_id)

        if not success:
            return jsonify({
                "error": ERROR_CONVERSATION_NOT_FOUND,
                "message": MSG_CONVERSATION_NOT_FOUND
            }), HTTP_NOT_FOUND

        return jsonify({
            "message": MSG_CONVERSATION_DELETED
        }), HTTP_OK

    except Exception as e:
        logger.error(f"Error deleting conversation: {e}")
        return jsonify({
            "error": ERROR_DATABASE_ERROR,
            "message": "Failed to delete conversation"
        }), HTTP_INTERNAL_SERVER_ERROR


@chat_bp.route('/new', methods=['POST'])
def new_conversation():
    """Create a new conversation"""
    return jsonify({
        'conversation_id': None
    }), HTTP_OK
