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
st.set_page_config(page_title="Atlas — Agentic Memory", layout="centered")

WELCOME = (
    "I'm **Atlas**. I remember what your company believed, when, and why it changed "
    "its mind — not just where things stand today.\n\n"
    "Ask me about a decision and I'll trace how the thinking got there."
)

EXAMPLE_QUESTIONS = [
    "Should we hire another engineer?",
    "Why did we deprioritize mobile offline sync?",
]


# --- The one seam that becomes the real agent later --------------------------
def generate_response(user_message: str, history: list[dict]) -> str:
    """Return the assistant's reply to `user_message`.

    RIGHT NOW: a mock so the UI is testable without Bedrock/DB.
    LATER (Day 3-5): replace the body with the Bedrock Converse tool-use loop —
    embed the question, let Claude call search_memory_index / fetch_decisions,
    then return its answer. The signature stays the same, so nothing else changes.
    """
    return (
        f"You asked: **{user_message}**\n\n"
        "This is where Atlas will search the memory index, fetch the relevant "
        "revisions, and answer with real provenance once the agent is connected.\n\n"
        "*(placeholder response — reasoning engine not wired up yet)*"
    )


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

        /* Hide default Streamlit chrome */
        [data-testid="stHeader"] { background: transparent; }
        #MainMenu, footer, [data-testid="stToolbar"] { visibility: hidden; }

        /* Keep the bottom input band on-theme (no white strip) */
        [data-testid="stBottom"], [data-testid="stBottom"] > div {
            background: transparent;
        }

        .block-container { max-width: 780px; padding-top: 2.2rem; padding-bottom: 6rem; }

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
        </style>
        """,
        unsafe_allow_html=True,
    )


# --- Session state -----------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": WELCOME}]


def send(user_message: str) -> None:
    st.session_state.messages.append({"role": "user", "content": user_message})
    reply = generate_response(user_message, st.session_state.messages)
    st.session_state.messages.append({"role": "assistant", "content": reply})


# --- UI ----------------------------------------------------------------------
inject_theme()

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

# Example-question buttons (only before the first user turn).
if len(st.session_state.messages) == 1:
    cols = st.columns(len(EXAMPLE_QUESTIONS))
    for col, q in zip(cols, EXAMPLE_QUESTIONS):
        if col.button(q, use_container_width=True):
            send(q)
            st.rerun()

if prompt := st.chat_input("Ask about the company's decision history"):
    send(prompt)
    st.rerun()

with st.sidebar:
    st.markdown('<div class="side-brand">ATLAS</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="side-meta">Sheet 01 &middot; Rev C<br>2026-08-09</div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="side-status">UI shell — mock responses</div>', unsafe_allow_html=True)
    st.markdown('<hr class="side-rule">', unsafe_allow_html=True)
    if st.button("Reset conversation", use_container_width=True):
        st.session_state.messages = [{"role": "assistant", "content": WELCOME}]
        st.rerun()
