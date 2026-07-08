from crewai import Agent
from tools.llm import get_llm
from tools.search_tool import web_search
from tools.file_editor import make_file_tools
from tools.memory import read_memory, write_memory, list_memory_keys


def content_writer_agent(repo_path: str = "clients/gta-scrub/repo"):
    _, write_ft, _, _ = make_file_tools(repo_path)
    return Agent(
        role="SEO Content Strategist and Writer",
        goal=(
            "Create high-quality SEO blog posts that rank on search engines "
            "and convert visitors into customers. Save them as markdown files "
            "in the client's repository."
        ),
        backstory=(
            "You are an expert SEO copywriter specializing in local "
            "business websites. You research topics online, write "
            "helpful authoritative content using search intent and "
            "semantic keywords, then save the post directly to the repo "
            "so it can be published. You use Read/Write Memory to share "
            "topic research and writing decisions with other agents."
        ),
        tools=[web_search, write_ft, read_memory, write_memory, list_memory_keys],
        llm=get_llm(),
        verbose=True
    )
