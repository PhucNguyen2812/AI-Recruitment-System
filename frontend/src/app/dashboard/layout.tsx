"use client"

import * as React from "react"
import Link from "next/link"
import { usePathname, useRouter } from "next/navigation"
import {
    Users,
    LogOut,
    Menu,
    Megaphone,
    Briefcase,
    Shield,
    UserCheck,
} from "lucide-react"
import dynamic from "next/dynamic"

const NotificationBell = dynamic(() => import("@/components/NotificationBell"), { ssr: false })

export default function DashboardLayout({
    children,
}: {
    children: React.ReactNode
}) {
    const pathname = usePathname()
    const router = useRouter()
    const [sidebarOpen, setSidebarOpen] = React.useState(true)
    const [user, setUser] = React.useState<any>(null)
    const [isLoading, setIsLoading] = React.useState(true)

    React.useEffect(() => {
        const checkAuth = () => {
            const token = localStorage.getItem("token")
            const storedUser = localStorage.getItem("user")

            if (!token || !storedUser || storedUser === "undefined") {
                console.log("No valid session found, redirecting to login...");
                localStorage.clear()
                router.replace("/login")
                return
            }

            try {
                const parsedUser = JSON.parse(storedUser)
                setUser(parsedUser)
                setIsLoading(false)
            } catch (e) {
                console.error("Failed to parse user from localStorage", e)
                localStorage.clear()
                router.replace("/login")
            }
        }

        checkAuth()
    }, [router])

    const navigation = [
        { name: "Chiến dịch tuyển dụng", href: "/dashboard/campaigns", icon: Megaphone },
        { name: "Vị trí tuyển dụng", href: "/dashboard/positions", icon: Briefcase },
        { name: "Ứng viên", href: "/dashboard/candidates", icon: Users },
    ]

    // Add Audit Logs for admin only
    if (user?.vai_tro === "admin") {
        navigation.push({ name: "Nhật ký hệ thống", href: "/dashboard/admin/audit", icon: Shield })
    }

    const pageTitle = navigation.find(n =>
        pathname.startsWith(n.href)
    )?.name || "Dashboard"

    const handleLogout = () => {
        localStorage.clear()
        router.push("/login")
    }

    if (isLoading) {
        return (
            <div className="h-screen w-screen bg-black flex items-center justify-center">
                <div className="flex flex-col items-center gap-4">
                    <div className="h-12 w-12 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
                    <p className="text-neutral-400 animate-pulse text-sm">Đang xác thực phiên làm việc...</p>
                </div>
            </div>
        )
    }

    return (
        <div className="flex h-screen bg-black text-white overflow-hidden">
            {/* Sidebar */}
            <aside
                className={`${sidebarOpen ? "w-64" : "w-16"
                    } transition-all duration-300 ease-in-out border-r border-neutral-800 bg-neutral-950 flex flex-col flex-shrink-0`}
            >
                {/* Logo */}
                <div className="h-16 flex items-center justify-between px-4 border-b border-neutral-800">
                    {sidebarOpen && (
                        <div className="flex items-center gap-2">
                            <div className="h-8 w-8 rounded-lg bg-primary/20 flex items-center justify-center border border-primary/30">
                                <UserCheck className="h-4 w-4 text-primary" />
                            </div>
                            <span className="text-white font-bold tracking-tight text-lg">AHB</span>
                        </div>
                    )}
                    <button
                        onClick={() => setSidebarOpen(!sidebarOpen)}
                        className="p-2 rounded-md hover:bg-neutral-800 transition-colors ml-auto"
                        aria-label="Toggle sidebar"
                    >
                        <Menu className="h-4 w-4" />
                    </button>
                </div>

                {/* Navigation */}
                <nav className="flex-1 overflow-y-auto py-4">
                    <ul className="space-y-1 px-2">
                        {navigation.map((item) => {
                            const isActive = pathname.startsWith(item.href)
                            const Icon = item.icon
                            return (
                                <li key={item.name}>
                                    <Link
                                        href={item.href}
                                        className={`flex items-center px-3 py-2.5 rounded-lg transition-all text-sm ${isActive
                                                ? "bg-neutral-800 text-white font-semibold"
                                                : "text-neutral-500 hover:bg-neutral-900 hover:text-white"
                                            } ${!sidebarOpen ? "justify-center" : ""}`}
                                        title={!sidebarOpen ? item.name : undefined}
                                    >
                                        <Icon className={`h-4 w-4 flex-shrink-0 ${sidebarOpen ? "mr-3" : ""} ${isActive ? "text-primary" : ""}`} />
                                        {sidebarOpen && <span>{item.name}</span>}
                                    </Link>
                                </li>
                            )
                        })}
                    </ul>

                    {/* Divider + Candidate Portal link */}
                    {sidebarOpen && (
                        <div className="mt-4 px-3">
                            <p className="text-[10px] font-semibold uppercase text-neutral-700 tracking-widest mb-2 px-1">Liên kết ngoài</p>
                            <Link
                                href="/candidate/apply"
                                target="_blank"
                                className="flex items-center px-3 py-2 rounded-lg text-xs text-neutral-600 hover:text-neutral-400 hover:bg-neutral-900 transition-colors"
                            >
                                → Cổng ứng viên
                            </Link>
                        </div>
                    )}
                </nav>

                {/* User / Logout */}
                <div className="p-3 border-t border-neutral-800">
                    <button
                        onClick={handleLogout}
                        className={`flex items-center w-full px-3 py-2 rounded-lg text-neutral-500 hover:bg-neutral-900 hover:text-white transition-colors text-sm ${!sidebarOpen ? "justify-center" : ""}`}
                        title={!sidebarOpen ? "Đăng xuất" : undefined}
                    >
                        <LogOut className={`h-4 w-4 flex-shrink-0 ${sidebarOpen ? "mr-3" : ""}`} />
                        {sidebarOpen && <span>Đăng xuất</span>}
                    </button>
                </div>
            </aside>

            {/* Main Content */}
            <div className="flex-1 flex flex-col overflow-hidden min-w-0">
                {/* Header */}
                <header className="h-16 flex items-center justify-between px-6 border-b border-neutral-800 bg-neutral-950/80 backdrop-blur-md z-20 flex-shrink-0">
                    <h1 className="text-base font-semibold text-white">{pageTitle}</h1>
                    <div className="flex items-center gap-3">
                        {/* API status */}
                        <span className="hidden sm:flex text-xs text-neutral-500 bg-neutral-900 border border-neutral-800 px-2.5 py-1 rounded-full items-center gap-1.5">
                            <span className="h-1.5 w-1.5 rounded-full bg-green-500 shadow-[0_0_6px_rgba(34,197,94,0.7)]" />
                            API Online
                        </span>

                        {/* Notification Bell */}
                        <NotificationBell />

                        {/* HR Avatar */}
                        <div className="h-8 w-8 rounded-full bg-neutral-800 flex items-center justify-center border border-neutral-700 flex-shrink-0">
                            <span className="text-xs font-bold text-neutral-300">HR</span>
                        </div>
                    </div>
                </header>

                {/* Scrollable Content */}
                <main className="flex-1 overflow-y-auto p-6 lg:p-8 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-neutral-900/30 to-black">
                    {children}
                </main>
            </div>
        </div>
    )
}
