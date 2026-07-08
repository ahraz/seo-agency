from crewai import Task, Crew
from agents.technical_seo import technical_seo_agent
from agents.content_writer import content_writer_agent
from agents.seo_developer import seo_developer_agent
from agents.qa_engineer import qa_engineer_agent


def run_full_campaign(
    repo_path: str = "clients/gta-scrub/repo",
    client_name: str = "Client",
    client_location: str = "",
):
    tech = technical_seo_agent()
    writer = content_writer_agent(repo_path=repo_path)
    dev = seo_developer_agent(repo_path=repo_path)
    qa = qa_engineer_agent(repo_path=repo_path)

    tasks = [
        Task(
            description=f"Audit the website at {repo_path} for technical SEO issues. List specific file paths and what needs to change.",
            expected_output="SEO audit report with file paths and issues.",
            agent=tech,
        ),
        Task(
            description=f"Research and write an SEO-optimized blog post about {client_name} in {client_location}. Save it to the blog/ directory.",
            expected_output="Confirmation of blog post saved.",
            agent=writer,
        ),
        Task(
            description="Review the blog post and audit report. Check the blog post for quality and confirm the audit issues are clear.",
            expected_output="QA report on blog post quality and audit clarity.",
            agent=qa,
        ),
    ]

    crew = Crew(agents=[tech, writer, qa], tasks=tasks, verbose=True)
    return crew.kickoff()


if __name__ == "__main__":
    print("Initiating full swarm intelligence (including Image SEO & Internal Linking)...")
    result = run_full_campaign()
    print("\n==== FINAL SWARM STRATEGY ====\n")
    print(result)
