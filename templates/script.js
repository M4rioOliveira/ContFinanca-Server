class Chatbot {
    constructor() {
        this.messageInput = document.getElementById('message-input');
        this.sendBtn = document.getElementById('send-btn');
        this.clearBtn = document.getElementById('clear-btn');
        this.chatMessages = document.getElementById('chat-messages');
        this.typingIndicator = document.getElementById('typing-indicator');
        this.statusElement = document.getElementById('status');
        
        this.init();
    }
    
    init() {
        this.checkStatus();
        this.setupEventListeners();
    }
    
    setupEventListeners() {
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        this.clearBtn.addEventListener('click', () => this.clearChat());
        
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendMessage();
            }
        });
    }
    
    async checkStatus() {
        try {
            const response = await fetch('/status');
            const data = await response.json();
            
            if (data.ollama_running) {
                this.statusElement.textContent = '';
                this.statusElement.className = '';
                
                if (data.gemma3_available) {
                    this.statusElement.textContent += ' - Gemma3 model available';
                } else {
                    this.statusElement.textContent += ' - Gemma3 model not found';
                }
            } else {
                this.statusElement.textContent = 'Ollama is not running';
                this.statusElement.className = 'status offline';
            }
        } catch (error) {
            this.statusElement.textContent = '';
            this.statusElement.className = 'status offline';
        }
    }
    
    async sendMessage() {
        const message = this.messageInput.value.trim();
        
        if (!message) return;
        
        // Add user message to chat
        this.addMessage(message, 'user');
        this.messageInput.value = '';
        this.setLoading(true);
        
        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message })
            });
            
            const data = await response.json();
            
            if (data.formatted_response) {
                this.addFormattedMessage(data.formatted_response, 'bot');
            } else if (data.response) {
                this.addMessage(data.response, 'bot');
            } else {
                this.addMessage('Error: No response from server', 'error');
            }
        } catch (error) {
            this.addMessage('Error: Could not send message', 'error');
        } finally {
            this.setLoading(false);
        }
    }
    
    async clearChat() {
        try {
            await fetch('/clear', { method: 'POST' });
            this.chatMessages.innerHTML = 
                '<div class="message bot-message">Chat history cleared. How can I help you?</div>';
        } catch (error) {
            this.addMessage('Error: Could not clear chat', 'error');
        }
    }
    
    addMessage(content, type) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}-message`;
        messageDiv.textContent = content;
        
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    addFormattedMessage(htmlContent, type) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}-message`;
        messageDiv.innerHTML = htmlContent;
        
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    setLoading(loading) {
        if (loading) {
            this.typingIndicator.style.display = 'block';
            this.sendBtn.disabled = true;
        } else {
            this.typingIndicator.style.display = 'none';
            this.sendBtn.disabled = false;
        }
        this.scrollToBottom();
    }
    
    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
}

// Inicia quando a pag carregar
document.addEventListener('DOMContentLoaded', () => {
    new Chatbot();
});