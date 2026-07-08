from crewai import Agent
from tools.llm import get_llm

def internal_linking_agent():
    return Agent(
        role="Internal Linking Strategist",
        goal=(
            "Analyze website architecture and content to recommend strategic, "
            "contextual internal links between pages to distribute PageRank "
            "and establish topical authority."
        ),
        backstory=(
            "You are a Master Site Architect. You know that orphaned pages "
            "never rank. You study the relationships between different service "
            "and location pages, and you map out exactly which exact anchor text "
            "should link to which URLs to maximize crawlability."
        ),
        llm=get_llm(),
        verbose=True
    )
