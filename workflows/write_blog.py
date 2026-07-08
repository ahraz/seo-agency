"""Write an SEO-optimized blog post and save it to the client's repo."""

import os
from crewai import Task, Crew
from agents.content_writer import content_writer_agent
from agents.qa_engineer import qa_engineer_agent


def write_blog_post(
    topic: str,
    keywords: str = "",
    repo_path: str = "clients/gta-scrub/repo",
    blog_dir: str = "blog",
) -> str:
    """Research, write, and save an SEO blog post using the Writer + Reviewer crew.

    Args:
        topic: The blog topic (e.g. "Benefits of commercial cleaning in Toronto").
        keywords: Optional comma-separated target keywords.
        repo_path: Path to the website repo where the post will be saved.
        blog_dir: Directory inside the repo to save the post (default: 'blog/').

    Returns:
        The Crew output (should confirm the file was written).
    """
    writer = content_writer_agent(repo_path=repo_path)
    reviewer = qa_engineer_agent(repo_path=repo_path)

    blog_file = f"{blog_dir}/{topic.lower().replace(' ', '-').replace('/', '-')[:60]}.md"

    research_task = Task(
        description=f"""Research this blog topic online using your Web Search tool:
Topic: {topic}
Target keywords: {keywords if keywords else topic}

Use Web Search to find:
1. What people are searching for related to this topic
2. What competing blogs cover (and what they miss)
3. High-volume keyword variations and related questions

Write a brief research summary with your findings.""",
        expected_output="A research summary with keyword opportunities, competitor gaps, and topic angles.",
        agent=writer,
    )

    write_task = Task(
        description=f"""Using your research, write a complete SEO-optimized blog post.

Save it using your Write File tool to: {blog_file}

The post MUST include:
- SEO title (under 60 chars)
- Meta description (under 160 chars)
- H1 heading
- Well-structured H2 and H3 subheadings with keyword placement
- 800-1500 words of helpful content
- Internal link placeholders like [Link: /services]
- A JSON-LD BlogPosting schema script tag
- Image placeholders with alt text

Use your Write File tool to save the file. Then confirm the path.""",
        expected_output=f"Confirmation that {blog_file} was written with the full blog post content.",
        agent=writer,
    )

    qa_task = Task(
        description=f"""Review the blog post that was saved to {blog_file}.

Read the file using your Read File tool, then check:
1. Is there a title tag / SEO title under 60 chars?
2. Is there a meta description under 160 chars?
3. Are keywords naturally placed in headings and body?
4. Is the post at least 800 words?
5. Is JSON-LD schema included?

Report: pass or fail, and if fail, what needs fixing.""",
        expected_output="QA report: PASS or FAIL with specific feedback.",
        agent=reviewer,
    )

    crew = Crew(
        agents=[writer, reviewer],
        tasks=[research_task, write_task, qa_task],
        verbose=True,
    )

    result = crew.kickoff()
    return f"Blog post created: {blog_file}\n\n{result}"


if __name__ == "__main__":
    import sys
    topic = " ".join(sys.argv[1:]) or "Benefits of professional commercial cleaning"
    print(write_blog_post(topic=topic))
