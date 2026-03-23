"use client"

import * as React from "react"
import { Shield, Loader2, AlertCircle, Search } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { useRouter } from "next/navigation"

interface AuditLog {
    id: number
    id_nguoi_dung: string | null
    hanh_dong: string
    chi_tiet: string | null
    dia_chi_ip: string | null
    ngay_tao: string
}

export default function AuditLogPage() {
    const [logs, setLogs] = React.useState<AuditLog[]>([])
    const [loading, setLoading] = React.useState(true)
    const [error, setError] = React.useState<string | null>(null)
    const [searchTerm, setSearchTerm] = React.useState("")
    const router = useRouter()

    const fetchLogs = async () => {
        setLoading(true)
        const token = localStorage.getItem("token")
        if (!token) {
            router.push("/login")
            return
        }

        try {
            const res = await fetch("http://localhost:8000/api/admin/audit-logs", {
                headers: { "Authorization": `Bearer ${token}` }
            })
            if (!res.ok) {
                if (res.status === 403) throw new Error("Bạn không có quyền truy cập trang này.")
                throw new Error("Không thể tải nhật ký hệ thống.")
            }
            const data = await res.json()
            setLogs(data)
        } catch (err: any) {
            setError(err.message)
        } finally {
            setLoading(false)
        }
    }

    React.useEffect(() => {
        fetchLogs()
    }, [])

    const filteredLogs = logs.filter(log => 
        log.hanh_dong.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (log.chi_tiet && log.chi_tiet.toLowerCase().includes(searchTerm.toLowerCase()))
    )

    const formatDate = (iso: string) => {
        return new Date(iso).toLocaleString("vi-VN")
    }

    if (error) {
        return (
            <div className="flex flex-col items-center justify-center h-[60vh] space-y-4">
                <AlertCircle className="h-12 w-12 text-red-500" />
                <h2 className="text-xl font-bold text-white">Lỗi truy cập</h2>
                <p className="text-neutral-400">{error}</p>
            </div>
        )
    }

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold text-white flex items-center gap-2">
                        <Shield className="h-6 w-6 text-primary" />
                        Nhật ký hệ thống (Audit Logs)
                    </h2>
                    <p className="text-sm text-neutral-400 mt-1">
                        Theo dõi các hành động nhạy cảm của người dùng và hệ thống.
                    </p>
                </div>
                <div className="relative w-64">
                    <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-neutral-500" />
                    <Input
                        placeholder="Tìm kiếm hành động..."
                        className="pl-9 bg-neutral-900 border-neutral-800 text-white"
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                    />
                </div>
            </div>

            <Card className="bg-neutral-900 border-neutral-800 shadow-xl overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                        <thead>
                            <tr className="border-b border-neutral-800 bg-neutral-950/60">
                                <th className="px-4 py-3 text-left text-xs font-semibold text-neutral-400">Thời gian</th>
                                <th className="px-4 py-3 text-left text-xs font-semibold text-neutral-400">Hành động</th>
                                <th className="px-4 py-3 text-left text-xs font-semibold text-neutral-400">Chi tiết</th>
                                <th className="px-4 py-3 text-left text-xs font-semibold text-neutral-400">User ID</th>
                                <th className="px-4 py-3 text-left text-xs font-semibold text-neutral-400">IP</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-neutral-800/60">
                            {loading ? (
                                <tr>
                                    <td colSpan={5} className="px-4 py-12 text-center">
                                        <Loader2 className="h-6 w-6 animate-spin mx-auto text-primary" />
                                        <p className="text-xs text-neutral-500 mt-2">Đang tải nhật ký...</p>
                                    </td>
                                </tr>
                            ) : filteredLogs.length === 0 ? (
                                <tr>
                                    <td colSpan={5} className="px-4 py-12 text-center text-neutral-500">
                                        Không tìm thấy nhật ký nào.
                                    </td>
                                </tr>
                            ) : (
                                filteredLogs.map((log) => (
                                    <tr key={log.id} className="hover:bg-neutral-800/30 transition-colors">
                                        <td className="px-4 py-3 text-xs text-neutral-400 whitespace-nowrap">
                                            {formatDate(log.ngay_tao)}
                                        </td>
                                        <td className="px-4 py-3">
                                            <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-primary/10 text-primary border border-primary/20">
                                                {log.hanh_dong}
                                            </span>
                                        </td>
                                        <td className="px-4 py-3 text-xs text-neutral-300">
                                            {log.chi_tiet}
                                        </td>
                                        <td className="px-4 py-3 text-[10px] font-mono text-neutral-500">
                                            {log.id_nguoi_dung || "SYSTEM"}
                                        </td>
                                        <td className="px-4 py-3 text-xs text-neutral-500">
                                            {log.dia_chi_ip || "N/A"}
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </Card>
        </div>
    )
}
