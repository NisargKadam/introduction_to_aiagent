"""
models.py - Pydantic State Model for the Agent Graph

This module defines the state that flows between nodes in the graph.
Each node reads from and writes to this shared state object.

The state follows the ReAct pattern:
  Thought -> Action -> Observation -> Final Answer
"""

import operator
from typing import Annotated, Optional
from pydantic import BaseModel, Field
from typing_extensions import TypedDict


# --- LangGraph State Definition ---
# LangGraph uses TypedDict for graph state (not Pydantic BaseModel).
# This is the state that gets passed between every node in the graph.

class AgentState(TypedDict):
    """State shared across all nodes in the agent graph.

    Fields:
        user_input:    The original question from the user.
        thought:       Reasoning produced by the Reason node (Node 1).
        action:        The tool/action chosen by the Tool Decision node (Node 2).
        observation:   What the tool observed or found (Node 2).
        final_answer:  The completed response for the user (Node 3).
    """
    user_input: str
    thought: str
    action: str
    observation: str
    final_answer: str


# --- Pattern 2: Branching (Router) State ---
# The router classifies the query and sends it to one specialist branch.

class BranchingState(TypedDict):
    """State for the Branching/Router pattern.

    Fields:
        user_input:     The original question from the user.
        route:          Classification result ("technical", "creative", or "factual").
        branch_output:  Output from whichever specialist branch was chosen.
        final_answer:   The completed response for the user.
    """
    user_input: str
    route: str
    branch_output: str
    final_answer: str


# --- Pattern 3: Parallel (Fan-out/Fan-in) State ---
# Multiple analysts run simultaneously, results merged via reducer.
# The Annotated[list, operator.add] tells LangGraph:
#   "When multiple nodes write to this field at the same time,
#    APPEND their results instead of overwriting."

class ParallelState(TypedDict):
    """State for the Parallel/Fan-out pattern.

    Fields:
        user_input:     The original question from the user.
        perspectives:   List of answers from parallel analysts (merged by reducer).
        final_answer:   The synthesized response for the user.
    """
    user_input: str
    perspectives: Annotated[list[str], operator.add]
    final_answer: str


# --- Pattern 4: Loop (Reflexion) State ---
# The agent drafts, self-critiques, and revises in a loop.

class LoopState(TypedDict):
    """State for the Loop/Reflexion pattern.

    Fields:
        user_input:      The original question from the user.
        draft:           The current draft answer.
        critique:        Feedback from the self-critique step.
        iteration:       How many draft-critique cycles have run.
        is_good_enough:  Whether the critique approved the draft.
        final_answer:    The completed response for the user.
    """
    user_input: str
    draft: str
    critique: str
    iteration: int
    is_good_enough: bool
    final_answer: str


# --- API Request / Response Schemas ---
# These Pydantic models are used by the FastAPI endpoints.

class UserRequest(BaseModel):
    """Incoming request from the UI."""
    prompt: str = Field(..., min_length=1, description="The user's question")


class NodeUpdate(BaseModel):
    """One step of execution sent to the UI via SSE."""
    node: str
    status: str
    output: str


class AgentResponse(BaseModel):
    """Final response returned to the UI."""
    thought: str
    action: str
    observation: str
    final_answer: str
