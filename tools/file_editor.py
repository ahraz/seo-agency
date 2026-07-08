import os
from crewai.tools import tool


def make_file_tools(repo_root: str):
    """Create file-editing tools scoped to a specific repo root.

    Use this factory so tools work with any cloned repo, not just GTA Scrub.
    """
    abs_root = os.path.abspath(repo_root)

    if not os.path.exists(abs_root):
        os.makedirs(abs_root, exist_ok=True)

    def _safe_path(path: str) -> str:
        full = os.path.abspath(os.path.join(abs_root, path))
        if not full.startswith(abs_root):
            raise ValueError(f"Blocked: {path} is outside the allowed repo directory")
        return full

    @tool("Read File")
    def read_file_tool(path: str) -> str:
        """Read a file from the repo. Path is relative to repo root, e.g. 'app/layout.tsx'."""
        with open(_safe_path(path), "r", encoding="utf-8") as f:
            return f.read()

    @tool("Write File")
    def write_file_tool(path: str, content: str) -> str:
        """Write (overwrite) a file in the repo. Path is relative to repo root."""
        full_path = _safe_path(path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Updated {path}"

    @tool("Delete File")
    def delete_file_tool(path: str) -> str:
        """Delete a file from the repo. Path is relative to repo root. Use this when a file needs to be removed entirely."""
        full_path = _safe_path(path)
        if not os.path.exists(full_path):
            return f"File already gone: {path}"
        os.remove(full_path)
        return f"Deleted {path}"

    @tool("List Files")
    def list_files_tool(directory: str = ".") -> str:
        """List files under a directory of the repo, relative to repo root."""
        full_dir = _safe_path(directory)
        files = []
        for root, _, filenames in os.walk(full_dir):
            for name in filenames:
                rel = os.path.relpath(os.path.join(root, name), abs_root)
                files.append(rel)
        return "\n".join(files)

    return read_file_tool, write_file_tool, list_files_tool, delete_file_tool
