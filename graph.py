"""
graph.py - LangGraph Workflow Definition

This module wires the three nodes into a sequential graph:

  START  -->  reason_node  -->  tool_node  -->  response_node  -->  END

LangGraph manages the state automatically: each node receives the full
state and returns only the fields it wants to update.
"""

from langgraph.graph import StateGraph, START, END
from models import AgentState
from nodes import reason_node, tool_node, response_node


def build_agent_graph() -> StateGraph:
    """
    Build and compile the agent graph.

    Returns:
        A compiled LangGraph that can be invoked with an initial state.
    """

    # 1. Create a new graph with our state schema
    workflow = StateGraph(AgentState)

    # 2. Add each node to the graph
    #    The first argument is the node name (shown in logs & UI).
    #    The second argument is the function that runs for that node.
    workflow.add_node("reason_node", reason_node)
    workflow.add_node("tool_node", tool_node)
    workflow.add_node("response_node", response_node)

    # 3. Define the edges (execution order)
    #    START -> reason_node -> tool_node -> response_node -> END
    workflow.add_edge(START, "reason_node")
    workflow.add_edge("reason_node", "tool_node")
    workflow.add_edge("tool_node", "response_node")
    workflow.add_edge("response_node", END)

    # 4. Compile the graph into a runnable
    graph = workflow.compile()

    print("[Graph] Agent graph compiled successfully!")
    print("[Graph] Flow: START -> reason_node -> tool_node -> response_node -> END")

    return graph
