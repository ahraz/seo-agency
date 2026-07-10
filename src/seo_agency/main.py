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
    """

    def _log(msg: str) -> None:
        print(f"[_ensure_repo] {msg}")

    abs_path = os.path.abspath(repo_path)
    os.makedirs(abs_path, exist_ok=True)

    # Already populated?
    items = os.listdir(abs_path)
    if items:
        _log(f"✅ repo already populated at {abs_path} ({len(items)} items)")
        return

    # Determine repo URL
    repo_url = (os.environ.get("REPO_URL") or "").strip()
    if not repo_url:
        # Try to detect from CWD's git remote (sandbox sometimes has this)
        try:
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                cwd=abs_path,
                capture_output=True, text=True, timeout=10,
            )
            if result.returncode == 0 and result.stdout.strip():
                repo_url = result.stdout.strip()
                _log(f"detected repo URL from git remote: {repo_url}")
        except Exception:
            pass

    if not repo_url:
        _log("❌ REPO_URL not set (and no git remote found). "
             "Add REPO_URL to your CrewAI dashboard Environment Variables, "
             "e.g. REPO_URL=https://github.com/ahraz/gtascrub.com")
        return

    # Ensure .git suffix for GitHub URLs
    if "github.com" in repo_url and not repo_url.endswith(".git"):
        repo_url += ".git"

    # Inject token for private repos
    token = (
        os.environ.get("GITHUB_TOKEN")
        or os.environ.get("GH_TOKEN")
        or ""
    )
    authed_url = repo_url
    if token and repo_url.startswith("https://"):
        if f"://{token}@" not in repo_url and f":{token}@" not in repo_url:
            authed_url = repo_url.replace("https://", f"https://{token}@", 1)

    _log(f"cloning {repo_url} → {abs_path} ...")
    try:
        result = subprocess.run(
            ["git", "clone", authed_url, abs_path],
            capture_output=True, text=True, timeout=120,
        )
        if result.returncode == 0:
            items = os.listdir(abs_path)
            _log(f"✅ clone successful ({len(items)} items)")
        else:
            # Retry without token (might be a public repo and token is bad)
            if authed_url != repo_url:
                _log(f"retry without token: {result.stderr.strip()[:200]}")
                result = subprocess.run(
                    ["git", "clone", repo_url, abs_path],
                    capture_output=True, text=True, timeout=120,
                )
                if result.returncode == 0:
                    items = os.listdir(abs_path)
                    _log(f"✅ clone successful without token ({len(items)} items)")
                    return
            _log(f"❌ clone failed: {result.stderr.strip()[:300]}")
    except Exception as e:
        _log(f"❌ clone exception: {e}")


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
