"""SEO Agency — One-page Streamlit UI."""

import os
import sys
import time
import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config.settings import DEEPSEEK_API_KEY, DEEPSEEK_MODEL

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="SEO Agency", page_icon="📈", layout="wide")

# ── Session state ────────────────────────────────────────────────────────────
for key, default in [
    ("cloned_repo_path", ""),
    ("cloned_repo_info", None),
    ("api_key", DEEPSEEK_API_KEY or ""),
    ("model", DEEPSEEK_MODEL or ""),
    ("results", ""),
    ("running", False),
]:
    if key not in st.session_state:
        st.session_state[key] = default

ACTIVE_API_KEY = st.session_state.api_key or DEEPSEEK_API_KEY
ACTIVE_MODEL = st.session_state.model or DEEPSEEK_MODEL

if ACTIVE_API_KEY:
    os.environ.setdefault("OPENAI_API_KEY", ACTIVE_API_KEY)
if ACTIVE_MODEL:
    os.environ.setdefault("OPENAI_MODEL", ACTIVE_MODEL)


# ── CSS ──────────────────────────────────────────────────────────────────────
st.markdown(
    """
<style>
    .main > div { padding: 1rem 2rem; }
    .big-btn { font-size: 1.3rem !important; font-weight: 600 !important; padding: 0.75rem 1rem !important; }
    .result-box {
        background: #1a1a2e; color: #e0e0e0; border-radius: 8px;
        padding: 1.2rem; font-family: monospace; font-size: 0.85rem;
        white-space: pre-wrap; margin-top: 1rem; max-height: 500px; overflow-y: auto;
    }
    .badge-ok { background: #059669; color: #fff; padding: 0.15rem 0.6rem; border-radius: 4px; font-size: 0.75rem; }
    .badge-err { background: #dc2626; color: #fff; padding: 0.15rem 0.6rem; border-radius: 4px; font-size: 0.75rem; }
    .sidebar .sidebar-content { background: #0f1419; }
    h1, h2, h3 { margin-top: 0; }
    .stButton button { width: 100%; }
</style>
""",
    unsafe_allow_html=True,
)

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/lan-connection.png", width=48)
    st.markdown("### 📈 SEO Agency")
    st.markdown("---")

    repo_url = st.text_input(
        "GitHub Repo URL",
        placeholder="https://github.com/user/repo",
        key="repo_url_input",
    )
    if st.button("📦 Clone Repo", use_container_width=True):
        if repo_url:
            from tools.repo_analyzer import clone_repo, analyze_repo
            repo_name = repo_url.rstrip("/").split("/")[-1]
            dest = os.path.join("/tmp", "seo-clones", repo_name)
            with st.spinner(f"Cloning {repo_name}..."):
                msg = clone_repo(repo_url, dest)
                if "already exists" in msg:
                    st.info("Repo already cloned.")
                else:
                    st.success("Cloned!")
            info = analyze_repo(dest)
            st.session_state.cloned_repo_path = dest
            st.session_state.cloned_repo_info = info
        else:
            st.warning("Enter a repo URL first.")

    if st.session_state.cloned_repo_info:
        info = st.session_state.cloned_repo_info
        st.markdown("**Repo:** " + repo_url.split("/")[-1])
        st.markdown(f"Files: {info.get('total_files', '?')}  |  Images: {info.get('images_count', '?')}")

    st.markdown("---")
    st.markdown("### ⚙️ Settings")

    new_key = st.text_input(
        "API Key",
        value=st.session_state.api_key,
        type="password",
        placeholder="sk-...",
        key="sidebar_api_key",
    )
    new_model = st.text_input(
        "Model",
        value=st.session_state.model,
        placeholder="deepseek-chat",
        key="sidebar_model",
    )
    if st.button("Apply", use_container_width=True):
        st.session_state.api_key = new_key
        st.session_state.model = new_model
        if new_key:
            os.environ["OPENAI_API_KEY"] = new_key
        if new_model:
            os.environ["OPENAI_MODEL"] = new_model
        st.success("Applied!")
        time.sleep(0.3)
        st.rerun()

    status = "🟢 Active" if ACTIVE_API_KEY else "🔴 No Key"
    st.markdown(f"**Status:** {status}  |  {ACTIVE_MODEL or '—'}")

