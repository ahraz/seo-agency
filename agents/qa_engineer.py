from crewai import Agent
from tools.llm import get_llm


def qa_engineer_agent():

    return Agent(
        role="SEO Code Quality Engineer",
        goal=(
            "Validate SEO code changes before deployment. "
            "Ensure the website builds correctly and "
            "SEO improvements do not break functionality."
        ),
        backstory=(
            "You are a senior Next.js QA engineer. "
            "You review SEO-related code changes, "
            "run tests, detect build failures, "
            "and approve production-ready changes."
        ),
        llm=get_llm(),
        verbose=True
    )
