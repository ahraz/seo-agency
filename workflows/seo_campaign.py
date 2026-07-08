from crewai import Task, Crew
from agents.seo_director import seo_director
from agents.keyword_research import keyword_research_agent
from agents.competitor_analysis import competitor_analysis_agent
from agents.content_writer import content_writer_agent
from agents.technical_seo import technical_seo_agent
from agents.schema import schema_agent
from agents.image_seo import image_seo_agent
from agents.internal_linking import internal_linking_agent


def get_default_agents():
    return {
        "director": seo_director(),
        "keyword": keyword_research_agent(),
        "competitor": competitor_analysis_agent(),
        "writer": content_writer_agent(),
        "technical": technical_seo_agent(),
        "schema": schema_agent(),
        "image_seo": image_seo_agent(),
        "linker": internal_linking_agent(),
    }


def run_full_campaign(client_name="GTA Scrub", client_location="Greater Toronto Area"):
    agents = get_default_agents()

    tasks = [
        Task(
            description=f"Create an SEO strategy for {client_name} to increase organic leads.",
            expected_output="SEO strategy document",
            agent=agents["director"]
        ),
        Task(
            description=f"Find high-value commercial cleaning keywords in {client_location}.",
            expected_output="Keyword research report",
            agent=agents["keyword"]
        ),
        Task(
            description="Analyze competitor content gaps and ranking opportunities.",
            expected_output="Competitor analysis",
            agent=agents["competitor"]
        ),
        Task(
            description="Recommend structured data (LocalBusiness, Service) implementation.",
            expected_output="Schema recommendations",
            agent=agents["schema"]
        ),
        Task(
            description="Audit all website images and generate optimized alt text for missing ones.",
            expected_output="A list of images with new, optimized alt text.",
            agent=agents["image_seo"]
        ),
        Task(
            description="Map out 5 new high-value internal links between existing service pages.",
            expected_output="Internal link map with exact anchor text and target URLs.",
            agent=agents["linker"]
        )
    ]

    crew = Crew(
        agents=list(agents.values()),
        tasks=tasks,
        verbose=True
    )

    return crew.kickoff()


if __name__ == "__main__":
    print("Initiating full swarm intelligence (including Image SEO & Internal Linking)...")
    result = run_full_campaign()
    print("\n==== FINAL SWARM STRATEGY ====\n")
    print(result)
