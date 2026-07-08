from crewai import Task, Crew
from agents.seo_developer import seo_developer_agent

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
print(crew.kickoff())
