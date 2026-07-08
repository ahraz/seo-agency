from crewai import Task, Crew

from agents.competitor_analysis import competitor_analysis_agent


agent = competitor_analysis_agent()


task = Task(
    description="""
    Analyze competitors for GTA Scrub.

    Industry:
    Commercial cleaning services.

    Location:
    Greater Toronto Area, Ontario.

    Analyze:
    - competitor SEO strategy
    - service pages needed
    - content gaps
    - keyword opportunities
    - website improvements

    Competitors to consider:
    - janitorial companies in Toronto
    - commercial cleaning companies in GTA
    """,
    expected_output="""
    A detailed competitor SEO analysis report.
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
