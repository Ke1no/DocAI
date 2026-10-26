# Document AI

Full-stack document Q&A **scaffold / work in progress**, based on the supplied project overview.

## What works now
- Next.js/React/TypeScript/Tailwind UI and server Route Handlers.
- Upload UTF-8 `.txt` / `.md` files (up to 1 MiB), list and delete documents.
- LangChain text splitting, persistent SQLite documents/chunks, browser-session namespaces.
- Deterministic keyword retrieval with source excerpts and citations; explicit no-evidence responses.
- Streaming answer text and citation state using an AG-UI-shaped SSE event subset.

**Local mode is extractive retrieval, not a completed generative RAG agent.** It does not call a model, embed vectors, query Pinecone or search the web. The answer is quoted source text. No API key is required.

## Run
Python 3.12+, Node 22.12+.

```sh
cd agent
python -m venv .venv
source .venv/bin/activate
# Windows PowerShell instead: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.lock.txt
python -m uvicorn document_ai.app:app --host 127.0.0.1 --port 8000
```

In a second terminal:
```sh
cd frontend
npm ci
npm run dev
```

Open http://localhost:3000 and upload `examples/project-notes.txt`. Ask `When is the deadline?`.
Next.js forwards through its own API routes to the local Python service. `AGENT_BASE_URL` is server-only; `.env.local` may override it.

## Next integrations
`agent/document_ai/integrations` contains optional ADK/Pinecone/MCP integration entry points. See [integration boundaries](docs/INTEGRATIONS.md). Google ADK orchestration, dense/vector and hybrid retrieval, CopilotKit runtime, full AG-UI input compatibility, external MCP tools, web search and model generation are **not connected or live-tested**.
Model IDs are configurable; the screenshot's product/model label is not assumed to be an available API ID.

This is a local, single-machine development demo. Namespace separation is not account authentication. Do not expose the Python port or deploy private documents until authentication, authorization, quotas and retention controls are implemented.

## Validation
Verified locally: frontend production build; five Python test cases; end-to-end HTTP checks through Next.js for upload, retrieval, citation streaming, session isolation, deletion and browser-origin rejection. External integrations were not exercised.

```sh
cd agent
python -m unittest discover -s tests -v
cd ../frontend
npm run build
```

See [中文开发清单](docs/NEXT_STEPS.zh-CN.md) and [architecture](docs/ARCHITECTURE.md).
