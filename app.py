"""ATLAS — Streamlit chat shell. [Track B]

Runs today with NO Bedrock and NO database. It's the UI skeleton + the seam where
the real agent plugs in later.

The ONLY place that needs to change when Bedrock comes online is generate_response().
Everything else (styling, chat history, input box, rendering) is already done.

Theme: the "drafting sheet" system from landing.html — drafting-film ground, Prussian
ink, process blue, redline used only semantically. Archivo display + IBM Plex Sans/Mono.

Run:  streamlit run app.py
"""
import streamlit as st

# --- Page config -------------------------------------------------------------
st.set_page_config(page_title="Atlas — Agentic Memory", layout="wide")

WELCOME = (
    "I'm **Atlas**. I remember what your company believed, when, and why it changed "
    "its mind — not just where things stand today.\n\n"
    "Ask me about a decision and I'll trace how the thinking got there."
)

EXAMPLE_QUESTIONS = [
    "Should we hire another engineer?",
    "Why did we deprioritize mobile offline sync?",
]


# --- The seam: now backed by the real tool-use agent (on mock memory) --------
def generate_response(user_message: str, history: list[dict]) -> str:
    """Run the Atlas agent loop and return its answer.

    The agent (agent.py) runs the search -> fetch -> (record) -> answer loop over
    Track A's real CockroachDB tools.
    """
    try:
        import agent
        return agent.answer(user_message, history)
    except (Exception, SystemExit) as e:  # never let one bad call crash the whole chat
        msg = str(e)
        if "RESOURCE_EXHAUSTED" in msg or "429" in msg:
            return ("**Atlas is rate-limited right now** (free-tier quota). Wait a moment "
                    "and try again, or switch `GEMINI_CHAT_MODEL` in `.env` to a higher-quota model.")
        if "COCKROACH_DATABASE_URL" in msg:
            return ("**Atlas can't reach its memory database.** Add `COCKROACH_DATABASE_URL` to "
                    "your `.env` — ask your teammate for the CockroachDB connection string.")
        return f"**Something went wrong reaching the agent.**\n\n`{type(e).__name__}: {e}`"


