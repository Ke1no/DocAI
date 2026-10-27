import type { ReactNode } from 'react'
import './globals.css'
export const metadata = { title: 'DocAI · Local retrieval scaffold', description: 'Upload text, retrieve evidence, inspect citations.' }
export default function Layout({ children }: { children: ReactNode }) { return <html lang="en"><body>{children}</body></html> }
