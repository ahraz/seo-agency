#!/usr/bin/env python3
"""Entry point for CrewAI Enterprise deployment.

Called by `crewai run` or by the CrewAI Enterprise platform when
a run is triggered from the web UI at https://app.crewai.com.
"""

import sys
import os

# Ensure both project root and src/ are on the path
_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
_src_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in (_project_root, _src_root):
    if p not in sys.path:
        sys.path.insert(0, p)

import subprocess
from seo_agency.crew import SeoAgencyCrew
from dotenv import load_dotenv

load_dotenv()


def _ensure_repo(repo_path: str) -> None:
    """Clone the repo if the target directory is empty.

    The platform creates the working directory but does NOT populate it.
    The agent file tools need files to work with, so we clone here so the
    crew starts with a populated repo.

    REPO_URL must be set as an environment variable in the CrewAI dashboard.
    """
    repo_url = os.environ.get("REPO_URL", "").strip()
    if not repo_url:
        print("⚠️  REPO_URL not set — skipping clone. Agents will find an empty repo.")
        return

    abs_path = os.path.abspath(repo_path)
    os.makedirs(abs_path, exist_ok=True)

    # Check if already populated
    if os.listdir(abs_path):
        print(f"📁 Repo already populated at {abs_path} — skipping clone.")
        return

    token = (
        os.environ.get("GITHUB_TOKEN")
        or os.environ.get("GH_TOKEN")
        or ""
    )
    if token and repo_url.startswith("https://"):
        repo_url = repo_url.replace("https://", f"https://{token}@", 1)

    print(f"📦 Cloning {os.environ.get('REPO_URL', '')} → {abs_path} ...")
    try:
        result = subprocess.run(
            ["git", "clone", repo_url, abs_path],
            capture_output=True, text=True, timeout=120,
        )
        if result.returncode == 0:
            print(f"✅ Clone successful ({len(os.listdir(abs_path))} items)")
        else:
            print(f"❌ Clone failed: {result.stderr.strip()[:300]}")
    except Exception as e:
        print(f"❌ Clone exception: {e}")


def run():
    """Run the full SEO audit + fix crew.

    This is the entry point that CrewAI Enterprise calls when you
    trigger a run from the web dashboard.

    On CrewAI Enterprise the working directory IS the repo root, so
    REPO_PATH defaults to '.' (current directory). REPO_URL must be
    set so the repo can be cloned if the directory is empty.

    Configure these in the CrewAI Enterprise dashboard
    under Environment Variables:

        REPO_URL   — e.g. https://github.com/ahraz/gtascrub.com (required)
        REPO_PATH  — path to the repo (default: '.' — the CWD on the platform)
    """
    repo_path = os.getenv("REPO_PATH", ".")
    _ensure_repo(repo_path)
    crew = SeoAgencyCrew(repo_path=repo_path).crew()
    result = crew.kickoff(inputs={"repo_path": repo_path})
    return result
