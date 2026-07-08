from crewai import Task, Crew

from agents.keyword_research import keyword_research_agent


agent = keyword_research_agent()


task = Task(
    description="""
    Perform keyword research for GTA Scrub.

    Business:
    Commercial cleaning company in Greater Toronto Area.

    Find:
    - primary keywords
    - service keywords
    - location keywords
    - long-tail keywords
    - blog opportunities

    Target:
    Generate qualified cleaning service leads.
    """,
    expected_output="""
    A structured keyword research report.
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
