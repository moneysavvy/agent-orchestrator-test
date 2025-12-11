#!/usr/bin/env python3
"""
Local Agent Runtime for GitHub App Integration
Listens for GitHub webhooks and processes agent tasks using local Ollama
"""

import os
import json
import time
import jwt
import requests
from flask import Flask, request, jsonify
from datetime import datetime, timedelta

app = Flask(__name__)

# Configuration
APP_ID = os.getenv('GITHUB_APP_ID', '1052939')  # Replace with your App ID
PRIVATE_KEY_PATH = os.getenv('PRIVATE_KEY_PATH', './private-key.pem')
INSTALLATION_ID = os.getenv('INSTALLATION_ID', '99085453')  # Replace with your Installation ID
OLLAMA_URL = os.getenv('OLLAMA_URL', 'http://localhost:11434')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'qwen2.5:latest')

def generate_jwt():
    """Generate JWT for GitHub App authentication"""
    with open(PRIVATE_KEY_PATH, 'r') as key_file:
        private_key = key_file.read()
    
    payload = {
        'iat': int(time.time()),
        'exp': int(time.time()) + 600,  # 10 minutes
        'iss': APP_ID
    }
    
    return jwt.encode(payload, private_key, algorithm='RS256')

def get_installation_token():
    """Get installation access token"""
    jwt_token = generate_jwt()
    headers = {
        'Authorization': f'Bearer {jwt_token}',
        'Accept': 'application/vnd.github+json'
    }
    
    response = requests.post(
        f'https://api.github.com/app/installations/{INSTALLATION_ID}/access_tokens',
        headers=headers
    )
    
    return response.json()['token']

def call_ollama(prompt, model=OLLAMA_MODEL):
    """Call local Ollama API"""
    try:
        response = requests.post(
            f'{OLLAMA_URL}/api/generate',
            json={
                'model': model,
                'prompt': prompt,
                'stream': False
            },
            timeout=120
        )
        response.raise_for_status()
        return response.json()['response']
    except Exception as e:
        return f"Error calling Ollama: {str(e)}"

def post_github_comment(repo_full_name, issue_number, comment_body):
    """Post a comment to a GitHub issue or PR"""
    token = get_installation_token()
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github+json'
    }
    
    response = requests.post(
        f'https://api.github.com/repos/{repo_full_name}/issues/{issue_number}/comments',
        headers=headers,
        json={'body': comment_body}
    )
    
    return response.status_code == 201

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle GitHub webhook events"""
    event_type = request.headers.get('X-GitHub-Event')
    payload = request.json
    
    print(f"Received {event_type} event")
    
    # Handle issue comments
    if event_type == 'issue_comment' and payload.get('action') == 'created':
        comment_body = payload['comment']['body']
        
        # Check if comment mentions the agent
        if '@agent' in comment_body.lower():
            issue_number = payload['issue']['number']
            repo_full_name = payload['repository']['full_name']
            
            # Extract the prompt (everything after @agent)
            prompt = comment_body.split('@agent', 1)[1].strip()
            
            # Call Ollama
            response = call_ollama(prompt)
            
            # Post response back to GitHub
            comment = f"🤖 **Agent Response:**\n\n{response}"
            post_github_comment(repo_full_name, issue_number, comment)
            
            return jsonify({'status': 'processed'}), 200
    
    # Handle new issues
    elif event_type == 'issues' and payload.get('action') == 'opened':
        issue_title = payload['issue']['title']
        issue_body = payload['issue']['body'] or ''
        issue_number = payload['issue']['number']
        repo_full_name = payload['repository']['full_name']
        
        # Auto-respond to new issues
        prompt = f"Analyze this GitHub issue and provide helpful suggestions:\n\nTitle: {issue_title}\n\nBody: {issue_body}"
        response = call_ollama(prompt)
        
        comment = f"👋 **Automated Analysis:**\n\n{response}"
        post_github_comment(repo_full_name, issue_number, comment)
        
        return jsonify({'status': 'processed'}), 200
    
    return jsonify({'status': 'ignored'}), 200

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'ollama_url': OLLAMA_URL,
        'model': OLLAMA_MODEL,
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print(f"🚀 Starting Local Agent Runtime...")
    print(f"📡 Ollama URL: {OLLAMA_URL}")
    print(f"🤖 Model: {OLLAMA_MODEL}")
    print(f"🔑 GitHub App ID: {APP_ID}")
    print(f"📦 Installation ID: {INSTALLATION_ID}")
    print(f"\n✅ Agent is ready to receive webhooks!\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
