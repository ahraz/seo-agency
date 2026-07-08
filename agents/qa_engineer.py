from crewai import Agent
from tools.llm import get_llm
from tools.file_editor import make_file_tools
from tools.qa_runner import run_shell_command


def qa_engineer_agent(repo_path: str = "clients/gta-scrub/repo"):
    read_ft, _, list_ft = make_file_tools(repo_path)
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
            "and approve production-ready changes."
        ),
        tools=[read_ft, list_ft, run_shell_command],
        llm=get_llm(),
        verbose=True
    )
