import os
from crewai.tools import tool

REPO_ROOT = os.path.abspath("clients/gta-scrub/repo")


def _safe_path(path):
    full_path = os.path.abspath(os.path.join(REPO_ROOT, path))
    if not full_path.startswith(REPO_ROOT):
        raise ValueError(f"Blocked: {path} is outside the allowed repo directory")
    return full_path


@tool("Read File")
def read_file_tool(path: str) -> str:
    """Read a file inside the GTA Scrub repo. Path is relative to repo root, e.g. 'app/layout.tsx'."""
    with open(_safe_path(path), "r", encoding="utf-8") as f:
        return f.read()


@tool("Write File")
def write_file_tool(path: str, content: str) -> str:
    """Overwrite a file inside the GTA Scrub repo with new content. Path is relative to repo root."""
    with open(_safe_path(path), "w", encoding="utf-8") as f:
        f.write(content)
    return f"Updated {path}"


@tool("List Files")
def list_files_tool(directory: str = ".") -> str:
    """List files under a directory of the GTA Scrub repo, relative to repo root."""
    full_dir = _safe_path(directory)
    files = []
    for root, _, filenames in os.walk(full_dir):
        for name in filenames:
            files.append(os.path.relpath(os.path.join(root, name), REPO_ROOT))
    return "\n".join(files)
