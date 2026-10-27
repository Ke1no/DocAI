import json
import os
from pathlib import Path
from uuid import uuid4
from fastapi import FastAPI, File, Header, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, field_validator
from .store import Store

LIMIT = 1024 * 1024
class Query(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    document_ids: list[str] = Field(min_length=1, max_length=20)
    @field_validator('question')
    @classmethod
    def not_blank(cls, value):
        if not value.strip(): raise ValueError('Question must not be blank')
        return value.strip()

def create_app(path=None):
    app = FastAPI(title='DocAI local scaffold')
    store = Store(path or os.environ.get('DOCUMENT_AI_DB', 'documents.db'))
    def owner(value):
        if not value or len(value) > 100: raise HTTPException(400, 'Missing local namespace')
        return value
    @app.get('/health')
    def health(): return {'status': 'ok', 'mode': 'local-extractive'}
    @app.get('/documents')
    def documents(x_document_session: str = Header()): return store.list(owner(x_document_session))
    @app.post('/documents', status_code=201)
    async def upload(file: UploadFile = File(), x_document_session: str = Header()):
        namespace = owner(x_document_session)
        filename = (file.filename or '').replace('\\', '/').rsplit('/', 1)[-1][:150]
        if Path(filename).suffix.lower() not in {'.txt', '.md'}: raise HTTPException(415, 'Use UTF-8 .txt or .md')
        raw = await file.read(LIMIT + 1)
        await file.close()
        if len(raw) > LIMIT: raise HTTPException(413, 'Maximum file size is 1 MiB')
        try: text = raw.decode('utf-8-sig')
        except UnicodeDecodeError: raise HTTPException(400, 'File must be UTF-8')
        if not text.strip() or '\x00' in text: raise HTTPException(400, 'Upload nonempty text')
        if len(store.list(namespace)) >= 50: raise HTTPException(429, 'Local document limit reached; delete a document first')
        return store.add(namespace, filename, text)
    @app.delete('/documents/{doc_id}', status_code=204)
    def delete(doc_id: str, x_document_session: str = Header()):
        if not store.delete(owner(x_document_session), doc_id): raise HTTPException(404, 'Document not found')
    def answer(body, namespace):
        try: return store.answer(owner(namespace), body.document_ids, body.question)
        except KeyError: raise HTTPException(404, 'Document not found')
    @app.post('/query')
    def query(body: Query, x_document_session: str = Header()): return answer(body, x_document_session)
    @app.post('/agent')
    def stream(body: Query, x_document_session: str = Header()):
        result = answer(body, x_document_session)
        run_id, message_id = str(uuid4()), str(uuid4())
        def events():
            def event(data): return 'data: ' + json.dumps(data) + '\n\n'
            yield event({'type':'RUN_STARTED','threadId':run_id,'runId':run_id})
            yield event({'type':'STATE_SNAPSHOT','snapshot': {'citations': result['citations'], 'mode': result['mode'], 'insufficient_evidence': result['insufficient_evidence']}})
            yield event({'type':'TEXT_MESSAGE_START','messageId':message_id,'role':'assistant'})
            for start in range(0,len(result['text']),80):
                yield event({'type':'TEXT_MESSAGE_CONTENT','messageId':message_id,'delta':result['text'][start:start+80]})
            yield event({'type':'TEXT_MESSAGE_END','messageId':message_id})
            yield event({'type':'RUN_FINISHED','threadId':run_id,'runId':run_id})
        return StreamingResponse(events(), media_type='text/event-stream', headers={'Cache-Control':'no-store','X-Accel-Buffering':'no'})
    return app

app = create_app()
