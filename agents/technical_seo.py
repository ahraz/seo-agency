from crewai import Agent
from tools.llm import get_llm
from tools.search_tool import web_search
from tools.browser_tool import browse_web_page


def technical_seo_agent():
    return Agent(
        role="Technical SEO Engineer",
        goal=(
            "Audit websites and identify technical SEO issues "
            "that prevent search engines from properly crawling, "
            "indexing, and ranking pages. Use web search and "
            "browsing to research best practices."
        ),
        backstory=(
            "You are a senior technical SEO engineer. "
            "You specialize in website audits, Core Web Vitals, "
            "structured data, crawling, indexing, and performance "
            "optimization. You research issues online before "
            "recommending fixes."
        ),
        tools=[web_search, browse_web_page],
        llm=get_llm(),
        verbose=True
    )
