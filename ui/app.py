"""SEO Agency — One-page Streamlit UI with live streaming agent logs."""

import os
import sys
import time
import tempfile
import threading
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
    ("_clean_results", ""),
    ("_raw_log", ""),
    # Background-action tracking
    ("_action", None),       # "audit" | "fix" | "blog" | None
    ("_log_file", None),     # path to temp log file
    ("_thread", None),       # background thread
    ("_done", False),        # thread completed
    ("_blog_topic", ""),     # pending blog topic
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
    .result-box {
        background: #0d1117; color: #e6edf3; border-radius: 8px;
        padding: 1rem; font-family: 'JetBrains Mono', 'Fira Code', monospace;
        font-size: 0.82rem; line-height: 1.5;
        white-space: pre-wrap; margin-top: 0.5rem;
        height: 450px; overflow-y: auto;
        border: 1px solid #30363d;
    }
    .result-box .ts { color: #8b949e; }
    .result-box .info { color: #58a6ff; }
    .result-box .ok   { color: #3fb950; }
    .result-box .warn { color: #d29922; }
    .result-box .err  { color: #f85149; }
    .result-box .agent { color: #bc8cff; font-weight: 600; }
    .badge-ok { background: #059669; color: #fff; padding: 0.15rem 0.6rem; border-radius: 4px; font-size: 0.75rem; }
    .badge-err { background: #dc2626; color: #fff; padding: 0.15rem 0.6rem; border-radius: 4px; font-size: 0.75rem; }
    .sidebar .sidebar-content { background: #0f1419; }
    h1, h2, h3 { margin-top: 0; }
    .stButton button { width: 100%; }
    .spinner-text { color: #8b949e; font-size: 0.85rem; }
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


# ── Helpers: background execution with live log ──────────────────────────────
def _start_action(action_name: str, func):
    """Run `func` in a background thread, streaming stdout/stderr to a temp log."""
    log_file = tempfile.mktemp(suffix=".log", prefix=f"seo-{action_name}-")
    st.session_state._action = action_name
    st.session_state._log_file = log_file
    st.session_state._done = False

    def _worker():
        with open(log_file, "w", buffering=1) as f:
            import contextlib
            with contextlib.redirect_stdout(f):
                with contextlib.redirect_stderr(f):
                    try:
                        func()
                    except Exception as e:
                        print(f"❌ Unhandled error: {e}")
        st.session_state._done = True

    t = threading.Thread(target=_worker, daemon=True)
    st.session_state._thread = t
    t.start()


def _read_log() -> str:
    """Return the full contents of the current log file (or empty string)."""
    lf = st.session_state._log_file
    if lf and os.path.exists(lf):
        with open(lf, "r") as f:
            return f.read()
    return ""


def _is_running() -> bool:
    """True if a background action is still in progress."""
    if not st.session_state._action:
        return False
    t = st.session_state._thread
    if t is None:
        return False
    return t.is_alive()


def _stop_action():
    """Clear action state (called when done or cancelled)."""
    st.session_state._action = None
    st.session_state._log_file = None
    st.session_state._thread = None
    st.session_state._done = False


# ── Log summarizer ───────────────────────────────────────────────────────────
import re as _re


def _strip_ansi(text: str) -> str:
    """Remove ANSI escape sequences from text."""
    return _re.sub(r"\x1b\[[0-9;]*[a-zA-Z]", "", text)


def _summarize_log(raw: str) -> str:
    """Extract a clean summary from the raw verbose log.

    Strips ANSI codes, removes box-drawing borders, and keeps only
    meaningful action lines: tool calls, agent output, errors, and
    key results.  Returns *both* the clean summary and stores the
    full raw text separately for the copy-logs button.
    """
    # Store raw for clipboard access
    st.session_state._raw_log = raw

    text = _strip_ansi(raw)
    lines = text.split("\n")
    kept = []
    for line in lines:
        stripped = line.strip()

        # Skip empty lines
        if not stripped:
            continue

        # Skip box-drawing borders
        if _re.match(r"^[╭─╮│╰╯┌┐└┘├┤┬┴┼━┃\s]+$", stripped):
            continue

        # Skip purely decorative lines (only special chars)
        if _re.match(r"^[\s│╎┃╏═║╔╗╚╝╟╢╞╡╪╫╤╧╨╩╦╬╠╣≈─━═\s]{10,}$", stripped):
            continue

        # Skip "Crew Execution Started" and "Tracing Status" banners
        if "Crew Execution Started" in stripped or "Tracing Status" in stripped:
            continue
        if "Name:" in stripped and "ID:" in stripped:
            continue
        if _re.match(r"^[a-f0-9-]{20,}$", stripped):
            continue

        # Skip CrewAI verbose meta lines
        if stripped.startswith("╭") or stripped.startswith("╰"):
            continue
        if stripped in ("│", "│\x1b[0m"):
            continue
        if "To enable tracing" in stripped:
            continue

        # Simplify tool execution headers
        if "Tool Execution Started" in stripped:
            m = _re.search(r"Tool:\s*(\S+)", stripped)
            args_match = _re.search(r"Args:\s*(\{.*\})", stripped)
            if m:
                tool_name = m.group(1)
                args_str = ""
                if args_match:
                    # Try to show a short summary of args
                    args_raw = args_match.group(1)
                    # Extract key info
                    path_m = _re.search(r"['\"]path['\"]:\s*['\"]([^'\"]+)['\"]", args_raw)
                    query_m = _re.search(r"['\"]query['\"]:\s*['\"]([^'\"<]{,80})['\"]", args_raw)
                    if path_m:
                        args_str = f" ({path_m.group(1)})"
                    elif query_m:
                        q = query_m.group(1)
                        args_str = f" \"{q}{'...' if len(query_m.group(0)) > 80 else ''}\""
                kept.append(f"🔧 {tool_name}{args_str}")
            else:
                kept.append(f"🔧 Tool call...")
            continue

        if "Tool Execution Completed" in stripped:
            m = _re.search(r"Tool:\s*(\S+)", stripped)
            if m:
                kept.append(f"✅ {m.group(1)} completed")
            continue

        # Simplify agent started
        if "Agent Started" in stripped:
            m = _re.search(r"Agent:\s*(.+?)\s*\x1b", stripped) or _re.search(r"Agent:\s*(.+)", stripped)
            if m:
                kept.append(f"🤖 **{m.group(1).strip()}** is working...")
            else:
                kept.append("🤖 Agent thinking...")
            continue

        # Simplify agent final answer
        if "Agent Final Answer" in stripped:
            kept.append("📝 **Agent finalizing...**")
            continue

        # Simplify task started/completed
        if "Task Started" in stripped:
            kept.append("📋 Task assigned")
            continue
        if "Task Completed" in stripped:
            kept.append("✅ Task complete")
            continue

        # Keep error lines
        if "Error" in stripped or "error" in stripped.lower():
            kept.append(f"❌ {stripped[:200]}")
            continue

        # Keep lines that look like meaningful output (#, numbers, bullets)
        if _re.match(r"^[\d#]", stripped):
            kept.append(stripped[:200])
            continue

        # Keep our own print() output (starts with emoji or has clear meaning)
        if _re.match(r"^[✅❌🔍🔧✍️⚠️🔄📝📋✅❌➕➖]", stripped):
            kept.append(stripped[:200])
            continue

        # Keep lines shorter than 120 that have content (likely agent thoughts)
        if len(stripped) < 120 and len(stripped) > 10 and " " in stripped:
            kept.append(stripped[:200])

    # Deduplicate consecutive identical lines
    final = []
    for line in kept:
        if not final or line != final[-1]:
            final.append(line)

    return "\n".join(final[-80:])  # cap at 80 lines


# ── Action functions ─────────────────────────────────────────────────────────
def _run_audit(path):
    from tools.seo_audit import scan_files
    print("🔍 SEO Audit starting...\n")
    issues = scan_files(path)
    if issues:
        print(f"\n{'='*50}")
        print(f" Found {len(issues)} SEO issues:")
        print(f"{'='*50}\n")
        for i, issue in enumerate(issues[:40], 1):
            print(f"  {i:>2}. {issue}")
        if len(issues) > 40:
            print(f"\n  ... and {len(issues) - 40} more.")
        print(f"\n{'='*50}")
        print(" ✅ Audit complete")
    else:
        print("\n✅ No SEO issues found! Your site is in good shape.")


def _run_fix(path):
    from workflows.autonomous_pipeline import run_autonomous_loop
    run_autonomous_loop(repo_path=path)


def _run_blog(path, topic):
    from workflows.write_blog import write_blog_post
    result = write_blog_post(topic=topic, repo_path=path)
    print(result)


# ── Button handlers ──────────────────────────────────────────────────────────
running = _is_running()

if not running:
    if st.session_state._action:  # just finished — capture results before clearing
        log_content = _read_log()
        if log_content:
            st.session_state.results = log_content
        _stop_action()
        st.rerun()

audit_clicked = False
fix_clicked = False
blog_clicked = False
blog_go_clicked = False

repo_path = st.session_state.cloned_repo_path
has_repo = bool(repo_path and os.path.exists(repo_path))

# Show repo info
if has_repo and st.session_state.cloned_repo_info:
    info = st.session_state.cloned_repo_info
    st.markdown(
        f"**{repo_url.split('/')[-1]}** — {info.get('total_files', 0)} files, "
        f"{info.get('images_count', 0)} images, "
        f"{len(info.get('seo_related_files', []))} SEO-related files"
    )

# ── Main: 3 action buttons (disabled while running) ─────────────────────────
col1, col2, col3 = st.columns(3)
with col1:
    audit_clicked = st.button(
        "🔍 Audit Site", type="primary", use_container_width=True,
        disabled=not has_repo or running,
    )
with col2:
    fix_clicked = st.button(
        "🔧 Fix Issues", type="primary", use_container_width=True,
        disabled=not has_repo or running,
    )
with col3:
    blog_clicked = st.button(
        "✍️ Write Blog", type="primary", use_container_width=True,
        disabled=not has_repo or running,
    )

if not has_repo:
    st.info("👈 Enter a GitHub repo URL in the sidebar and click **Clone Repo** to get started.")

# ── Start actions on click ───────────────────────────────────────────────────
if not running:
    if audit_clicked:
        _start_action("audit", lambda: _run_audit(repo_path))
        st.rerun()

    if fix_clicked:
        _start_action("fix", lambda: _run_fix(repo_path))
        st.rerun()

    if blog_clicked:
        st.session_state._blog_topic = ""
        # Don't start yet — we need the topic
        # The next block handles this

# ── Blog topic prompt (shown after clicking Write Blog, before starting) ─────
if blog_clicked and not running and st.session_state._blog_topic == "":
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
            _start_action("blog", lambda: _run_blog(repo_path, topic))
            st.rerun()


# ── Live streaming log (when an action is running or just finished) ──────────
if st.session_state._action:
    log_content = _read_log()

    # Determine status label
    action_labels = {"audit": "🔍 Auditing", "fix": "🔧 Fixing Issues", "blog": "✍️ Writing Blog"}
    label = action_labels.get(st.session_state._action, "Running")

    if running:
        st.markdown(f"### ⏳ {label}...")
    else:
        st.markdown(f"### ✅ {label} — Complete")
        log_content = _read_log()

    # Summarize the log for clean display
    clean = _summarize_log(log_content) if log_content else ""

    # Show clean summary
    if clean:
        display = clean[-30000:] if len(clean) > 30000 else clean
    else:
        display = log_content[-30000:] if len(log_content) > 30000 else log_content

    st.markdown(f'<div class="result-box">{display}</div>', unsafe_allow_html=True)

    col_copy, col_status = st.columns([1, 3])
    with col_copy:
        # Button to copy the full raw log
        if st.button("📋 Copy Full Logs", use_container_width=True):
            raw = st.session_state.get("_raw_log", log_content)
            js = f"""
            <script>
            navigator.clipboard.writeText({raw!r});
            </script>
            """
            st.markdown(js, unsafe_allow_html=True)
            st.success("Copied!")

    if running:
        with col_status:
            st.caption("🔄 Streaming live — this page auto-refreshes every 2 seconds")
        time.sleep(2)
        st.rerun()
    else:
        # Capture into results for persistence
        st.session_state.results = log_content
        st.session_state._clean_results = clean

        with col_status:
            st.success("✅ Done!")
        col_clr, _ = st.columns([1, 3])
        with col_clr:
            if st.button("Clear", use_container_width=True):
                st.session_state.results = ""
                st.session_state._clean_results = ""
                st.session_state.pop("_blog_topic", None)
                _stop_action()
                st.rerun()

# ── Persisted results (shown when no action is happening) ────────────────────
if not st.session_state._action and st.session_state.results:
    st.markdown("### 📋 Last Run Results")

    clean = st.session_state.get("_clean_results", "")
    if clean:
        display = clean[-30000:] if len(clean) > 30000 else clean
    else:
        display = st.session_state.results[-30000:] if len(st.session_state.results) > 30000 else st.session_state.results

    st.markdown(f'<div class="result-box">{display}</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("📋 Copy Full Logs", use_container_width=True, key="copy_persisted"):
            st.markdown(f"<script>navigator.clipboard.writeText({st.session_state.results!r})</script>", unsafe_allow_html=True)
            st.success("Copied!")
    if st.button("Clear Results"):
        st.session_state.results = ""
        st.session_state._clean_results = ""
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
        "SELECT agent_name, task_name, status, timestamp FROM activity_log ORDER BY id DESC LIMIT 15"
    ).fetchall()
    conn.close()
    if rows:
        for agent, task, status, ts in rows:
            icon = "✅" if status == "Done" else "🔄"
            st.markdown(f"{icon} **{agent}** — {task} _{ts[:19]}_")
    else:
        st.caption("No activity yet.")
except Exception:
    st.caption("Log db not available.")
