from crewai import Agent
from tools.llm import get_llm


def schema_agent():

    return Agent(
        role="Structured Data SEO Specialist",
        goal=(
            "Create and optimize JSON-LD structured data "
            "to improve search engine understanding "
            "and rich result eligibility."
        ),
        backstory=(
            "You are a technical SEO specialist focused on "
            "Schema.org implementation. You create accurate "
            "structured data for local businesses, services, "
            "FAQs, and websites."
        ),
        llm=get_llm(),
        verbose=True
    )
