"use client"

import * as React from "react"
import { CheckCircle2, Circle, Clock, XCircle, ArrowRight, Loader2, RefreshCw } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import Link from "next/link"

type StatusKey = "submitted" | "accepted" | "rejected" | "pending"

interface ApplicationStatus {
    id: string
    candidate_name: string
    position: string
    submitted_at: string
    status: StatusKey
    updated_at: string
}

const STATUS_LABELS: Record<StatusKey, string> = {
    submitted: "Đã nộp",
    accepted: "Được nhận",
    rejected: "Không phù hợp",
    pending: "Đang xử lý",
}

const STEPS: { key: StatusKey; label: string; description: string }[] = [
    {
        key: "submitted",
        label: "Đã nộp",
        description: "Hồ sơ đã được tiếp nhận vào hệ thống, chờ AI xử lý.",
    },
    {
        key: "accepted",
        label: "Được nhận",
        description: "CV vượt qua vòng Random Forest. Đang đợi kết quả AHP ranking.",
    },
    {
        key: "rejected",
        label: "Không phù hợp",
        description: "Hồ sơ không phù hợp với yêu cầu vị trí. Cảm ơn bạn đã ứng tuyển!",
    },
]

function getStepIndex(status: StatusKey): number {
    if (status === "submitted" || status === "pending") return 0
    if (status === "accepted") return 1
    if (status === "rejected") return 2
    return 0
}

function StepIcon({ stepIdx, currentIdx, rejected }: { stepIdx: number; currentIdx: number; rejected: boolean }) {
    if (rejected && stepIdx === 2) return <XCircle className="h-5 w-5 text-red-400" />
    if (stepIdx < currentIdx) return <CheckCircle2 className="h-5 w-5 text-green-400" />
    if (stepIdx === currentIdx && !rejected) return <Clock className="h-5 w-5 text-primary animate-pulse" />
    return <Circle className="h-5 w-5 text-neutral-700" />
}

