import { NextResponse } from 'next/server'
import { proxy } from '@/lib/server'
export const runtime = 'nodejs'
export async function GET(request: Request) { return proxy(request, '/documents') }
export async function POST(request: Request) {
  if (Number(request.headers.get('content-length') || '0') > 1100000) return NextResponse.json({ error: 'Maximum file size is 1 MiB' }, { status: 413 })
  try {
    const form = await request.formData()
    const file = form.get('file')
    if (!(file instanceof File) || file.size > 1048576) return NextResponse.json({ error: 'Upload one file up to 1 MiB' }, { status: 400 })
    return proxy(request, '/documents', form)
  } catch { return NextResponse.json({ error: 'Invalid upload' }, { status: 400 }) }
}
