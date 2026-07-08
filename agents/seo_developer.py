from crewai import Agent
from tools.llm import get_llm
from tools.file_editor import read_file_tool, write_file_tool, list_files_tool
from tools.swarm_logger import log_activity


def seo_developer_agent():
    return Agent(
        role="SEO Developer Engineer",
        goal=(
            "Implement SEO improvements directly into website code "
            "while maintaining functionality and code quality."
        ),
        backstory=(
            "You are a senior frontend developer specialized in technical SEO. "
            "You always read a file before editing it, and change only what is "
            "needed to fix the SEO issue."
        ),
        tools=[read_file_tool, write_file_tool, list_files_tool],
        llm=get_llm(),
        verbose=True,
        step_callback=lambda step: log_activity(
            "SEO Developer",
            "Technical Task",
            "Running",
            str(step)
        )
    )
