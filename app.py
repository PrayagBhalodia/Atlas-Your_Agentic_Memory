"""ATLAS — Streamlit chat shell. [Track B]

Runs today with NO Bedrock and NO database. It's the UI skeleton + the seam where
the real agent plugs in later.

The ONLY place that needs to change when Bedrock comes online is generate_response().
Everything else (styling, chat history, input box, rendering) is already done.

Theme: the "drafting sheet" system from landing.html — drafting-film ground, Prussian
ink, process blue, redline used only semantically. Archivo display + IBM Plex Sans/Mono.

Run:  streamlit run app.py
"""
import html as html_lib

import streamlit as st

# --- Page config -------------------------------------------------------------
st.set_page_config(page_title="Atlas — Agentic Memory", layout="wide")


def _esc(value) -> str:
    """HTML-escape any value that gets interpolated into unsafe_allow_html markup.
    DB rows and model output originate from user-supplied documents, so rendering them
    unescaped would let an uploaded file inject markup/script into the page."""
    return html_lib.escape(str(value)) if value is not None else ""

WELCOME = (
    "I'm **Atlas**. I remember what your company believed, when, and why it changed "
    "its mind — not just where things stand today.\n\n"
    "Ask me about a decision and I'll trace how the thinking got there."
)

# --- The seam: now backed by the real tool-use agent (on mock memory) --------
def generate_response(user_message, history, on_event=None) -> str:
    """Run the three-agent loop and return its answer.

    agent.py runs Finance + Product + Strategy over Track A's CockroachDB tools; `on_event`
    streams the thinking trace (which agent, what it searched, which records it used).
    """
    try:
        import agent
        return agent.answer(user_message, history, on_event=on_event)
    except (Exception, SystemExit) as e:  # never let one bad call crash the whole chat
        msg = str(e)
        if "RESOURCE_EXHAUSTED" in msg or "429" in msg:
            return ("**Atlas is rate-limited right now** (free-tier quota). Wait a moment "
                    "and try again, or switch `GEMINI_CHAT_MODEL` in `.env` to a higher-quota model.")
        if "COCKROACH_DATABASE_URL" in msg:
            return ("**Atlas can't reach its memory database.** Add `COCKROACH_DATABASE_URL` to "
                    "your `.env` — ask your teammate for the CockroachDB connection string.")
        return f"**Something went wrong reaching the agent.**\n\n`{type(e).__name__}: {e}`"