# --- Theme (drafting-sheet CSS on top of .streamlit/config.toml) -------------
def inject_theme() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Archivo:wght@600;700;800&family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600&display=swap');

        :root {
            --paper:      #EAEFF2;
            --vellum:     #F7F9FB;
            --ink:        #16324A;
            --process:    #2F6D9B;
            --faded:      #5E7385;
            --redline:    #B0342B;
            --grid:       rgba(22, 50, 74, 0.055);
            --grid-major: rgba(22, 50, 74, 0.09);
            --line:       rgba(22, 50, 74, 0.22);
        }

        /* Drafting film ground with graph-paper grid */
        .stApp {
            background-color: var(--paper);
            background-image:
                linear-gradient(var(--grid-major) 1px, transparent 1px),
                linear-gradient(90deg, var(--grid-major) 1px, transparent 1px),
                linear-gradient(var(--grid) 1px, transparent 1px),
                linear-gradient(90deg, var(--grid) 1px, transparent 1px);
            background-size: 120px 120px, 120px 120px, 24px 24px, 24px 24px;
            color: var(--ink);
            font-family: 'IBM Plex Sans', system-ui, sans-serif;
        }

        /* Hide default Streamlit chrome (reclaim the top for our own navbar) */
        [data-testid="stHeader"] { display: none; }
        #MainMenu, footer, [data-testid="stToolbar"] { visibility: hidden; }
        /* Hide the auto "anchor link" icons Streamlit adds beside headings */
        [data-testid="stHeaderActionElements"] { display: none !important; }

        /* Keep the bottom input band on-theme + aligned to the content column */
        [data-testid="stBottom"], [data-testid="stBottom"] > div { background: transparent; }
        [data-testid="stBottom"] .stChatInput { max-width: 1040px; margin: 0 auto; }

        /* Content column: wider than default so the grid margins don't feel empty,
           and top padding to clear the fixed full-width navbar. */
        .block-container {
            max-width: 1040px; margin: 0 auto;
            padding-top: 5.2rem; padding-bottom: 7rem;
        }

        /* Masthead ----------------------------------------------------------- */
        .atlas-kicker {
            font-family: 'IBM Plex Mono', monospace; font-size: 0.72rem; font-weight: 500;
            letter-spacing: 0.22em; text-transform: uppercase; color: var(--process);
            margin-bottom: 0.5rem;
        }
        .atlas-wordmark {
            font-family: 'Archivo', sans-serif; font-weight: 800;
            font-size: 3rem; line-height: 1; letter-spacing: -0.015em;
            color: var(--ink); margin: 0;
        }
        .atlas-tagline {
            font-family: 'IBM Plex Sans', sans-serif;
            font-size: 1.02rem; color: var(--faded); margin-top: 0.55rem;
        }
        .atlas-specline {
            font-family: 'IBM Plex Mono', monospace; font-size: 0.68rem; font-weight: 500;
            letter-spacing: 0.16em; text-transform: uppercase; color: var(--faded);
            margin-top: 0.9rem;
        }
        .atlas-rule {
            height: 2px; border: none; margin: 1.3rem 0 0.4rem;
            background: var(--ink);
        }

        /* Navbar (matches landing.html masthead) ---------------------------- */
        .atlas-nav {
            display: flex; align-items: center; justify-content: space-between; gap: 16px;
            /* break out of the centered column -> full viewport width, pinned to top */
            position: fixed; top: 0; left: 0; right: 0; z-index: 1000;
            padding: 13px clamp(20px, 5vw, 60px);
            border-bottom: 2px solid var(--ink);
            background: var(--paper);
        }
        .nav-brand {
            display: flex; align-items: center; gap: 11px;
            text-decoration: none !important; transition: transform 0.15s ease;
        }
        .nav-brand:hover { transform: translateY(-1px); }
        .brand-tile {
            width: 36px; height: 36px; flex: none;
            display: flex; align-items: center; justify-content: center;
            background: var(--ink); color: var(--paper);
            font-family: 'Archivo', sans-serif; font-weight: 800; font-size: 1.25rem; line-height: 1;
            border-radius: 5px; box-shadow: 3px 3px 0 rgba(22, 50, 74, 0.18);
            transition: box-shadow 0.15s ease;
        }
        .nav-brand:hover .brand-tile { box-shadow: 2px 2px 0 rgba(176, 52, 43, 0.55); }
        .brand-stack { display: flex; flex-direction: column; line-height: 1; }
        .brand-glyph { display: flex; flex-direction: column; gap: 3px; }
        .brand-glyph i { height: 2.4px; border-radius: 2px; background: currentColor; display: block; }
        .brand-glyph i:nth-child(1) { width: 19px; opacity: 1; }
        .brand-glyph i:nth-child(2) { width: 19px; opacity: 0.6; }
        .brand-glyph i:nth-child(3) { width: 11px; opacity: 0.32; }
        .brand-word {
            font-family: 'Archivo', sans-serif; font-weight: 800; font-size: 1.12rem;
            letter-spacing: 0.16em;
        }
        .brand-word .bw-ink { color: var(--ink) !important; }
        .brand-word .bw-accent { color: var(--process) !important; }
        .brand-tag {
            font-family: 'IBM Plex Mono', monospace; font-size: 0.55rem; font-weight: 500;
            letter-spacing: 0.2em; text-transform: uppercase; color: var(--process); margin-top: 4px;
        }
        .nav-links { display: flex; gap: clamp(12px, 2vw, 28px); }
        .nav-links a {
            font-family: 'IBM Plex Mono', monospace; font-size: 0.7rem; font-weight: 500;
            letter-spacing: 0.14em; text-transform: uppercase; color: var(--ink);
            text-decoration: none; padding-bottom: 3px; border-bottom: 2px solid transparent;
            transition: border-color 0.15s ease, color 0.15s ease;
        }
        .nav-links a:hover { border-bottom-color: var(--redline); }
        .nav-links a.active { border-bottom-color: var(--process); color: var(--process); }
        .nav-meta {
            font-family: 'IBM Plex Mono', monospace; font-size: 0.66rem; font-weight: 500;
            letter-spacing: 0.14em; text-transform: uppercase; color: var(--faded);
        }
        @media (max-width: 640px) { .nav-meta { display: none; } }

        /* Chat bubbles ------------------------------------------------------- */
        [data-testid="stChatMessageAvatarUser"],
        [data-testid="stChatMessageAvatarAssistant"] { display: none; }

        .stChatMessage {
            border-radius: 3px; padding: 0.9rem 1.15rem; margin: 0.55rem 0;
            border: 2px solid var(--ink);
            width: fit-content; max-width: 88%;
        }
        /* Assistant: vellum card with the register-card offset shadow, left */
        .stChatMessage:has([data-testid="stChatMessageAvatarAssistant"]) {
            background: var(--vellum); margin-right: auto;
            box-shadow: 5px 5px 0 rgba(22, 50, 74, 0.08);
        }
        /* User: Prussian ink fill, vellum text, right-aligned */
        .stChatMessage:has([data-testid="stChatMessageAvatarUser"]) {
            background: var(--ink); border-color: var(--ink);
            margin-left: auto; max-width: 78%;
        }
        .stChatMessage:has([data-testid="stChatMessageAvatarUser"]) * { color: var(--vellum); }

        /* Buttons (example questions + reset): drafting rectangles ----------- */
        .stButton > button {
            background: transparent; color: var(--ink);
            border: 2px solid var(--ink); border-radius: 2px;
            padding: 0.7rem 1rem;
            font-family: 'IBM Plex Mono', monospace; font-weight: 600;
            font-size: 0.78rem; letter-spacing: 0.06em; text-transform: uppercase;
            text-align: left; transition: all 0.15s ease;
        }
        .stButton > button:hover {
            border-color: var(--process); color: var(--process);
            background: rgba(47, 109, 155, 0.06);
        }
        .stButton > button:focus-visible {
            outline: 3px solid var(--process); outline-offset: 3px;
        }

        /* Chat input --------------------------------------------------------- */
        [data-testid="stChatInput"] {
            background: var(--vellum); border: 2px solid var(--ink);
            border-radius: 3px; box-shadow: 5px 5px 0 rgba(22, 50, 74, 0.08);
        }
        [data-testid="stChatInput"] textarea {
            color: var(--ink); font-family: 'IBM Plex Sans', sans-serif;
        }
        [data-testid="stChatInput"]:focus-within { border-color: var(--process); }

        /* Sidebar: sheet-meta panel ------------------------------------------ */
        [data-testid="stSidebar"] {
            background: var(--vellum); border-right: 2px solid var(--ink);
        }
        .side-brand {
            font-family: 'Archivo', sans-serif; font-weight: 800; font-size: 1.35rem;
            letter-spacing: 0.18em; color: var(--ink);
            display: flex; align-items: center; gap: 10px;
        }
        .side-brand::before {
            content: ""; width: 10px; height: 10px; background: var(--ink);
            display: inline-block;
        }
        .side-meta {
            font-family: 'IBM Plex Mono', monospace; font-size: 0.68rem; font-weight: 500;
            letter-spacing: 0.14em; text-transform: uppercase; color: var(--faded);
            margin-top: 0.5rem; line-height: 2;
        }
        .side-status {
            font-family: 'IBM Plex Mono', monospace; font-size: 0.66rem; font-weight: 600;
            letter-spacing: 0.1em; text-transform: uppercase; color: var(--redline);
            border: 1.5px solid var(--redline); border-radius: 2px;
            display: inline-block; padding: 2px 9px; margin-top: 0.8rem;
        }
        .side-rule { height: 1.5px; border: none; background: var(--line); margin: 1.2rem 0; }

        /* Page headers for Timeline / About --------------------------------- */
        .page-title { font-family: 'Archivo', sans-serif; font-weight: 800; font-size: 2.1rem;
            letter-spacing: -0.01em; color: var(--ink); margin: 0; }
        .page-sub { font-family: 'IBM Plex Sans', sans-serif; color: var(--faded);
            margin-top: 0.5rem; font-size: 1rem; max-width: 60ch; }

        /* Decision Register (Timeline page) --------------------------------- */
        .reg-topic { margin-bottom: 2.2rem; }
        .reg-topic-head { font-family: 'IBM Plex Mono', monospace; font-size: 0.72rem;
            font-weight: 600; letter-spacing: 0.14em; text-transform: uppercase;
            color: var(--faded); border-bottom: 2px solid var(--ink); padding-bottom: 8px; }
        .reg-topic-head b { color: var(--ink); }
        .reg-body { position: relative; padding: 4px 0 4px 46px; }
        .reg-body::before { content: ""; position: absolute; left: 14px; top: 26px; bottom: 26px;
            width: 2px; background: var(--ink); }
        .rev { position: relative; padding: 18px 0; }
        .rev + .rev { border-top: 1.5px dashed var(--line); }
        .rev::before { content: ""; position: absolute; left: -37px; top: 24px; width: 10px; height: 10px;
            background: var(--paper); border: 2px solid var(--ink); }
        .rev.current::before { background: var(--process); border-color: var(--process); }
        .rev-head { display: flex; flex-wrap: wrap; align-items: center; gap: 8px 14px; margin-bottom: 8px; }
        .rev-id { font-family: 'IBM Plex Mono', monospace; font-weight: 600; font-size: 0.8rem;
            letter-spacing: 0.1em; color: var(--ink); }
        .rev-head time { font-family: 'IBM Plex Mono', monospace; font-size: 0.72rem; color: var(--faded); }
        .recorded { font-family: 'IBM Plex Mono', monospace; font-size: 0.64rem; letter-spacing: 0.1em;
            text-transform: uppercase; color: var(--faded); }
        .stamp { font-family: 'IBM Plex Mono', monospace; font-size: 0.62rem; font-weight: 600;
            letter-spacing: 0.1em; text-transform: uppercase; border: 1.5px solid var(--redline);
            color: var(--redline); padding: 2px 9px; border-radius: 2px; }
        .stamp-current { border-color: var(--process); background: var(--process);
            color: var(--vellum); transform: rotate(-1.5deg); }
        .belief { font-size: 1.02rem; font-weight: 500; margin: 0; }
        .rev.superseded .belief { color: #51677A; text-decoration: line-through;
            text-decoration-color: var(--redline); text-decoration-thickness: 2px; }
        .prov { margin: 10px 0 0; display: grid; gap: 5px; }
        .prov > div { display: grid; grid-template-columns: 82px 1fr; gap: 12px; }
        .prov dt { font-family: 'IBM Plex Mono', monospace; font-size: 0.62rem; font-weight: 600;
            letter-spacing: 0.12em; color: var(--faded); text-transform: uppercase; }
        .prov dd { font-size: 0.9rem; color: var(--ink); margin: 0; }

        /* About page -------------------------------------------------------- */
        .about-card { background: var(--vellum); border: 2px solid var(--ink); border-radius: 3px;
            padding: 20px 24px; box-shadow: 5px 5px 0 rgba(22, 50, 74, 0.08); margin-bottom: 1.1rem; }
        .about-verb { font-family: 'IBM Plex Mono', monospace; font-size: 0.66rem; font-weight: 600;
            letter-spacing: 0.14em; text-transform: uppercase; color: var(--redline); }
        .about-card h3 { font-family: 'Archivo', sans-serif; font-weight: 700; font-size: 1.1rem;
            margin: 4px 0 0; color: var(--ink); }
        .about-card p { margin: 6px 0 0; font-size: 0.96rem; color: var(--ink); }
        </style>
        """,
        unsafe_allow_html=True,
    )


# --- Session state -----------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": WELCOME}]


def send(user_message: str) -> None:
    st.session_state.messages.append({"role": "user", "content": user_message})
    with st.spinner("Atlas is searching its memory…"):
        reply = generate_response(user_message, st.session_state.messages)
    st.session_state.messages.append({"role": "assistant", "content": reply})


# --- Page routing ------------------------------------------------------------
# Which page to show is driven by the ?view= URL query param, so the navbar links
# (?view=chat / ?view=timeline / ?view=about) actually switch pages.
def render_navbar(active: str) -> None:
    def link(view_name: str, label: str) -> str:
        cls = ' class="active"' if view_name == active else ""
        return f'<a href="?view={view_name}" target="_self"{cls}>{label}</a>'

    st.markdown(
        f"""
        <nav class="atlas-nav">
            <a class="nav-brand" href="?view=chat" target="_self"><span class="brand-tile"><span class="brand-glyph"><i></i><i></i><i></i></span></span><span class="brand-stack"><span class="brand-word"><span class="bw-ink">AT</span><span class="bw-accent">LAS</span></span><span class="brand-tag">Time-aware memory</span></span></a>
            <div class="nav-links">{link('chat', 'Chat')}{link('timeline', 'Timeline')}{link('about', 'About')}</div>
            <div class="nav-meta">Sheet 01 &middot; Rev C</div>
        </nav>
        """,
        unsafe_allow_html=True,
    )


def render_chat() -> None:
    st.markdown(
        """
        <div class="atlas-header">
            <div class="atlas-kicker">Time-aware organizational memory</div>
            <h1 class="atlas-wordmark">Atlas</h1>
            <div class="atlas-tagline">What your company believed, when, and why it changed its mind.</div>
            <div class="atlas-specline">Append-only ledger &middot; Vector-indexed recall &middot; Agents write back</div>
            <hr class="atlas-rule">
        </div>
        """,
        unsafe_allow_html=True,
    )
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    if len(st.session_state.messages) == 1:
        cols = st.columns(len(EXAMPLE_QUESTIONS))
        for col, q in zip(cols, EXAMPLE_QUESTIONS):
            if col.button(q, use_container_width=True):
                send(q)
                st.rerun()
    if prompt := st.chat_input("Ask about the company's decision history"):
        send(prompt)
        st.rerun()


def render_timeline() -> None:
    import os
    import sys
    from collections import OrderedDict

    st.markdown(
        """
        <div class="atlas-header">
            <div class="atlas-kicker">Decision register</div>
            <h1 class="page-title">Provenance Timeline</h1>
            <div class="page-sub">Every belief change kept as a revision — superseded entries struck through, never erased.</div>
            <hr class="atlas-rule">
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Load live decisions from CockroachDB (Track A's data layer), incl. agent write-backs.
    db_dir = os.path.join(os.path.dirname(__file__), "db")
    if db_dir not in sys.path:
        sys.path.insert(0, db_dir)
    try:
        import tools as memory
        decisions = memory.list_decisions()
    except (Exception, SystemExit) as e:
        hint = ("Add <code>COCKROACH_DATABASE_URL</code> to your <code>.env</code> — ask your "
                "teammate for the connection string.") if "COCKROACH_DATABASE_URL" in str(e) else str(e)
        st.markdown(f'<div class="about-card"><p><b>Can\'t load the timeline.</b> {hint}</p></div>',
                    unsafe_allow_html=True)
        return

    if not decisions:
        st.markdown('<div class="about-card"><p>No decisions recorded yet.</p></div>',
                    unsafe_allow_html=True)
        return

    topics: "OrderedDict[str, list]" = OrderedDict()
    for d in decisions:  # already ordered by topic, then created_at (oldest first)
        topics.setdefault(d["topic"], []).append(d)

    def prov_row(label: str, value) -> str:
        return f"<div><dt>{label}</dt><dd>{value}</dd></div>" if value else ""

    blocks = []
    for topic, revs in topics.items():
        rows = [f'<div class="reg-topic"><div class="reg-topic-head">Topic: <b>{topic}</b> &middot; {len(revs)} revisions</div><div class="reg-body">']
        for i, d in enumerate(revs):
            current = i == len(revs) - 1
            letter = chr(ord("A") + i)
            if current:
                stamp, state = '<span class="stamp stamp-current">Current</span>', "current"
            else:
                stamp = f'<span class="stamp">Superseded &rarr; Rev {chr(ord("A") + i + 1)}</span>'
                state = "superseded"
            rows.append(
                f'<article class="rev {state}">'
                f'<div class="rev-head"><span class="rev-id">Rev {letter}</span>'
                f'<time>{(d["created_at"] or "")[:10]}</time>{stamp}'
                f'<span class="recorded">— {d["recorded_by"]}</span></div>'
                f'<p class="belief">{d["new_state"]}</p>'
                f'<dl class="prov">{prov_row("Cause", d["cause"])}{prov_row("Trigger", d["trigger_event"])}{prov_row("Tension", d["tension"])}</dl>'
                f'</article>'
            )
        rows.append("</div></div>")
        blocks.append("".join(rows))
    st.markdown("".join(blocks), unsafe_allow_html=True)


def render_about() -> None:
    st.markdown(
        """
        <div class="atlas-header">
            <div class="atlas-kicker">About</div>
            <h1 class="page-title">What Atlas is</h1>
            <div class="page-sub">A shared memory for how your organization thinks and decides.</div>
            <hr class="atlas-rule">
        </div>
        <div class="about-card">
            <p>Every organization makes countless decisions, but the reasons behind them fade — scattered across messages and documents, or lost entirely when people move on. Atlas remembers not just what was decided, but why, and how that thinking changed over time. So the story behind every choice stays with the organization, instead of living in one person's head.</p>
        </div>
        <div class="about-card"><span class="about-verb">Remembers</span><h3>Nothing gets erased</h3><p>When thinking changes, Atlas keeps the earlier version instead of writing over it. The full history stays intact, so you can always trace how a decision came to be what it is today.</p></div>
        <div class="about-card"><span class="about-verb">Understands</span><h3>Ask in plain words</h3><p>You can ask Atlas a question the way you would ask a colleague. It works out what you actually mean and brings back the decisions that matter — no need to recall exact wording or remember where anything was written down.</p></div>
        <div class="about-card"><span class="about-verb">Learns</span><h3>Gets better over time</h3><p>Each time Atlas works something out, it adds that to what it knows. The picture of how your organization thinks grows richer the more you use it.</p></div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar(active: str) -> None:
    with st.sidebar:
        st.markdown('<div class="side-brand">ATLAS</div>', unsafe_allow_html=True)
        st.markdown('<div class="side-meta">Sheet 01 &middot; Rev C<br>2026-08-09</div>', unsafe_allow_html=True)
        st.markdown('<div class="side-status">Live agent — mock memory</div>', unsafe_allow_html=True)
        st.markdown('<hr class="side-rule">', unsafe_allow_html=True)
        if active == "chat" and st.button("Reset conversation", use_container_width=True):
            st.session_state.messages = [{"role": "assistant", "content": WELCOME}]
            st.rerun()


# --- Render the current page -------------------------------------------------
inject_theme()

view = st.query_params.get("view", "chat")
if view not in ("chat", "timeline", "about"):
    view = "chat"

render_navbar(view)
render_sidebar(view)

if view == "timeline":
    render_timeline()
elif view == "about":
    render_about()
else:
    render_chat()
