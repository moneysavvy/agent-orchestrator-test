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
