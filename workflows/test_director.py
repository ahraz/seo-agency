from crewai import Task, Crew
from agents.seo_director import seo_director


director = seo_director()


task = Task(
    description="""
    Create an SEO growth plan for GTA Scrub,
    a commercial cleaning company in the Greater Toronto Area.

    Focus on:
    - keyword targets
    - service pages
    - location pages
    - blog strategy
    - technical SEO priorities
    """,
    expected_output="""
    A structured 90-day SEO action plan.
    """,
    agent=director
)


crew = Crew(
    agents=[director],
    tasks=[task],
    verbose=True
)


result = crew.kickoff()

print(result)
