"use client"

import * as React from "react"
import { Bell } from "lucide-react"

interface Notification {
    id: number
    message: string
    time: string
    read: boolean
    type: "info" | "success" | "warning"
}

const MOCK_NOTIFICATIONS: Notification[] = [
    {
        id: 1,
        message: "RF Batch hoàn thành: 12 CV rác bị loại",
        time: "5 phút trước",
        read: false,
        type: "success",
    },
    {
        id: 2,
        message: "Ứng viên mới nộp CV vào vị trí IT Intern",
        time: "20 phút trước",
        read: false,
        type: "info",
    },
    {
        id: 3,
        message: "AHP Batch chạy thành công — Top 10 đã được xác định",
        time: "1 giờ trước",
        read: false,
        type: "success",
    },
    {
        id: 4,
        message: "Cảnh báo: CR = 0.12 vượt ngưỡng, HR cần kéo lại slider",
        time: "2 giờ trước",
        read: true,
        type: "warning",
    },
    {
        id: 5,
        message: "Chiến dịch Marketing Intern Q1 2026 đã đóng",
        time: "1 ngày trước",
        read: true,
        type: "info",
    },
]

const typeColorMap: Record<string, string> = {
    success: "bg-green-500",
    warning: "bg-yellow-500",
    info: "bg-blue-500",
}

import axios from "@/lib/axios"

export default function NotificationBell() {
    const [open, setOpen] = React.useState(false)
    const [notifications, setNotifications] = React.useState<Notification[]>([])
    const ref = React.useRef<HTMLDivElement>(null)

    const fetchNotifications = async () => {
        try {
            const res = await axios.get("/api/notifications")
            setNotifications(res.data)
        } catch (err) {
            console.error("Failed to fetch notifications", err)
        }
    }

    React.useEffect(() => {
        fetchNotifications()
        // Poll every 1 minute
        const interval = setInterval(fetchNotifications, 60000)
        return () => clearInterval(interval)
    }, [])

    const unreadCount = notifications.filter((n) => !n.read).length

    const markRead = async (id: number) => {
        try {
            const res = await axios.patch(`/api/notifications/${id}/read`)
            if (res.status === 200) {
                setNotifications((prev) =>
                    prev.map((n) => (n.id === id ? { ...n, read: true } : n))
                )
            }
        } catch (err) {
            console.error("Failed to mark notification as read", err)
        }
    }


    // Close on outside click
    React.useEffect(() => {
        const handler = (e: MouseEvent) => {
            if (ref.current && !ref.current.contains(e.target as Node)) {
                setOpen(false)
            }
        }
        document.addEventListener("mousedown", handler)
        return () => document.removeEventListener("mousedown", handler)
    }, [])

    return (
        <div className="relative" ref={ref}>
            <button
                onClick={() => setOpen(!open)}
                className="relative p-2 rounded-md hover:bg-neutral-800 transition-colors text-neutral-400 hover:text-white"
                aria-label="Notifications"
            >
                <Bell className="h-5 w-5" />
                {unreadCount > 0 && (
                    <span className="absolute top-1 right-1 flex h-4 w-4 items-center justify-center rounded-full bg-red-500 text-[9px] font-bold text-white shadow-[0_0_6px_rgba(239,68,68,0.6)]">
                        {unreadCount}
                    </span>
                )}
            </button>

            {open && (
                <div className="absolute right-0 mt-2 w-80 bg-neutral-900 border border-neutral-800 rounded-xl shadow-2xl z-50 overflow-hidden">
                    {/* Header */}
                    <div className="flex items-center justify-between px-4 py-3 border-b border-neutral-800">
                        <span className="text-sm font-semibold text-white">Thông báo</span>
                        {unreadCount > 0 && (
                            <button
                                className="text-xs text-neutral-400 hover:text-white transition-colors"
                            >
                                Đánh dấu tất cả đã đọc
                            </button>
                        )}
                    </div>

                    {/* List */}
                    <ul className="max-h-72 overflow-y-auto divide-y divide-neutral-800/50">
                        {notifications.map((n) => (
                            <li
                                key={n.id}
                                onClick={() => markRead(n.id)}
                                className={`flex items-start gap-3 px-4 py-3 cursor-pointer transition-colors ${n.read
                                        ? "opacity-50 hover:opacity-70"
                                        : "bg-neutral-800/30 hover:bg-neutral-800/50"
                                    }`}
                            >
                                <span
                                    className={`mt-1 flex-shrink-0 h-2 w-2 rounded-full ${typeColorMap[n.type]}`}
                                />
                                <div className="flex-1 min-w-0">
                                    <p className="text-xs text-neutral-200 leading-snug">{n.message}</p>
                                    <p className="text-[10px] text-neutral-500 mt-0.5">{n.time}</p>
                                </div>
                                {!n.read && (
                                    <span className="flex-shrink-0 h-1.5 w-1.5 rounded-full bg-blue-400 mt-2" />
                                )}
                            </li>
                        ))}
                    </ul>

                    {/* Footer */}
                    <div className="px-4 py-2 border-t border-neutral-800 text-center">
                        <span className="text-xs text-neutral-500">
                            {unreadCount} thông báo chưa đọc
                        </span>
                    </div>
                </div>
            )}
        </div>
    )
}
