"""SEO Agency Crew — deployable to CrewAI Enterprise."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from crewai import Agent, Crew, Process, Task
from agents.technical_seo import technical_seo_agent
from agents.seo_developer import seo_developer_agent
from agents.content_writer import content_writer_agent
from agents.qa_engineer import qa_engineer_agent


class SeoAgencyCrew:
    """Crew that runs a full SEO audit + fix workflow on a client repo."""

    def __init__(self, repo_path: str = "clients/gta-scrub/repo"):
        self.repo_path = repo_path

    # ── Agents ────────────────────────────────────────────────────────────────

    def technical_seo(self) -> Agent:
        return technical_seo_agent(repo_path=self.repo_path)

    def developer(self) -> Agent:
        return seo_developer_agent(repo_path=self.repo_path)

    def content_writer(self) -> Agent:
        return content_writer_agent(repo_path=self.repo_path)

    def qa_engineer(self) -> Agent:
        return qa_engineer_agent(repo_path=self.repo_path)

    # ── Tasks ─────────────────────────────────────────────────────────────────

    def audit_task(self) -> Task:
        return Task(
            description=(
                "Scan the repository at {repo_path} for technical SEO issues. "
                "Check for: missing meta descriptions, missing title tags, "
                "missing alt text on images, missing JSON-LD schema, "
                "missing sitemap.xml or robots.txt. "
                "Report every issue found."
            ),
            expected_output="A numbered list of SEO issues found in the repo.",
            agent=self.technical_seo(),
        )

    def fix_task(self) -> Task:
        return Task(
            description=(
                "Read the audit results and fix all SEO issues found. "
                "Edit files directly in the repository. "
                "Report exactly which files were changed and what was added."
            ),
            expected_output="Summary of all changes made to fix SEO issues.",
            agent=self.developer(),
        )

    def qa_task(self) -> Task:
        return Task(
            description=(
                "Verify the fixes made by the developer. "
                "Check that the site still builds, no files are broken, "
                "and the SEO improvements are correctly implemented."
            ),
            expected_output="QA pass/fail report with details.",
            agent=self.qa_engineer(),
        )

    # ── Crew ──────────────────────────────────────────────────────────────────

    def crew(self) -> Crew:
        return Crew(
            agents=[self.technical_seo(), self.developer(), self.qa_engineer()],
            tasks=[self.audit_task(), self.fix_task(), self.qa_task()],
            process=Process.sequential,
            verbose=True,
        )
