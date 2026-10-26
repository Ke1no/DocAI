# Local API

Next.js: GET/POST `/api/documents`; DELETE `/api/documents/{id}`; POST `/api/queries`; POST `/api/agent`.
Python: GET/POST `/documents`; DELETE `/documents/{id}`; POST `/query`; POST `/agent`; GET `/health`.

Upload: multipart form with `file`. Query: `{"question":"...","document_ids":["..."]}`.
Answer: `text`, `citations` (document_id, chunk_id, filename, excerpt), `insufficient_evidence`, `mode`.
The stream emits RUN_STARTED, STATE_SNAPSHOT, TEXT_MESSAGE_START/CONTENT/END, RUN_FINISHED. It is an event subset for this demo, not the full CopilotKit runtime contract.
Unsupported file extension, invalid UTF-8, empty content, excessive size, unknown/foreign IDs and empty questions are rejected.
