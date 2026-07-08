from crewai import Agent
from tools.llm import get_llm
from tools.search_tool import web_search
from tools.file_editor import make_file_tools
from tools.memory import read_memory, write_memory, list_memory_keys


def technical_seo_agent(repo_path: str = "clients/gta-scrub/repo"):
    read_ft, _, list_ft, _ = make_file_tools(repo_path)
    return Agent(
        role="Technical SEO Engineer",
        goal=(
            "Audit websites and identify technical SEO issues "
            "that prevent search engines from properly crawling, "
            "indexing, and ranking pages. Use web search to research "
            "best practices, and read files to inspect the codebase."
        ),
        backstory=(
            "You are a senior technical SEO engineer. "
            "You specialize in website audits, Core Web Vitals, "
            "structured data, crawling, indexing, and performance "
            "optimization. You use Read File to inspect source code "
            "and Web Search to research solutions. You use Read/Write "
            "Memory to share findings and context with other agents."
        ),
        tools=[web_search, read_ft, list_ft, read_memory, write_memory, list_memory_keys],
        llm=get_llm(),
        verbose=True
    )
