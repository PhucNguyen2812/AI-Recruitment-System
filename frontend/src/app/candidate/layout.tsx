"use client"

import * as React from "react"
import Link from "next/link"
import { UserCheck } from "lucide-react"

export default function CandidateLayout({
    children,
}: {
    children: React.ReactNode
}) {
    return (
        <div className="min-h-screen bg-black text-white flex flex-col">
            {/* Candidate Header */}
            <header className="h-14 flex items-center justify-between px-6 border-b border-neutral-800 bg-neutral-950/90 backdrop-blur-md sticky top-0 z-50">
                <Link href="/" className="flex items-center gap-2">
                    <div className="h-8 w-8 rounded-lg bg-primary/20 flex items-center justify-center border border-primary/30">
                        <UserCheck className="h-4 w-4 text-primary" />
                    </div>
                    <span className="text-white font-bold tracking-tight text-lg">AHB</span>
                </Link>
                <div className="flex items-center space-x-4">
                    <Link
                        href="/candidate/apply"
                        className="text-sm text-neutral-400 hover:text-white transition-colors px-3 py-1.5 rounded-md hover:bg-neutral-800"
                    >
                        Nộp CV
                    </Link>
                    <Link
                        href="/candidate/status"
                        className="text-sm text-neutral-400 hover:text-white transition-colors px-3 py-1.5 rounded-md hover:bg-neutral-800"
                    >
                        Theo dõi hồ sơ
                    </Link>
                    <Link
                        href="/login"
                        className="text-sm bg-neutral-800 hover:bg-neutral-700 transition-colors px-3 py-1.5 rounded-md"
                    >
                        HR Login
                    </Link>
                </div>
            </header>

            {/* Main */}
            <main className="flex-1 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-neutral-900/30 to-black">
                {children}
            </main>

            {/* Footer */}
            <footer className="h-10 flex items-center justify-center border-t border-neutral-800 text-xs text-neutral-600">
                AI Recruitment System © 2026 — Powered by Random Forest + AHP
            </footer>
        </div>
    )
}
