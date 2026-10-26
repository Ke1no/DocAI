import { queryProxy } from '@/lib/server'
export async function POST(request: Request) { return queryProxy(request, '/agent') }
