# chatbot_backend.py
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS  # Add this import
import requests
import json
import threading
import markdown
import re

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

class OllamaChatbot:
    def __init__(self, model="gemma3"):
        self.model = model
        self.base_url = "http://localhost:11434"
        self.conversation_history = []
        
    def generate_response(self, message):
        """Send message to Ollama and get response"""
        try:
            # Add user message to history
            self.conversation_history.append({"role": "user", "content": message})
            
            # Prepare the payload
            payload = {
                "model": self.model,
                "messages": self.conversation_history,
                "stream": False
            }
            
            # Make request to Ollama
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=9000
            )
            
            if response.status_code == 200:
                result = response.json()
                assistant_message = result['message']['content']
                
                # Add assistant response to history
                self.conversation_history.append({"role": "assistant", "content": assistant_message})
                
                return assistant_message
            else:
                return f"Error: Unable to get response from Ollama. Status code: {response.status_code}"
                
        except requests.exceptions.ConnectionError:
            return "Error: Cannot connect to Ollama. Please make sure Ollama is running on localhost:11434"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        return "Conversation history cleared"

def markdown_to_html(text):
    """Convert markdown text to HTML with custom styling"""
    # Convert markdown to HTML
    html_content = markdown.markdown(
        text,
        extensions=['fenced_code', 'tables', 'nl2br']
    )
    
    # Add custom classes for styling
    html_content = html_content.replace('<p>', '<p class="markdown-paragraph">')
    html_content = html_content.replace('<ul>', '<ul class="markdown-list">')
    html_content = html_content.replace('<ol>', '<ol class="markdown-list">')
    html_content = html_content.replace('<li>', '<li class="markdown-list-item">')
    html_content = html_content.replace('<strong>', '<strong class="markdown-bold">')
    html_content = html_content.replace('<em>', '<em class="markdown-italic">')
    html_content = html_content.replace('<code>', '<code class="markdown-inline-code">')
    html_content = html_content.replace('<pre>', '<pre class="markdown-code-block">')
    html_content = html_content.replace('<blockquote>', '<blockquote class="markdown-blockquote">')
    html_content = html_content.replace('<h1>', '<h3 class="markdown-heading">')
    html_content = html_content.replace('</h1>', '</h3>')
    html_content = html_content.replace('<h2>', '<h4 class="markdown-heading">')
    html_content = html_content.replace('</h2>', '</h4>')
    html_content = html_content.replace('<h3>', '<h5 class="markdown-heading">')
    html_content = html_content.replace('</h3>', '</h5>')
    
    return html_content

# Initialize chatbot
chatbot = OllamaChatbot()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST', 'GET'])  # Allow both POST and GET
def chat():
    """Handle chat messages"""
    if request.method == 'GET':
        return jsonify({'message': 'Chat endpoint is working'})
    
    user_message = request.json.get('message', '')
    
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400
    
    # Generate response
    response = chatbot.generate_response(user_message)
    
    # Convert markdown to HTML
    formatted_response = markdown_to_html(response)
    
    return jsonify({
        'response': response,
        'formatted_response': formatted_response,
        'user_message': user_message
    })

@app.route('/clear', methods=['POST', 'GET'])
def clear_chat():
    """Clear conversation history"""
    chatbot.clear_history()
    return jsonify({'message': 'Chat history cleared'})

@app.route('/status', methods=['GET'])
def status():
    """Check if Ollama is running and model is available"""
    try:
        response = requests.get(f"{chatbot.base_url}/api/tags")
        if response.status_code == 200:
            models = response.json().get('models', [])
            model_names = [model['name'] for model in models]
            return jsonify({
                'ollama_running': True,
                'models_available': model_names,
                'gemma3_available': any('gemma3' in name for name in model_names)
            })
    except:
        return jsonify({'ollama_running': False, 'models_available': []})

# New endpoint for mobile app
@app.route('/api/mobile/chat', methods=['POST'])
def mobile_chat():
    """Simplified endpoint for mobile apps"""
    data = request.get_json()
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400
    
    response = chatbot.generate_response(user_message)
    
    return jsonify({
        'success': True,
        'response': response,
        'user_message': user_message
    })

@app.route('/api/mobile/status', methods=['GET'])
def mobile_status():
    """Status endpoint for mobile apps"""
    try:
        response = requests.get(f"{chatbot.base_url}/api/tags")
        if response.status_code == 200:
            return jsonify({
                'success': True,
                'ollama_running': True,
                'message': 'Ollama is running'
            })
        else:
            return jsonify({
                'success': False,
                'ollama_running': False,
                'message': 'Ollama is not responding'
            })
    except:
        return jsonify({
            'success': False,
            'ollama_running': False,
            'message': 'Cannot connect to Ollama'
        })

if __name__ == '__main__':
    print("Starting Gemma3 Chatbot...")
    print("Make sure Ollama is running with: ollama serve")
    print("Local access: http://localhost:5000")
    print("Network access: http://YOUR_LOCAL_IP:5000")
    print("\nTo find your local IP address:")
    print("Windows: ipconfig | findstr \"IPv4\"")
    print("Mac/Linux: ifconfig | grep \"inet \"")
    
    # Run on all network interfaces
    app.run(debug=True, host='0.0.0.0', port=5000)