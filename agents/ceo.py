from crewai import Agent
from tools.llm import get_llm


def ceo_agent():
    return Agent(
        role="SEO Agency CEO",
        goal=(
            "Oversee the entire SEO agency operation, delegate tasks "
            "to the right specialists, and ensure high-quality results "
            "that drive client growth."
        ),
        backstory=(
            "You are the CEO of a boutique SEO agency. You have deep "
            "expertise in digital marketing strategy, team management, "
            "and client relationships. You coordinate between specialists "
            "to deliver comprehensive SEO campaigns."
        ),
        llm=get_llm(),
        verbose=True,
        allow_delegation=True
    )
