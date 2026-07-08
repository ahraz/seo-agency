# SEO Agency — Architecture & Strategy

## CrewAI Pattern That Works

The project uses CrewAI (`Agent` + `Task` + `Crew`). One agent actually works:
`seo_developer_agent()` — because it has `tools=[read_file_tool, write_file_tool, list_files_tool]`.

**Rule**: An agent without tools can only *talk*. An agent with tools can *act*.
Every production agent must have at least one tool.

---

## Current Problems

1. **11 agents, 9 are hollow** — they have no `tools=[]`, so they just generate text that nobody uses.
2. **No blog writing** — the `content_writer` agent exists but no workflow creates/saves a blog post.
3. **Hardcoded paths** — `file_editor.py` has `REPO_ROOT = "clients/gta-scrub/repo"`. Can't work with other repos.
4. **17 workflow files, 14 are throwaway tests** — they were one-off experiments, not production code.
5. **Campaign workflow produces nothing real** — runs 6 agents in sequence, each writes text, nothing gets committed or deployed.

---

## Target Architecture: 4 Agents, 2 Workflows

### The 4 Agents

| Agent | Tools | Produces |
|---|---|---|
| **Auditor** (keep `technical_seo`) | `web_search`, `scan_files`, `browse_web_page` | SEO issue report with file paths + line numbers |
| **Developer** (keep `seo_developer`) | `read_file`, `write_file`, `list_files`, `git_manager` | Edited code + GitHub PR |
| **Writer** (keep `content_writer`) | `web_search`, `write_file` | Markdown blog post saved to repo |
| **Reviewer** (keep `qa_engineer`) | `run_command`, `read_file` | QA pass/fail + build output |

### The 2 Workflows

```
Workflow 1: "Fix My Website"
─────────────────────────────
  Input: A GitHub repo URL
  1. Auditor clones repo → scans for SEO issues
  2. Developer picks #1 issue → reads file → edits code
  3. Reviewer runs npm build/lint → validates
  4. Developer commits → creates PR on the real repo
  Output: Link to GitHub PR

Workflow 2: "Write a Blog Post"
────────────────────────────────
  Input: Topic + keywords (e.g. "commercial cleaning Toronto")
  1. Writer researches topic via web_search
  2. Writer creates blog post (title, meta, headings, body, schema)
  3. Writer saves as .md file in the client's repo
  4. Reviewer checks quality and keyword usage
  Output: Path to the saved blog post file
```

### How CrewAI Makes This Work

```python
# This is the pattern — it already works in autonomous_pipeline.py:
crew = Crew(
    agents=[tech_agent, dev_agent],    # 2 agents, each with tools
    tasks=[plan_task, fix_task],        # sequential: plan → execute
    verbose=True
)
result = crew.kickoff()                # runs both agents in sequence
```

The key insight: **Each agent gets `tools=` that let it actually modify files on disk.**
The `Task.description` tells it *what* to do. The `Task.expected_output` tells it *how to confirm*.

---

## Implementation Steps

### Step 1: Make file_editor tools dynamic
- `file_editor.py` currently hardcodes `REPO_ROOT = "clients/gta-scrub/repo"`
- Change to accept `repo_path` at call time so any cloned repo works
- The `@tool` decorator from CrewAI supports parameters

### Step 2: Give remaining agents tools
- `content_writer_agent()` needs `tools=[web_search, write_file_tool]`
- `technical_seo_agent()` needs `tools=[web_search, scan_files]`
- `qa_engineer_agent()` needs `tools=[run_command, read_file_tool]`

### Step 3: Build the blog writing workflow
- New file: `workflows/write_blog.py`
- Uses `Crew(agents=[writer, reviewer], tasks=[research_task, write_task, qa_task])`
- Writer researches → writes → saves .md file → Reviewer checks

### Step 4: Strip hardcoded paths from pipeline
- `autonomous_pipeline.py` reads repo path from a parameter, not a constant
- When called from UI, uses `st.session_state.cloned_repo_path`

### Step 5: Simplify UI to 1 page
- Remove sidebar page navigation
- Show just: repo input, 3 action buttons, results area, activity log

---

## File Cleanup

### Keep (core production files):
```
main.py
agents/seo_developer.py       # Has real tools — template for others
agents/content_writer.py       # Upgrade with tools
agents/technical_seo.py        # Upgrade with tools
agents/qa_engineer.py          # Upgrade with tools
tools/file_editor.py           # Make dynamic
tools/search_tool.py           # Already good
tools/seo_audit.py             # Already good
tools/llm.py                   # Already good
tools/git_manager.py           # Already good
tools/swarm_logger.py          # Already good
tools/repo_analyzer.py         # Already good
workflows/autonomous_pipeline.py  # Working — just de-hardcode paths
workflows/pipeline.py             # Working — just de-hardcode paths
ui/app.py                      # Simplify to 1-page layout
config/settings.py             # Already good
```

### Delete (hollow agents — no tools, no unique function):
```
agents/ceo.py                  # No tools, just talks
agents/analytics.py            # No tools, just talks
agents/seo_optimizer.py        # No tools, just talks
agents/qa.py                   # Duplicates qa_engineer
agents/competitor_analysis.py  # No tools, just talks
agents/schema.py               # No tools, just talks
agents/image_seo.py            # No tools, just talks
agents/internal_linking.py     # No tools, just talks
agents/keyword_research.py     # No tools, just talks
agents/github_manager.py       # No tools, just talks — duplicates seo_developer
```

### Delete (throwaway test files):
```
workflows/test_*.py             # 14 files — one-off experiments
workflows/analyze_gta_scrub.py  # Hardcoded to one client
workflows/run_seo_audit.py      # Redundant with autonomous_pipeline
```

### Clean up config:
```
config/agents.yaml              # Remove entries for deleted agents
config/tasks.yaml               # Remove entries for deleted agents
config/settings.yaml            # Empty file — delete
```

---

## Why This Works With CrewAI

CrewAI's strength is **task orchestration with tool-using agents**. The current codebase uses CrewAI for *talk-only agents*, which is like buying a race car and only sitting in it idling.

The fix is simple: **give each agent the tools it needs to actually do its job**, and write tasks that produce real artifacts (edited files, saved blog posts, GitHub PRs).

The pattern is already proven by `seo_developer_agent` + `autonomous_pipeline.py` — it just needs to be extended to blog writing and generalized to any repo.
