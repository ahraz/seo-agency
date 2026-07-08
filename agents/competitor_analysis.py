from crewai import Agent
from tools.llm import get_llm


def competitor_analysis_agent():

    return Agent(
        role="Competitor SEO Analyst",
        goal=(
            "Analyze competing websites and discover "
            "SEO opportunities, content gaps, and ranking strategies."
        ),
        backstory=(
            "You are an advanced SEO analyst who studies "
            "top-ranking websites. You reverse engineer "
            "competitor strategies including content, "
            "structure, keywords, and technical SEO."
        ),
        llm=get_llm(),
        verbose=True
    )
