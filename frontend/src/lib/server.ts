import { cookies } from 'next/headers'
import { NextResponse } from 'next/server'
import { randomUUID } from 'node:crypto'
const base = (process.env.AGENT_BASE_URL || 'http://127.0.0.1:8000').replace(/\/$/, '')
export async function proxy(request: Request, path: string, body?: BodyInit, contentType?: string) {
  const jar = await cookies()
  let namespace = jar.get('document-session')?.value
  if (!namespace || !/^[a-f0-9-]{36}$/.test(namespace)) {
    namespace = randomUUID()
    jar.set('document-session', namespace, { httpOnly: true, sameSite: 'strict', path: '/', secure: new URL(request.url).protocol === 'https:' })
  }
  // Restrict browser-origin writes; production still needs real account authentication.
  const origin = request.headers.get('origin')
  if (request.method !== 'GET' && origin && origin !== new URL(request.url).origin) return NextResponse.json({ error: 'Invalid origin' }, { status: 403 })
  const headers = new Headers({ 'x-document-session': namespace })
  if (contentType) headers.set('Content-Type', contentType)
  try {
    const upstream = await fetch(`${base}${path}`, { method: request.method, headers, body, cache: 'no-store', signal: AbortSignal.timeout(30000) })
    return new Response(upstream.body, { status: upstream.status, headers: { 'Content-Type': upstream.headers.get('content-type') || 'application/json', 'Cache-Control': 'no-store' } })
  } catch { return NextResponse.json({ error: 'Start the Python service on port 8000, then retry.' }, { status: 502 }) }
}
export async function queryProxy(request: Request, path: string) {
  const text = await request.text()
  if (text.length > 20000) return NextResponse.json({ error: 'Query too large' }, { status: 413 })
  try { JSON.parse(text) } catch { return NextResponse.json({ error: 'Invalid JSON' }, { status: 400 }) }
  return proxy(request, path, text, 'application/json')
}
