#!/usr/bin/env python3
"""SEO Agency — CrewAI-powered multi-agent SEO automation platform.

Run a full campaign:
    python main.py campaign

Run the autonomous pipeline (audit -> fix -> PR):
    python main.py pipeline

Run a single SEO fix:
    python main.py fix

Run the LLM connection test:
    python main.py test

Launch the web UI:
    python main.py ui
"""

import sys
import os

# Ensure the project root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    command = sys.argv[1]

    if command == "campaign":
        from workflows.seo_campaign import run_full_campaign
        print("Running full SEO campaign...\n")
        result = run_full_campaign()
        print("\n==== CAMPAIGN RESULT ====\n")
        print(result)

    elif command == "pipeline":
        from workflows.autonomous_pipeline import run_autonomous_loop
        print("Running autonomous SEO pipeline...\n")
        run_autonomous_loop()

    elif command == "fix":
        from workflows.pipeline import run_seo_fix
        description = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else (
            "List the repo's files, then read app/layout.tsx. "
            "Add a LocalBusiness JSON-LD schema script tag to the <head>, "
            "using: Name: GTA Scrub, Type: LocalBusiness."
        )
        run_seo_fix(description)

    elif command == "test":
        from tools.llm import get_llm
        llm = get_llm()
        response = llm.call("Reply only with: DeepSeek connection successful")
        print(response)

    elif command == "ui":
        try:
            from ui.app import main as ui_main
        except ImportError as e:
            name = e.name or ""
            if "streamlit" in name or "ui" in str(e):
                print("❌ Missing UI dependencies. Run:  pip install -r requirements.txt")
            else:
                print(f"❌ Import error: {e}")
            return
        ui_main()

    else:
        print(f"Unknown command: {command}")
        print(__doc__)


if __name__ == "__main__":
    main()