export default function CandidateStatusPage() {
    const [email, setEmail] = React.useState("")
    const [statuses, setStatuses] = React.useState<any[]>([])
    const [loading, setLoading] = React.useState(false)
    const [error, setError] = React.useState<string | null>(null)

    // Auto-load from localStorage on mount
    React.useEffect(() => {
        const storedEmail = localStorage.getItem("applicant_email")
        if (storedEmail) setEmail(storedEmail)
    }, [])

    const handleSearch = async (e?: React.FormEvent) => {
        if (e) e.preventDefault()
        if (!email.trim()) return

        setLoading(true)
        setError(null)

        try {
            const res = await fetch(`http://localhost:8000/api/cv/track`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email: email.trim() })
            })

            if (!res.ok) {
                const data = await res.json()
                throw new Error(data.detail || "Không tìm thấy hồ sơ khớp với email đã cung cấp.")
            }

            const data = await res.json()
            setStatuses(data)
        } catch (err: any) {
            setError(err.message || "Đã có lỗi xảy ra.")
            setStatuses([])
        } finally {
            setLoading(false)
        }
    }

    const formatDate = (iso: string) => {
        try {
            return new Date(iso).toLocaleString("vi-VN", {
                day: "2-digit", month: "2-digit", year: "numeric",
                hour: "2-digit", minute: "2-digit",
            })
        } catch {
            return iso
        }
    }

    return (
            <div className="flex min-h-[calc(100vh-112px)] items-start justify-center px-4 py-12">
                <div className="w-full max-w-2xl space-y-6">
                    <div className="text-center">
                        <h1 className="text-3xl font-bold text-white tracking-tight">Theo dõi hồ sơ</h1>
                        <p className="text-neutral-400 mt-2 text-sm">Nhập Email và Mã hồ sơ để xem trạng thái xử lý của CV.</p>
                    </div>

                    {/* Search bar */}
                    <Card className="bg-neutral-900 border-neutral-800 shadow-xl">
                        <CardContent className="pt-5 pb-5">
                            <form onSubmit={handleSearch} className="space-y-4">
                                <div className="flex gap-4">
                                    <div className="flex-1 space-y-1">
                                        <Label htmlFor="email" className="text-xs text-neutral-500">Email ứng tuyển</Label>
                                        <Input
                                            id="email"
                                            type="email"
                                            placeholder="email@example.com"
                                            value={email}
                                            onChange={(e) => setEmail(e.target.value)}
                                            className="bg-neutral-950 border-neutral-700 text-white placeholder:text-neutral-600"
                                            required
                                        />
                                    </div>
                                    <div className="flex items-end">
                                        <Button type="submit" disabled={loading || !email.trim()} className="w-full md:w-32 h-10">
                                            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : "Tra cứu"}
                                        </Button>
                                    </div>
                                </div>
                            </form>
                            {error && (
                                <p className="text-red-400 text-xs mt-3">{error}</p>
                            )}
                        </CardContent>
                    </Card>

                    {/* Status Cards */}
                    {statuses.length > 0 && (
                        <div className="space-y-4">
                            <div className="flex items-center justify-between mb-2 px-1">
                                <h2 className="text-lg font-semibold text-white">Kết quả ứng tuyển ({statuses.length})</h2>
                                <button
                                    onClick={() => handleSearch()}
                                    disabled={loading}
                                    className="flex items-center text-xs text-neutral-400 hover:text-white transition-colors"
                                >
                                    <RefreshCw className={`h-3.5 w-3.5 mr-1.5 ${loading ? "animate-spin" : ""}`} />
                                    Làm mới
                                </button>
                            </div>

                            {statuses.map((statusItem, index) => {
                                const currentIdx = getStepIndex(statusItem.trang_thai)
                                const isRejected = statusItem.trang_thai === "khong_phu_hop"

                                return (
                                    <Card key={statusItem.id || index} className="bg-neutral-900 border-neutral-800 shadow-xl overflow-hidden">
                                        <CardHeader className="border-b border-neutral-800 pb-4">
                                            <div className="flex items-start justify-between">
                                                <div>
                                                    <div className="flex items-center gap-2 mb-1">
                                                        <span className="text-xs font-semibold bg-neutral-800 text-neutral-300 px-2 py-0.5 rounded-full">
                                                            {statusItem.job_title}
                                                        </span>
                                                    </div>
                                                    <CardTitle className="text-base text-white">{statusItem.candidate_name}</CardTitle>
                                                    <p className="text-xs text-neutral-600 mt-1">Mã hồ sơ: <span className="font-mono text-neutral-400">{statusItem.id}</span></p>
                                                </div>
                                            </div>
                                        </CardHeader>

                                        <CardContent className="pt-8 pb-8">
                                            {/* Stepper */}
                                            <div className="relative flex flex-col gap-0">
                                                {STEPS.map((step, i) => {
                                                    const isDone = i < currentIdx
                                                    const isCurrent = i === currentIdx
                                                    const isPending = i > currentIdx

                                                    // Skip the "rejected" step if status is "accepted"
                                                    // But always show all 3 steps in the UI
                                                    const stepRejected = isRejected && i === 2

                                                    return (
                                                        <div key={step.key} className="flex gap-4">
                                                            {/* Icon + Line */}
                                                            <div className="flex flex-col items-center">
                                                                <div className={`flex h-9 w-9 items-center justify-center rounded-full border-2 transition-all ${stepRejected
                                                                    ? "border-red-500/60 bg-red-500/10"
                                                                    : isDone
                                                                        ? "border-green-500/60 bg-green-500/10"
                                                                        : isCurrent && !isRejected
                                                                            ? "border-primary/60 bg-primary/10"
                                                                            : "border-neutral-800 bg-neutral-950"
                                                                    }`}>
                                                                    <StepIcon stepIdx={i} currentIdx={currentIdx} rejected={isRejected} />
                                                                </div>
                                                                {i < STEPS.length - 1 && (
                                                                    <div className={`w-0.5 h-10 my-1 rounded-full ${isDone ? "bg-green-500/40" : "bg-neutral-800"}`} />
                                                                )}
                                                            </div>

                                                            {/* Content */}
                                                            <div className={`pb-8 ${i === STEPS.length - 1 ? "pb-0" : ""}`}>
                                                                <p className={`font-semibold text-sm ${stepRejected ? "text-red-400"
                                                                    : isDone ? "text-green-400"
                                                                        : isCurrent && !isRejected ? "text-white"
                                                                            : "text-neutral-700"
                                                                    }`}>
                                                                    {step.label}
                                                                    {isCurrent && !isRejected && (
                                                                        <span className="ml-2 inline-block text-[10px] font-normal bg-primary/20 text-primary px-1.5 py-0.5 rounded-full">
                                                                            Hiện tại
                                                                        </span>
                                                                    )}
                                                                </p>
                                                                <p className={`text-xs mt-0.5 leading-relaxed ${isPending && !stepRejected ? "text-neutral-800" : "text-neutral-500"
                                                                    }`}>
                                                                    {step.description}
                                                                </p>
                                                                {isCurrent && (
                                                                    <p className="text-[10px] text-neutral-600 mt-1">
                                                                        Cập nhật: {formatDate(statusItem.ngay_nop || statusItem.updated_at)}
                                                                    </p>
                                                                )}
                                                            </div>
                                                        </div>
                                                    )
                                                })}
                                            </div>

                                            {/* Final state message */}
                                            {isRejected && (
                                                <div className="mt-4 bg-red-500/10 border border-red-500/30 rounded-lg px-4 py-3">
                                                    <p className="text-sm text-red-300 font-medium">Hồ sơ không đạt yêu cầu</p>
                                                    <p className="text-xs text-red-400/70 mt-1">
                                                        Cảm ơn bạn đã quan tâm và ứng tuyển. Chúng tôi sẽ lưu ý hồ sơ cho các đợt tuyển dụng tiếp theo.
                                                    </p>
                                                </div>
                                            )}
                                            {statusItem.trang_thai === "da_nhan" && (
                                                <div className="mt-4 bg-green-500/10 border border-green-500/30 rounded-lg px-4 py-3">
                                                    <div className="flex items-center space-x-2">
                                                        <CheckCircle2 className="h-4 w-4 text-green-400 flex-shrink-0" />
                                                        <p className="text-sm text-green-300 font-medium">Chúc mừng! Hồ sơ đã vượt qua vòng sàng lọc.</p>
                                                    </div>
                                                    <p className="text-xs text-green-400/70 mt-1 pl-6">
                                                        Kết quả xếp hạng AHP sẽ được thông báo sớm qua email của bạn. Điểm AI tự đánh giá nội bộ: {(statusItem.diem_ahp || 0).toFixed(4)}
                                                    </p>
                                                </div>
                                            )}
                                        </CardContent>
                                    </Card>
                                )
                            })}
                        </div>
                    )}

                    {/* No result yet */}
                    {statuses.length === 0 && !loading && (
                        <div className="text-center py-8 text-neutral-600 text-sm space-y-3">
                            <p>Vừa nộp CV? <Link href="/candidate/apply" className="text-primary underline">Nộp hồ sơ ngay</Link></p>
                            <div className="flex items-center justify-center text-neutral-700 text-xs space-x-1">
                                <ArrowRight className="h-3 w-3" />
                                <span>Bạn có thể kiểm tra danh sách kết quả ngay sau khi nộp</span>
                            </div>
                        </div>
                    )}
                </div>
            </div>
    )
}
