# Architecture

Next.js UI → Next.js Route Handlers → loopback Python service → LangChain splitter → SQLite document/chunk store → lexical retrieval → extractive excerpts and source citations.

A random HttpOnly same-site cookie identifies a local browser namespace. The frontend proxy supplies the namespace header; document listing, retrieval and deletion always filter by that namespace. The loopback service trusts this header, so this is not a production authentication boundary.

Target architecture from the screenshot: Next.js + CopilotKit/AG-UI → custom Google ADK orchestration → LangChain loaders/chunking/embedding/retrieval → Pinecone, with allowlisted MCP tools for external information.

Extension boundaries are explicit: replace the local retriever with a scoped Pinecone retriever; provide a configured ADK model and tool; expose a full AG-UI/CopilotKit runtime only after the agent contract is implemented. Do not silently turn local mode into a paid remote mode.
