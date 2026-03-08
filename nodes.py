"""
nodes.py - Node Definitions for the Agent Graph (OpenAI Powered)

Each function here is a "node" in the LangGraph workflow.
Nodes receive the current state, do some work, and return updates to the state.

The three nodes follow the ReAct (Reason + Act) pattern:

  Node 1 - Reason:    Interpret the user's input and think step-by-step.
  Node 2 - Tool:      Decide which tool/action to take and observe the result.
  Node 3 - Response:  Produce the final answer for the user.

Each node calls OpenAI with a specific system prompt.
All parameters (temperature, max_tokens, etc.) are loaded from the .env file.
"""

import os
from dotenv import load_dotenv
from openai import OpenAI
from models import AgentState

# Load configuration from .env file
load_dotenv()

# ──────────────────────────────────────────────
# OpenAI Client Setup
# ──────────────────────────────────────────────

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ── Available Models ──
# 4 carefully chosen models across different tiers:
#
#   gpt-4o        → LLM (Large Language Model) - Most capable, best reasoning
#   gpt-4o-mini   → SLM (Small Language Model) - Fast, cheap, good quality
#   gpt-4.1-mini  → Latest SLM - Newest architecture, great for structured tasks
#   gpt-4-turbo   → Turbo - High capability with optimized speed
#
AVAILABLE_MODELS = [
    "gpt-4o",          # LLM  - Best quality, slower, higher cost
    "gpt-4o-mini",     # SLM  - Great balance of speed and quality
    "gpt-4.1-mini",    # SLM  - Latest generation, structured output
    "gpt-4-turbo",     # Turbo - Fast and capable
]

# The active model (can be changed at runtime via the /set-model endpoint)
current_model = os.getenv("DEFAULT_MODEL", "gpt-4o-mini")

# ── LLM Parameters (loaded from .env) ──
LLM_TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
LLM_MAX_TOKENS = int(os.getenv("MAX_TOKENS", "300"))
LLM_TOP_P = float(os.getenv("TOP_P", "0.9"))
LLM_FREQUENCY_PENALTY = float(os.getenv("FREQUENCY_PENALTY", "0.3"))
LLM_PRESENCE_PENALTY = float(os.getenv("PRESENCE_PENALTY", "0.2"))


# ──────────────────────────────────────────────
# ORCHESTRATOR SYSTEM PROMPT
# ──────────────────────────────────────────────
# This is the master prompt that defines who the agent is.
# It is sent to the LLM at the start of every interaction.
# It tells the agent WHO it is, HOW to think, and WHAT tools it has.

ORCHESTRATOR_PROMPT = """
You are an AI Teaching Assistant specialized in explaining AI and technology concepts.

Your role:
  - You help students understand AI agents, machine learning, and related topics.
  - You follow the ReAct (Reason + Act) pattern for every question.
  - You always think step-by-step before answering.

Your available tools:
  - knowledge_lookup: Search the knowledge base for factual information.
  - web_search:       Search the web for current information.
  - calculator:       Perform mathematical calculations.

Your process for every question:
  1. THINK:    Break down what the user is really asking.
  2. ACT:      Choose the best tool and use it.
  3. OBSERVE:  Read what the tool returned.
  4. RESPOND:  Give a clear, educational answer.

Rules:
  - Always explain concepts simply, as if teaching a beginner.
  - Use examples and analogies where possible.
  - If you don't know something, say so honestly.
  - Keep responses concise (2-4 sentences per section).
"""


def _call_llm(system_prompt: str, user_message: str) -> str:
    """
    Helper: Call OpenAI and return the response text.

    Uses parameters from the .env file:
      - TEMPERATURE:       Controls creativity (0.0 = focused, 1.0 = creative)
      - MAX_TOKENS:        Maximum response length
      - TOP_P:             Nucleus sampling threshold
      - FREQUENCY_PENALTY: Reduces word repetition
      - PRESENCE_PENALTY:  Encourages new topics

    Args:
        system_prompt: Instructions for the LLM (who it is, what to do).
        user_message:  The actual content to process.

    Returns:
        The LLM's response as a string.
    """
    # gpt-4.1-* models use max_completion_tokens instead of max_tokens
    is_4_1 = current_model.startswith("gpt-4.1")
    token_key = "max_completion_tokens" if is_4_1 else "max_tokens"

    response = client.chat.completions.create(
        model=current_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        temperature=LLM_TEMPERATURE,
        top_p=LLM_TOP_P,
        frequency_penalty=LLM_FREQUENCY_PENALTY,
        presence_penalty=LLM_PRESENCE_PENALTY,
        **{token_key: LLM_MAX_TOKENS},
    )
    return response.choices[0].message.content.strip()


