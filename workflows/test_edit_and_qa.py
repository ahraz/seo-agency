from crewai import Task, Crew
from agents.seo_developer import seo_developer_agent
from tools.qa_runner import run_nextjs_checks

agent = seo_developer_agent()

task = Task(
    description="""
    List the repo's files, then read app/layout.tsx.
    Add a LocalBusiness JSON-LD schema script tag to the <head>,
    using: Name: GTA Scrub, Type: LocalBusiness.
    Write the change back using the Write File tool.
    Report exactly which file changed and what you added.
    """,
    expected_output="Confirmation of the file changed and the exact schema block added.",
    agent=agent
)

crew = Crew(agents=[agent], tasks=[task], verbose=True)
result = crew.kickoff()

print("\n==== DEVELOPER RESULT ====")
print(result)

print("\n==== RUNNING QA ====")
repo = "clients/gta-scrub/repo"
qa_results = run_nextjs_checks(repo)

for check, res in qa_results.items():
    print(f"\n==== {check} ====")
    print("PASSED" if res["success"] else "FAILED")
    print(res["output"][-1000:])

