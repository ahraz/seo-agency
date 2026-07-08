from crewai import Task, Crew

from agents.technical_seo import technical_seo_agent


agent = technical_seo_agent()


task = Task(
    description="""
    Create a technical SEO audit checklist for GTA Scrub website.

    Website type:
    Commercial cleaning company.

    Platform:
    GitHub hosted website.

    Analyze:
    - technical SEO
    - crawling
    - indexing
    - metadata
    - schema
    - images
    - performance
    - mobile SEO
    - security

    Provide actionable fixes.
    """,
    expected_output="""
    A technical SEO audit report with prioritized fixes.
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
