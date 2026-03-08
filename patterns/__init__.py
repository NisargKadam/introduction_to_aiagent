"""
patterns/__init__.py - Pattern Registry

Central registry mapping pattern names to their graph builders
and metadata for the UI.
"""

from graph import build_agent_graph
from patterns.branching import build_branching_graph
from patterns.parallel import build_parallel_graph
from patterns.loop import build_loop_graph


PATTERN_REGISTRY = {
    "sequential": {
        "name": "Sequential (ReAct)",
        "description": "Linear step-by-step: Reason -> Act -> Respond",
        "builder": build_agent_graph,
    },
    "branching": {
        "name": "Branching (Router)",
        "description": "Classify input, route to one specialist branch",
        "builder": build_branching_graph,
    },
    "parallel": {
        "name": "Parallel (Fan-out/Fan-in)",
        "description": "3 analysts run concurrently, then synthesize",
        "builder": build_parallel_graph,
    },
    "loop": {
        "name": "Loop (Reflexion)",
        "description": "Draft -> Critique -> Revise until approved",
        "builder": build_loop_graph,
    },
}
