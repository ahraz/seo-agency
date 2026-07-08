import time
import subprocess
from crewai import Task, Crew
from agents.technical_seo import technical_seo_agent
from agents.seo_developer import seo_developer_agent
from tools.seo_audit import scan_files
from tools.qa_runner import run_nextjs_checks
from tools.git_manager import create_branch, commit_changes, push_branch, create_pull_request

REPO_PATH = "clients/gta-scrub/repo"
REPO_NAME = "ahraz/gtascrub.com"

def run_autonomous_loop():
    print("1. Running Technical SEO Audit...")
    issues = scan_files(REPO_PATH)
    
    if not issues:
        print("No issues found! Your website is fully optimized.")
        return

    print(f"Found {len(issues)} issues. Passing to the Swarm...")
    issues_text = "\n".join(issues)

    tech_agent = technical_seo_agent()
    dev_agent = seo_developer_agent()

    # Task 1: Technical SEO Agent plans
    plan_task = Task(
        description=f"""Review this raw SEO audit of the GTA Scrub repository:
        \n{issues_text}\n
        Pick EXACTLY ONE critical issue to fix right now. 
        Formulate a specific, step-by-step code fix for the Developer Agent.""",
        expected_output="A specific plan targeting one file with exact code to add/change.",
        agent=tech_agent
    )

    # Task 2: Developer Agent executes (STRICT TOOL ENFORCEMENT)
    # Task 2: Developer Agent executes (STRICT TOOL & PATH ENFORCEMENT)
    fix_task = Task(
        description="""Take the plan from the Technical SEO Agent. 
        CRITICAL INSTRUCTIONS:
        1. YOU MUST USE YOUR TOOLS. Do not just type the code in your response.
        2. FILE PATHS: The audit gives you full paths (e.g., 'clients/gta-scrub/repo/app/page.tsx'). You MUST strip 'clients/gta-scrub/repo/' from the path before using your tools. Use ONLY the relative path (e.g., 'app/page.tsx').
        3. Use 'Read File' to look at the target file.
        4. Use 'Write File' to save the exact code fix back to the repository.
        If you say "I fixed it" but did not successfully execute the 'Write File' tool, you will fail.""",
        expected_output="Confirmation of the exact file changed using the Write File tool.",
        agent=dev_agent
    )

    crew = Crew(
        agents=[tech_agent, dev_agent],
        tasks=[plan_task, fix_task],
        verbose=True
    )

    print("\n2. Swarm is thinking and coding...")
    dev_result = crew.kickoff()

    # CHECK: Did it actually modify a file?
    git_status = subprocess.run("git status --porcelain", cwd=REPO_PATH, shell=True, capture_output=True, text=True).stdout
    if not git_status.strip():
        print("\n❌ ABORTING: The agent talked about the fix but failed to physically edit any files.")
        return

    print("\n3. Running QA Validation...")
    qa_results = run_nextjs_checks(REPO_PATH)
    
    lint_ok = qa_results["lint"]["success"]
    build_ok = qa_results["build"]["success"]

    if not (lint_ok and build_ok):
        print("QA FAILED. The agent broke the build. Aborting commit.")
        subprocess.run("git checkout .", cwd=REPO_PATH, shell=True)
        return

    print("\n4. QA PASSED - Committing and opening PR...")
    branch_name = f"auto-seo-fix-{int(time.time())}"
    
    create_branch(REPO_PATH, branch_name)
    commit_changes(REPO_PATH, "SEO Swarm: Autonomous fix based on technical audit")
    push_branch(REPO_PATH, branch_name)
    
    pr_number = create_pull_request(
        repo_name=REPO_NAME,
        title="Autonomous SEO Swarm Fix",
        body=str(dev_result),
        branch=branch_name
    )
    
    print(f"\n✅ AUTONOMOUS PIPELINE COMPLETE! PR opened: #{pr_number}")

if __name__ == "__main__":
    run_autonomous_loop()
