'use client'
import { useEffect, useState, type FormEvent } from 'react'
import type { DocumentRecord, Citation } from '@/lib/types'
export default function Home() {
  const [docs,setDocs]=useState<DocumentRecord[]>([]), [selected,setSelected]=useState<string[]>([])
  const [question,setQuestion]=useState('When is the deadline?'), [answer,setAnswer]=useState('')
  const [citations,setCitations]=useState<Citation[]>([]), [busy,setBusy]=useState(false), [error,setError]=useState('')
  async function refresh() {
    const r=await fetch('/api/documents');if(!r.ok) throw Error('Start the Python service on port 8000.')
    const data:DocumentRecord[]=await r.json();setDocs(data);setSelected(old=>old.filter(id=>data.some(d=>d.id===id)))
  }
  useEffect(()=>{void refresh().catch(e=>setError(String(e.message)))},[])
  async function upload(e:FormEvent<HTMLFormElement>) {
    e.preventDefault();const form=e.currentTarget;setBusy(true);setError('')
    try { const r=await fetch('/api/documents',{method:'POST',body:new FormData(form)});if(!r.ok) throw Error('Upload failed. Use nonempty UTF-8 .txt/.md up to 1 MiB.');const doc:DocumentRecord=await r.json();await refresh();setSelected(old=>[...old,doc.id]);form.reset() }
    catch(e){setError(e instanceof Error?e.message:'Upload failed')}finally{setBusy(false)}
  }
  async function remove(id:string) {
    setBusy(true);setError('');try{const r=await fetch(`/api/documents/${id}`,{method:'DELETE'});if(!r.ok)throw Error('Delete failed');setAnswer('');setCitations([]);await refresh()}catch(e){setError(String(e))}finally{setBusy(false)}
  }
  async function ask(e:FormEvent) {
    e.preventDefault();setBusy(true);setError('');setAnswer('');setCitations([])
    try {
      const r=await fetch('/api/agent',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question,document_ids:selected})})
      if(!r.ok||!r.body)throw Error(`Query failed (${r.status}). Check the service and selected documents.`)
      const reader=r.body.getReader(), decoder=new TextDecoder();let buffer='',finished=false
      while(true){const {done,value}=await reader.read();buffer+=decoder.decode(value,{stream:!done});let boundary
        while((boundary=buffer.indexOf('\n\n'))>=0){const frame=buffer.slice(0,boundary);buffer=buffer.slice(boundary+2);const data=frame.split('\n').filter(l=>l.startsWith('data: ')).map(l=>l.slice(6)).join('\n');if(!data)continue;const event=JSON.parse(data)
          if(event.type==='TEXT_MESSAGE_CONTENT')setAnswer(old=>old+event.delta)
          if(event.type==='STATE_SNAPSHOT')setCitations(event.snapshot.citations||[])
          if(event.type==='RUN_ERROR')throw Error('Agent stream failed')
          if(event.type==='RUN_FINISHED')finished=true
        }if(done)break
      }if(!finished)throw Error('The response stream was interrupted; retry the query.')
    }catch(e){setError(e instanceof Error?e.message:'Query failed')}finally{setBusy(false)}
  }
  return <main><header><strong>Doc<span>AI</span></strong><small>LOCAL EXTRACTIVE MODE · NO MODEL CONNECTED</small></header><section className="hero"><p className="eyebrow">FROM DOCUMENTS TO EVIDENCE</p><h1>Your documents.<br/><span>Answers you can trace.</span></h1><p>Upload text, select your sources, and inspect the matching excerpts.</p></section><div className="workspace"><aside><h2>Sources</h2><form onSubmit={upload}><label htmlFor="file">UTF-8 text or Markdown · up to 1 MiB</label><input id="file" name="file" type="file" accept=".txt,.md" required disabled={busy}/><button disabled={busy}>Upload document</button></form><div className="documents">{docs.map(d=><div className="document" key={d.id}><label><input type="checkbox" disabled={busy} checked={selected.includes(d.id)} onChange={e=>setSelected(old=>e.target.checked?[...old,d.id]:old.filter(id=>id!==d.id))}/><span>{d.filename}<small>{d.chunks} chunks</small></span></label><button className="text-button" disabled={busy} onClick={()=>void remove(d.id)}>Delete</button></div>)}{!docs.length&&<p>No documents yet. Start with the example notes.</p>}</div></aside><section className="answer"><form onSubmit={ask}><label htmlFor="question">Ask your documents</label><textarea id="question" rows={3} value={question} maxLength={2000} onChange={e=>setQuestion(e.target.value)} required/><button disabled={busy||!selected.length||!question.trim()}>{busy?'Working…':'Find evidence →'}</button></form>{error&&<p className="error" role="alert">{error}</p>}<div className="result" aria-live="polite">{answer||'Matching passages will appear here. This mode quotes sources; it does not generate an LLM answer.'}</div>{citations.length>0&&<section><h3>Source citations</h3>{citations.map((c,i)=><details key={c.chunk_id}><summary>[{i+1}] {c.filename}</summary><p>{c.excerpt}</p><small>{c.chunk_id}</small></details>)}</section>}</section></div><footer>Scaffold · ADK, Pinecone, CopilotKit and external MCP integrations are next.</footer></main>
}
