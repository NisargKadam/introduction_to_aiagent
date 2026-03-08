"""
patterns/loop.py - Loop (Reflexion) Agent Pattern

This pattern demonstrates CYCLIC EXECUTION in a graph.
The agent drafts an answer, critiques it, and loops back to revise
until the critique approves OR a max iteration limit is reached.

  START -> draft -> critique -> [loop back to draft | finalize] -> END

This teaches students how agents can self-improve through iteration,
similar to how humans review and revise their own work.

LangGraph API used:
  - add_conditional_edges() that can route BACK to an earlier node
"""

from langgraph.graph import StateGraph, START, END

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import LoopState
from nodes import _call_llm, ORCHESTRATOR_PROMPT


# Maximum number of draft-critique iterations
MAX_ITERATIONS = 3


# ──────────────────────────────────────────────
# Node 1 - Draft
# ──────────────────────────────────────────────

DRAFT_PROMPT = ORCHESTRATOR_PROMPT + """
YOUR TASK: Write a clear, educational answer to the user's question.

Keep it to 3-5 sentences. Be thorough but concise.
"""

REVISE_PROMPT = ORCHESTRATOR_PROMPT + """
YOUR TASK: Revise your previous draft based on the critique feedback.

Improve the areas mentioned in the critique while keeping what was good.
Keep it to 3-5 sentences.
"""


def draft_node(state: LoopState) -> dict:
    """Write or revise a draft answer."""
    iteration = state.get("iteration", 0) + 1

    if iteration == 1:
        # First draft: write from scratch
        result = _call_llm(DRAFT_PROMPT, state["user_input"])
        print(f"[Draft Node] Iteration {iteration} - Initial draft")
    else:
        # Revision: use critique to improve
        context = (
            f"User question: {state['user_input']}\n\n"
            f"Previous draft: {state['draft']}\n\n"
            f"Critique: {state['critique']}\n\n"
            f"Please revise the draft to address the critique."
        )
        result = _call_llm(REVISE_PROMPT, context)
        print(f"[Draft Node] Iteration {iteration} - Revised draft")

    return {"draft": result, "iteration": iteration}


# ──────────────────────────────────────────────
# Node 2 - Critique
# ──────────────────────────────────────────────

CRITIQUE_PROMPT = """You are a strict quality reviewer for educational content.

Evaluate this draft answer for:
1. Accuracy - Is the information correct?
2. Clarity - Is it easy for a beginner to understand?
3. Completeness - Does it answer the full question?

If the draft is GOOD (meets all 3 criteria), respond starting with "APPROVED:" followed by brief praise.
If the draft NEEDS IMPROVEMENT, respond starting with "NEEDS_WORK:" followed by specific feedback.

Be concise (2-3 sentences max)."""


def critique_node(state: LoopState) -> dict:
    """Critique the current draft and decide if it's good enough."""
    context = (
        f"User question: {state['user_input']}\n\n"
        f"Draft answer (iteration {state['iteration']}):\n{state['draft']}"
    )
    result = _call_llm(CRITIQUE_PROMPT, context)

    is_good = result.strip().upper().startswith("APPROVED")

    print(f"[Critique Node] {'APPROVED' if is_good else 'NEEDS_WORK'} (iteration {state['iteration']})")
    return {"critique": result, "is_good_enough": is_good}


# ──────────────────────────────────────────────
# Node 3 - Finalize
# ──────────────────────────────────────────────

def finalize_node(state: LoopState) -> dict:
    """Format the approved draft as the final answer."""
    iterations = state["iteration"]
    draft = state["draft"]

    final_answer = (
        f"Final Answer (after {iterations} iteration{'s' if iterations > 1 else ''}):\n\n"
        f"{draft}"
    )

    print(f"[Finalize Node] Completed after {iterations} iterations")
    return {"final_answer": final_answer}


# ──────────────────────────────────────────────
# Routing Function (loop or exit)
# ──────────────────────────────────────────────

def should_continue(state: LoopState) -> str:
    """Decide whether to loop back for revision or finalize.

    Exit conditions:
      1. Critique said it's good enough
      2. Max iterations reached (safety limit)
    """
    if state["is_good_enough"]:
        print(f"[Router] Critique approved -> finalize")
        return "finalize"
    if state["iteration"] >= MAX_ITERATIONS:
        print(f"[Router] Max iterations ({MAX_ITERATIONS}) reached -> finalize")
        return "finalize"
    print(f"[Router] Needs work -> loop back to draft")
    return "draft"


# ──────────────────────────────────────────────
# Graph Builder
# ──────────────────────────────────────────────

def build_loop_graph():
    """Build the Loop (Reflexion) agent graph.

    Graph flow:
      START -> draft -> critique -> [draft (loop) | finalize] -> END
    """
    workflow = StateGraph(LoopState)

    # Add nodes
    workflow.add_node("draft", draft_node)
    workflow.add_node("critique", critique_node)
    workflow.add_node("finalize", finalize_node)

    # Edges
    workflow.add_edge(START, "draft")
    workflow.add_edge("draft", "critique")

    # Conditional: loop back to draft OR proceed to finalize
    workflow.add_conditional_edges(
        "critique",
        should_continue,
        {"draft": "draft", "finalize": "finalize"},
    )

    workflow.add_edge("finalize", END)

    graph = workflow.compile()
    print("[Graph] Loop (Reflexion) graph compiled!")
    return graph
