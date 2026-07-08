from crewai import Task, Crew

from agents.seo_developer import seo_developer_agent


agent = seo_developer_agent()


task = Task(
    description="""
    You are working on the GTA Scrub website repository.

    Task:
    Explain how you would add a LocalBusiness schema
    to the homepage.

    Include:
    - files you would inspect
    - code changes required
    - testing steps
    - git commit message
    """,
    expected_output="""
    Detailed implementation plan.
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