# ──────────────────────────────────────────────
# Node 1 - Reason Node
# ──────────────────────────────────────────────

REASON_PROMPT = ORCHESTRATOR_PROMPT + """
YOUR TASK: You are in the REASONING step of the ReAct loop.

Given the user's question, think step by step about:
  - What is the user really asking?
  - What concepts are involved?
  - What approach should I take to answer this?

Start your response with "Thought:" and explain your reasoning.
Keep it to 2-3 sentences.
"""


def reason_node(state: AgentState) -> dict:
    """
    Node 1: Interpret the user's input and produce a chain-of-thought.

    Calls the LLM with the reasoning prompt to generate a "Thought:" trace.

    Returns:
        dict with 'thought' key to merge into state.
    """
    user_input = state["user_input"]

    # Call the LLM to generate reasoning
    thought = _call_llm(REASON_PROMPT, user_input)

    print(f"[Reason Node] {thought}")
    return {"thought": thought}


# ──────────────────────────────────────────────
# Node 2 - Tool Decision Node
# ──────────────────────────────────────────────

TOOL_PROMPT = ORCHESTRATOR_PROMPT + """
YOUR TASK: You are in the ACTION step of the ReAct loop.

Based on the user's question and the reasoning provided, decide:
  1. Which tool to use (knowledge_lookup, web_search, or calculator)
  2. What information the tool found

Format your response EXACTLY like this:
Action: <tool_name>
Observation: <what the tool found - provide factual, detailed information>

Keep the observation to 2-3 sentences of factual content.
"""


def tool_node(state: AgentState) -> dict:
    """
    Node 2: Decide which tool to use and generate an observation.

    Calls the LLM with the previous reasoning context to generate
    an Action + Observation in ReAct format.

    Returns:
        dict with 'action' and 'observation' keys to merge into state.
    """
    user_input = state["user_input"]
    thought = state["thought"]

    # Give the LLM the context from the previous node
    context = f"User question: {user_input}\n\nPrevious reasoning: {thought}"

    # Call the LLM to decide on a tool and generate observation
    result = _call_llm(TOOL_PROMPT, context)

    # Parse the Action and Observation from the response
    action = "knowledge_lookup"
    observation = result

    if "Action:" in result:
        lines = result.split("\n")
        for line in lines:
            if line.strip().startswith("Action:"):
                action = line.split("Action:")[-1].strip()
            if line.strip().startswith("Observation:"):
                observation = line.split("Observation:")[-1].strip()

    print(f"[Tool Node] Action: {action}")
    print(f"[Tool Node] Observation: {observation}")
    return {"action": action, "observation": observation}


# ──────────────────────────────────────────────
# Node 3 - Final Response Node
# ──────────────────────────────────────────────

RESPONSE_PROMPT = ORCHESTRATOR_PROMPT + """
YOUR TASK: You are in the RESPOND step of the ReAct loop.

You have already:
  1. Reasoned about the question (Thought)
  2. Used a tool and got information (Action + Observation)

Now synthesize everything into a clear, educational final answer.

Start your response with "Final Answer:" and give a helpful, beginner-friendly explanation.
Keep it to 3-5 sentences.
"""


def response_node(state: AgentState) -> dict:
    """
    Node 3: Generate the final answer using all previous context.

    Calls the LLM with the full ReAct chain (thought + action + observation)
    to produce a clear final answer.

    Returns:
        dict with 'final_answer' key to merge into state.
    """
    user_input = state["user_input"]
    thought = state["thought"]
    action = state["action"]
    observation = state["observation"]

    # Give the LLM the full context from all previous nodes
    context = (
        f"User question: {user_input}\n\n"
        f"Thought: {thought}\n\n"
        f"Action: {action}\n"
        f"Observation: {observation}"
    )

    # Call the LLM to generate the final answer
    final_answer = _call_llm(RESPONSE_PROMPT, context)

    print(f"[Response Node] {final_answer}")
    return {"final_answer": final_answer}