# ── Main area ────────────────────────────────────────────────────────────────
st.title("📈 SEO Agency")
st.markdown("Clone any GitHub repo → audit SEO → fix issues → write blog posts")

repo_path = st.session_state.cloned_repo_path
has_repo = bool(repo_path and os.path.exists(repo_path))

col1, col2, col3 = st.columns(3)
with col1:
    audit_clicked = st.button("🔍 Audit Site", type="primary", use_container_width=True, disabled=not has_repo)
with col2:
    fix_clicked = st.button("🔧 Fix Issues", type="primary", use_container_width=True, disabled=not has_repo)
with col3:
    blog_clicked = st.button("✍️ Write Blog", type="primary", use_container_width=True, disabled=not has_repo)

if not has_repo:
    st.info("👈 Enter a GitHub repo URL in the sidebar and click **Clone Repo** to get started.")
elif st.session_state.cloned_repo_info:
    info = st.session_state.cloned_repo_info
    st.markdown(
        f"**{repo_url.split('/')[-1]}** — {info.get('total_files', 0)} files, "
        f"{info.get('images_count', 0)} images, "
        f"{len(info.get('seo_related_files', []))} SEO-related files"
    )


# ── Action handlers ──────────────────────────────────────────────────────────
def _run_and_capture(func, label):
    from io import StringIO
    import contextlib
    buf = StringIO()
    st.session_state.running = True
    try:
        with contextlib.redirect_stdout(buf):
            func()
    except Exception as e:
        print(f"❌ Error: {e}")
    st.session_state.results = buf.getvalue()
    st.session_state.running = False


def _run_audit(path):
    from tools.seo_audit import scan_files
    issues = scan_files(path)
    if issues:
        print(f"Found {len(issues)} SEO issues:\n")
        for i, issue in enumerate(issues[:30], 1):
            print(f"  {i}. {issue}")
        if len(issues) > 30:
            print(f"\n  ... and {len(issues) - 30} more.")
    else:
        print("✅ No SEO issues found! Your site is in good shape.")


def _run_fix(path):
    from workflows.autonomous_pipeline import run_autonomous_loop
    run_autonomous_loop(repo_path=path)


def _run_blog(path, topic):
    from workflows.write_blog import write_blog_post
    result = write_blog_post(topic=topic, repo_path=path)
    print(result)


if audit_clicked:
    _run_and_capture(lambda: _run_audit(repo_path), "Auditing...")
    st.rerun()

if fix_clicked:
    _run_and_capture(lambda: _run_fix(repo_path), "Fixing...")
    st.rerun()

# ── Blog topic prompt ────────────────────────────────────────────────────────
if blog_clicked and not st.session_state.get("_blog_topic"):
    st.session_state["_blog_topic"] = ""

if blog_clicked and not st.session_state._blog_topic:
    st.markdown("### ✍️ What do you want to write about?")
    col_topic, col_go = st.columns([3, 1])
    with col_topic:
        topic = st.text_input(
            "Blog topic",
            placeholder="e.g. Benefits of commercial cleaning in Toronto",
            label_visibility="collapsed",
            key="blog_topic_input",
        )
    with col_go:
        if st.button("Go", type="primary", use_container_width=True) and topic:
            st.session_state._blog_topic = topic
            _run_and_capture(lambda: _run_blog(repo_path, topic), "Writing...")
            st.rerun()

# ── Results output ───────────────────────────────────────────────────────────
if st.session_state.results:
    st.markdown("### 📋 Results")
    st.markdown(
        f'<div class="result-box">{st.session_state.results}</div>',
        unsafe_allow_html=True,
    )
    if st.button("Clear Results"):
        st.session_state.results = ""
        st.session_state.pop("_blog_topic", None)
        st.rerun()

# ── Activity log ─────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 📜 Activity Log")
try:
    from tools.swarm_logger import DB_PATH
    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT agent_name, task_name, status, timestamp FROM activity_log ORDER BY id DESC LIMIT 20"
    ).fetchall()
    conn.close()
    if rows:
        for agent, task, status, ts in rows:
            icon = "✅" if status == "Done" else "🔄" if status == "Running" else "❌"
            st.markdown(f"{icon} **{agent}** — {task} _{ts[:19]}_")
    else:
        st.caption("No activity yet.")
except Exception:
    st.caption("Log db not available.")
