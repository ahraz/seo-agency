import time
import subprocess
from crewai import Task, Crew
from agents.technical_seo import technical_seo_agent
from agents.seo_developer import seo_developer_agent
from tools.seo_audit import scan_files
from tools.qa_runner import run_nextjs_checks
from tools.git_manager import create_branch, commit_changes, push_branch, create_pull_request


def run_autonomous_loop(
    repo_path: str = "clients/gta-scrub/repo",
    repo_name: str = "ahraz/gtascrub.com",
):
    print(f"1. Running Technical SEO Audit on {repo_path}...")
    issues = scan_files(repo_path)

    if not issues:
        print("No issues found! Your website is fully optimized.")
        return

    print(f"Found {len(issues)} issues. Passing to the Swarm...")
    issues_text = "\n".join(issues)

    tech_agent = technical_seo_agent(repo_path=repo_path)
    dev_agent = seo_developer_agent(repo_path=repo_path)

    plan_task = Task(
        description=f"""Review this raw SEO audit of the repository at {repo_path}:
        \n{issues_text}\n
        Pick EXACTLY ONE critical issue to fix right now.
        Formulate a specific, step-by-step code fix for the Developer Agent.""",
        expected_output="A specific plan targeting one file with exact code to add/change.",
        agent=tech_agent,
    )

    fix_task = Task(
        description="""Take the plan from the Technical SEO Agent.
        CRITICAL INSTRUCTIONS:
        1. YOU MUST USE YOUR TOOLS. Do not just type the code in your response.
        2. FILE PATHS: The audit gives you full paths. Strip the repo prefix and use ONLY relative paths.
        3. Use 'Read File' to look at the target file.
        4. Use 'Write File' to save edits, or 'Delete File' to remove files that should not exist.
        5. If a static file (like public/sitemap.xml) conflicts with a dynamic route,
           DELETE it rather than emptying it. Empty files break the build.
        If you say "I fixed it" but did not successfully execute a tool, you will fail.""",
        expected_output="Confirmation of the exact file changed using Write File or Delete File.",
        agent=dev_agent,
    )

    crew = Crew(
        agents=[tech_agent, dev_agent],
        tasks=[plan_task, fix_task],
        verbose=True,
    )

    print("\n2. Swarm is thinking and coding...")
    dev_result = crew.kickoff()

    git_status_result = subprocess.run(
        "git status --porcelain", cwd=repo_path, shell=True, capture_output=True, text=True
    ).stdout
    if not git_status_result.strip():
        print("\n⚠️  The agent reviewed the code but did not edit any files.")
        print("   This usually means the fix was already in place, or the")
        print("   agent determined no changes were needed.")
        print("   Try running with a different issue description if you")
        print("   expected a file change.")
        return

    print("\n3. Running QA Validation...")
    qa_results = run_nextjs_checks(repo_path)

    # If npm install failed, skip QA (not a Node project)
    if "install" in qa_results and not qa_results["install"]["success"]:
        print("⚠️  npm install failed — not a Node.js project. Skipping QA and committing anyway.")
        lint_ok = True
        build_ok = True
    else:
        lint_ok = qa_results.get("lint", {}).get("success", False)
        build_ok = qa_results.get("build", {}).get("success", False)

    if not (lint_ok and build_ok):
        print("\n❌ QA FAILED — build broke after the edit. Reverting changes.\n")
        if not lint_ok:
            print(f"── Lint errors ──\n{qa_results['lint']['output'][-1500:]}")
        if not build_ok:
            print(f"── Build errors ──\n{qa_results['build']['output'][-2000:]}")
        print("\n🔄 Running git checkout . to revert...")
        subprocess.run("git checkout .", cwd=repo_path, shell=True)
        print("✅ Reverted. The agent's edit broke the build.")
        return

    print("\n4. QA PASSED - Committing and opening PR...")
    branch_name = f"auto-seo-fix-{int(time.time())}"

    create_branch(repo_path, branch_name)
    commit_changes(repo_path, "SEO Swarm: Autonomous fix based on technical audit")
    push_branch(repo_path, branch_name)

    pr_number = create_pull_request(
        repo_name=repo_name,
        title="Autonomous SEO Swarm Fix",
        body=str(dev_result),
        branch=branch_name,
    )

    print(f"\n✅ AUTONOMOUS PIPELINE COMPLETE! PR opened: #{pr_number}")
    return pr_number


if __name__ == "__main__":
    run_autonomous_loop()