# --- Thinking-trace formatting -----------------------------------------------
def _event_md(ev: dict) -> str:
    """Render one agent trace event as a themed HTML line (or '' to skip). No vector scores;
    kept concise and readable — the search phrase, the records actually used, the agent's view."""
    kind, agent = ev.get("type"), ev.get("agent", "")

    if kind == "phase":
        return f'<div class="think-step">{_esc(ev.get("text", ""))}</div>'

    if kind == "agent_start":
        return f'<div class="think-agent">{_esc(agent)} Agent</div>'

    if kind == "tool_call":
        tool, inp = ev["tool"], ev.get("input", {})
        if tool == "search_memory_index":
            return f'<div class="think-step">Searched memory for “{_esc(inp.get("query_text", ""))}”</div>'
        if tool == "record_decision":
            return f'<div class="think-step">Recorded a new decision: <span class="ref">{_esc(inp.get("topic", ""))}</span></div>'
        return ""  # fetch call is covered by its result line

    if kind == "tool_result":
        tool, res = ev["tool"], ev.get("result")
        if isinstance(res, dict) and "error" in res:  # hardened tool wrapper feeds errors back
            return f'<div class="think-step">Tool hiccup (recovering): {_esc(res["error"])}</div>'
        if not isinstance(res, list):
            return ""
        if tool == "search_memory_index" and not res:
            return '<div class="think-step">Found no relevant records</div>'
        if tool == "fetch_decisions" and res:
            topics = list(dict.fromkeys(r["topic"] for r in res))
            names = ", ".join(f'<span class="ref">{_esc(t)}</span>' for t in topics)
            return f'<div class="think-step">Read {len(res)} record(s) on {names}</div>'
        return ""  # non-empty search result and record result add no readable value

    if kind == "agent_view" and agent in ("Finance", "Product"):
        return f'<div class="think-view">{_esc(ev.get("text", ""))}</div>'

    return ""


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
            --sage:       #4E6151;
            --faded:      #4F6274;
            --redline:    #B0342B;
            --grid:       rgba(22, 50, 74, 0.05);
            --grid-major: rgba(22, 50, 74, 0.06);
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

        /* Content column framed as a drafting "sheet": flat paper interior (so the grid shows
           only in the margins = the table), thin side rules, and a soft depth shadow. */
        .block-container {
            max-width: 1040px; margin: 0 auto;
            padding: 5.2rem clamp(1.5rem, 4vw, 3.4rem) 7rem;
            background: var(--paper);
            border-left: 1.5px solid var(--line); border-right: 1.5px solid var(--line);
            box-shadow: 0 0 40px -22px rgba(22, 50, 74, 0.5);
        }

        /* Masthead ----------------------------------------------------------- */
        .atlas-kicker {
            font-family: 'IBM Plex Mono', monospace; font-size: 0.72rem; font-weight: 500;
            letter-spacing: 0.22em; text-transform: uppercase; color: var(--process);
            margin-bottom: 0.5rem;
        }
        .atlas-wordmark {
            font-family: 'Archivo', sans-serif; font-weight: 800;
            font-size: 2.2rem; line-height: 1; letter-spacing: -0.015em;
            color: var(--ink); margin: 0;
        }
        .atlas-tagline {
            font-family: 'IBM Plex Sans', sans-serif;
            font-size: 1.02rem; color: var(--faded); margin-top: 0.55rem;
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
        .nav-links a:focus-visible, .nav-brand:focus-visible {
            outline: 2px solid var(--process); outline-offset: 3px; border-radius: 2px;
        }
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
            letter-spacing: 0.1em; text-transform: uppercase; color: var(--sage);
            border: 1.5px solid var(--sage); border-radius: 2px;
            display: inline-flex; align-items: center; gap: 6px; padding: 3px 9px; margin-top: 0.8rem;
        }
        .side-status::before { content: ""; width: 6px; height: 6px; border-radius: 50%; background: var(--sage); }
        .side-rule { height: 1.5px; border: none; background: var(--line); margin: 1.2rem 0; }

        /* Page headers for Timeline / About --------------------------------- */
        .page-title { font-family: 'Archivo', sans-serif; font-weight: 800; font-size: 2.1rem;
            letter-spacing: -0.01em; color: var(--ink); margin: 0; }
        .page-sub { font-family: 'IBM Plex Sans', sans-serif; color: var(--faded);
            margin-top: 0.5rem; font-size: 1rem; max-width: 60ch; }
        .chat-hint { font-size: 0.9rem; color: var(--faded); margin: 0.6rem 0 0 2px; max-width: 62ch; }
        .reg-current { font-size: 0.9rem; color: var(--ink); margin-bottom: 12px;
            padding-left: 11px; border-left: 2px solid var(--process); }

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
        .about-card ul { margin: 8px 0 0; padding-left: 18px; }
        .about-card li { font-size: 0.92rem; margin: 3px 0; }
        .ingest-src { font-family: 'IBM Plex Mono', monospace; font-size: 0.66rem;
            color: var(--faded); margin-top: 10px; word-break: break-all; }
        .ingest-src code { font-size: 0.66rem; background: none; color: var(--process); }

        /* Agent "thinking" trace ------------------------------------------- */
        .think-agent { font-family: 'IBM Plex Mono', monospace; font-size: 0.72rem; font-weight: 600;
            letter-spacing: 0.1em; text-transform: uppercase; color: var(--ink);
            margin: 14px 0 5px; display: flex; align-items: center; gap: 8px; }
        .think-agent::before { content: ""; width: 7px; height: 7px; background: var(--process); flex: none; }
        .think-step { font-size: 0.85rem; color: var(--faded); margin: 3px 0 3px 16px; line-height: 1.5; }
        .think-step .ref { color: var(--process); font-weight: 500; }
        .think-view { font-size: 0.88rem; color: var(--ink); margin: 6px 0 4px 16px;
            padding-left: 11px; border-left: 2px solid var(--line); line-height: 1.55; }

        /* Timeline topic dropdowns (st.expander) ---------------------------- */
        [data-testid="stExpander"] {
            border: 2px solid var(--ink); border-radius: 3px; background: var(--vellum);
            margin-bottom: 0.9rem; box-shadow: 4px 4px 0 rgba(22, 50, 74, 0.07);
        }
        /* Style ONLY the label paragraph — never the toggle icon (it's an icon font) */
        [data-testid="stExpander"] summary p {
            font-family: 'IBM Plex Mono', monospace; font-weight: 600; font-size: 0.78rem;
            letter-spacing: 0.06em; text-transform: uppercase; color: var(--ink); margin: 0;
        }
        [data-testid="stExpander"] summary:hover p { color: var(--process); }
        /* Belt-and-suspenders: don't let text-transform/spacing leak onto the icon
           (leave its font-family alone — that's the Material Symbols icon font) */
        [data-testid="stExpanderToggleIcon"], [data-testid="stExpanderToggleIcon"] * {
            text-transform: none !important; letter-spacing: normal !important;
        }

        /* File uploader (Ingest page) --------------------------------------- */
        [data-testid="stFileUploaderDropzone"] {
            background: var(--vellum); border: 2px dashed var(--line); border-radius: 3px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# --- Chat history ------------------------------------------------------------
@st.cache_resource(show_spinner=False)
def _chat_store() -> dict:
    """Server-side chat history. Navbar links do a full page reload (new Streamlit
    session), which wipes st.session_state — this cache_resource singleton lives with
    the server process instead, so the conversation survives hopping between pages.
    Single-user demo scope: all browser tabs share this one conversation."""
    return {"messages": [{"role": "assistant", "content": WELCOME}]}


messages = _chat_store()["messages"]

# Error replies produced by generate_response's handler — used to flip the status UI.
_ERROR_PREFIXES = ("**Atlas is rate-limited", "**Atlas can't reach", "**Something went wrong")


def send(user_message: str) -> None:
    messages.append({"role": "user", "content": user_message})
    trace = []
    with st.status("Atlas is consulting its agents…", expanded=True) as status:
        def on_event(ev):
            trace.append(ev)
            md = _event_md(ev)
            if md:
                st.markdown(md, unsafe_allow_html=True)
        reply = generate_response(user_message, messages, on_event)
        if reply.startswith(_ERROR_PREFIXES):
            status.update(label="Atlas hit a problem", state="error", expanded=False)
        else:
            status.update(label="Atlas answered", state="complete", expanded=False)
    messages.append({"role": "assistant", "content": reply, "trace": trace})
    _memory_stats.clear()  # a write-back may have changed the counts shown in the sidebar


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
            <div class="nav-links">{link('chat', 'Chat')}{link('timeline', 'Timeline')}{link('ingest', 'Ingest')}{link('about', 'About')}</div>
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
            <hr class="atlas-rule">
        </div>
        """,
        unsafe_allow_html=True,
    )
    for msg in messages:
        with st.chat_message(msg["role"]):
            if msg.get("trace"):
                with st.expander("Agent reasoning"):
                    for ev in msg["trace"]:
                        md = _event_md(ev)
                        if md:
                            st.markdown(md, unsafe_allow_html=True)
            st.markdown(msg["content"])
    if len(messages) == 1:
        st.markdown(
            '<div class="chat-hint">Ask how a decision changed over time, or a resourcing '
            'question — Finance, Product, and Strategy each weigh in, then Strategy answers.</div>',
            unsafe_allow_html=True,
        )
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
        with st.spinner("Loading the decision timeline…"):
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
        return f"<div><dt>{label}</dt><dd>{_esc(value)}</dd></div>" if value else ""

    def topic_html(revs: list) -> str:
        rows = ['<div class="reg-body">']
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
                f'<span class="recorded">— {_esc(d["recorded_by"])}</span></div>'
                f'<p class="belief">{_esc(d["new_state"])}</p>'
                f'<dl class="prov">{prov_row("Cause", d["cause"])}{prov_row("Trigger", d["trigger_event"])}{prov_row("Tension", d["tension"])}</dl>'
                f'</article>'
            )
        rows.append("</div>")
        return "".join(rows)

    # Collapsible per-topic dropdowns, most recently changed topic first (freshly
    # ingested or written-back topics surface at the top of the register).
    ordered = sorted(topics.items(),
                     key=lambda kv: max((d["created_at"] or "") for d in kv[1]),
                     reverse=True)
    for topic, revs in ordered:
        current_state = revs[-1]["new_state"]
        n = len(revs)
        with st.expander(f"{topic}  ·  {n} revision{'s' if n != 1 else ''}", expanded=False):
            st.markdown(f'<div class="reg-current">Current: {_esc(current_state)}</div>', unsafe_allow_html=True)
            st.markdown(topic_html(revs), unsafe_allow_html=True)


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


def render_ingest() -> None:
    st.markdown(
        """
        <div class="atlas-header">
            <div class="atlas-kicker">Ingest</div>
            <h1 class="page-title">Add documents to memory</h1>
            <div class="page-sub">Upload a document or a full meeting discussion (PDF, Word, Markdown,
            PowerPoint). The original is stored in Amazon S3, then Atlas distills it into one compact
            record per decision or change and appends each to memory — where it appears in the Timeline.</div>
            <hr class="atlas-rule">
        </div>
        """,
        unsafe_allow_html=True,
    )

    files = st.file_uploader(
        "Drop files here",
        type=["pdf", "docx", "md", "txt", "pptx"],
        accept_multiple_files=True,
    )

    if files and st.button("Extract key points and append to memory", use_container_width=True):
        import ingest
        import storage
        total = 0
        for f in files:
            data = f.getvalue()
            # 1) stage the original document in S3 (keeps the source; provenance)
            source_line = ""
            if storage.is_configured():
                try:
                    with st.spinner(f"Staging {f.name} in S3…"):
                        uri = storage.upload_document(f.name, data)
                    source_line = f'<div class="ingest-src">Staged in S3: <code>{_esc(uri)}</code></div>'
                except Exception as e:
                    source_line = f'<div class="ingest-src">S3 staging skipped: {_esc(e)}</div>'
            # 2) distill + append to memory
            with st.spinner(f"Distilling {f.name} and saving decisions…"):
                try:
                    recorded = ingest.ingest_file(f.name, data)
                except (Exception, SystemExit) as e:
                    st.markdown(
                        f'<div class="about-card"><p><b>{_esc(f.name)} — could not process.</b><br>{_esc(e)}</p>{source_line}</div>',
                        unsafe_allow_html=True,
                    )
                    continue
            if not recorded:
                st.markdown(
                    f'<div class="about-card"><p><b>{_esc(f.name)}:</b> no decisions found to record.</p>{source_line}</div>',
                    unsafe_allow_html=True,
                )
                continue
            total += len(recorded)
            items = "".join(f'<li><b>{_esc(r["topic"])}</b>: {_esc(r["new_state"])}</li>' for r in recorded)
            st.markdown(
                f'<div class="about-card"><span class="about-verb">Appended {len(recorded)}</span>'
                f'<h3>{_esc(f.name)}</h3><ul>{items}</ul>{source_line}</div>',
                unsafe_allow_html=True,
            )
        if total:
            _memory_stats.clear()  # sidebar counts changed — drop the 30s cache now
            st.success(f"Appended {total} decision(s) to memory. Open the Timeline to see them.")


@st.cache_data(ttl=30, show_spinner=False)
def _memory_stats() -> tuple[int, int]:
    """(topics, decisions) currently in memory — cached briefly so it's cheap per page."""
    import os
    import sys
    db_dir = os.path.join(os.path.dirname(__file__), "db")
    if db_dir not in sys.path:
        sys.path.insert(0, db_dir)
    import tools as memory
    decs = memory.list_decisions()
    return len({d["topic"] for d in decs}), len(decs)


def render_sidebar(active: str) -> None:
    with st.sidebar:
        st.markdown('<div class="side-brand">ATLAS</div>', unsafe_allow_html=True)
        try:
            topics, count = _memory_stats()
            st.markdown(f'<div class="side-meta">{topics} topics &middot; {count} decisions</div>',
                        unsafe_allow_html=True)
        except Exception:
            pass
        st.markdown('<div class="side-status">Live &middot; CockroachDB</div>', unsafe_allow_html=True)
        st.markdown('<hr class="side-rule">', unsafe_allow_html=True)
        if active == "chat" and st.button("Reset conversation", use_container_width=True):
            # Mutate in place — the cached store holds a reference to this exact list.
            messages.clear()
            messages.append({"role": "assistant", "content": WELCOME})
            st.rerun()


# --- Render the current page -------------------------------------------------
inject_theme()

view = st.query_params.get("view", "chat")
if view not in ("chat", "timeline", "ingest", "about"):
    view = "chat"

render_navbar(view)
render_sidebar(view)

if view == "timeline":
    render_timeline()
elif view == "ingest":
    render_ingest()
elif view == "about":
    render_about()
else:
    render_chat()
