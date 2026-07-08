from crewai import Agent
from tools.llm import get_llm


def technical_seo_agent():

    return Agent(
        role="Technical SEO Engineer",
        goal=(
            "Audit websites and identify technical SEO issues "
            "that prevent search engines from properly crawling, "
            "indexing, and ranking pages."
        ),
        backstory=(
            "You are a senior technical SEO engineer. "
            "You specialize in website audits, Core Web Vitals, "
            "structured data, crawling, indexing, and performance "
            "optimization."
        ),
        llm=get_llm(),
        verbose=True
    )
