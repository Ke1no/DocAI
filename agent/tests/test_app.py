import json
import tempfile
import unittest
from pathlib import Path
from fastapi.testclient import TestClient
from document_ai.app import create_app

class AppTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.client = TestClient(create_app(Path(self.temp.name)/'test.db'))
        self.owner = {'x-document-session':'alice'}
        r=self.client.post('/documents',headers=self.owner,files={'file':('notes.txt',b'The project deadline is December 15, 2026.')})
        self.assertEqual(r.status_code,201);self.doc=r.json()['id']
    def tearDown(self): self.client.close();self.temp.cleanup()
    def body(self,q='When is the deadline?'):return {'question':q,'document_ids':[self.doc]}
    def test_evidence_and_abstention(self):
        answer=self.client.post('/query',headers=self.owner,json=self.body()).json()
        self.assertIn('December 15',answer['text']);self.assertEqual(answer['citations'][0]['document_id'],self.doc)
        self.assertTrue(self.client.post('/query',headers=self.owner,json=self.body('galaxy unicorn')).json()['insufficient_evidence'])
    def test_namespace_and_delete(self):
        bob={'x-document-session':'bob'}
        self.assertEqual(self.client.get('/documents',headers=bob).json(),[])
        self.assertEqual(self.client.post('/query',headers=bob,json=self.body()).status_code,404)
        self.assertEqual(self.client.delete('/documents/'+self.doc,headers=bob).status_code,404)
        self.assertEqual(self.client.delete('/documents/'+self.doc,headers=self.owner).status_code,204)
        self.assertEqual(self.client.post('/query',headers=self.owner,json=self.body()).status_code,404)
    def test_bad_uploads(self):
        for name,data,status in [('bad.pdf',b'test',415),('bad.txt',b'\xff',400),('empty.txt',b' ',400),('large.txt',b'x'*(1024*1024+1),413)]:
            self.assertEqual(self.client.post('/documents',headers=self.owner,files={'file':(name,data)}).status_code,status)
    def test_stream_lifecycle(self):
        r=self.client.post('/agent',headers=self.owner,json=self.body())
        events=[json.loads(s[6:]) for s in r.text.strip().split('\n\n')]
        self.assertEqual(events[0]['type'],'RUN_STARTED');self.assertEqual(events[-1]['type'],'RUN_FINISHED')
        self.assertTrue(any(e['type']=='STATE_SNAPSHOT' and e['snapshot']['citations'] for e in events))
        self.assertIn('December 15',''.join(e['delta'] for e in events if e['type']=='TEXT_MESSAGE_CONTENT'))
    def test_blank_query(self):
        self.assertEqual(self.client.post('/query',headers=self.owner,json=self.body(' ')).status_code,422)
if __name__=='__main__': unittest.main()
