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

from seo_agency.crew import SeoAgencyCrew
from dotenv import load_dotenv

load_dotenv()


def run():
    """Run the full SEO audit + fix crew.

    This is the entry point that CrewAI Enterprise calls when you
    trigger a run from the web dashboard.

    On CrewAI Enterprise the repo is already cloned and the working directory
    IS the repo root, so REPO_PATH defaults to '.' (current directory).

    Inputs are read from environment variables so you can configure
    them in the CrewAI Enterprise dashboard under Environment Variables:

        REPO_PATH  — path to the repo (default: '.' — the CWD on the platform)
    """
    repo_path = os.getenv("REPO_PATH", ".")
    crew = SeoAgencyCrew(repo_path=repo_path).crew()
    result = crew.kickoff(inputs={"repo_path": repo_path})
    return result
