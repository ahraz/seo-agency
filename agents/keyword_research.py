from crewai import Agent
from tools.llm import get_llm


def keyword_research_agent():

    return Agent(
        role="Keyword Research Specialist",
        goal=(
            "Discover profitable SEO keywords, search intent, "
            "keyword clusters, and content opportunities "
            "for local businesses."
        ),
        backstory=(
            "You are an SEO keyword strategist specializing in "
            "local SEO campaigns. You analyze search behavior, "
            "competitors, and customer intent to find keywords "
            "that generate leads."
        ),
        llm=get_llm(),
        verbose=True
    )
