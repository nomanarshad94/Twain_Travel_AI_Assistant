"""
Constants for the Travel Application
Including HTTP status codes, error codes, and application-level constants
"""

# HTTP Status Codes
HTTP_OK = 200
HTTP_CREATED = 201
HTTP_BAD_REQUEST = 400
HTTP_UNAUTHORIZED = 401
HTTP_FORBIDDEN = 403
HTTP_NOT_FOUND = 404
HTTP_INTERNAL_SERVER_ERROR = 500

# Error Codes
ERROR_NO_MESSAGE = "NO_MESSAGE_PROVIDED"
ERROR_CONVERSATION_NOT_FOUND = "CONVERSATION_NOT_FOUND"
ERROR_MESSAGE_NOT_FOUND = "MESSAGE_NOT_FOUND"
ERROR_INVALID_CONVERSATION_ID = "INVALID_CONVERSATION_ID"
ERROR_DATABASE_ERROR = "DATABASE_ERROR"
ERROR_AGENT_ERROR = "AGENT_ERROR"
ERROR_WEATHER_API_ERROR = "WEATHER_API_ERROR"
ERROR_BOOK_NOT_FOUND = "BOOK_NOT_FOUND"
ERROR_INVALID_REQUEST = "INVALID_REQUEST"

# Error Messages
MSG_NO_MESSAGE = "No message provided in request"
MSG_CONVERSATION_NOT_FOUND = "Conversation not found"
MSG_CONVERSATION_DELETED = "Conversation deleted successfully"
MSG_DATABASE_ERROR = "Database operation failed"
MSG_AGENT_ERROR = "Error processing request with agent"
MSG_INVALID_CONVERSATION_ID = "Invalid conversation ID format"

# Application Constants
DEFAULT_CONVERSATION_TITLE_LENGTH = 35
DEFAULT_RECURSION_LIMIT = 10

# Agent Response Messages
AGENT_ERROR_RESPONSE = "I apologize, but I encountered an error while processing your request. Please try again."
AGENT_OUT_OF_DOMAIN_RESPONSE = "I specialize in Mark Twain's 'The Innocents Abroad' and/or current weather " \
                               "information. I cannot answer questions outside this scope. "

