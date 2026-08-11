# ATLAS — Time-Aware Organizational Memory

> An AI that remembers what your company **believed, when, and why it changed its mind** —
> not just where things stand today.

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

### Multi-agent collaboration
A **Strategy** orchestrator answers questions, and for decisions that hinge on money or
roadmap it **consults specialist agents** — **Finance** (runway, burn, hiring cost) and
**Product** (roadmap, workload, backlog) — each grounded in the same shared memory. It then
synthesizes their input and records the outcome. Provenance questions skip the specialists.

### Write-back (the "act" loop)
After making a recommendation, the Strategy agent **writes it back** into `decisions` as a
new row. The system's own reasoning becomes new memory: query → retrieve → reason → record.

### Document ingestion (distiller + S3)
Upload a PDF / Word / Markdown / PowerPoint or a raw meeting transcript. The original is
**staged in Amazon S3**, then a **distiller agent** compresses the messy conversation into
one structured record per decision (reusing existing topic labels), and appends each to
memory — where it appears on the provenance timeline.

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
| LLM (chat, multi-agent, distiller) | **Gemini** |
| Embeddings (vector search) | **Gemini `gemini-embedding-001`**, 1536-dim |
| Frontend | **Streamlit** |

> **Note on models:** the original design targets **Amazon Bedrock** (Claude + Titan). On
> the team's free-tier AWS account, Bedrock text models require a paid Marketplace
> subscription and Titan embeddings were rate-limited to unusable, so we run the LLM and
> embeddings on **Gemini**. Bedrock is a drop-in swap behind `agent.py` / `db/embeddings.py`
> once a paid plan is available (`hello.py` is the Bedrock connectivity check).

---

## Setup

1. **Install** (Python 3.11+):
   ```bash
   python3 -m venv .venv && ./.venv/bin/pip install -r requirements.txt
   ```
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

## Asking questions

Every question runs through all three agents: Finance and Product each give their domain's
read, then Strategy synthesizes with the decision history.

- Ask **how or why a stance changed** and Strategy walks the provenance — old vs. new state
  across the revision chain, citing cause and tension.
- Ask a **forward-looking or resourcing question** and the Finance and Product views shape the
  Strategy recommendation, which is then recorded back into memory (the write-back).

---

## Project structure

```
app.py            Streamlit UI — Chat / Timeline / Ingest / About
agent.py          Strategy orchestrator + Finance/Product specialist agents [Track B]
distiller.py      Ingestion agent: raw conversation -> structured change records
ingest.py         Extract text (PDF/Word/MD/PPT) -> distiller -> memory
storage.py        S3 staging for uploaded source documents
landing.html      Standalone landing page (drafting-sheet identity)
db/               Data layer [Track A]: schema, connection, embeddings, tools, seed
samples/          Example documents for testing ingestion
```
