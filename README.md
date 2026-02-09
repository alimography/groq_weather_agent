🚀 Project Overview

This project implements a deterministic AI agent framework powered by Groq LLMs, designed to strictly follow a JSON state machine for reasoning and action execution. The agent progresses through well-defined steps—PLAN, TOOL, and OUTPUT—ensuring predictable and reliable behavior.

The system validates every model response using Pydantic, safely executes external tools (such as weather APIs and system commands), and includes recovery mechanisms for invalid or malformed LLM outputs. This design makes the agent suitable for real-world, production-grade workflows where consistency and control are critical.

Tech Stack (Resume + GitHub)

Languages: Python

LLMs: Groq (LLaMA-3.1)

Frameworks: Pydantic

Concepts: LLM Agents, Tool Calling, Chain-of-Thought Control, State Machines

APIs: REST (wttr.in weather API)
