# 🤖 Ollama Browser Agent - Architecture

## Overview

This document describes how to transform your local Ollama instance (running in Page Assist) into a **browser-controlling agent** like Comet, with the ability to:

1. **Control browsers** via Playwright/Selenium
2. **Execute terminal commands** in iTerm2
3. **Take screenshots** and interact with UI elements
4. **Read and manipulate web pages**
5. **Execute Python/Bash scripts**

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                     PAGE ASSIST UI                            │
│  (Chrome Extension: chrome-extension://jfgfiigpkhlkb...)    │
└────────────────────┬─────────────────────────────────────────┘
                     │
                     │ WebSocket/HTTP
                     ▼
┌──────────────────────────────────────────────────────────────┐
│                 OLLAMA (localhost:11434)                     │
│  Models: llama3.2, qwen2.5, mistral, etc.                   │
└────────────────────┬─────────────────────────────────────────┘
                     │
                     │ Function Calling API
                     ▼
┌──────────────────────────────────────────────────────────────┐
│              BROWSER AGENT TOOLS SERVER                      │
│              (Python Flask: localhost:5001)                  │
│                                                               │
│  ┌────────────────────────────────────────────────────┐    │
│  │  TOOL REGISTRY                                       │    │
│  ├────────────────────────────────────────────────────┤    │
│  │  1. browser_navigate(url)                           │    │
│  │  2. browser_click(selector)                         │    │
│  │  3. browser_type(selector, text)                    │    │
│  │  4. browser_screenshot()                            │    │
│  │  5. browser_read_page()                             │    │
│  │  6. terminal_execute(command)                       │    │
│  │  7. python_execute(code)                            │    │
│  │  8. file_read(path)                                  │    │
│  │  9. file_write(path, content)                       │    │
│  │ 10. web_search(query)                               │    │
│  └────────────────────────────────────────────────────┘    │
└────────────────────┬─────────────────────────────────────────┘
                     │
       ┌─────────────┴───────────────┐
       │                             │
       ▼                             ▼
┌──────────────┐              ┌──────────────┐
│  PLAYWRIGHT  │              │   iTerm2     │
│   BROWSER    │              │  AppleScript │
│   CONTROL    │              │    Bridge    │
└──────────────┘              └──────────────┘
```

## Implementation Components

### 1. Ollama Function Calling Setup

Ollama supports tool calling[web:28][web:37]. Define tools that Ollama can call:

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "browser_navigate",
            "description": "Navigate browser to a URL",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL to navigate to"}
                },
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "browser_click",
            "description": "Click an element on the page",
            "parameters": {
                "type": "object",
                "properties": {
                    "selector": {"type": "string", "description": "CSS selector or text to click"}
                },
                "required": ["selector"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "terminal_execute",
            "description": "Execute command in iTerm2 terminal",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "Command to execute"}
                },
                "required": ["command"]
            }
        }
    }
]
```

### 2. Browser Agent Tools Server

Create a Flask server that implements all browser/terminal tools:

**File: `ollama_browser_tools.py`**

Key functions:
- Browser control via Playwright (headless Chrome)
- Terminal execution via AppleScript (iTerm2 integration)
- Screenshot capture and OCR
- Page content extraction
- Form filling and interaction

### 3. Page Assist Integration

Page Assist[web:24] is open-source. Two integration approaches:

**Option A: Proxy Server** (Easiest)
- Run a proxy between Page Assist → Ollama
- Intercept responses and inject tool calls
- Return results back to Page Assist

**Option B: Fork Page Assist** (Most Control)
- Clone Page Assist repo
- Add tool calling UI
- Build custom extension

### 4. iTerm2 AppleScript Bridge

Execute terminal commands from Python:

```python
import subprocess

def execute_in_iterm(command):
    """Execute command in iTerm2 using AppleScript"""
    applescript = f'''
    tell application "iTerm2"
        tell current session of current window
            write text "{command}"
        end tell
    end tell
    '''
    subprocess.run(["osascript", "-e", applescript])
```

## Usage Workflow

### Example 1: Browser Task

**User in Page Assist:**
> "Navigate to GitHub, search for 'playwright', and open the first result"

**Ollama with Tools:**
1. Calls `browser_navigate("https://github.com")`
2. Calls `browser_type("input[name='q']", "playwright")`
3. Calls `browser_click("button[type='submit']")`
4. Calls `browser_read_page()`
5. Calls `browser_click("a.repo-link:first")`
6. Returns summary to user

### Example 2: Terminal Task

**User in Page Assist:**
> "Check my git status and list modified files"

**Ollama with Tools:**
1. Calls `terminal_execute("git status")`
2. Parses output
3. Calls `terminal_execute("git diff --name-only")`
4. Returns formatted summary

## Quick Start Implementation

### Step 1: Install Dependencies

```bash
pip install playwright flask ollama anthropic
playwright install chromium
```

### Step 2: Run the Tools Server

```bash
python ollama_browser_tools.py
# Starts on http://localhost:5001
```

### Step 3: Configure Ollama

Create a custom model with tool support:

```bash
# Create modelfile
cat > Modelfile <<EOF
FROM qwen2.5:latest
SYSTEM You are a browser automation agent with access to tools for controlling browsers and terminals.
EOF

# Create model
ollama create browser-agent -f Modelfile
```

### Step 4: Test from Page Assist

In Page Assist, select `browser-agent` model and try:
> "Open GitHub and show me my repositories"

## Model Context Protocol (MCP) Integration

For advanced integration, implement MCP[web:29][web:35]:

- MCP provides standardized tool interface
- Works with VS Code, Claude Desktop, Cursor
- Browser MCP extension available[web:29]

## Security Considerations

⚠️ **IMPORTANT**: This gives AI full control of your browser and terminal!

- Run in isolated environment
- Review all terminal commands before execution
- Sandbox browser sessions
- Never run with elevated privileges
- Log all tool calls

## Comparison to Comet

| Feature | Comet (Perplexity) | Your Ollama Agent |
|---------|-------------------|-------------------|
| Browser Control | ✅ | ✅ |
| Terminal Execution | ✅ | ✅ |
| Cloud-based | ✅ | ❌ |
| Local/Private | ❌ | ✅ |
| Cost | Subscription | Free |
| Model | Proprietary | Any Ollama model |
| Customizable | ❌ | ✅ |

## Next Steps

1. **Implement Core Tools** - Start with browser_navigate, browser_click, browser_read
2. **Test with Simple Tasks** - Navigate to websites, extract data
3. **Add Terminal Integration** - iTerm2 AppleScript bridge
4. **Build UI Enhancement** - Fork Page Assist or create proxy
5. **Add Advanced Features** - Screenshots, OCR, file operations

## Resources

- [web:24] Page Assist GitHub: https://github.com/n4ze3m/page-assist
- [web:28] Ollama Function Calling: https://ollama.com/blog/functions-as-tools
- [web:29] Browser MCP: Chrome extension for MCP browser control
- [web:35] MCP-B: Model Context Protocol for browsers
- [web:38] Playwright MCP Server: https://github.com/microsoft/playwright-mcp

## Code Repository Structure

```
agent-orchestrator-test/
├── ollama_browser_tools.py    # Main tools server
├── browser_agent.py           # Playwright browser controller  
├── terminal_agent.py          # iTerm2 AppleScript bridge
├── pageassist_proxy.py        # Optional: Proxy for Page Assist
├── requirements.txt           # Updated dependencies
└── README.md                  # Updated documentation
```

---

**Status**: Architecture Complete ✅  
**Next**: Implementation of ollama_browser_tools.py


---

# 🏗️ ENHANCED ARCHITECTURE: Local Agent Orchestrator

## System Enhancement Overview

This section expands the browser agent architecture into a **comprehensive Local Agent Orchestrator** - a privacy-focused, agentic-first platform that replicates Motion (Scheduling), rtrvr (Browser Automation), and Cluely (Real-time Assistance) into a single, locally hosted system.

**Core Philosophy**: Agentic-first | Privacy-focused | Local-first execution

## Integrated System Architecture

```
graph TD
    User[User] --> UI[Frontend / Overlay UI]
    UI --> API[FastAPI Gateway]
    
    subgraph "Core Brain (Ollama/OpenRouter)"
        Router[Model Router]
        Planner[Task Planner]
        Coder[Coding Specialist]
    end

    subgraph "Module A: The Manager (Motion)"
        Scheduler[Constraint Solver Engine]
        CalSync[Calendar Sync Service]
        TaskDB[(Task Database)]
    end

    subgraph "Module B: The Hand (rtrvr)"
        Nav[Playwright Controller]
        DOM[DOM Parser / Scraper]
        MCP[MCP Server Interface]
    end

    subgraph "Module C: The Co-Pilot (Cluely)"
        Audio[Whisper STT Stream]
        Screen[Screen Capture / OCR]
        Overlay[Transparent Window Service]
    end

    API --> Router
    Router --> Scheduler
    Router --> Nav
    Router --> Audio
    
    Nav --> Browser[Local Chrome Instance]
    Audio --> Mic[Microphone]
    Screen --> Display[System Display]
```

## Enhanced Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|----------|
| **Runtime/Backend** | Python 3.11+ (FastAPI) | High-performance async API gateway |
| **LLM Inference** | Ollama (7B/13B local) + OpenRouter (fallback) | Speed-first local, complex reasoning fallback |
| **Browser Automation** | Playwright (Python async API) | Headless/headed browser control |
| **Database** | SQLite (tasks/events) + ChromaDB (vector memory) | Structured data + semantic search |
| **Frontend/Overlay** | Electron OR PyQt6 | Invisible click-through overlay |
| **Audio/Vision** | faster-whisper (STT) + pyautogui/mss | Real-time transcription + screen capture |
| **Task Scheduling** | Custom CSP Solver | Constraint satisfaction for calendar |
| **Message Queue** | Redis (optional) | Inter-module communication buffer |

## Module Specifications

### Module A: The Scheduler (Motion Clone)

**Goal**: Auto-schedule tasks into calendar slots based on priority, deadlines, and constraints.

**Core Logic**: Constraint Satisfaction Problem (CSP) solver

**Data Structures**:
```python
Task = {
    "id": UUID,
    "title": str,
    "duration": int,  # minutes
    "deadline": datetime,
    "priority": int,  # 1-5
    "dependency_id": Optional[UUID],
    "hard_scheduled_time": Optional[datetime],
    "tags": List[str],
    "recurrence": Optional[str]  # RRULE format
}

Event = {
    "id": UUID,
    "start_time": datetime,
    "end_time": datetime,
    "is_fixed": bool,
    "source": str  # "google", "outlook", "manual"
}
```

**Algorithm**:
1. Fetch "Fixed" events from Calendar API
2. Identify "Free Blocks" (time chunks > 30 mins)
3. Sort Tasks: `Priority DESC > Deadline ASC > Duration ASC`
4. Bin-pack Tasks into Free Blocks ("Tetris algorithm")
5. Handle dependencies (Task B cannot start before Task A completes)
6. Trigger `rebalance()` on new urgent task

**Edge Cases**:
- **Overlapping deadlines**: Priority tiebreaker
- **No available slots**: Push to next day, alert user
- **Dependency chains**: Use topological sort
- **Buffer time**: Add 10-min padding between tasks
- **Timezone shifts**: Store all times in UTC
- **Recurring tasks**: Expand RRULE into discrete instances

**Agent Instruction**:
> "Create SchedulerService class that takes tasks[] and events[], returns optimized schedule. Use heuristic bin-packing (First-Fit Decreasing). Implement rebalance() for dynamic re-scheduling. Handle edge case: if no slots available within deadline, return warning with suggested deadline extension."

### Module B: The Browser Agent (rtrvr Clone)

**Goal**: Execute web scraping and navigation via natural language commands.

**Core Logic**: DOM-to-Text simplification for LLM consumption

**Components**:

1. **Interactive DOM Cleaner**
```python
def simplify_dom(html: str) -> Dict:
    """
    Strip CSS/SVG, keep only interactive elements.
    Assign unique numeric IDs to each element.
    """
    soup = BeautifulSoup(html, 'lxml')
    interactive = soup.find_all(['a', 'button', 'input', 'select', 'textarea'])
    
    simplified = {}
    for idx, elem in enumerate(interactive):
        simplified[idx] = {
            "tag": elem.name,
            "text": elem.get_text(strip=True),
            "attrs": {k: v for k, v in elem.attrs.items() if k in ['href', 'type', 'name']},
            "xpath": get_xpath(elem)
        }
    return simplified
```

2. **Action Engine**
```python
def execute_action(action: Dict, page: Page):
    """
    Map LLM output to Playwright commands.
    Example: {"action": "click", "id": 42}
    """
    if action["action"] == "click":
        page.locator(f"[data-agent-id='{action['id']}']"



3. **Trick Recorder**
```python
def record_sequence(start_url: str, actions: List[Action]) -> Trick:
    """
    Record browser interactions as reusable 'tricks'.
    Store in vector DB for semantic retrieval.
    """
    return {
        "name": generate_trick_name(actions),
        "embedding": embed_action_sequence(actions),
        "actions": actions
    }
```

4. **MCP Server Bridge**
```python
class BrowserMCPServer:
    """
    Expose browser automation via Model Context Protocol.
    Allows other agents/tools to control browser.
    """
    
    def handle_tool_call(self, tool: str, params: dict):
        if tool == "browser_navigate":
            return self.browser.goto(params["url"])
        elif tool == "browser_extract":
            return self.browser.evaluate(params["script"])
```

---

### Module C: The Co-Pilot (Agentic Interface)

**Core Logic**:
```python
class AgentCoPilot:
    """
    Natural language interface for agent orchestration.
    """
    
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.llm = OllamaClient(ollama_url)
        self.browser = BrowserAgent()
        self.terminal = TerminalAgent()
    
    async def execute_command(self, user_input: str):
        # Parse intent
        intent = await self.llm.classify_intent(user_input)
        
        if intent["type"] == "browser":
            return await self.browser.execute(intent["action"])
        elif intent["type"] == "terminal":
            return await self.terminal.execute(intent["command"])
        elif intent["type"] == "workflow":
            return await self.orchestrate_workflow(intent["steps"])
```

---

## 🔄 Integrated Workflow Examples

### Example 1: GitHub Issue → Browser Research → Terminal Action
```python
# User: "Research the top 3 Python testing frameworks and create a comparison chart"

# Step 1: Browser Agent extracts data
browser_data = await browser.search_and_extract([
    "pytest features",
    "unittest capabilities",
    "nose2 documentation"
])

# Step 2: LLM processes and structures
comparison = await llm.generate_comparison(browser_data)

# Step 3: Terminal Agent creates file
await terminal.execute(f"echo '{comparison}' > testing_frameworks.md")

# Step 4: GitHub workflow commits result
await github.create_commit("testing_frameworks.md", comparison)
```

### Example 2: Automated Monitoring Workflow
```yaml
# .github/workflows/agent-monitor.yml
name: Periodic Agent Tasks

on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours

jobs:
  run-agent:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Trigger Local Agent
        run: |
          curl -X POST http://localhost:5000/webhook \
            -H "Content-Type: application/json" \
            -d '{"task": "check_documentation_updates"}'
```

---

## 📦 Complete File Structure

```
agent-orchestrator-test/
├── .github/
│   ├── workflows/
│   │   ├── agent-dispatch.yml       # Webhook receiver
│   │   ├── scheduled-tasks.yml      # Cron-based triggers
│   │   └── self-update.yml          # Agent auto-update
│   └── app-config/
│       ├── private-key.pem          # GitHub App private key (gitignored)
│       └── app-manifest.json        # App configuration backup
│
├── modules/
│   ├── browser_agent/
│   │   ├── __init__.py
│   │   ├── dom_cleaner.py           # Interactive DOM simplification
│   │   ├── action_engine.py         # Playwright command executor
│   │   ├── trick_recorder.py        # Sequence recording/playback
│   │   └── mcp_server.py            # MCP protocol implementation
│   │
│   ├── terminal_agent/
│   │   ├── __init__.py
│   │   ├── iterm_bridge.py          # iTerm2 AppleScript control
│   │   ├── command_validator.py     # Safety checks for shell commands
│   │   └── session_manager.py       # Multi-session handling
│   │
│   └── copilot/
│       ├── __init__.py
│       ├── intent_parser.py         # NLU for user commands
│       ├── workflow_orchestrator.py # Multi-agent coordination
│       └── context_manager.py       # Maintain conversation state
│
├── agent_runtime.py                 # Main FastAPI server
├── requirements.txt
├── ARCHITECTURE.md                  # This file
├── README.md
└── .env.example                     # Environment variable template
```

---

## 🚀 Implementation Phases for Aider/Cursor

### Phase 1: Core Infrastructure (Week 1)
- [ ] Set up FastAPI server with webhook endpoints
- [ ] Implement GitHub App authentication
- [ ] Create basic Ollama client wrapper
- [ ] Add health check endpoints

### Phase 2: Browser Agent (Week 2)
- [ ] Build Interactive DOM Cleaner
- [ ] Implement Action Engine with Playwright
- [ ] Add screenshot/OCR capabilities
- [ ] Create Trick Recorder for reusable sequences

### Phase 3: Terminal Agent (Week 3)
- [ ] iTerm2 AppleScript integration
- [ ] Command safety validator
- [ ] Session management
- [ ] Output streaming to GitHub/logs

### Phase 4: Co-Pilot Interface (Week 4)
- [ ] Intent classification with Ollama
- [ ] Multi-agent workflow orchestration
- [ ] Context/memory management
- [ ] Error handling and retries

### Phase 5: Integration & Testing (Week 5)
- [ ] End-to-end workflow tests
- [ ] GitHub Actions integration testing
- [ ] Performance optimization
- [ ] Documentation and examples

---

## 🔒 Security & Edge Cases

### Authentication
- **GitHub App JWT**: Generated from private key, expires every 10 minutes
- **Installation Token**: Refreshed every 60 minutes
- **Local Agent**: Validate webhook signatures using GITHUB_WEBHOOK_SECRET

### Rate Limiting
- GitHub API: 5000 requests/hour per installation
- Ollama: No hard limit, but consider local resource constraints
- Browser automation: Respect robots.txt and site rate limits

### Error Handling
```python
class AgentError(Exception):
    """Base exception for agent errors"""
    pass

class BrowserTimeoutError(AgentError):
    """Browser action exceeded timeout"""
    pass

class LLMResponseError(AgentError):
    """LLM returned invalid/unexpected response"""
    pass

# Retry decorator
@retry(max_attempts=3, backoff=2.0)
async def resilient_browser_action(action):
    try:
        return await browser.execute(action)
    except BrowserTimeoutError:
        await browser.refresh()
        raise
```

### Data Privacy
- Never log sensitive data (passwords, API keys, PII)
- Sanitize URLs before storing in GitHub logs
- Use environment variables for all credentials
- Implement opt-in telemetry only

### Resource Management
```python
class ResourceManager:
    """Prevent resource exhaustion"""
    
    MAX_BROWSER_TABS = 5
    MAX_CONCURRENT_TASKS = 3
    BROWSER_IDLE_TIMEOUT = 300  # 5 minutes
    
    async def cleanup_idle_resources(self):
        # Close unused browser contexts
        # Terminate stale terminal sessions
        # Clear old vector embeddings
        pass
```

---

## 🔗 Integration Points

### With Page Assist Extension
```javascript
// Extension calls local agent
const response = await fetch('http://localhost:5000/api/browser/action', {
  method: 'POST',
  body: JSON.stringify({
    action: 'extract',
    selector: '.product-price',
    context: currentTabDOM
  })
});
```

### With GitHub Workflows
```yaml
# Workflow dispatches to local agent
- name: Trigger Research Task
  uses: peter-evans/repository-dispatch@v2
  with:
    event-type: agent-task
    client-payload: |
      {
        "task_type": "research",
        "query": "Latest AI news",
        "output_format": "markdown"
      }
```

### With Ollama Models
```python
# Model selection based on task complexity
model_map = {
    "simple_extraction": "llama3.2:1b",
    "reasoning": "llama3.2:3b",
    "complex_workflow": "qwen2.5:7b"
}

async def select_model(task_complexity: str) -> str:
    return model_map.get(task_complexity, "llama3.2:3b")
```

---

## 📊 Monitoring & Observability

### Logging Structure
```python
import structlog

logger = structlog.get_logger()

# Structured logging
logger.info(
    "browser_action_completed",
    action_type="click",
    element_id="submit_button",
    duration_ms=250,
    success=True
)
```

### Metrics Collection
```python
from prometheus_client import Counter, Histogram

browser_actions = Counter('browser_actions_total', 'Total browser actions', ['action_type', 'status'])
action_duration = Histogram('browser_action_duration_seconds', 'Browser action duration')

@action_duration.time()
async def execute_browser_action(action):
    result = await browser.execute(action)
    browser_actions.labels(action['type'], 'success').inc()
    return result
```

---

## 🎯 Next Steps for Development

1. **Clone and Initialize**
   ```bash
   git clone https://github.com/moneysavvy/agent-orchestrator-test.git
   cd agent-orchestrator-test
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Add GitHub App credentials
   # Set OLLAMA_URL=http://localhost:11434
   ```

3. **Start Development Server**
   ```bash
   uvicorn agent_runtime:app --reload --port 5000
   ```

4. **Test GitHub App Webhook**
   ```bash
   ngrok http 5000  # For local testing
   # Update GitHub App webhook URL
   ```

5. **Begin Implementation**
   - Start with Phase 1 tasks
   - Use Aider/Cursor for code generation
   - Test each module independently before integration

---

## 📚 Additional Resources

- **GitHub Apps API**: https://docs.github.com/en/apps
- **Playwright Python**: https://playwright.dev/python/
- **Ollama API**: https://github.com/ollama/ollama/blob/main/docs/api.md
- **FastAPI**: https://fastapi.tiangolo.com/
- **Model Context Protocol**: https://github.com/modelcontextprotocol
- **iTerm2 AppleScript**: https://iterm2.com/documentation-scripting.html

---

## ✅ Success Criteria

The system is production-ready when:

1. ✅ GitHub App successfully authenticates and receives webhooks
2. ✅ Browser agent can navigate, extract data, and execute actions
3. ✅ Terminal agent safely executes commands in iTerm2
4. ✅ Co-pilot correctly interprets natural language commands
5. ✅ End-to-end workflows complete without manual intervention
6. ✅ Error handling gracefully recovers from failures
7. ✅ All sensitive data is properly secured
8. ✅ Documentation covers all use cases and edge cases

---

**Status**: Architecture complete ✅  
**Next**: Implementation with Aider/Cursor coding agent  
**Maintainer**: Local Agent Orchestrator System