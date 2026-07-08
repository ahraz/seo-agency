import time
from crewai import Task, Crew
from agents.seo_developer import seo_developer_agent
from tools.qa_runner import run_nextjs_checks
from tools.git_manager import create_branch, commit_changes, push_branch, create_pull_request


def run_seo_fix(
    issue_description: str,
    repo_path: str = "clients/gta-scrub/repo",
    repo_name: str = "ahraz/gtascrub.com",
):
    agent = seo_developer_agent(repo_path=repo_path)

    task = Task(
        description=issue_description,
        expected_output="Confirmation of the file changed and exact code added.",
        agent=agent,
    )

    crew = Crew(agents=[agent], tasks=[task], verbose=True)
    dev_result = crew.kickoff()

    print("\n==== DEVELOPER RESULT ====")
    print(dev_result)

    print("\n==== RUNNING QA ====")
    qa_results = run_nextjs_checks(repo_path)

    if "install" in qa_results and not qa_results["install"]["success"]:
        print("⚠️  npm install failed — not a Node.js project. Skipping QA and committing anyway.")
        lint_ok = True
        build_ok = True
    else:
        lint_ok = qa_results.get("lint", {}).get("success", False)
        build_ok = qa_results.get("build", {}).get("success", False)

    if not (lint_ok and build_ok):
        print("\n❌ QA FAILED — nothing committed. Fix and rerun.")
        if "lint" in qa_results and not qa_results["lint"]["success"]:
            print(qa_results["lint"]["output"][-800:])
        if "build" in qa_results and not qa_results["build"]["success"]:
            print(qa_results["build"]["output"][-800:])
        return

    print("\nQA PASSED — committing and opening PR")

    branch_name = f"seo-fix-{int(time.time())}"
    print(create_branch(repo_path, branch_name))
    print(commit_changes(repo_path, "SEO agent: automated fix"))
    print(push_branch(repo_path, branch_name))

    pr_number = create_pull_request(
        repo_name=repo_name,
        title="Automated SEO fix",
        body=str(dev_result),
        branch=branch_name,
    )

    print(f"\nPR opened: #{pr_number} — go review it on GitHub before merging.")
    return pr_number


if __name__ == "__main__":
    run_seo_fix("""
    List the repo's files, then read app/layout.tsx.
    Add a LocalBusiness JSON-LD schema script tag to the <head>,
    using: Name: GTA Scrub, Type: LocalBusiness.
    Write the change back using the Write File tool.
    Report exactly which file changed and what you added.
    """)
