# agent-orchestrator-test
Test repository for Local Agent Orchestrator GitHub App integration with Ollama and GitHub Actions

## 🚀 Local Agent Orchestrator Setup

This repository contains a complete GitHub Apps + Actions + Local Ollama Agent Orchestration System.

### Architecture

- **GitHub App**: "Local-Agent-Orchestrator" (App ID: 1052939, Installation ID: 99085453)
- **GitHub Actions**: Cloud control plane for orchestration and validation
- **Local Agent Runtime**: Python Flask app that processes webhooks using local Ollama
- **Page Assist**: Browser extension for Ollama interaction

### Prerequisites

1. **Ollama installed and running** on `localhost:11434`
   ```bash
   # Verify Ollama is running
   curl http://localhost:11434/api/tags
   ```

2. **Python 3.8+** installed

3. **GitHub App Private Key** downloaded from your GitHub App settings

### Setup Instructions

#### Step 1: Clone the Repository

```bash
git clone https://github.com/moneysavvy/agent-orchestrator-test.git
cd agent-orchestrator-test
```

#### Step 2: Move Private Key

Move your downloaded private key to the repository directory:

```bash
# Replace the filename with your actual downloaded key filename
mv ~/Downloads/local-agent-orchestrator.*.private-key.pem ./private-key.pem
```

#### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

#### Step 4: Configure Environment Variables (Optional)

The agent_runtime.py has default values, but you can override them:

```bash
export GITHUB_APP_ID="1052939"
export INSTALLATION_ID="99085453"
export PRIVATE_KEY_PATH="./private-key.pem"
export OLLAMA_URL="http://localhost:11434"
export OLLAMA_MODEL="qwen2.5:latest"
```

#### Step 5: Start the Local Agent Runtime

```bash
python agent_runtime.py
```

You should see:

```
🚀 Starting Local Agent Runtime...
📡 Ollama URL: http://localhost:11434
🤖 Model: qwen2.5:latest
🔑 GitHub App ID: 1052939
📦 Installation ID: 99085453

✅ Agent is ready to receive webhooks!

 * Running on http://0.0.0.0:5000
```

#### Step 6: Expose Local Webhook (Development)

For development, use a webhook proxy to forward GitHub webhooks to your local machine:

**Option A: Using smee.io**

```bash
npm install -g smee-client
smee -u https://smee.io/BpafjJYOxxMI9OSi -t http://localhost:5000/webhook
```

**Option B: Using ngrok**

```bash
ngrok http 5000
# Update your GitHub App webhook URL with the ngrok URL
```

### Testing the Agent

#### Test 1: Create a New Issue

1. Go to the [Issues tab](https://github.com/moneysavvy/agent-orchestrator-test/issues)
2. Create a new issue with any title and description
3. The agent will automatically analyze it and post a comment

#### Test 2: Mention the Agent

1. In any issue or PR, add a comment with `@agent` followed by your question
2. Example: `@agent Explain what this repository does`
3. The agent will respond with an AI-generated answer

#### Test 3: Health Check

```bash
curl http://localhost:5000/health
```

### Files Overview

- **agent_runtime.py**: Main Flask application that handles GitHub webhooks and calls Ollama
- **requirements.txt**: Python dependencies (Flask, PyJWT, requests, cryptography, gitpython)
- **.github/workflows/agent-validation.yml**: GitHub Actions workflow for validation
- **private-key.pem**: Your GitHub App private key (not tracked in git)

### How It Works

1. **GitHub Event Occurs**: Someone creates an issue or comments on an issue/PR
2. **Webhook Sent**: GitHub sends webhook to your local agent via smee.io
3. **Agent Receives**: Flask app receives webhook at `/webhook` endpoint
4. **Ollama Processing**: Agent extracts the text and sends it to local Ollama
5. **Response Posted**: Agent posts Ollama's response back to GitHub as a comment

### Troubleshooting

**Issue**: `FileNotFoundError: private-key.pem`
- **Solution**: Make sure you've moved your private key to the repository directory

**Issue**: `Connection refused to localhost:11434`
- **Solution**: Verify Ollama is running with `ollama serve`

**Issue**: Webhooks not arriving
- **Solution**: Ensure smee-client is running and connected to the correct URL

**Issue**: Agent not responding to comments
- **Solution**: Check that comments contain `@agent` (case insensitive)

### Page Assist Integration

This setup works seamlessly with Page Assist browser extension:

1. Open Page Assist at `chrome-extension://jfgfiigpkhlkbnfnbobbkinehhfdhndo/options.html`
2. Configure Ollama connection to `http://localhost:11434`
3. Select your preferred model (e.g., `qwen2.5:latest`)
4. Use both the agent and Page Assist to interact with Ollama

### GitHub App Configuration

**App Name**: Local-Agent-Orchestrator

**Webhook URL**: https://smee.io/BpafjJYOxxMI9OSi

**Permissions**:
- Repository Contents: Read & Write
- Issues: Read & Write
- Pull Requests: Read & Write
- Checks: Read & Write
- Workflows: Read & Write

**Subscribed Events**:
- push
- pull_request
- issues
- issue_comment
- workflow_run

### Next Steps

- ✅ GitHub App created and installed
- ✅ Repository setup with workflows
- ✅ Local agent runtime implemented
- 🎯 Test by creating issues and mentioning @agent
- 🎯 Customize the agent's behavior in `agent_runtime.py`
- 🎯 Add more webhook event handlers
- 🎯 Deploy to a server for 24/7 operation

### License

MIT
