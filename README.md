# ATLAS — Time-Aware Organizational Memory

> An AI that remembers what your company **believed, when, and why it changed its mind** —
> not just where things stand today.

**Live demo:** https://atlas-agentic-memory.streamlit.app/

Built for the **CockroachDB × AWS "Build with Agentic Memory"** hackathon.

Startup knowledge is scattered across Slack, Notion, decks, and Jira. Those tools store
information; they don't connect it, and they don't remember how it changed. When people
leave, the *reasoning* leaves with them. Atlas keeps an append-only, versioned record of
every decision — the belief, the cause, what it traded off against — and lets agents
search it, reason over it, and write new conclusions back into it.

---

## How it works

### Two-tier memory (CockroachDB)
- **`decisions`** — append-only, versioned. Every belief change is a *new row*, never an
  overwrite. Structured fields (`old_state`, `new_state`, `cause`, `trigger_event`,
  `tension`) capture the causal "why" explicitly, so nothing has to be reconstructed later.
- **`memory_index`** — small, vector-searchable pointer rows (a short `tag` + its
  embedding). Cheap to scan; used to find the right topic before pulling full records.

### Agent-directed, two-stage retrieval
Agents call two separate tools rather than a fixed pipeline: a cheap **vector search** over
`memory_index`, then a precise **fetch** of only the matched `decisions` rows. The agent
decides *when* and *how deep* to retrieve — that's what makes it agentic, not hardcoded RAG.

### Multi-agent collaboration (parallel execution)
Every question fans out to **Finance** and **Product** specialist agents **in parallel** —
each constrained to its own domain, each grounding itself in the shared CockroachDB memory
via `search_memory_index` / `fetch_decisions`. The **Strategy** agent then synthesizes both
domain views with the decision history. For provenance questions ("how did X change?"),
Strategy answers directly from the history; for forward-looking questions, it weaves in the
specialist views and records its recommendation back to memory.

### Write-back (the "act" loop)
When the Strategy agent reaches a new recommendation, it calls `record_decision` to append
it as a new row. The system's own reasoning becomes queryable memory: query → retrieve →
reason → record.

### Document ingestion (distiller + S3)
Upload a PDF, Word (docx), Markdown, text, or PowerPoint (pptx) file. The original is
**staged in Amazon S3** (for provenance + reprocessing), then a **distiller agent** reads
the raw text and outputs one structured record per distinct decision or stance change —
reusing existing topic labels and extracting real decision dates. Each record is appended to
memory and appears on the Timeline.

---

## Store / Retrieve / Act (the hackathon's own framing)

| Verb | In Atlas |
| --- | --- |
| **Store** | Append-only versioned `decisions`; ingestion distills documents into new records. |
| **Retrieve** | Two-stage, agent-directed: vector search over the index → targeted fetch. |
| **Act** | The Strategy agent records its own recommendations back as new memory. |

---

## Tech stack

| Layer | Service |
| --- | --- |
| Database (relational + vector) | **CockroachDB Serverless** |
| Object storage (doc staging) | **Amazon S3** |
| LLM (chat, multi-agent, distiller) | **Gemini** (`gemini-flash-lite-latest` by default) |
| Embeddings (vector search) | **CockroachDB (Distributed Vector Embedding)** |
| Frontend | **Streamlit** (4 pages: Chat, Timeline, Ingest, About) |

---

## Setup

1. **Install** (Python 3.11+):
   ```bash
   python3 -m venv .venv && ./.venv/bin/pip install -r requirements.txt
   ```
   Document parsers need: `pip install pypdf python-docx python-pptx`

2. **Configure `.env`** in the project root:
   ```
   COCKROACH_DATABASE_URL=postgresql://...        # CockroachDB Cloud "Connect" string
   GEMINI_API_KEY=...                             # Google AI Studio
   GEMINI_CHAT_MODEL=gemini-flash-lite-latest     # optional (higher free quota)
   AWS_REGION=us-east-1                           # for S3
   AWS_ACCESS_KEY_ID=...                          # IAM user with S3 access
   AWS_SECRET_ACCESS_KEY=...
   S3_BUCKET=atlas-docs-<something-unique>        # optional; auto-derived if unset
   ```

3. **Create schema + load seed data** (also the "reset memory" path):
   ```bash
   ./.venv/bin/python -c "import sys; sys.path.insert(0,'db'); from connection import get_conn; \
     c=get_conn(); cur=c.cursor(); cur.execute(open('db/schema.sql').read()); c.commit()"
   ./.venv/bin/python db/load_seed.py
   ```

4. **Run:**
   ```bash
   ./.venv/bin/streamlit run app.py
   ```

---

## The 4-page UI

| Page | Purpose |
| --- | --- |
| **Chat** | Ask questions. Finance + Product run in parallel; Strategy answers and writes back. Live "thinking trace" shows each agent's searches, reads, and views. |
| **Timeline** | Full provenance register. Every topic as a collapsible revision chain — superseded entries struck through, current highlighted. Loads live from CockroachDB. |
| **Ingest** | Upload PDF / Word / Markdown / PowerPoint. Files staged in S3 → distilled → appended to memory. Results show immediately on Timeline. |
| **About** | Architecture diagram + 7 decision cards (DEC-01 through DEC-07) documenting every engineering tradeoff. |

---

## Asking questions

Every question runs through all three agents: Finance and Product each give their domain's
read (in parallel), then Strategy synthesizes with the decision history.

- Ask **how or why a stance changed** and Strategy walks the provenance — old vs. new state
  across the revision chain, citing cause and tension.
- Ask a **forward-looking or resourcing question** and the Finance and Product views shape the
  Strategy recommendation, which is then recorded back into memory (the write-back).
- Follow-up questions ("why?", "what about Q3?") resolve against conversation history.

---

## Project structure

```
app.py            Streamlit UI — Chat / Timeline / Ingest / About (4 pages, routing via ?view=)
agent.py          Strategy orchestrator + Finance/Product specialist agents (parallel execution)
distiller.py      Ingestion agent: raw text -> structured change records (JSON)
ingest.py         Extract text (PDF/Word/MD/PPT) -> distiller -> record_decision
storage.py        S3 staging for uploaded source documents (bucket auto-created)
landing.html      Standalone landing page (drafting-sheet identity)
db/               Data layer: schema, connection pool, embeddings, tools (search/fetch/record), seed
samples/          Example documents for testing ingestion
```
