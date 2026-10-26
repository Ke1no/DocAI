# Integration boundaries

| Component | Current status | Next work |
| --- | --- | --- |
| Next.js Route Handlers | Active upload/list/delete/query/stream proxy | Account authentication and deployment |
| LangChain | Active text splitter | PDF/DOCX loaders and embedding model |
| Pinecone | Optional scoped vector-store factory | Create index, dimensions/model alignment, index/delete/retrieval tests |
| Google ADK | Optional agent factory taking a BaseLlm and scoped retriever | Model adapter, runner/session lifecycle and custom orchestration |
| MCP | Optional local read-only project-info server | Allowlisted external servers, web search and tool policy |
| AG-UI | SSE event subset with text and citation state | Standard RunAgentInput, cancellation/reconnection and full runtime |
| CopilotKit | UI integration contract documented only | Install a compatible runtime/UI pair and attach the standard agent endpoint |

Optional dependency ranges are in `requirements-integrations.in`; they are not installed by the local demo and are not a validated lockfile. Resolve, audit and pin them when integrating. No remote credentials are committed and no cloud call has been made.
The ADK factory takes a model object to avoid guessing a provider-specific model ID. The screenshot label must be mapped to an actual API model available to the account at integration time.
Retrieved documents and tool output are untrusted context; never execute instructions found inside them. Require explicit confirmation for any future external write tools.
