"""SEO Agency — Streamlit Web UI."""

import sys
import os
import time
import json
import io
from contextlib import redirect_stdout, redirect_stderr

import streamlit as st
import pandas as pd
import plotly.express as px

# Ensure project root is on path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tools.llm import get_llm
from tools.swarm_logger import log_activity, DB_PATH
from tools.client_memory import load_client_profile
from config.settings import DEEPSEEK_API_KEY, DEEPSEEK_MODEL

st.set_page_config(
    page_title="SEO Agency",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    .stSidebar .sidebar-content { padding-top: 1rem; }
    h1, h2, h3 { margin-bottom: 0.5rem; }
    .report-box {
        background: #f0f2f6;
        border-radius: 0.5rem;
        padding: 1rem;
        font-family: monospace;
        white-space: pre-wrap;
        font-size: 0.85rem;
        max-height: 400px;
        overflow-y: auto;
    }
    .metric-card {
        background: white;
        border-radius: 0.5rem;
        padding: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)


# ─── Sidebar ────────────────────────────────────────────────────────────────

def render_sidebar():
    st.sidebar.title("📈 SEO Agency")
    st.sidebar.markdown("Multi-agent SEO automation platform")

    st.sidebar.divider()
    st.sidebar.subheader("LLM Configuration")

    api_key = st.sidebar.text_input(
        "API Key",
        value=DEEPSEEK_API_KEY or "",
        type="password",
        help="DeepSeek or OpenAI-compatible API key",
    )
    model = st.sidebar.text_input(
        "Model",
        value=DEEPSEEK_MODEL or "deepseek-chat",
    )

    st.sidebar.divider()
    st.sidebar.subheader("Navigation")

    page = st.sidebar.radio(
        "Go to",
        ["Dashboard", "Campaign", "SEO Audit", "Workflows", "Activity Log", "Settings"],
        label_visibility="collapsed",
    )

    st.sidebar.divider()
    st.sidebar.caption("v1.0 — CrewAI Powered")

    return page, api_key, model


# ─── Pages ──────────────────────────────────────────────────────────────────

def render_dashboard():
    st.title("📊 Dashboard")
    st.markdown("Overview of your SEO agency activity")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Agents Available", "11")
    with col2:
        st.metric("Workflows", "4")
    with col3:
        st.metric("Clients", "1")
    with col4:
        st.metric("LLM Status", "✅ Connected" if DEEPSEEK_API_KEY else "⚠️ No Key")

    st.divider()
    st.subheader("Quick Actions")

    qa, qb, qc = st.columns(3)
    with qa:
        if st.button("🚀 Run Full Campaign", use_container_width=True):
            st.switch_page("app.py")  # no-op, handled via session
            st.session_state["navigate_to"] = "campaign"
            st.rerun()
    with qb:
        if st.button("🔍 Run SEO Audit", use_container_width=True):
            st.session_state["navigate_to"] = "seo-audit"
            st.rerun()
    with qc:
        if st.button("📋 View Activity Log", use_container_width=True):
            st.session_state["navigate_to"] = "activity-log"
            st.rerun()

    st.divider()

    # Show recent activity from DB
    st.subheader("Recent Activity")
    try:
        import sqlite3
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(
            "SELECT agent_name, task_name, status, timestamp FROM activity_log ORDER BY id DESC LIMIT 20",
            conn,
        )
        conn.close()
        if not df.empty:
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No activity logged yet. Run a campaign to see results here.")
    except Exception:
        st.info("No activity logged yet. Run a campaign to see results here.")


def render_campaign():
    st.title("🚀 SEO Campaign")
    st.markdown("Run a full multi-agent SEO campaign")

    with st.expander("Client Configuration", expanded=True):
        client_name = st.text_input("Client Name", "GTA Scrub")
        client_location = st.text_input("Location", "Greater Toronto Area")

    if st.button("▶️ Run Campaign", type="primary", use_container_width=True):
        with st.spinner("Running campaign — this may take a few minutes..."):
            buf = io.StringIO()
            with redirect_stdout(buf), redirect_stderr(buf):
                from workflows.seo_campaign import run_full_campaign
                result = run_full_campaign(
                    client_name=client_name,
                    client_location=client_location,
                )
            output = buf.getvalue()

        st.success("Campaign complete!")
        tab1, tab2 = st.tabs(["Result", "Logs"])
        with tab1:
            st.markdown(f'<div class="report-box">{result}</div>', unsafe_allow_html=True)
        with tab2:
            st.markdown(f'<div class="report-box">{output}</div>', unsafe_allow_html=True)


def render_seo_audit():
    st.title("🔍 SEO Audit")
    st.markdown("Scan a website for common SEO issues")

    repo_path = st.text_input(
        "Repository Path",
        "clients/gta-scrub/repo",
        help="Path to the website repository to scan",
    )

    if st.button("▶️ Run Audit", type="primary", use_container_width=True):
        if not os.path.exists(repo_path):
            st.error(f"Path not found: {repo_path}")
            return

        with st.spinner("Scanning files for SEO issues..."):
            from tools.seo_audit import scan_files
            findings = scan_files(repo_path)

        if findings:
            st.warning(f"Found {len(findings)} issues")
            df = pd.DataFrame({"Issue": findings})
            st.dataframe(df, use_container_width=True)

            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Download CSV", csv, "seo-audit.csv", "text/csv")
        else:
            st.success("No SEO issues found! Your website is well-optimized.")


def render_workflows():
    st.title("⚙️ Workflows")
    st.markdown("Run individual workflows")

    workflows = {
        "Autonomous Pipeline": {
            "desc": "Audit → Plan → Code → QA → PR — fully automated",
            "module": "workflows.autonomous_pipeline",
            "func": "run_autonomous_loop",
        },
        "SEO Fix": {
            "desc": "Describe an SEO fix and let the Developer agent implement it",
            "module": "workflows.pipeline",
            "func": "run_seo_fix",
        },
        "Internal Links": {
            "desc": "Execute internal linking recommendations via the Developer agent",
            "module": "workflows.execute_links",
            "func": "execute_internal_links",
        },
    }

    for name, info in workflows.items():
        with st.expander(f"**{name}** — {info['desc']}"):
            if st.button(f"▶️ Run {name}", key=f"wf_{name}", use_container_width=True):
                with st.spinner(f"Running {name}..."):
                    buf = io.StringIO()
                    with redirect_stdout(buf), redirect_stderr(buf):
                        module = __import__(info["module"], fromlist=[info["func"]])
                        getattr(module, info["func"])()
                    output = buf.getvalue()
                st.markdown(f'<div class="report-box">{output}</div>', unsafe_allow_html=True)


def render_activity_log():
    st.title("📋 Activity Log")
    st.markdown("Historical log of all agent activity")

    try:
        import sqlite3
        conn = sqlite3.connect(DB_PATH)

        total = pd.read_sql_query("SELECT COUNT(*) as count FROM activity_log", conn)
        st.metric("Total Entries", total["count"].iloc[0])

        df = pd.read_sql_query(
            "SELECT id, agent_name, task_name, status, details, timestamp FROM activity_log ORDER BY id DESC LIMIT 500",
            conn,
        )
        conn.close()

        if df.empty:
            st.info("No activity logged yet.")
            return

        # Filters
        col1, col2 = st.columns(2)
        with col1:
            agents = ["All"] + sorted(df["agent_name"].unique().tolist())
            agent_filter = st.selectbox("Filter by Agent", agents)
        with col2:
            statuses = ["All"] + sorted(df["status"].unique().tolist())
            status_filter = st.selectbox("Filter by Status", statuses)

        if agent_filter != "All":
            df = df[df["agent_name"] == agent_filter]
        if status_filter != "All":
            df = df[df["status"] == status_filter]

        # Chart
        if not df.empty:
            chart_data = df["agent_name"].value_counts().reset_index()
            chart_data.columns = ["Agent", "Count"]
            fig = px.bar(chart_data, x="Agent", y="Count", title="Activity by Agent")
            st.plotly_chart(fig, use_container_width=True)

        st.dataframe(df, use_container_width=True)

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Download CSV", csv, "activity-log.csv", "text/csv")

    except Exception as e:
        st.error(f"Could not load activity log: {e}")
        st.info("Run a workflow first to generate activity data.")


def render_settings():
    st.title("⚙️ Settings")
    st.markdown("Configuration and environment")

    st.subheader("Environment Variables")
    env_vars = {
        "OPENAI_API_KEY": f"{DEEPSEEK_API_KEY[:8]}...{DEEPSEEK_API_KEY[-4:]}" if DEEPSEEK_API_KEY and len(DEEPSEEK_API_KEY) > 12 else "Not set",
        "OPENAI_MODEL": DEEPSEEK_MODEL or "Not set",
        "GITHUB_TOKEN": "Set" if os.getenv("GITHUB_TOKEN") else "Not set",
    }
    for k, v in env_vars.items():
        st.text_input(k, value=v, disabled=True)

    st.divider()
    st.subheader("LLM Test")
    if st.button("Test LLM Connection", use_container_width=True):
        with st.spinner("Testing..."):
            try:
                llm = get_llm()
                response = llm.call("Reply only with: Connection successful")
                st.success(f"✅ {response}")
            except Exception as e:
                st.error(f"❌ Connection failed: {e}")

    st.divider()
    st.subheader("Client Profile")
    profile_path = "clients/gta-scrub/profile/client.json"
    if os.path.exists(profile_path):
        profile = load_client_profile(profile_path)
        st.json(profile)
    else:
        st.info("No client profile found.")

    st.divider()
    st.subheader("Database")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear Activity Log", use_container_width=True):
            try:
                import sqlite3
                conn = sqlite3.connect(DB_PATH)
                conn.execute("DELETE FROM activity_log")
                conn.commit()
                conn.close()
                st.success("Activity log cleared!")
            except Exception as e:
                st.error(f"Error: {e}")
    with col2:
        db_size = os.path.getsize(DB_PATH) if os.path.exists(DB_PATH) else 0
        st.metric("Database Size", f"{db_size / 1024:.1f} KB")


# ─── Main ───────────────────────────────────────────────────────────────────

def main():
    page, api_key, model = render_sidebar()

    # Handle navigation from dashboard buttons
    navigate = st.session_state.pop("navigate_to", None)
    if navigate == "campaign":
        page = "Campaign"
    elif navigate == "seo-audit":
        page = "SEO Audit"
    elif navigate == "activity-log":
        page = "Activity Log"

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
