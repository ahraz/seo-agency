from crewai import Task, Crew

from agents.schema import schema_agent


agent = schema_agent()


task = Task(
    description="""
    Create structured data recommendations for GTA Scrub.

    Business:
    Commercial cleaning company.

    Location:
    Greater Toronto Area.

    Create:
    - LocalBusiness schema
    - Service schema
    - FAQ schema
    - Organization schema

    Explain where each should be placed.
    """,
    expected_output="""
    Complete schema implementation plan with JSON-LD examples.
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
