from crewai import Agent
from tools.llm import get_llm


def github_manager_agent():

    return Agent(
        role="GitHub SEO Developer",
        goal=(
            "Implement SEO improvements directly in website "
            "code repositories while maintaining code quality."
        ),
        backstory=(
            "You are a senior web developer specialized in "
            "SEO engineering. You understand HTML, React, "
            "JavaScript, metadata, schema markup, Git workflows, "
            "and production deployments."
        ),
        llm=get_llm(),
        verbose=True
    )
