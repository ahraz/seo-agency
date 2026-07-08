"""SEO Agency — Streamlit Web UI."""

import sys
import os
import io
import re
import time
import urllib.parse
from contextlib import redirect_stdout, redirect_stderr

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config.settings import DEEPSEEK_API_KEY, DEEPSEEK_MODEL

st.set_page_config(
    page_title="SEO Agency",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ──────────────────────────────────────────────────────────────

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,600;9..40,700&family=DM+Serif+Display:ital@0;1&display=swap');

    * { font-family: 'DM Sans', sans-serif; }

    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
        max-width: 1200px;
    }

    /* ── Sidebar ───────────────────────────────────────── */
    section[data-testid="stSidebar"] {
        background: #0f1419;
        min-width: 260px !important;
    }
    section[data-testid="stSidebar"] .stApp * { color: #e1e8ed; }
    section[data-testid="stSidebar"] .sidebar-content { padding: 0.5rem 0.75rem; }

    .sidebar-brand {
        font-family: 'DM Serif Display', serif;
        font-size: 1.6rem;
        color: white;
        padding: 0.75rem 1rem 0.25rem;
        letter-spacing: -0.02em;
    }
    .sidebar-brand span { color: #3b82f6; font-family: inherit; }
    .sidebar-tagline {
        font-size: 0.75rem;
        color: #6b7280;
        padding: 0 1rem 1rem;
        border-bottom: 1px solid #1f2937;
        margin-bottom: 0.75rem;
    }
    .sidebar-footer {
        position: fixed;
        bottom: 1rem;
        font-size: 0.7rem;
        color: #4b5563;
        padding: 0 1rem;
    }

    section[data-testid="stSidebar"] .stRadio > label {
        font-size: 0.85rem;
        padding: 0.4rem 0.75rem;
        border-radius: 8px;
        transition: all 0.15s;
    }
    section[data-testid="stSidebar"] .stRadio > label:hover {
        background: rgba(59,130,246,0.1);
        color: #3b82f6;
    }
    section[data-testid="stSidebar"] .stRadio > label[data-selected="true"] {
        background: rgba(59,130,246,0.15);
        color: #3b82f6;
        font-weight: 600;
    }

    /* ── Cards ──────────────────────────────────────────── */
    .card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 1.25rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        transition: box-shadow 0.2s, transform 0.2s;
    }
    .card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        transform: translateY(-1px);
    }
    .card h3 { font-size: 0.85rem; color: #6b7280; margin: 0 0 0.5rem; text-transform: uppercase; letter-spacing: 0.05em; }
    .card .value { font-size: 2rem; font-weight: 700; color: #111827; }

    /* ── Status badges ──────────────────────────────────── */
    .badge {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 9999px;
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }
    .badge-ok { background: #d1fae5; color: #065f46; }
    .badge-warn { background: #fef3c7; color: #92400e; }
    .badge-err { background: #fee2e2; color: #991b1b; }
    .badge-info { background: #dbeafe; color: #1e40af; }

    /* ── Result box ─────────────────────────────────────── */
    .result-box {
        background: #0f1419;
        border-radius: 10px;
        padding: 1rem 1.25rem;
        font-family: 'JetBrains Mono', 'Fira Code', monospace;
        font-size: 0.8rem;
        line-height: 1.5;
        color: #e1e8ed;
        max-height: 500px;
        overflow-y: auto;
        white-space: pre-wrap;
        word-break: break-word;
    }
    .result-box::-webkit-scrollbar { width: 6px; }
    .result-box::-webkit-scrollbar-thumb { background: #374151; border-radius: 3px; }

    /* ── Section headers ────────────────────────────────── */
    .section-title {
        font-family: 'DM Serif Display', serif;
        font-size: 1.8rem;
        color: #111827;
        margin: 0 0 0.25rem;
        letter-spacing: -0.02em;
    }
    .section-sub {
        font-size: 0.9rem;
        color: #6b7280;
        margin-bottom: 1.5rem;
    }

    /* ── Divider ────────────────────────────────────────── */
    hr.sep { margin: 1.5rem 0; border: none; border-top: 1px solid #e5e7eb; }

    /* ── Button overrides ───────────────────────────────── */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        font-size: 0.85rem;
        padding: 0.4rem 1rem;
        transition: all 0.15s;
    }
    .stButton > button[kind="primary"] {
        background: #3b82f6;
        color: white;
        border: none;
    }
    .stButton > button[kind="primary"]:hover {
        background: #2563eb;
        box-shadow: 0 4px 12px rgba(59,130,246,0.3);
    }

    /* ── DataFrames ─────────────────────────────────────── */
    [data-testid="stDataFrame"] {
        border: 1px solid #e5e7eb;
        border-radius: 10px;
        overflow: hidden;
    }

    /* ── Tabs ────────────────────────────────────────────── */
    .stTabs [data-baseweb="tab-list"] { gap: 0; }
    .stTabs [data-baseweb="tab"] {
        font-size: 0.8rem;
        font-weight: 500;
        padding: 0.5rem 1rem;
    }
    .stTabs [aria-selected="true"] { color: #3b82f6 !important; }

    /* ── Footer ─────────────────────────────────────────── */
    .ui-footer {
        text-align: center;
        padding: 2rem 0 1rem;
        font-size: 0.75rem;
        color: #9ca3af;
        border-top: 1px solid #e5e7eb;
        margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)


# ─── Session State ───────────────────────────────────────────────────────────

if "page" not in st.session_state:
    st.session_state.page = "Dashboard"
if "audit_results" not in st.session_state:
    st.session_state.audit_results = None
if "campaign_log" not in st.session_state:
    st.session_state.campaign_log = ""
if "campaign_result" not in st.session_state:
    st.session_state.campaign_result = ""
if "cloned_repo_path" not in st.session_state:
    st.session_state.cloned_repo_path = None
if "cloned_repo_info" not in st.session_state:
    st.session_state.cloned_repo_info = None
if "quick_check_result" not in st.session_state:
    st.session_state.quick_check_result = None


# ─── Sidebar ─────────────────────────────────────────────────────────────────

def render_sidebar():
    st.sidebar.markdown(
        '<div class="sidebar-brand">SEO<span>Agency</span></div>',
        unsafe_allow_html=True,
    )
    st.sidebar.markdown(
        '<div class="sidebar-tagline">Multi-agent SEO automation</div>',
        unsafe_allow_html=True,
    )

    st.sidebar.markdown("### Navigation")
    pages = ["Dashboard", "Campaign", "SEO Audit", "Workflows", "Activity Log", "Settings"]
    selected = st.sidebar.radio("Go to", pages, label_visibility="collapsed", index=pages.index(st.session_state.page))
    st.session_state.page = selected

    # ── GitHub Repo Cloner ──────────────────────────────────────────
    st.sidebar.markdown("---")
    st.sidebar.markdown("### GitHub Repo")
    repo_url = st.sidebar.text_input(
        "Repo URL",
        placeholder="https://github.com/owner/repo",
        label_visibility="collapsed",
        key="sidebar_repo_url",
    )

    col_a, col_b = st.sidebar.columns([1, 1])
    with col_a:
        clone_clicked = st.button("📥 Clone", use_container_width=True, key="clone_btn")
    with col_b:
        clear_clicked = st.button("✕ Clear", use_container_width=True, key="clear_repo_btn")

    if clear_clicked:
        st.session_state.cloned_repo_path = None
        st.session_state.cloned_repo_info = None
        st.session_state.sidebar_repo_url = ""
        st.rerun()

    if clone_clicked and repo_url:
        _clone_github_repo(repo_url)

    # Show cloned repo info
    info = st.session_state.cloned_repo_info
    if info:
        st.sidebar.markdown(
            f'<div style="background:#1f2937;border-radius:8px;padding:0.6rem 0.75rem;font-size:0.75rem">'
            f'<div style="color:#3b82f6;font-weight:600;margin-bottom:0.2rem">📦 {info["name"]}</div>'
            f'<div style="color:#9ca3af">{info["files"]} files · {info.get("framework", "Unknown")}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    elif repo_url and not clone_clicked:
        placeholder = repo_url.rstrip("/").split("/")[-1] or "repo"
        st.sidebar.markdown(
            f'<div style="font-size:0.72rem;color:#6b7280;padding:0.2rem 0">'
            f'Click Clone to fetch <strong>{placeholder}</strong></div>',
            unsafe_allow_html=True,
        )

    st.sidebar.markdown("---")
    st.sidebar.markdown("### System Status")
    has_key = bool(DEEPSEEK_API_KEY)
    st.sidebar.markdown(
        f'<span class="badge {"badge-ok" if has_key else "badge-err"}">'
        f'{"LLM Connected" if has_key else "No API Key"}</span>',
        unsafe_allow_html=True,
    )

    if has_key:
        st.sidebar.markdown(f'<span class="badge badge-info" style="margin-left:0.3rem">{DEEPSEEK_MODEL or "deepseek-chat"}</span>', unsafe_allow_html=True)
    else:
        st.sidebar.markdown(
            '<div style="font-size:0.75rem;color:#9ca3af;margin-top:0.5rem">'
            'Set OPENAI_API_KEY in .env to enable agents</div>',
            unsafe_allow_html=True,
        )

    st.sidebar.markdown(
        '<div class="sidebar-footer">v1.0 &middot; CrewAI &middot; Streamlit</div>',
        unsafe_allow_html=True,
    )


def _clone_github_repo(repo_url: str):
    """Clone a GitHub repo and store metadata in session state."""
    repo_url = repo_url.strip()
    if not repo_url.startswith("http"):
        st.sidebar.error("Enter a full GitHub URL (https://github.com/...)")
        return

    # Extract owner/name from URL
    match = re.search(r"github\.com[:/]([^/]+/[^/]+?)(?:\.git)?$", repo_url)
    if not match:
        st.sidebar.error("Could not parse repo name from URL")
        return
    repo_full = match.group(1).rstrip("/")
    local_name = repo_full.replace("/", "-")
    dest = os.path.join(os.path.dirname(__file__), "..", "clients", local_name, "repo")
    dest = os.path.abspath(dest)

    with st.sidebar.status(f"Cloning {repo_full}...", expanded=False) as status:
        try:
            from tools.repo_analyzer import clone_repo, analyze_repo
            result = clone_repo(repo_url, dest)
            status.write(f"Clone: {result}")
            report = analyze_repo(dest)

            # Detect framework
            framework = "Unknown"
            deps_dict = report.get("framework", {})
            if isinstance(deps_dict, dict):
                all_deps = list(deps_dict.get("dependencies", {}).keys())
                if any("next" in d for d in all_deps):
                    framework = "Next.js"
                elif any("react" in d for d in all_deps):
                    framework = "React"
                elif any("vue" in d for d in all_deps):
                    framework = "Vue"
                elif any("angular" in d for d in all_deps):
                    framework = "Angular"

            info = {
                "name": repo_full,
                "path": dest,
                "files": report.get("total_files", 0),
                "images": report.get("images_count", 0),
                "framework": framework,
                "seo_files": report.get("seo_related_files", []),
            }
            st.session_state.cloned_repo_path = dest
            st.session_state.cloned_repo_info = info
            status.update(label=f"✅ Cloned {repo_full}", state="complete")
            st.rerun()
        except Exception as e:
            status.update(label=f"❌ Clone failed", state="error")
            st.sidebar.error(str(e))


# ─── Live URL Audit Engine ──────────────────────────────────────────────────

def audit_live_url(url: str) -> dict:
    """Fetch a URL and analyze its HTML for common SEO issues."""
    import requests
    issues = []
    suggestions = []
    score = 100
    data = {"url": url, "title": "", "description": "", "h1_count": 0, "h1s": [], "img_count": 0, "img_no_alt": 0, "has_og": False, "has_viewport": False, "has_canonical": False, "has_favicon": False, "word_count": 0, "links": 0, "status": 0}

    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }
        resp = requests.get(url, headers=headers, timeout=20)
        data["status"] = resp.status_code
        html = resp.text
    except Exception as e:
        return {"error": str(e), "issues": [], "score": 0, "suggestions": []}

    # Title
    m = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
    if m:
        data["title"] = m.group(1).strip()
        if len(data["title"]) < 30:
            issues.append("Title tag too short (< 30 chars)")
            score -= 5
        elif len(data["title"]) > 60:
            issues.append("Title tag too long (> 60 chars)")
            score -= 3
        else:
            suggestions.append("✅ Title tag looks good")
    else:
        issues.append("Missing <title> tag")
        score -= 15

    # Meta description
    m = re.search(r'<meta\s+[^>]*name=["\']description["\'][^>]*content=["\'](.*?)["\']', html, re.IGNORECASE)
    if m:
        data["description"] = m.group(1)
        if len(data["description"]) < 50:
            issues.append("Meta description too short (< 50 chars)")
            score -= 5
        elif len(data["description"]) > 160:
            issues.append("Meta description too long (> 160 chars)")
            score -= 3
        else:
            suggestions.append("✅ Meta description looks good")
    else:
        issues.append("Missing meta description")
        score -= 15

    # H1
    h1s = re.findall(r"<h1[^>]*>(.*?)</h1>", html, re.IGNORECASE | re.DOTALL)
    data["h1_count"] = len(h1s)
    data["h1s"] = [re.sub(r"<[^>]+>", "", h).strip() for h in h1s]
    if len(h1s) == 0:
        issues.append("No <h1> tag found")
        score -= 10
    elif len(h1s) > 1:
        issues.append(f"Multiple <h1> tags ({len(h1s)})")
        score -= 5
    else:
        suggestions.append("✅ One <h1> tag present")

    # Images
    imgs = re.findall(r"<img[^>]*>", html, re.IGNORECASE)
    data["img_count"] = len(imgs)
    no_alt = 0
    for img in imgs:
        if "alt=" not in img.lower():
            no_alt += 1
    data["img_no_alt"] = no_alt
    if no_alt > 0:
        issues.append(f"{no_alt} image(s) missing alt text")
        score -= min(no_alt * 2, 10)

    # OG tags
    if re.search(r'<meta\s+[^>]*property=["\']og:', html, re.IGNORECASE):
        data["has_og"] = True
        suggestions.append("✅ OG tags present")
    else:
        issues.append("Missing Open Graph (og:) meta tags")
        score -= 8

    # Viewport
    if re.search(r'<meta\s+[^>]*name=["\']viewport["\']', html, re.IGNORECASE):
        data["has_viewport"] = True
    else:
        issues.append("Missing viewport meta tag (not mobile-responsive)")
        score -= 10

    # Canonical
    if re.search(r'<link[^>]*rel=["\']canonical["\']', html, re.IGNORECASE):
        data["has_canonical"] = True
        suggestions.append("✅ Canonical URL set")
    else:
        issues.append("Missing canonical URL tag")
        score -= 5

    # Favicon
    if re.search(r'<link[^>]*rel=["\'](shortcut )?icon["\']', html, re.IGNORECASE):
        data["has_favicon"] = True
    else:
        issues.append("Missing favicon")
        score -= 3

    # Word count
    text = re.sub(r"<[^>]+>", " ", html)
    words = re.findall(r"\b\w{3,}\b", text)
    data["word_count"] = len(words)
    if data["word_count"] < 300:
        issues.append(f"Very low word count ({data['word_count']} words)")
        score -= 5

    # Links
    data["links"] = len(re.findall(r"<a\s+", html, re.IGNORECASE))

    data["score"] = max(score, 0)
    data["issues"] = issues
    data["suggestions"] = suggestions
    return data


# ─── Dashboard ───────────────────────────────────────────────────────────────

def render_dashboard():
    st.markdown('<div class="section-title">Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Overview of your SEO agency activity</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(
            f'<div class="card"><h3>Agents</h3><div class="value">11</div>'
            f'<div style="font-size:0.75rem;color:#6b7280">SEO specialists</div></div>',
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f'<div class="card"><h3>Workflows</h3><div class="value">4</div>'
            f'<div style="font-size:0.75rem;color:#6b7280">automation pipelines</div></div>',
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f'<div class="card"><h3>Clients</h3><div class="value">1</div>'
            f'<div style="font-size:0.75rem;color:#6b7280">on file</div></div>',
            unsafe_allow_html=True,
        )
    with col4:
        status = "Active" if DEEPSEEK_API_KEY else "No Key"
        badge = "badge badge-ok" if DEEPSEEK_API_KEY else "badge badge-err"
        st.markdown(
            f'<div class="card"><h3>LLM</h3><div class="value" style="font-size:1.2rem">'
            f'<span class="{badge}">{status}</span></div>'
            f'<div style="font-size:0.75rem;color:#6b7280">{DEEPSEEK_MODEL or "—"}</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown('<hr class="sep">', unsafe_allow_html=True)

    # Cloned repo summary
    info = st.session_state.cloned_repo_info
    if info:
        st.markdown("### 📦 Active Repository")
        repo_path = info["path"]
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(
                f'<div class="card"><h3>Repo</h3><div class="value" style="font-size:1rem">{info["name"]}</div></div>',
                unsafe_allow_html=True,
            )
        with col2:
            st.markdown(
                f'<div class="card"><h3>Files</h3><div class="value">{info["files"]}</div></div>',
                unsafe_allow_html=True,
            )
        with col3:
            st.markdown(
                f'<div class="card"><h3>Framework</h3><div class="value" style="font-size:1.2rem">{info["framework"]}</div></div>',
                unsafe_allow_html=True,
            )
        with col4:
            st.markdown(
                f'<div class="card"><h3>Images</h3><div class="value">{info["images"]}</div></div>',
                unsafe_allow_html=True,
            )
        st.markdown(
            f'<div style="font-size:0.8rem;color:#6b7280">Path: <code>{repo_path}</code></div>',
            unsafe_allow_html=True,
        )

        st.markdown('<hr class="sep">', unsafe_allow_html=True)

    # Quick actions
    st.markdown("### Quick Actions")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("🚀 Run Campaign", use_container_width=True, key="db_campaign"):
            st.session_state.page = "Campaign"
            st.rerun()
    with col2:
        if st.button("🔍 URL Audit", use_container_width=True, key="db_audit"):
            st.session_state.page = "SEO Audit"
            st.rerun()
    with col3:
        if st.button("📋 Activity Log", use_container_width=True, key="db_log"):
            st.session_state.page = "Activity Log"
            st.rerun()
    with col4:
        if st.button("⚙️ Settings", use_container_width=True, key="db_settings"):
            st.session_state.page = "Settings"
            st.rerun()

    st.markdown('<hr class="sep">', unsafe_allow_html=True)

    # Quick URL check widget on dashboard
    st.markdown("### Quick SEO Check")
    check_url = st.text_input("Enter a URL to check", placeholder="https://example.com", label_visibility="collapsed", key="dash_quick_url")
    if check_url:
        if st.button("Check URL", key="db_check"):
            if not check_url.startswith("http"):
                check_url = "https://" + check_url
            with st.spinner(f"Analyzing {check_url}..."):
                data = audit_live_url(check_url)
            st.session_state.quick_check_result = data

    if st.session_state.quick_check_result:
        data = st.session_state.quick_check_result
        if "error" in data:
            st.error(f"Error: {data['error']}")
        else:
            _render_audit_results_compact(data)

    # Recent activity
    st.markdown('<hr class="sep">', unsafe_allow_html=True)
    st.markdown("### Recent Activity")
    try:
        from tools.swarm_logger import DB_PATH
        import sqlite3
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query("SELECT agent_name, task_name, status, timestamp FROM activity_log ORDER BY id DESC LIMIT 15", conn)
        conn.close()
        if not df.empty:
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No activity yet. Run a campaign to generate data.")
    except Exception:
        st.info("No activity yet. Run a campaign to generate data.")


def _render_audit_results_compact(data):
    score = data["score"]
    if score >= 80:
        color = "#065f46"
        bg = "#d1fae5"
        label = "Great"
    elif score >= 50:
        color = "#92400e"
        bg = "#fef3c7"
        label = "Needs Work"
    else:
        color = "#991b1b"
        bg = "#fee2e2"
        label = "Poor"

    st.markdown(
        f'<div style="display:flex;align-items:center;gap:1rem;padding:0.75rem;'
        f'background:{bg};border-radius:10px;margin:0.5rem 0">'
        f'<div style="font-size:2rem;font-weight:700;color:{color}">{score}/100</div>'
        f'<div><strong style="color:{color}">{label}</strong><br>'
        f'<span style="font-size:0.8rem;color:#6b7280">{len(data.get("issues",[]))} issues found</span></div>'
        f'</div>',
        unsafe_allow_html=True,
    )
    if data.get("issues"):
        for iss in data["issues"][:5]:
            st.markdown(f'<span class="badge badge-err">!</span> {iss}', unsafe_allow_html=True)


# ─── Campaign ────────────────────────────────────────────────────────────────

def render_campaign():
    st.markdown('<div class="section-title">🚀 Campaign</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Run a full multi-agent SEO campaign</div>', unsafe_allow_html=True)

    if not DEEPSEEK_API_KEY:
        st.warning("⚠️ No API key configured. Set OPENAI_API_KEY in your .env file to run campaigns.")
        st.markdown("""
        <div style="background:#f9fafb;border-radius:10px;padding:1rem;font-size:0.85rem">
        <strong>To set up:</strong><br>
        1. Copy <code>.env.example</code> → <code>.env</code><br>
        2. Add your <strong>OpenAI</strong> or <strong>DeepSeek</strong> API key<br>
        3. Restart the app
        </div>
        """, unsafe_allow_html=True)
        return

    # Show cloned repo info if available
    cloned_info = st.session_state.cloned_repo_info
    if cloned_info:
        st.success(
            f"📦 Cloned repo **{cloned_info['name']}** ({cloned_info['files']} files, "
            f"{cloned_info['framework']}) — will use this for campaign analysis"
        )

    with st.expander("Client Configuration", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            client_name = st.text_input(
                "Client Name",
                value=cloned_info["name"].split("/")[-1].replace("-", " ").title() if cloned_info else "GTA Scrub",
            )
        with col2:
            client_location = st.text_input("Location", "Greater Toronto Area")

        col1, col2 = st.columns(2)
        with col1:
            industry = st.text_input("Industry", "Commercial Cleaning")
        with col2:
            website = st.text_input(
                "Website",
                value=f"https://{cloned_info['name']}" if cloned_info else "https://gtascrub.com",
            )

    if st.button("▶️ Run Campaign", type="primary", use_container_width=True):
        progress_bar = st.progress(0, text="Initializing agents...")
        status_text = st.empty()

        buf = io.StringIO()
        stages = [
            "🧠 Assembling SEO team...",
            "🔍 Researching keywords...",
            "📝 Analyzing competitors...",
            "⚡ Running technical audit...",
            "📊 Generating strategy...",
            "✅ Campaign complete!",
        ]

        try:
            for i, stage in enumerate(stages):
                progress_bar.progress((i + 1) / len(stages), text=stage)
                status_text.markdown(f"**{stage}**")

            with redirect_stdout(buf), redirect_stderr(buf):
                from workflows.seo_campaign import run_full_campaign
                result = run_full_campaign(
                    client_name=client_name,
                    client_location=client_location,
                )

            progress_bar.progress(1.0, text="✅ Campaign complete!")
            output = buf.getvalue()

            st.session_state.campaign_result = str(result)
            st.session_state.campaign_log = output
            st.success("Campaign finished successfully!")

        except Exception as e:
            progress_bar.progress(1.0, text="❌ Failed")
            st.error(f"Campaign failed: {e}")
            output = buf.getvalue()
            if output:
                st.markdown(f'<div class="result-box">{output}</div>', unsafe_allow_html=True)
            return

    if st.session_state.campaign_result:
        st.markdown('<hr class="sep">', unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["📋 Result", "📄 Logs"])
        with tab1:
            st.markdown(f'<div class="result-box">{st.session_state.campaign_result}</div>', unsafe_allow_html=True)
        with tab2:
            st.markdown(f'<div class="result-box">{st.session_state.campaign_log}</div>', unsafe_allow_html=True)


# ─── SEO Audit ───────────────────────────────────────────────────────────────

def render_seo_audit():
    st.markdown('<div class="section-title">🔍 SEO Audit</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Analyze any website for SEO issues</div>', unsafe_allow_html=True)

    mode = st.radio("Audit mode", ["🌐 Live URL", "📁 Local Folder"], horizontal=True, label_visibility="collapsed")

    if mode == "🌐 Live URL":
        url = st.text_input("Website URL", placeholder="https://example.com", label_visibility="collapsed")
        if url and not url.startswith("http"):
            url = "https://" + url

        if st.button("▶️ Run Audit", type="primary", use_container_width=True):
            if not url:
                st.error("Please enter a URL")
            else:
                with st.spinner(f"Fetching and analyzing {url}..."):
                    data = audit_live_url(url)

                if "error" in data:
                    st.error(f"Could not reach {url}: {data['error']}")
                else:
                    st.session_state.audit_results = data
                    _render_audit_results(data)

    else:
        # Show cloned repo shortcut
        cloned_path = st.session_state.cloned_repo_path
        cloned_info = st.session_state.cloned_repo_info

        if cloned_path and cloned_info:
            st.info(f"📦 Cloned repo: **{cloned_info['name']}** ({cloned_info['files']} files, {cloned_info['framework']})")

        # Use a key based on cloned path so widget remounts when repo changes
        widget_key = f"folder_path_{cloned_path.replace('/', '_')}" if cloned_path else "folder_path_empty"

        path = st.text_input(
            "Folder Path",
            value=cloned_path if cloned_path else "",
            placeholder="/path/to/website",
            label_visibility="collapsed",
            key=widget_key,
        )
        if st.button("▶️ Scan Folder", type="primary", use_container_width=True):
            if not path or not os.path.exists(path):
                st.error(f"Path not found: {path}")
            else:
                with st.spinner("Scanning files..."):
                    from tools.seo_audit import scan_files
                    findings = scan_files(path)

                st.session_state.audit_results = {"local_findings": findings, "mode": "local"}
                _render_local_audit(findings, path)


def _render_audit_results(data):
    score = data["score"]
    if score >= 80:
        color = "#065f46"
        bg = "#d1fae5"
        label = "Well Optimized"
        icon = "✅"
    elif score >= 50:
        color = "#92400e"
        bg = "#fef3c7"
        label = "Needs Improvement"
        icon = "⚠️"
    else:
        color = "#991b1b"
        bg = "#fee2e2"
        label = "Poor"
        icon = "❌"

    col1, col2 = st.columns([1, 2])

    with col1:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            domain={"x": [0, 1], "y": [0, 1]},
            number={"font": {"size": 48, "color": color}, "suffix": "/100"},
            gauge={
                "axis": {"range": [0, 100], "tickwidth": 1},
                "bar": {"color": color, "thickness": 0.3},
                "steps": [
                    {"range": [0, 30], "color": "#fee2e2"},
                    {"range": [30, 70], "color": "#fef3c7"},
                    {"range": [70, 100], "color": "#d1fae5"},
                ],
                "threshold": {
                    "line": {"color": color, "width": 4},
                    "thickness": 0.75,
                    "value": score,
                },
            },
        ))
        fig.update_layout(height=250, margin=dict(l=20, r=20, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown(
            f'<div style="padding:0.5rem 0">'
            f'<div style="font-size:1.5rem;font-weight:700;color:{color}">{icon} {label}</div>'
            f'<div style="font-size:0.85rem;color:#6b7280">{data["url"]}</div>'
            f'<div style="margin-top:0.75rem">'
            f'<span class="badge badge-info">HTTP {data["status"]}</span> '
            f'<span class="badge badge-info">{data["word_count"]} words</span> '
            f'<span class="badge badge-info">{data["links"]} links</span> '
            f'<span class="badge badge-info">{data["img_count"]} images</span>'
            f'</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown('<hr class="sep">', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["⚠️ Issues", "💡 Suggestions", "📊 Details"])

    with tab1:
        if data.get("issues"):
            for iss in data["issues"]:
                st.markdown(f'<span class="badge badge-err">!</span> {iss}', unsafe_allow_html=True)
        else:
            st.success("No issues found!")

    with tab2:
        for sug in data.get("suggestions", []):
            st.markdown(f'{sug}', unsafe_allow_html=True)

    with tab3:
        meta = {
            "Title": data.get("title", "—") or "—",
            "Meta Description": (data.get("description", "—")[:120] + "...") if data.get("description") else "—",
            "H1 Tags": ", ".join(data.get("h1s", [])) or "—",
            "Images": f'{data["img_count"]} total, {data["img_no_alt"]} without alt text',
            "Open Graph": "✅ Present" if data.get("has_og") else "❌ Missing",
            "Viewport": "✅ Set" if data.get("has_viewport") else "❌ Missing",
            "Canonical": "✅ Set" if data.get("has_canonical") else "❌ Missing",
            "Favicon": "✅ Present" if data.get("has_favicon") else "❌ Missing",
        }
        df = pd.DataFrame(list(meta.items()), columns=["Property", "Value"])
        st.dataframe(df, use_container_width=True, hide_index=True)

    csv = pd.DataFrame(data.get("issues", []), columns=["Issue"]).to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download Issues CSV", csv, "seo-audit-issues.csv", "text/csv")


def _render_local_audit(findings, path):
    if findings:
        st.warning(f"Found {len(findings)} issues in {path}")
        df = pd.DataFrame({"Issue": findings})
        st.dataframe(df, use_container_width=True, hide_index=True)
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Download CSV", csv, "seo-audit.csv", "text/csv")
    else:
        st.success("No SEO issues found — your website is well-optimized!")


# ─── Workflows ──────────────────────────────────────────────────────────────

def render_workflows():
    st.markdown('<div class="section-title">⚙️ Workflows</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Run individual automation pipelines</div>', unsafe_allow_html=True)

    if not DEEPSEEK_API_KEY:
        st.warning("⚠️ Workflows require an API key. Configure OPENAI_API_KEY in your .env file.")
        return

    workflows = {
        "Autonomous Pipeline": {
            "desc": "Audit → Plan → Code → QA → PR — fully autonomous",
            "module": "workflows.autonomous_pipeline",
            "func": "run_autonomous_loop",
        },
        "SEO Fix": {
            "desc": "Describe an SEO fix and let agents implement it",
            "module": "workflows.pipeline",
            "func": "run_seo_fix",
        },
        "Internal Links": {
            "desc": "Execute internal linking recommendations",
            "module": "workflows.execute_links",
            "func": "execute_internal_links",
        },
    }

    for name, info in workflows.items():
        with st.container():
            st.markdown(
                f'<div class="card" style="margin-bottom:0.75rem">'
                f'<div style="font-weight:600;font-size:1rem">{name}</div>'
                f'<div style="font-size:0.85rem;color:#6b7280;margin:0.25rem 0 0.75rem">{info["desc"]}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
            if st.button(f"▶️ Run {name}", key=f"wf_{name}", use_container_width=True):
                with st.spinner(f"Running {name}..."):
                    buf = io.StringIO()
                    with redirect_stdout(buf), redirect_stderr(buf):
                        mod = __import__(info["module"], fromlist=[info["func"]])
                        getattr(mod, info["func"])()
                    output = buf.getvalue()
                st.markdown(f'<div class="result-box">{output}</div>', unsafe_allow_html=True)


# ─── Activity Log ────────────────────────────────────────────────────────────

def render_activity_log():
    st.markdown('<div class="section-title">📋 Activity Log</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Historical record of all agent actions</div>', unsafe_allow_html=True)

    try:
        from tools.swarm_logger import DB_PATH
        import sqlite3
        conn = sqlite3.connect(DB_PATH)

        total = pd.read_sql_query("SELECT COUNT(*) as count FROM activity_log", conn)
        count = total["count"].iloc[0] if not total.empty else 0
        st.markdown(
            f'<div class="card" style="display:inline-block;padding:0.75rem 1.5rem">'
            f'<span class="value" style="font-size:1.5rem">{count}</span> total entries</div>',
            unsafe_allow_html=True,
        )

        df = pd.read_sql_query(
            "SELECT id, agent_name, task_name, status, details, timestamp FROM activity_log ORDER BY id DESC LIMIT 500",
            conn,
        )
        conn.close()

        if df.empty:
            st.info("No activity logged yet. Run a workflow to generate data.")
            return

        col1, col2 = st.columns(2)
        with col1:
            agents = ["All"] + sorted(df["agent_name"].unique().tolist())
            agent_filter = st.selectbox("Filter by agent", agents)
        with col2:
            statuses = ["All"] + sorted(df["status"].unique().tolist())
            status_filter = st.selectbox("Filter by status", statuses)

        filtered = df.copy()
        if agent_filter != "All":
            filtered = filtered[filtered["agent_name"] == agent_filter]
        if status_filter != "All":
            filtered = filtered[filtered["status"] == status_filter]

        if not filtered.empty:
            chart_data = filtered["agent_name"].value_counts().reset_index()
            chart_data.columns = ["Agent", "Count"]
            fig = px.bar(chart_data, x="Agent", y="Count", color="Agent",
                         color_discrete_sequence=px.colors.qualifier.Bold,
                         title="Activity by Agent")
            fig.update_layout(showlegend=False, height=300, margin=dict(l=0, r=0, t=30, b=0))
            st.plotly_chart(fig, use_container_width=True)

        st.dataframe(filtered, use_container_width=True, hide_index=True)

        csv = filtered.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Download CSV", csv, "activity-log.csv", "text/csv")

    except Exception as e:
        st.error(f"Could not load activity log: {e}")
        st.info("Run a workflow first to generate activity data.")


# ─── Settings ────────────────────────────────────────────────────────────────

def render_settings():
    st.markdown('<div class="section-title">⚙️ Settings</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Configuration and system info</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Environment")
        env_vars = {
            "OPENAI_API_KEY": f"{DEEPSEEK_API_KEY[:8]}...{DEEPSEEK_API_KEY[-4:]}" if DEEPSEEK_API_KEY and len(DEEPSEEK_API_KEY) > 12 else "Not set",
            "OPENAI_MODEL": DEEPSEEK_MODEL or "Not set",
            "GITHUB_TOKEN": "Set" if os.getenv("GITHUB_TOKEN") else "Not set",
        }
        for k, v in env_vars.items():
            st.text_input(k, value=v, disabled=True)

        st.markdown("### LLM Test")
        if st.button("Test LLM Connection", use_container_width=True):
            with st.spinner("Testing..."):
                try:
                    from tools.llm import get_llm
                    llm = get_llm()
                    response = llm.call("Reply only with: ✅ Connection successful")
                    st.success(response)
                except Exception as e:
                    st.error(f"Connection failed: {e}")

    with col2:
        st.markdown("### Client Profile")
        profile_path = os.path.join(os.path.dirname(__file__), "..", "clients", "gta-scrub", "profile", "client.json")
        if os.path.exists(profile_path):
            from tools.client_memory import load_client_profile
            profile = load_client_profile(profile_path)
            st.json(profile)
        else:
            st.info("No client profile found at clients/gta-scrub/profile/client.json")

        st.markdown("### Database")
        try:
            from tools.swarm_logger import DB_PATH
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("🗑️ Clear Activity Log", use_container_width=True):
                    import sqlite3
                    conn = sqlite3.connect(DB_PATH)
                    conn.execute("DELETE FROM activity_log")
                    conn.commit()
                    conn.close()
                    st.success("Activity log cleared!")
            with col_b:
                db_size = os.path.getsize(DB_PATH) if os.path.exists(DB_PATH) else 0
                st.metric("Database Size", f"{db_size / 1024:.1f} KB")
        except Exception:
            st.info("Database not initialized yet.")

    st.markdown('<div class="ui-footer">SEO Agency v1.0 — Built with CrewAI + Streamlit</div>', unsafe_allow_html=True)


# ─── Main ────────────────────────────────────────────────────────────────────


def main():
    render_sidebar()
    page = st.session_state.page

    if page == "Dashboard":
        render_dashboard()
    elif page == "Campaign":
        render_campaign()
    elif page == "SEO Audit":
        render_seo_audit()
    elif page == "Workflows":
        render_workflows()
    elif page == "Activity Log":
        render_activity_log()
    elif page == "Settings":
        render_settings()


if __name__ == "__main__":
    main()

