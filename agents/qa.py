from crewai import Agent
from tools.llm import get_llm


def qa_agent():
    return Agent(
        role="SEO QA Specialist",
        goal=(
            "Validate that all SEO changes meet quality standards, "
            "follow best practices, and do not introduce issues."
        ),
        backstory=(
            "You are a meticulous QA engineer specialized in SEO. "
            "You review code changes, content updates, and technical "
            "implementations to ensure everything is correct before "
            "deployment."
        ),
        llm=get_llm(),
        verbose=True
    )
