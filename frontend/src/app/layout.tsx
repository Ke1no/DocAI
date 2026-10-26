import type { ReactNode } from 'react'
import './globals.css'
export const metadata = { title: 'Document AI · Local retrieval scaffold', description: 'Upload text, retrieve evidence, inspect citations.' }
export default function Layout({ children }: { children: ReactNode }) { return <html lang="en"><body>{children}</body></html> }
