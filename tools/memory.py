"""Central memory — persistent key-value store shared by all agents.

Each agent can read/write facts, decisions, and context.  Memory lives
in a JSON file at the project root so it survives across runs.
"""

import json
import os
from crewai.tools import tool

MEMORY_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".agent_memory.json")


def _load() -> dict:
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def _save(memory: dict):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)


@tool("Read Memory")
def read_memory(key: str) -> str:
    """Read a value from the shared agent memory by key.
    Use this to recall facts, decisions, or context stored by another agent.
    Returns the value as a string, or 'Key not found.' if the key doesn't exist.
    """
    memory = _load()
    val = memory.get(key)
    if val is None:
        return f"Key not found: {key}"
    return str(val)


@tool("Write Memory")
def write_memory(key: str, value: str) -> str:
    """Write a fact, decision, or piece of context into the shared agent memory.
    The value is stored under the given key and can be read by any agent later
    using the Read Memory tool.
    """
    memory = _load()
    memory[key] = value
    _save(memory)
    return f"Stored: {key}"


@tool("List Memory Keys")
def list_memory_keys(pattern: str = "") -> str:
    """List all keys available in shared agent memory.
    Optionally filter by a substring pattern.
    """
    memory = _load()
    keys = list(memory.keys())
    if pattern:
        keys = [k for k in keys if pattern.lower() in k.lower()]
    if not keys:
        return "No keys found."
    return "\n".join(keys)


def get_all() -> dict:
    """Return the full memory dict (for use outside the tool interface)."""
    return _load()
