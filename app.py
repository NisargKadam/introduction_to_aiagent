"""
app.py - FastAPI Server for the Multi-Pattern AI Agent Demo

This server provides:
  1. A static file server for the UI (HTML/CSS/JS)
  2. Pattern switching between 4 agent architectures
  3. An SSE (Server-Sent Events) endpoint that streams graph execution
     step-by-step so the UI can show live progress.

Run with:
    python app.py
"""

import json
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel

from models import UserRequest
from patterns import PATTERN_REGISTRY
import nodes

# ──────────────────────────────────────────────
# App Setup
# ──────────────────────────────────────────────

app = FastAPI(
    title="Introduction to AI Agents",
    description="Educational demo showing multiple agent graph patterns.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ──────────────────────────────────────────────
# Pattern State
# ──────────────────────────────────────────────

current_pattern = "sequential"
compiled_graphs = {}


def get_graph(pattern_name: str):
    """Get or build the compiled graph for a pattern."""
    if pattern_name not in compiled_graphs:
        builder = PATTERN_REGISTRY[pattern_name]["builder"]
        compiled_graphs[pattern_name] = builder()
    return compiled_graphs[pattern_name]


# Build the default graph at startup
get_graph(current_pattern)


# ──────────────────────────────────────────────
# Initial State Builders
# ──────────────────────────────────────────────

def build_initial_state(pattern: str, prompt: str) -> dict:
    """Build the correct initial state dict for each pattern."""
    if pattern == "sequential":
        return {
            "user_input": prompt,
            "thought": "",
            "action": "",
            "observation": "",
            "final_answer": "",
        }
    elif pattern == "branching":
        return {
            "user_input": prompt,
            "route": "",
            "branch_output": "",
            "final_answer": "",
        }
    elif pattern == "parallel":
        return {
            "user_input": prompt,
            "perspectives": [],
            "final_answer": "",
        }
    elif pattern == "loop":
        return {
            "user_input": prompt,
            "draft": "",
            "critique": "",
            "iteration": 0,
            "is_good_enough": False,
            "final_answer": "",
        }


# ──────────────────────────────────────────────
# Node Display Info (for SSE labels)
# ──────────────────────────────────────────────

NODE_LABELS = {
    # Sequential
    "reason_node": "Reasoning...",
    "tool_node": "Deciding tool...",
    "response_node": "Generating answer...",
    # Branching
    "classify": "Classifying query...",
    "technical": "Technical analysis...",
    "creative": "Creative analysis...",
    "factual": "Factual analysis...",
    "merge": "Merging result...",
    # Parallel
    "analyst_technical": "Technical perspective...",
    "analyst_practical": "Practical perspective...",
    "analyst_beginner": "Beginner perspective...",
    "synthesize": "Synthesizing...",
    # Loop
    "draft": "Drafting...",
    "critique": "Critiquing...",
    "finalize": "Finalizing...",
}


def get_node_output(node_name: str, node_output: dict) -> str:
    """Extract the display-worthy output from a node's state update."""
    # Try common output fields in priority order
    for key in ["final_answer", "thought", "branch_output", "draft", "critique"]:
        if key in node_output and node_output[key]:
            return str(node_output[key])

    # For parallel analysts, return perspectives
    if "perspectives" in node_output and node_output["perspectives"]:
        return str(node_output["perspectives"][-1]) if node_output["perspectives"] else ""

    # For tool_node, combine action + observation
    if "action" in node_output:
        action = node_output.get("action", "")
        observation = node_output.get("observation", "")
        return f"Action: {action}\nObservation: {observation}"

    # For classify/route nodes
    if "route" in node_output:
        return f"Routed to: {node_output['route']}"

    # For critique with is_good_enough
    if "is_good_enough" in node_output:
        status = "APPROVED" if node_output["is_good_enough"] else "NEEDS WORK"
        return f"[{status}] {node_output.get('critique', '')}"

    # Fallback: return all non-empty values
    parts = [f"{k}: {v}" for k, v in node_output.items() if v]
    return "\n".join(parts) if parts else "(no output)"


# ──────────────────────────────────────────────
# SSE Streaming Endpoint (Pattern-Agnostic)
# ──────────────────────────────────────────────

@app.post("/run")
async def run_agent(request: UserRequest):
    """Execute the active pattern's graph and stream each node via SSE."""

    def event_stream():
        pattern = current_pattern
        graph = get_graph(pattern)
        initial_state = build_initial_state(pattern, request.prompt)

        # Send pattern info first
        yield sse_event("pattern_info", {"pattern": pattern})

        for event in graph.stream(initial_state, stream_mode="updates"):
            for node_name, node_output in event.items():
                # Skip __start__ and __end__ internal nodes
                if node_name.startswith("__"):
                    continue

                label = NODE_LABELS.get(node_name, f"Running {node_name}...")
                output = get_node_output(node_name, node_output)

                # Send start event
                yield sse_event("node_start", {
                    "node": node_name,
                    "label": label,
                })

                # Send complete event with output
                yield sse_event("node_complete", {
                    "node": node_name,
                    "output": output,
                    "state": {k: str(v)[:200] for k, v in node_output.items()},
                })

        yield sse_event("done", {"status": "complete"})

    return StreamingResponse(event_stream(), media_type="text/event-stream")


def sse_event(event_type: str, data: dict) -> str:
    """Format a dict as a Server-Sent Event string."""
    return f"event: {event_type}\ndata: {json.dumps(data)}\n\n"


# ──────────────────────────────────────────────
# Pattern Endpoints
# ──────────────────────────────────────────────

@app.get("/patterns")
async def get_patterns():
    """Return available patterns and which one is active."""
    patterns = {}
    for key, info in PATTERN_REGISTRY.items():
        patterns[key] = {
            "name": info["name"],
            "description": info["description"],
        }
    return {"patterns": patterns, "current": current_pattern}


class PatternRequest(BaseModel):
    pattern: str


@app.post("/set-pattern")
async def set_pattern(request: PatternRequest):
    """Switch the active agent pattern."""
    global current_pattern
    if request.pattern not in PATTERN_REGISTRY:
        return {"error": f"Unknown pattern. Choose from: {list(PATTERN_REGISTRY.keys())}"}
    current_pattern = request.pattern
    get_graph(current_pattern)  # pre-compile
    print(f"[Config] Pattern changed to: {current_pattern}")
    return {"current": current_pattern}


# ──────────────────────────────────────────────
# Model Selection Endpoints
# ──────────────────────────────────────────────

class ModelRequest(BaseModel):
    model: str


@app.get("/models")
async def get_models():
    return {
        "models": nodes.AVAILABLE_MODELS,
        "current": nodes.current_model,
    }


@app.post("/set-model")
async def set_model(request: ModelRequest):
    if request.model not in nodes.AVAILABLE_MODELS:
        return {"error": f"Unknown model. Choose from: {nodes.AVAILABLE_MODELS}"}
    nodes.current_model = request.model
    print(f"[Config] Model changed to: {request.model}")
    return {"current": nodes.current_model}


# ──────────────────────────────────────────────
# Parameter Tuning Endpoints
# ──────────────────────────────────────────────

@app.get("/params")
async def get_params():
    return {
        "temperature": nodes.LLM_TEMPERATURE,
        "max_tokens": nodes.LLM_MAX_TOKENS,
        "top_p": nodes.LLM_TOP_P,
        "frequency_penalty": nodes.LLM_FREQUENCY_PENALTY,
        "presence_penalty": nodes.LLM_PRESENCE_PENALTY,
    }


class ParamsRequest(BaseModel):
    temperature: float = None
    max_tokens: int = None
    top_p: float = None
    frequency_penalty: float = None
    presence_penalty: float = None


@app.post("/set-params")
async def set_params(request: ParamsRequest):
    if request.temperature is not None:
        nodes.LLM_TEMPERATURE = request.temperature
    if request.max_tokens is not None:
        nodes.LLM_MAX_TOKENS = request.max_tokens
    if request.top_p is not None:
        nodes.LLM_TOP_P = request.top_p
    if request.frequency_penalty is not None:
        nodes.LLM_FREQUENCY_PENALTY = request.frequency_penalty
    if request.presence_penalty is not None:
        nodes.LLM_PRESENCE_PENALTY = request.presence_penalty

    print(f"[Config] Params updated: temp={nodes.LLM_TEMPERATURE}, "
          f"max_tokens={nodes.LLM_MAX_TOKENS}, top_p={nodes.LLM_TOP_P}")

    return {
        "temperature": nodes.LLM_TEMPERATURE,
        "max_tokens": nodes.LLM_MAX_TOKENS,
        "top_p": nodes.LLM_TOP_P,
        "frequency_penalty": nodes.LLM_FREQUENCY_PENALTY,
        "presence_penalty": nodes.LLM_PRESENCE_PENALTY,
    }


# ──────────────────────────────────────────────
# Serve the UI
# ──────────────────────────────────────────────

app.mount("/ui", StaticFiles(directory="ui"), name="ui")


@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    with open("ui/index.html", "r") as f:
        return HTMLResponse(content=f.read())


# ──────────────────────────────────────────────
# Entry Point
# ──────────────────────────────────────────────

if __name__ == "__main__":
    print("\n=== Introduction to AI Agents ===")
    print(f"Pattern: {PATTERN_REGISTRY[current_pattern]['name']}")
    print(f"Model: {nodes.current_model}")
    print("Open http://localhost:8000 in your browser\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)
