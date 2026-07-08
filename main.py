#!/usr/bin/env python3
"""SEO Agency — CrewAI-powered multi-agent SEO automation platform.

Commands:
    python main.py campaign [name] [location]
    python main.py fix [description]
    python main.py blog <topic>
    python main.py test
    python main.py ui
"""

import subprocess
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    command = sys.argv[1]

    if command == "campaign":
        from workflows.seo_campaign import run_full_campaign
        name = sys.argv[2] if len(sys.argv) > 2 else "Client"
        location = sys.argv[3] if len(sys.argv) > 3 else ""
        print(f"Running SEO campaign for {name}...\n")
        result = run_full_campaign(client_name=name, client_location=location)
        print("\n==== RESULT ====\n")
        print(result)

    elif command == "fix":
        from workflows.pipeline import run_seo_fix
        description = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else (
            "List the repo's files, then read app/layout.tsx. "
            "Add a LocalBusiness JSON-LD schema script tag to the <head>, "
            "using: Name: GTA Scrub, Type: LocalBusiness."
        )
        run_seo_fix(description)

    elif command == "blog":
        from workflows.write_blog import write_blog_post
        topic = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "Benefits of professional commercial cleaning"
        print(f"Writing blog post: {topic}\n")
        result = write_blog_post(topic=topic)
        print(result)

    elif command == "test":
        from tools.llm import get_llm
        llm = get_llm()
        response = llm.call("Reply only with: Connection successful")
        print(response)

    elif command == "ui":
        path = os.path.join(os.path.dirname(__file__), "ui", "app.py")
        print("Launching Streamlit UI...")
        subprocess.run([sys.executable, "-m", "streamlit", "run", path])
        return

    else:
        print(f"Unknown command: {command}")
        print(__doc__)


if __name__ == "__main__":
    main()
