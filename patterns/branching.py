"""
patterns/branching.py - Branching (Router) Agent Pattern

This pattern demonstrates CONDITIONAL ROUTING in a graph.
A classifier node inspects the user's query and routes it to
one of three specialist branches:

  START -> classify -> [technical | creative | factual] -> merge -> END

Only ONE branch executes per query. This teaches students how
agents can dynamically choose different processing paths.

LangGraph API used:
  - add_conditional_edges(source, routing_function, path_map)
"""

from langgraph.graph import StateGraph, START, END

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import BranchingState
from nodes import _call_llm, ORCHESTRATOR_PROMPT


# ──────────────────────────────────────────────
# Node 1 - Classify (Router)
# ──────────────────────────────────────────────

CLASSIFY_PROMPT = """You are a query classifier. Classify the user's question into EXACTLY one category:

- "technical" -> if the question is about how something works, code, architecture, or systems
- "creative" -> if the question is about ideas, brainstorming, analogies, or creative explanations
- "factual" -> if the question is about definitions, facts, history, or straightforward information

Respond with ONLY the single word: technical, creative, or factual.
Nothing else."""


def classify_node(state: BranchingState) -> dict:
    """Classify the query to decide which branch to route to."""
    result = _call_llm(CLASSIFY_PROMPT, state["user_input"]).lower().strip()

    # Parse the classification (default to factual if unclear)
    route = "factual"
    for category in ["technical", "creative", "factual"]:
        if category in result:
            route = category
            break

    print(f"[Classify Node] Route: {route}")
    return {"route": route}


# ──────────────────────────────────────────────
# Node 2a - Technical Branch
# ──────────────────────────────────────────────

TECHNICAL_PROMPT = ORCHESTRATOR_PROMPT + """
YOUR TASK: You are the TECHNICAL specialist.

Provide a step-by-step technical explanation of the user's question.
Focus on: how things work, architecture, components, and mechanisms.
Keep it to 3-4 sentences.
"""


def technical_node(state: BranchingState) -> dict:
    """Handle technical queries with detailed explanations."""
    result = _call_llm(TECHNICAL_PROMPT, state["user_input"])
    print(f"[Technical Branch] {result[:80]}...")
    return {"branch_output": result}


# ──────────────────────────────────────────────
# Node 2b - Creative Branch
# ──────────────────────────────────────────────

CREATIVE_PROMPT = ORCHESTRATOR_PROMPT + """
YOUR TASK: You are the CREATIVE specialist.

Explain the user's question using vivid analogies, metaphors, and storytelling.
Make it memorable and fun. Think of it like explaining to a curious friend.
Keep it to 3-4 sentences.
"""


def creative_node(state: BranchingState) -> dict:
    """Handle creative queries with analogies and storytelling."""
    result = _call_llm(CREATIVE_PROMPT, state["user_input"])
    print(f"[Creative Branch] {result[:80]}...")
    return {"branch_output": result}


# ──────────────────────────────────────────────
# Node 2c - Factual Branch
# ──────────────────────────────────────────────

FACTUAL_PROMPT = ORCHESTRATOR_PROMPT + """
YOUR TASK: You are the FACTUAL specialist.

Provide a clear, concise, factual answer to the user's question.
Focus on: definitions, key facts, and accurate information.
Keep it to 2-3 sentences. Be precise.
"""


def factual_node(state: BranchingState) -> dict:
    """Handle factual queries with precise definitions."""
    result = _call_llm(FACTUAL_PROMPT, state["user_input"])
    print(f"[Factual Branch] {result[:80]}...")
    return {"branch_output": result}


# ──────────────────────────────────────────────
# Node 3 - Merge
# ──────────────────────────────────────────────

MERGE_PROMPT = ORCHESTRATOR_PROMPT + """
YOUR TASK: You are the MERGE node.

Take the specialist's response below and present it as a polished final answer.
Add a brief note about which specialist handled the query (technical, creative, or factual).
Start with "Final Answer:" and keep it to 3-5 sentences.
"""


def merge_node(state: BranchingState) -> dict:
    """Merge the branch output into a final answer."""
    context = (
        f"User question: {state['user_input']}\n"
        f"Specialist type: {state['route']}\n"
        f"Specialist response: {state['branch_output']}"
    )
    result = _call_llm(MERGE_PROMPT, context)
    print(f"[Merge Node] {result[:80]}...")
    return {"final_answer": result}


# ──────────────────────────────────────────────
# Routing Function
# ──────────────────────────────────────────────

def route_question(state: BranchingState) -> str:
    """Return the branch name based on the classification."""
    return state["route"]


# ──────────────────────────────────────────────
# Graph Builder
# ──────────────────────────────────────────────

def build_branching_graph():
    """Build the Branching (Router) agent graph.

    Graph flow:
      START -> classify -> (conditional) -> [technical | creative | factual] -> merge -> END
    """
    workflow = StateGraph(BranchingState)

    # Add nodes
    workflow.add_node("classify", classify_node)
    workflow.add_node("technical", technical_node)
    workflow.add_node("creative", creative_node)
    workflow.add_node("factual", factual_node)
    workflow.add_node("merge", merge_node)

    # Edges
    workflow.add_edge(START, "classify")

    # Conditional routing: classify decides which branch to take
    workflow.add_conditional_edges(
        "classify",
        route_question,
        {"technical": "technical", "creative": "creative", "factual": "factual"},
    )

    # All branches converge to merge
    workflow.add_edge("technical", "merge")
    workflow.add_edge("creative", "merge")
    workflow.add_edge("factual", "merge")
    workflow.add_edge("merge", END)

    graph = workflow.compile()
    print("[Graph] Branching (Router) graph compiled!")
    return graph
