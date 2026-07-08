from crewai import Agent
from tools.llm import get_llm
from tools.file_editor import make_file_tools
from tools.memory import read_memory, write_memory, list_memory_keys
from tools.swarm_logger import log_activity


def seo_developer_agent(repo_path: str = "clients/gta-scrub/repo"):
    read_ft, write_ft, list_ft, delete_ft = make_file_tools(repo_path)
    return Agent(
        role="SEO Developer Engineer",
        goal=(
            "Implement SEO improvements directly into website code "
            "while maintaining functionality and code quality."
        ),
        backstory=(
            "You are a senior frontend developer specialized in technical SEO. "
            "You always read a file before editing it, and change only what is "
            "needed to fix the SEO issue. You use Read/Write Memory to share "
            "fixes and context with other agents."
        ),
        tools=[read_ft, write_ft, list_ft, delete_ft, read_memory, write_memory, list_memory_keys],
        llm=get_llm(),
        verbose=True,
        step_callback=lambda step: log_activity(
            "SEO Developer",
            "Technical Task",
            "Running",
            str(step)
        )
    )
