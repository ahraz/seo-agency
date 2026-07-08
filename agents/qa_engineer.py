from crewai import Agent
from tools.llm import get_llm
from tools.file_editor import make_file_tools
from tools.qa_runner import run_shell_command
from tools.memory import read_memory, write_memory, list_memory_keys


def qa_engineer_agent(repo_path: str = "clients/gta-scrub/repo"):
    read_ft, _, list_ft, _ = make_file_tools(repo_path)
    return Agent(
        role="SEO Code Quality Engineer",
        goal=(
            "Validate SEO code changes before deployment. "
            "Ensure the website builds correctly and "
            "SEO improvements do not break functionality."
        ),
        backstory=(
            "You are a senior QA engineer. "
            "You review code changes, run builds, "
            "detect failures, "
            "and approve production-ready changes. "
            "You use Read/Write Memory to share validation "
            "results and context with other agents."
        ),
        tools=[read_ft, list_ft, run_shell_command, read_memory, write_memory, list_memory_keys],
        llm=get_llm(),
        verbose=True
    )
