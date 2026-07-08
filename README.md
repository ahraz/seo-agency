# SEO Agency — Multi-Agent SEO Automation

A CrewAI-powered multi-agent system that automates SEO workflows using a team of specialized AI agents.

## Architecture

The system uses **CrewAI** to coordinate multiple AI agents, each with a specific SEO role:

| Agent | Role |
|---|---|
| **SEO Director** | Creates strategies, coordinates the campaign |
| **Keyword Research Specialist** | Discovers profitable keywords and content opportunities |
| **Content Writer** | Creates high-quality SEO content |
| **Competitor Analyst** | Analyzes competitor strategies and finds gaps |
| **Technical SEO Engineer** | Audits websites for technical issues |
| **Schema Specialist** | Creates JSON-LD structured data |
| **Image SEO Specialist** | Optimizes images and alt text |
| **Internal Linking Strategist** | Maps internal link opportunities |
| **SEO Developer** | Implements code-level SEO fixes |
| **QA Engineer** | Validates changes before deployment |

## Quick Start

```bash
# 1. Create and activate a virtual environment (Ubuntu/Debian)
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up environment variables (copy and fill in)
cp .env.example .env
# Edit .env with your API keys (at minimum, set OPENAI_API_KEY)

# 4. Run a full campaign
python main.py campaign

# 5. Launch the web UI
python main.py ui
```

> **Troubleshooting Ubuntu/Debian**: If you see `externally-managed-environment`, you are not inside a virtual environment. Create one with `python3 -m venv venv && source venv/bin/activate`, then run `pip install -r requirements.txt`. If you already see `(crewai)` in your terminal prompt, you're inside one — just run `pip install -r requirements.txt`.

## Environment Variables

| Variable | Description |
|---|---|
| `OPENAI_API_KEY` | DeepSeek/OpenAI API key (used for all agents) |
| `OPENAI_MODEL` | Model name (default: `deepseek-chat`) |
| `OPENAI_API_BASE` | API base URL (default: `https://api.deepseek.com`) |
| `GITHUB_TOKEN` | GitHub token (optional, for PR workflows) |

## Commands

| Command | Description |
|---|---|
| `python main.py campaign` | Run a full SEO campaign with all agents |
| `python main.py pipeline` | Run autonomous audit -> fix -> PR pipeline |
| `python main.py fix` | Run a single SEO code fix |
| `python main.py test` | Test LLM connectivity |
| `python main.py ui` | Launch the web UI |

## Project Structure

```
seo-agency/
├── agents/          # AI agent definitions (one per specialist)
├── tools/           # Shared tools (LLM, git, SEO audit, etc.)
├── workflows/       # CrewAI workflows and pipelines
├── config/          # YAML configs and settings
├── clients/         # Client profiles
├── ui/              # Streamlit web interface
└── main.py          # Entry point
```
