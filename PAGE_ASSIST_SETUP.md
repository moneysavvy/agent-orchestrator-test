# 🔗 Page Assist Integration Guide

## Quick Setup for CEO Coding Boss

This guide will help you connect Page Assist to your Local Agent Orchestrator.

---

## Step 1: Start the Agent Runtime Server

First, start your FastAPI agent orchestrator:

```bash
cd ~/agent-orchestrator-test
python agent_runtime.py
```

The server will start at `http://localhost:5000`

Verify it's running:
```bash
curl http://localhost:5000/health
```

---

## Step 2: Configure Page Assist Settings

### A. Ollama Settings

1. Open Page Assist (click extension icon)
2. Click the **Settings gear icon** (⚙️) in the top right
3. Click **"Ollama Settings"** in the left sidebar
4. Verify settings:
   - **Ollama URL**: `http://localhost:11434`
   - **Enable Ollama**: ✅ Checked
   - Click **"Test Connection"** to verify

### B. Add Agent Orchestrator as OpenAI Compatible API

1. In Page Assist Settings, click **"OpenAI Compatible API"**
2. Click **"Add Provider"** button
3. Fill in the form:
   ```
   Provider Name: Local Agent Orchestrator
   Base URL: http://localhost:5000/v1
   API Key: (leave blank or use "local-dev")
   Model: agent-orchestrator
   ```
4. Click **"Save"**

---

## Step 3: Create CEO Coding Boss Prompt

1. In Page Assist Settings, click **"Manage Prompts"**
2. Click **"Add New Prompt"**
3. Fill in:

**Prompt Name**: CEO Coding Boss

**System Prompt**:
```
You are the CEO Coding Boss - an executive-level AI agent that orchestrates software development.

Your role:
- Receive high-level directives from the user
- Break them down into actionable tasks  
- Delegate to specialized agents (Browser, Terminal, Coding)
- Monitor progress and ensure quality
- Make strategic technical decisions
- Deliver production-ready results

Your personality:
- Decisive and confident in technical decisions
- Strategic thinker focused on long-term maintainability
- Pragmatic about trade-offs (perfect vs. ship)
- Clear communicator with concise updates
- Accountable for all deliverables

Your agents:
1. Browser Agent - Web automation, scraping, research
2. Terminal Agent - Command execution, git, deployment
3. Coding Agent - Code generation, refactoring, testing
4. Architecture Agent - System design, technical decisions

When you receive a directive:
1. Analyze: What's the core objective?
2. Plan: Break into sequential tasks
3. Delegate: Assign to appropriate agents
4. Monitor: Track progress and handle blockers
5. Validate: Ensure quality and completeness
6. Deliver: Provide final output with documentation

Be direct, efficient, and results-oriented. Start each response with a brief status update, then provide your analysis and action plan.

Example format:
**Status**: Directive received
**Analysis**: [Brief analysis]
**Plan**: 
1. [Task 1 - Agent]
2. [Task 2 - Agent]
**Execution**: [What you're doing now]
```

4. Click **"Save Prompt"**

---

## Step 4: Test the Connection

### Test 1: Direct Ollama (Baseline)

1. Go back to Page Assist chat
2. Make sure **Model** is set to `llama3.2:latest`
3. Send test message:
   ```
   Hello! Verify you're running on Ollama at localhost:11434
   ```

### Test 2: CEO Coding Boss

1. Select **"CEO Coding Boss"** from the Prompts dropdown
2. Send a directive:
   ```
   CEO: Create a simple Python function that validates email addresses using regex
   ```

### Test 3: Agent Orchestrator Integration

1. Switch Model to **"Local Agent Orchestrator"** (if you added it as OpenAI Compatible)
2. Send complex directive:
   ```
   CEO: Build a FastAPI endpoint that:
   - Accepts POST requests with JSON
   - Validates the input
   - Stores data in SQLite
   - Returns a success response
   Include tests and error handling.
   ```

---

## Step 5: Alternative - Direct API Usage

If the OpenAI Compatible API approach doesn't work, you can use the agent orchestrator REST API directly:

### Using curl:
```bash
curl -X POST http://localhost:5000/api/ceo/directive \
  -H "Content-Type: application/json" \
  -d '{
    "directive": "Create a Python function that fetches weather data from OpenWeatherMap API"
  }'
```

### Using Python:
```python
import requests

response = requests.post(
    "http://localhost:5000/api/ceo/directive",
    json={
        "directive": "Build a REST API for user authentication with JWT"
    }
)

print(response.json())
```

### Using JavaScript (from browser console):
```javascript
fetch('http://localhost:5000/api/ceo/directive', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    directive: 'Create a web scraper for product prices'
  })
})
.then(r => r.json())
.then(data => console.log(data));
```

