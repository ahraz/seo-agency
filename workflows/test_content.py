from crewai import Task, Crew

from agents.content_writer import content_writer_agent


agent = content_writer_agent()


task = Task(
    description="""
    Create an SEO service page for GTA Scrub.

    Page:
    Commercial Cleaning Services Toronto

    Requirements:
    - SEO optimized title
    - meta description
    - H1
    - H2 structure
    - service description
    - benefits
    - industries served
    - FAQ section
    - strong call to action

    Audience:
    Toronto businesses looking for professional cleaning.
    """,
    expected_output="""
    A complete SEO service page draft ready for publishing.
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
