# Introduction to AI Agents

A simple educational demo that visually demonstrates how an AI agent graph executes step-by-step using **LangGraph**.

Built for live AI masterclass sessions.

---

## What Are AI Agents?

AI agents are systems that can **reason**, **plan actions**, and **use tools** to achieve goals autonomously. Unlike a simple chatbot that just generates text, an agent follows a structured process:

1. **Think** about the problem (reasoning)
2. **Decide** which tool or action to take
3. **Observe** the result
4. **Respond** with a final answer

This is known as the **ReAct** (Reason + Act) pattern.

---

## What Is LangGraph?

LangGraph is a framework for building **stateful, multi-step AI workflows** as graphs. Each step in the process is a **node**, and data flows between nodes through a shared **state** object.

```
START --> Reason Node --> Tool Node --> Response Node --> END
```

LangGraph handles the execution order, state management, and flow control.

---

## How This Demo Works

The demo creates a simple 3-node agent graph:

| Node | Purpose | Output |
|------|---------|--------|
| **Reason Node** | Interprets the user's input and thinks step-by-step | `Thought: ...` |
| **Tool Decision Node** | Decides which tool/action to use | `Action: ... Observation: ...` |
| **Response Node** | Generates the final answer | `Final Answer: ...` |

The web UI streams the execution in real-time using Server-Sent Events (SSE), highlighting each node as it runs.

---

## Project Structure

```
introduction-to-ai-agent/
|
├── app.py              # FastAPI server with SSE streaming
├── graph.py            # LangGraph workflow definition
├── nodes.py            # Node functions (Reason, Tool, Response)
├── models.py           # Pydantic state model and API schemas
├── requirements.txt    # Python dependencies
|
├── ui/
│   ├── index.html      # Main HTML page
│   ├── script.js       # Client-side SSE handler
│   └── style.css       # Dark theme styling
|
└── README.md
```

---

## Getting Started

### Prerequisites

- Python 3.11 or higher

### Installation

```bash
pip install -r requirements.txt
```

### Run the Demo

```bash
python app.py
```

Then open **http://localhost:8000** in your browser.

### Usage

1. Type a question in the input box (e.g., "What are AI agents?")
2. Click **Run Agent**
3. Watch the graph execute node by node
4. Read the output from each step in the execution log

---

## Tech Stack

- **LangGraph** - Agent graph framework
- **LangChain Core** - Foundation for LangChain ecosystem
- **Pydantic** - Data validation and state models
- **FastAPI** - Web server with SSE streaming
- **Uvicorn** - ASGI server
- **HTML + CSS + JS** - Simple frontend (no frameworks)