---

## Troubleshooting

### Issue: "Connection refused" or "Cannot connect"

**Solution**:
1. Verify agent_runtime.py is running:
   ```bash
   ps aux | grep agent_runtime
   ```
2. Check port 5000 is not in use:
   ```bash
   lsof -i :5000
   ```
3. Try accessing directly:
   ```bash
   curl http://localhost:5000/health
   ```

### Issue: "Ollama is not running"

**Solution**:
1. Start Ollama:
   ```bash
   ollama serve
   ```
2. Verify it's running:
   ```bash
   ollama list
   curl http://localhost:11434/api/tags
   ```

### Issue: "Model not found"

**Solution**:
1. List available models:
   ```bash
   ollama list
   ```
2. Pull the required model:
   ```bash
   ollama pull llama3.2:latest
   ollama pull qwen2.5:latest
   ```

### Issue: Page Assist can't see custom prompts

**Solution**:
1. Refresh Page Assist extension
2. Close and reopen the popup
3. Check browser console for errors (F12)

---

## Advanced: Custom Tools for Page Assist

If Page Assist supports custom function calling, add these tools:

### Tool 1: Browser Automation
```json
{
  "name": "browser_action",
  "description": "Execute browser automation task (navigate, click, extract, screenshot)",
  "parameters": {
    "type": "object",
    "properties": {
      "action": {
        "type": "string",
        "enum": ["navigate", "click", "extract", "screenshot"],
        "description": "Type of browser action to perform"
      },
      "target": {
        "type": "string",
        "description": "URL (for navigate) or CSS selector (for click/extract)"
      }
    },
    "required": ["action", "target"]
  }
}
```

### Tool 2: Terminal Command
```json
{
  "name": "terminal_exec",
  "description": "Execute a terminal command",
  "parameters": {
    "type": "object",
    "properties": {
      "command": {
        "type": "string",
        "description": "Shell command to execute"
      },
      "working_dir": {
        "type": "string",
        "description": "Working directory (optional)"
      }
    },
    "required": ["command"]
  }
}
```

### Tool 3: File Operations
```json
{
  "name": "file_operation",
  "description": "Read or write files",
  "parameters": {
    "type": "object",
    "properties": {
      "operation": {
        "type": "string",
        "enum": ["read", "write", "append"],
        "description": "Type of file operation"
      },
      "path": {
        "type": "string",
        "description": "File path"
      },
      "content": {
        "type": "string",
        "description": "Content to write (for write/append operations)"
      }
    },
    "required": ["operation", "path"]
  }
}
```

---

## Usage Examples

### Example 1: Simple Code Generation
```
User: CEO, create a Python function that calculates fibonacci numbers recursively

CEO: **Status**: Directive received
**Analysis**: Simple code generation task, no external dependencies
**Plan**:
1. Generate fibonacci function - Coding Agent
2. Add docstring and type hints - Coding Agent
3. Create test cases - Coding Agent

**Execution**: Generating function...

[Provides code with tests]
```

### Example 2: Full Stack Feature
```
User: CEO, build a user authentication system with:
- FastAPI backend
- JWT tokens
- Password hashing
- SQLite database
- Registration and login endpoints

CEO: **Status**: Complex directive received
**Analysis**: Full-stack auth system, multiple components
**Plan**:
1. Research FastAPI auth patterns - Browser Agent
2. Set up project structure - Terminal Agent
3. Implement auth models - Coding Agent
4. Create API endpoints - Coding Agent
5. Add tests - Coding Agent
6. Validate security - Architecture Agent

**Execution**: Starting with research phase...

[Provides complete implementation]
```

### Example 3: Web Scraping Task
```
User: CEO, scrape the top 10 posts from Hacker News and save to CSV

CEO: **Status**: Web automation directive
**Analysis**: Browser automation + data extraction
**Plan**:
1. Navigate to news.ycombinator.com - Browser Agent
2. Extract post titles and links - Browser Agent
3. Format as CSV - Coding Agent
4. Save to file - Terminal Agent

**Execution**: Initiating browser agent...

[Provides CSV file]
```

---

## Next Steps

1. ✅ Start agent_runtime.py server
2. ✅ Configure Page Assist with CEO prompt
3. ✅ Test with simple directives
4. ✅ Scale to complex tasks
5. ✅ Monitor and refine based on outputs

---

## Support

- **Repository**: https://github.com/moneysavvy/agent-orchestrator-test
- **Architecture**: See ARCHITECTURE.md
- **CEO Spec**: See CEO_CODING_BOSS.md

---

**Status**: Ready for integration  
**Maintainer**: Local Agent Orchestrator System