"""SEO Agency Crew — deployable to CrewAI Enterprise."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent


@CrewBase
class SeoAgencyCrew:
    """Crew that runs a full SEO audit + fix workflow on a client repo."""

    agents: list[BaseAgent]
    tasks: list[Task]

    # ── Agents ────────────────────────────────────────────────────────────────

    @agent
    def technical_seo(self) -> Agent:
        from agents.technical_seo import technical_seo_agent
        return technical_seo_agent(
            repo_path=self._repo_path,
        )

    @agent
    def seo_developer(self) -> Agent:
        from agents.seo_developer import seo_developer_agent
        return seo_developer_agent(
            repo_path=self._repo_path,
        )

    @agent
    def content_writer(self) -> Agent:
        from agents.content_writer import content_writer_agent
        return content_writer_agent(
            repo_path=self._repo_path,
        )

    @agent
    def qa_engineer(self) -> Agent:
        from agents.qa_engineer import qa_engineer_agent
        return qa_engineer_agent(
            repo_path=self._repo_path,
        )

    # ── Tasks ─────────────────────────────────────────────────────────────────

    @task
    def audit_task(self) -> Task:
        return Task(
            config=self.tasks_config["audit_task"],
        )

    @task
    def fix_task(self) -> Task:
        return Task(
            config=self.tasks_config["fix_task"],
        )

    @task
    def qa_task(self) -> Task:
        return Task(
            config=self.tasks_config["qa_task"],
        )

    # ── Crew ──────────────────────────────────────────────────────────────────

    @crew
    def crew(self) -> Crew:
        """Creates the SEO Agency crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )

    def __init__(self, repo_path: str = "clients/gta-scrub/repo"):
        self._repo_path = repo_path
