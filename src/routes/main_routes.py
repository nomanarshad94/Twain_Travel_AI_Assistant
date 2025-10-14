from flask import Blueprint, redirect, url_for, jsonify
from src.utils.constants import HTTP_OK


main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Redirect to the main chat interface"""
    return redirect(url_for('chat.chat_page'))


@main_bp.route('/health')
def health_check():
    """Returns a simple JSON response indicating the service is healthy."""
    return jsonify({
        "status": "healthy",
        "service": "Travel Advisor AI"
    }), HTTP_OK
