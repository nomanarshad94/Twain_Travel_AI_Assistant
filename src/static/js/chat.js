// chat.js - Travel Advisor Chat UI Logic

// Get initial conversation ID from data attribute
const initialConv = document.getElementById('currentConversation')?.dataset?.conversationId;
let currentConversationId = initialConv || null;
let isProcessing = false;

document.addEventListener('DOMContentLoaded', function() {
    const chatHistory = document.getElementById('chatHistory');
    const userInput = document.getElementById('userInput');
    const sendButton = document.getElementById('sendButton');
    const newChatBtn = document.getElementById('newChat');
    const errorMessage = document.getElementById('errorMessage');

    // Load existing messages if conversation_id is set
    if (currentConversationId) {
        loadConversation(currentConversationId);
    }

    // Example query buttons
    document.querySelectorAll('.example-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            userInput.value = this.dataset.query;
            sendMessage();
        });
    });

    // Load conversation when clicking on sidebar
    document.querySelectorAll('.conv-link').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            currentConversationId = this.getAttribute('data-conv-id');
            loadConversation(currentConversationId);
        });
    });

    // Delete conversation
    document.querySelectorAll('.delete-conv-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.stopPropagation();
            e.preventDefault();

            const convId = this.getAttribute('data-conv-id');
            if (!confirm("Are you sure you want to delete this conversation?")) return;

            fetch(`/chat/conversations/${convId}`, {
                method: 'DELETE',
                headers: { 'Content-Type': 'application/json' }
            })
            .then(response => {
                if (!response.ok) throw new Error('Failed to delete conversation');
                // Remove from DOM
                const listItem = this.closest('li');
                if (listItem) listItem.remove();

                // Clear chat if currently viewing deleted conversation
                if (currentConversationId === convId) {
                    chatHistory.innerHTML = '<div class="welcome-message"><h3>Conversation deleted</h3><p>Start a new conversation!</p></div>';
                    currentConversationId = null;
                    window.history.pushState({}, '', '/chat/');
                }
            })
            .catch(error => {
                console.error('Delete conversation error:', error);
                showError(error.message || 'Failed to delete conversation');
            });
        });
    });

    // New conversation button
    newChatBtn.addEventListener('click', function() {
        currentConversationId = null;
        chatHistory.innerHTML = '';
        window.location.href = '/chat/';
    });

    function loadConversation(convId) {
        // Update URL
        window.history.pushState({}, '', `/chat/?conversation_id=${convId}`);

        fetch(`/chat/conversations/${convId}`)
        .then(response => {
            if (!response.ok) throw new Error('Failed to load conversation');
            return response.json();
        })
        .then(messages => {
            chatHistory.innerHTML = '';
            messages.forEach(msg => {
                if (msg.content && msg.content.trim()) {
                    addMessage(msg.content, msg.is_user, msg.timestamp);
                }
            });
        })
        .catch(error => {
            console.error('Load conversation error:', error);
            showError(error.message || 'Failed to load conversation');
        });
    }

    function addMessage(content, isUser, timestamp = new Date().toISOString()) {
        if (!content || !content.trim()) return;

        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user-message' : 'ai-message'}`;

        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'message-avatar';
        avatarDiv.innerHTML = isUser ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>';

        const contentWrapper = document.createElement('div');
        contentWrapper.className = 'message-wrapper';

        const timeElement = document.createElement('div');
        timeElement.className = 'message-time';
        timeElement.textContent = new Date(timestamp).toLocaleTimeString();

        const contentElement = document.createElement('div');
        contentElement.className = 'message-content';
        contentElement.innerHTML = formatMessage(content);

        contentWrapper.appendChild(timeElement);
        contentWrapper.appendChild(contentElement);

        messageDiv.appendChild(avatarDiv);
        messageDiv.appendChild(contentWrapper);

        chatHistory.appendChild(messageDiv);
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    function formatMessage(content) {
        // Basic markdown formatting
        let formatted = content;

        // Convert markdown headers (must be done before line break replacements)
        formatted = formatted.replace(/^#### (.*?)$/gm, '<h4>$1</h4>');
        formatted = formatted.replace(/^### (.*?)$/gm, '<h3>$1</h3>');
        formatted = formatted.replace(/^## (.*?)$/gm, '<h2>$1</h2>');
        formatted = formatted.replace(/^# (.*?)$/gm, '<h1>$1</h1>');

        // Convert bold text
        formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

        // Convert bullet points
        formatted = formatted.replace(/^- (.*?)$/gm, '<li>$1</li>');
        formatted = formatted.replace(/(<li>.*?<\/li>\n?)+/g, '<ul>$&</ul>');

        // Convert numbered lists
        formatted = formatted.replace(/^\d+\. (.*?)$/gm, '<li>$1</li>');

        // Convert chapter references
        formatted = formatted.replace(/\[([^\]]+)\]/g, '<span class="chapter-ref">$1</span>');

        // Convert line breaks (do this last)
        formatted = formatted.replace(/\n\n/g, '<br><br>');
        formatted = formatted.replace(/\n/g, '<br>');

        return formatted;
    }

    async function sendMessage() {
        if (isProcessing) return;

        const message = userInput.value.trim();
        if (!message) return;

        isProcessing = true;
        showLoading(sendButton);
        hideError();

        addMessage(message, true);
        userInput.value = '';

        try {
            const response = await fetch('/chat/message', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    conversation_id: currentConversationId || 'new',
                    message: message
                })
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.message || 'Failed to send message');
            }

            const data = await response.json();

            // Update conversation ID
            if (data.conversation_id) {
                const wasNewConversation = !currentConversationId;
                currentConversationId = data.conversation_id;

                // Update URL
                window.history.pushState({}, '', `/chat/?conversation_id=${currentConversationId}`);

                // Reload page to show new conversation in sidebar
                if (wasNewConversation) {
                    setTimeout(() => window.location.reload(), 1000);
                }
            }

            if (data.response && data.response.trim()) {
                addMessage(data.response, false);
            }
        } catch (error) {
            console.error('Send message error:', error);
            showError(error.message || 'Failed to send message');
        } finally {
            isProcessing = false;
            hideLoading(sendButton);
        }
    }

    function showLoading(element) {
        const spinner = element.querySelector('.spinner');
        const buttonText = element.querySelector('.button-text');
        if (spinner && buttonText) {
            spinner.classList.remove('hidden');
            buttonText.classList.add('hidden');
        }
        element.disabled = true;
    }

    function hideLoading(element) {
        const spinner = element.querySelector('.spinner');
        const buttonText = element.querySelector('.button-text');
        if (spinner && buttonText) {
            spinner.classList.add('hidden');
            buttonText.classList.remove('hidden');
        }
        element.disabled = false;
    }

    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.classList.remove('hidden');
        setTimeout(hideError, 5000);
    }

    function hideError() {
        errorMessage.classList.add('hidden');
    }

    // Event listeners
    sendButton.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
});
