from crewai import Task, Crew

from agents.github_manager import github_manager_agent


agent = github_manager_agent()


task = Task(
    description="""
    Explain how you would optimize a GitHub hosted website
    for SEO.

    Website:
    GTA Scrub commercial cleaning website.

    Include:
    - files to inspect
    - SEO improvements
    - safe Git workflow
    - deployment process
    """,
    expected_output="""
    A GitHub SEO implementation plan.
    """,
    agent=agent
)


crew = Crew(
    agents=[agent],
    tasks=[task],
    verbose=True
)


result = crew.kickoff()

print(result)
