import re
import sqlite3
import uuid
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter

STOP = set("a an the is are was were be when what where how why of to in and or for with on it this that".split())
def terms(text):
    words = set(re.findall(r"[a-z0-9]+", text.lower())) - STOP
    for run in re.findall(r"[\u4e00-\u9fff]+", text):
        words.update(run[i:i+2] for i in range(max(1, len(run)-1)))
    return words

class Store:
    def __init__(self, path):
        self.path = str(path)
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.executescript("""CREATE TABLE IF NOT EXISTS documents (id TEXT PRIMARY KEY, owner TEXT NOT NULL, filename TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS chunks (id TEXT PRIMARY KEY, document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE, text TEXT NOT NULL);
            CREATE INDEX IF NOT EXISTS documents_owner ON documents(owner);""")

    def connect(self):
        db = sqlite3.connect(self.path)
        db.row_factory = sqlite3.Row
        db.execute('PRAGMA foreign_keys=ON')
        return db

    def add(self, owner, filename, text):
        parts = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100).split_text(text)
        doc_id = str(uuid.uuid4())
        with self.connect() as db:
            db.execute('INSERT INTO documents VALUES (?,?,?)', (doc_id, owner, filename))
            db.executemany('INSERT INTO chunks VALUES (?,?,?)', [(f'{doc_id}:{i}', doc_id, part) for i, part in enumerate(parts)])
        return {'id': doc_id, 'filename': filename, 'chunks': len(parts)}

    def list(self, owner):
        with self.connect() as db:
            return [dict(r) for r in db.execute('SELECT d.id,d.filename,COUNT(c.id) AS chunks FROM documents d LEFT JOIN chunks c ON d.id=c.document_id WHERE d.owner=? GROUP BY d.id ORDER BY d.rowid DESC', (owner,))]

    def delete(self, owner, doc_id):
        with self.connect() as db:
            return db.execute('DELETE FROM documents WHERE id=? AND owner=?', (doc_id, owner)).rowcount > 0

    def answer(self, owner, ids, question):
        ids = list(dict.fromkeys(ids))
        markers = ','.join('?' for _ in ids)
        with self.connect() as db:
            found = db.execute(f'SELECT id FROM documents WHERE owner=? AND id IN ({markers})', [owner, *ids]).fetchall()
            if len(found) != len(ids): raise KeyError('Document not found')
            rows = db.execute(f'SELECT c.id AS chunk_id,c.document_id,d.filename,c.text AS excerpt FROM chunks c JOIN documents d ON d.id=c.document_id WHERE d.owner=? AND d.id IN ({markers}) ORDER BY c.id', [owner, *ids]).fetchall()
        query = terms(question)
        ranked = sorted(((len(query & terms(r['excerpt'])), dict(r)) for r in rows), key=lambda item: (-item[0], item[1]['chunk_id']))
        citations = [r for score, r in ranked[:3] if score > 0]
        text = '\n\n'.join(f'[{i+1}] {r["excerpt"]}' for i, r in enumerate(citations)) if citations else 'No matching evidence was found in the selected documents.'
        return {'text': text, 'citations': citations, 'insufficient_evidence': not citations, 'mode': 'local-extractive'}
