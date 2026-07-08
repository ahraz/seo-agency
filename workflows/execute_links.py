import time
import subprocess
from crewai import Task, Crew
from agents.seo_developer import seo_developer_agent
from tools.qa_runner import run_nextjs_checks
from tools.git_manager import create_branch, commit_changes, push_branch, create_pull_request

LINK_MAP = """
1. Source: app/commercial-floor-scrubbing/page.tsx
   Target: /pressure-washing-toronto/
   Anchor: "pressure washing services for exterior surfaces"

2. Source: app/graffiti-removal-toronto/page.tsx
   Target: /fleet-washing/
   Anchor: "commercial fleet washing services"

3. Source: app/post-construction-cleaning/page.tsx
   Target: /commercial-floor-scrubbing/
   Anchor: "deep commercial floor scrubbing"
"""


def execute_internal_links(
    repo_path: str = "clients/gta-scrub/repo",
    repo_name: str = "ahraz/gtascrub.com",
):
    print("1. Waking up SEO Developer Agent...")
    dev_agent = seo_developer_agent(repo_path=repo_path)

    link_task = Task(
        description=f"""Here is the internal linking map:
        \n{LINK_MAP}\n
        CRITICAL INSTRUCTIONS:
        1. YOU MUST USE YOUR TOOLS.
        2. FILE PATHS: Use the relative paths (e.g. 'app/commercial-floor-scrubbing/page.tsx').
        3. Use 'Read File' to look at the source files.
        4. Find a logical place in the text/JSX to inject the link.
        5. Use 'Write File' to save the exact code fix.
        6. Do this for AT LEAST ONE of the links in the map.
        """,
        expected_output="Confirmation of the exact file changed and the link code added.",
        agent=dev_agent,
    )

    crew = Crew(agents=[dev_agent], tasks=[link_task], verbose=True)
    print("\n2. Developer Agent is editing your codebase...")
    dev_result = crew.kickoff()

    git_status = subprocess.run(
        "git status --porcelain", cwd=repo_path, shell=True, capture_output=True, text=True
    ).stdout
    if not git_status.strip():
        print("\n❌ The agent failed to edit any files. Aborting.")
        return

    print("\n3. Running QA Validation (npm run lint & build)...")
    qa_results = run_nextjs_checks(repo_path)

    if not (qa_results["lint"]["success"] and qa_results["build"]["success"]):
        print("\n❌ QA FAILED. The agent broke the build. Reverting changes.")
        subprocess.run("git checkout .", cwd=repo_path, shell=True)
        return

    print("\n4. QA PASSED - Committing and opening PR...")
    branch_name = f"auto-links-{int(time.time())}"

    create_branch(repo_path, branch_name)
    commit_changes(repo_path, "SEO Swarm: Automated internal linking implementation")
    push_branch(repo_path, branch_name)

    pr_number = create_pull_request(
        repo_name=repo_name,
        title="Automated Internal Linking SEO Push",
        body=str(dev_result),
        branch=branch_name,
    )

    print(f"\n✅ SUCCESS! PR opened: #{pr_number}")
    return pr_number


if __name__ == "__main__":
    execute_internal_links()
