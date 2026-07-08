from crewai import Task, Crew
from agents.seo_director import seo_director
from agents.keyword_research import keyword_research_agent
from agents.competitor_analysis import competitor_analysis_agent
from agents.content_writer import content_writer_agent
from agents.technical_seo import technical_seo_agent
from agents.schema import schema_agent
from agents.image_seo import image_seo_agent
from agents.internal_linking import internal_linking_agent

director = seo_director()
keyword = keyword_research_agent()
competitor = competitor_analysis_agent()
writer = content_writer_agent()
technical = technical_seo_agent()
schema = schema_agent()
image_seo = image_seo_agent()
linker = internal_linking_agent()

tasks = [
    Task(
        description="Create an SEO strategy for GTA Scrub to increase organic leads.",
        expected_output="SEO strategy document",
        agent=director
    ),
    Task(
        description="Find high-value commercial cleaning keywords in Toronto.",
        expected_output="Keyword research report",
        agent=keyword
    ),
    Task(
        description="Analyze competitor content gaps and ranking opportunities.",
        expected_output="Competitor analysis",
        agent=competitor
    ),
    Task(
        description="Recommend structured data (LocalBusiness, Service) implementation.",
        expected_output="Schema recommendations",
        agent=schema
    ),
    Task(
        description="Audit all website images and generate optimized alt text for missing ones.",
        expected_output="A list of images with new, optimized alt text.",
        agent=image_seo
    ),
    Task(
        description="Map out 5 new high-value internal links between existing service pages.",
        expected_output="Internal link map with exact anchor text and target URLs.",
        agent=linker
    )
]

crew = Crew(
    agents=[director, keyword, competitor, writer, technical, schema, image_seo, linker],
    tasks=tasks,
    verbose=True
)

if __name__ == "__main__":
    print("Initiating full swarm intelligence (including Image SEO & Internal Linking)...")
    result = crew.kickoff()
    print("\n==== FINAL SWARM STRATEGY ====\n")
    print(result)
