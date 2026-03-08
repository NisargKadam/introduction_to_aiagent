"""
patterns/parallel.py - Parallel (Fan-out/Fan-in) Agent Pattern

This pattern demonstrates CONCURRENT EXECUTION in a graph.
Three analyst nodes run IN PARALLEL (like Java's ThreadPoolExecutor),
each answering from a different perspective. Their results are then
merged by a synthesizer node.

  START -> [analyst_technical & analyst_practical & analyst_beginner] -> synthesize -> END

The key concept is the REDUCER: when multiple nodes write to the same
state field concurrently, the reducer function (operator.add for lists)
merges their outputs instead of overwriting.

LangGraph API used:
  - Multiple add_edge(START, node) calls create a parallel "superstep"
  - Annotated[list, operator.add] reducer merges concurrent writes
"""

from langgraph.graph import StateGraph, START, END

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import ParallelState
from nodes import _call_llm, ORCHESTRATOR_PROMPT


# ──────────────────────────────────────────────
# Node 1a - Technical Analyst (runs in parallel)
# ──────────────────────────────────────────────

TECHNICAL_ANALYST_PROMPT = ORCHESTRATOR_PROMPT + """
YOUR TASK: You are the TECHNICAL analyst.

Answer the user's question from a TECHNICAL perspective.
Focus on: how it works under the hood, architecture, systems, and mechanisms.
Keep it to 2-3 sentences. Start with "[TECHNICAL]"
"""


def analyst_technical(state: ParallelState) -> dict:
    """Analyze from a technical perspective (runs in parallel)."""
    result = _call_llm(TECHNICAL_ANALYST_PROMPT, state["user_input"])
    print(f"[Technical Analyst] Done")
    # Return as a single-element list so the operator.add reducer can merge
    return {"perspectives": [result]}


# ──────────────────────────────────────────────
# Node 1b - Practical Analyst (runs in parallel)
# ──────────────────────────────────────────────

PRACTICAL_ANALYST_PROMPT = ORCHESTRATOR_PROMPT + """
YOUR TASK: You are the PRACTICAL analyst.

Answer the user's question from a PRACTICAL, real-world perspective.
Focus on: use cases, examples, applications, and everyday impact.
Keep it to 2-3 sentences. Start with "[PRACTICAL]"
"""


def analyst_practical(state: ParallelState) -> dict:
    """Analyze from a practical perspective (runs in parallel)."""
    result = _call_llm(PRACTICAL_ANALYST_PROMPT, state["user_input"])
    print(f"[Practical Analyst] Done")
    return {"perspectives": [result]}


# ──────────────────────────────────────────────
# Node 1c - Beginner Analyst (runs in parallel)
# ──────────────────────────────────────────────

BEGINNER_ANALYST_PROMPT = ORCHESTRATOR_PROMPT + """
YOUR TASK: You are the BEGINNER-FRIENDLY analyst.

Answer the user's question as if explaining to a complete beginner.
Focus on: simple language, analogies, and "why should I care?" motivation.
Keep it to 2-3 sentences. Start with "[BEGINNER]"
"""


def analyst_beginner(state: ParallelState) -> dict:
    """Analyze from a beginner perspective (runs in parallel)."""
    result = _call_llm(BEGINNER_ANALYST_PROMPT, state["user_input"])
    print(f"[Beginner Analyst] Done")
    return {"perspectives": [result]}


# ──────────────────────────────────────────────
# Node 2 - Synthesize (Fan-in)
# ──────────────────────────────────────────────

SYNTHESIZE_PROMPT = ORCHESTRATOR_PROMPT + """
YOUR TASK: You are the SYNTHESIZER.

You received answers from 3 analysts (technical, practical, and beginner).
Combine their perspectives into one cohesive, well-rounded final answer.

Start with "Final Answer:" and keep it to 4-6 sentences.
"""


def synthesize_node(state: ParallelState) -> dict:
    """Merge all parallel perspectives into a unified answer."""
    perspectives_text = "\n\n".join(state["perspectives"])
    context = (
        f"User question: {state['user_input']}\n\n"
        f"Analyst perspectives:\n{perspectives_text}"
    )
    result = _call_llm(SYNTHESIZE_PROMPT, context)
    print(f"[Synthesize Node] Merged {len(state['perspectives'])} perspectives")
    return {"final_answer": result}


# ──────────────────────────────────────────────
# Graph Builder
# ──────────────────────────────────────────────

def build_parallel_graph():
    """Build the Parallel (Fan-out/Fan-in) agent graph.

    Graph flow:
      START -> [analyst_technical & analyst_practical & analyst_beginner] -> synthesize -> END

    When multiple edges leave the same node (START in this case),
    LangGraph creates a "superstep" -- all target nodes run concurrently.
    The operator.add reducer on the 'perspectives' field safely merges
    their outputs as each analyst completes.
    """
    workflow = StateGraph(ParallelState)

    # Add nodes
    workflow.add_node("analyst_technical", analyst_technical)
    workflow.add_node("analyst_practical", analyst_practical)
    workflow.add_node("analyst_beginner", analyst_beginner)
    workflow.add_node("synthesize", synthesize_node)

    # Fan-out: START connects to all 3 analysts
    # LangGraph runs them as a parallel superstep automatically!
    workflow.add_edge(START, "analyst_technical")
    workflow.add_edge(START, "analyst_practical")
    workflow.add_edge(START, "analyst_beginner")

    # Fan-in: all analysts connect to synthesize
    workflow.add_edge("analyst_technical", "synthesize")
    workflow.add_edge("analyst_practical", "synthesize")
    workflow.add_edge("analyst_beginner", "synthesize")

    workflow.add_edge("synthesize", END)

    graph = workflow.compile()
    print("[Graph] Parallel (Fan-out/Fan-in) graph compiled!")
    return graph
