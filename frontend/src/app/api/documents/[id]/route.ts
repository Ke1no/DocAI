import { proxy } from '@/lib/server'
export async function DELETE(request: Request, context: { params: Promise<{ id: string }> }) {
  const { id } = await context.params
  return proxy(request, `/documents/${encodeURIComponent(id)}`)
}
