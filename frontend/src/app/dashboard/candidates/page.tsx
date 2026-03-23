"use client"

import * as React from "react"
import {
    Megaphone, Briefcase, Users, Download, FileText,
    ChevronRight, Loader2, Search, ArrowUpDown, AlertCircle, Archive
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import axios from "@/lib/axios"
import PdfViewer from "@/components/PdfViewer"

// ─── Types ───
interface AHPCandidate {
    don_id: string
    candidate_name: string
    candidate_id: string
    ahp_score: number
    rank: number
    scores: Record<string, number>
}

interface AHPResult {
    top_10: AHPCandidate[]
    reserve_20: AHPCandidate[]
    total_ranked: number
    weights: Record<string, number>
}

interface ArchiveRecord {
    id: string
    ho_ten: string
    email: string
    so_dien_thoai?: string
    hang: number
    diem_ahp: number
    nhom: string
    diem_chi_tiet?: Record<string, number>
    ten_cong_viec?: string
    ten_chien_dich?: string
    ngay_luu: string
}

export default function CandidatesPage() {
    // ── State ──
    const [campaigns, setCampaigns] = React.useState<any[]>([])
    const [jobs, setJobs] = React.useState<any[]>([])
    const [selectedCampaign, setSelectedCampaign] = React.useState("")
    const [selectedJob, setSelectedJob] = React.useState("")
    const [loadingCampaigns, setLoadingCampaigns] = React.useState(true)
    const [loadingJobs, setLoadingJobs] = React.useState(false)
    const [loadingRank, setLoadingRank] = React.useState(false)
    const [exporting, setExporting] = React.useState(false)

    // ── AHP Data (live) ──
    const [ahpResult, setAhpResult] = React.useState<AHPResult | null>(null)
    const [rankError, setRankError] = React.useState("")

    // ── Archive Data (closed campaigns) ──
    const [archiveData, setArchiveData] = React.useState<ArchiveRecord[]>([])
    const [isArchiveMode, setIsArchiveMode] = React.useState(false)

    // ── UI State ──
    const [filter, setFilter] = React.useState<"all" | "top10" | "reserve">("all")
    const [sortCol, setSortCol] = React.useState<"rank" | "ahp_score">("rank")
    const [sortDir, setSortDir] = React.useState<"asc" | "desc">("asc")
    const [searchQuery, setSearchQuery] = React.useState("")
    const [pdfInfo, setPdfInfo] = React.useState<{url: string, name: string} | null>(null)

    // ── Step indicator ──
    const currentStep = !selectedCampaign ? 0 : !selectedJob ? 1 : 2

    React.useEffect(() => {
        const fetchCampaigns = async () => {
            setLoadingCampaigns(true)
            try {
                const res = await axios.get("/api/campaigns/my")
                setCampaigns(res.data)
            } catch (err) {
                console.error("Failed to fetch campaigns", err)
            }
            setLoadingCampaigns(false)
        }
        fetchCampaigns()
    }, [])

    // ────────────── FETCH JOBS ──────────────
    React.useEffect(() => {
        if (!selectedCampaign) {
            setJobs([])
            setSelectedJob("")
            setAhpResult(null)
            setArchiveData([])
            setIsArchiveMode(false)
            setRankError("")
            return
        }

        const campaign = campaigns.find(c => c.id === selectedCampaign)
        const isClosed = campaign?.trang_thai === "da_dong"

        const fetchJobs = async () => {
            setLoadingJobs(true)
            setSelectedJob("")
            setAhpResult(null)
            setArchiveData([])
            setRankError("")
            setIsArchiveMode(isClosed)

            try {
                const res = await axios.get(`/api/jobs/my?campaign_id=${selectedCampaign}`)
                setJobs(res.data)
            } catch (err) {
                console.error("Failed to fetch jobs", err)
            }
            setLoadingJobs(false)
        }
        fetchJobs()
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [selectedCampaign])

    // ────────────── FETCH RANKING (live or archive) ──────────────
    React.useEffect(() => {
        if (!selectedJob || !selectedCampaign) {
            setAhpResult(null)
            setArchiveData([])
            setRankError("")
            return
        }

        if (isArchiveMode) {
            // Campaign đã đóng → đọc archive
            const fetchArchive = async () => {
                setLoadingRank(true)
                setRankError("")
                try {
                    const res = await axios.get(`/api/campaigns/${selectedCampaign}/archive?job_id=${selectedJob}`)
                    setArchiveData(res.data)
                    if (res.data.length === 0) {
                        setRankError("Không có dữ liệu xếp hạng đã lưu trữ cho vị trí này.")
                    }
                } catch (err: any) {
                    setRankError(err.response?.data?.detail || "Lỗi khi tải dữ liệu lưu trữ.")
                }
                setLoadingRank(false)
            }
            fetchArchive()
        } else {
            // Campaign đang mở → chạy AHP live
            const fetchRank = async () => {
                setLoadingRank(true)
                setRankError("")
                try {
                    const res = await axios.post("/api/ai/ahp/rank", { job_id: selectedJob })
                    setAhpResult(res.data)
                } catch (err: any) {
                    setRankError(err.response?.data?.detail || "Lỗi khi lấy dữ liệu xếp hạng.")
                }
                setLoadingRank(false)
            }
            fetchRank()
        }
    }, [selectedJob, selectedCampaign, isArchiveMode])

    // ────────────── COMPUTED DATA ──────────────
    // Convert both live AHP + archive into a unified display format
    const candidatesWithStatus = React.useMemo(() => {
        if (isArchiveMode) {
            return archiveData.map(a => ({
                candidate_name: a.ho_ten,
                candidate_id: "",
                don_id: a.id,
                ahp_score: a.diem_ahp,
                rank: a.hang,
                scores: a.diem_chi_tiet || {},
                status: a.nhom === "top10" ? "top10" as const : "reserve" as const,
                email: a.email,
            }))
        }
        if (!ahpResult) return []
        return [
            ...ahpResult.top_10.map(c => ({ ...c, status: "top10" as const })),
            ...ahpResult.reserve_20.map(c => ({ ...c, status: "reserve" as const })),
        ]
    }, [ahpResult, archiveData, isArchiveMode])

    const filteredAndSorted = React.useMemo(() => {
        let list = candidatesWithStatus
        if (filter === "top10") list = list.filter(c => c.status === "top10")
        if (filter === "reserve") list = list.filter(c => c.status === "reserve")
        if (searchQuery) {
            const q = searchQuery.toLowerCase()
            list = list.filter(c => c.candidate_name.toLowerCase().includes(q))
        }
        return [...list].sort((a, b) => {
            const av = a[sortCol]
            const bv = b[sortCol]
            if (typeof av === "number" && typeof bv === "number") {
                return sortDir === "asc" ? av - bv : bv - av
            }
            return 0
        })
    }, [candidatesWithStatus, sortCol, sortDir, filter, searchQuery])

    // ────────────── EXPORT EXCEL ──────────────
    const handleExport = async () => {
        if (!selectedJob) {
            alert("Vui lòng chọn vị trí tuyển dụng trước khi xuất báo cáo.")
            return
        }
        if (candidatesWithStatus.length === 0) {
            alert("Không có dữ liệu xếp hạng để xuất.")
            return
        }

        setExporting(true)

        try {
            const token = localStorage.getItem("token")
            const res = await fetch(`http://localhost:8000/api/cv/export/${selectedJob}`, {
                headers: { "Authorization": `Bearer ${token}` }
            })
            if (!res.ok) {
                const errText = await res.text()
                throw new Error(`Export failed: ${res.status} — ${errText}`)
            }
            const blob = await res.blob()
            const url = window.URL.createObjectURL(blob)
            const a = document.createElement('a')
            a.href = url
            const campaignName = campaigns.find(c => c.id === selectedCampaign)?.tieu_de || "export"
            const jobName = jobs.find(j => j.id === selectedJob)?.tieu_de || "job"
            a.download = `Xep_Hang_${campaignName}_${jobName}_${new Date().toISOString().slice(0, 10)}.xlsx`
            document.body.appendChild(a)
            a.click()
            a.remove()
            window.URL.revokeObjectURL(url)
        } catch (err) {
            console.error("[Export] Error:", err)
            alert("Không thể xuất báo cáo. " + (err instanceof Error ? err.message : ""))
        } finally {
            setExporting(false)
        }
    }

    // ────────────── TOGGLE SORT ──────────────
    const toggleSort = (col: "rank" | "ahp_score") => {
        if (sortCol === col) {
            setSortDir(prev => prev === "asc" ? "desc" : "asc")
        } else {
            setSortCol(col)
            setSortDir(col === "rank" ? "asc" : "desc")
        }
    }

    // ────────────── RENDER ──────────────
    return (
        <div className="space-y-6 max-w-6xl mx-auto">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold text-white">Bảng xếp hạng ứng viên</h2>
                    <p className="text-sm text-neutral-400 mt-1">Chọn đợt tuyển dụng và vị trí để xem bảng xếp hạng AHP</p>
                </div>
                <Button
                    variant="outline"
                    className="border-neutral-700 hover:bg-neutral-800"
                    onClick={handleExport}
                    disabled={exporting || candidatesWithStatus.length === 0}
                >
                    {exporting ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <Download className="h-4 w-4 mr-2" />}
                    Xuất Excel
                </Button>
            </div>

            {/* Step Indicator */}
            <div className="flex items-center gap-2 text-sm">
                {[
                    { icon: Megaphone, label: "Chọn đợt tuyển dụng" },
                    { icon: Briefcase, label: "Chọn vị trí" },
                    { icon: Users, label: "Xem xếp hạng" },
                ].map((step, i) => (
                    <React.Fragment key={i}>
                        {i > 0 && <ChevronRight className="h-4 w-4 text-neutral-700" />}
                        <div className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full transition-colors ${i <= currentStep
                            ? "bg-primary/10 text-primary"
                            : "text-neutral-600"
                            }`}>
                            <step.icon className="h-4 w-4" />
                            <span className="hidden sm:inline">{step.label}</span>
                        </div>
                    </React.Fragment>
                ))}
            </div>

            {/* Selection Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Campaign Selector */}
                <Card className="bg-neutral-900 border-neutral-800">
                    <CardContent className="p-5">
                        <div className="flex items-center gap-2 mb-3 text-sm font-semibold text-neutral-300 uppercase tracking-wider">
                            <Megaphone className="h-4 w-4" /> ĐỢT TUYỂN DỤNG
                        </div>
                        <select
                            className="w-full h-10 bg-neutral-800 border border-neutral-700 rounded-md px-3 text-sm text-white focus:outline-none focus:ring-1 focus:ring-primary"
                            value={selectedCampaign}
                            onChange={e => setSelectedCampaign(e.target.value)}
                            disabled={loadingCampaigns}
                        >
                            <option value="">— Chọn đợt tuyển dụng —</option>
                            {campaigns.map(c => (
                                <option key={c.id} value={c.id}>
                                    {c.tieu_de} {c.trang_thai === "da_dong" ? " [Đã đóng]" : ""}
                                </option>
                            ))}
                        </select>
                        {loadingCampaigns && <p className="text-xs text-neutral-500 mt-2">Đang tải...</p>}
                        {!loadingCampaigns && campaigns.length === 0 && (
                            <p className="text-xs text-neutral-500 mt-2">Chưa có đợt tuyển dụng nào.</p>
                        )}
                        {isArchiveMode && (
                            <div className="flex items-center gap-1.5 mt-2 text-xs text-orange-400 bg-orange-400/10 px-2 py-1.5 rounded-md">
                                <Archive className="h-3.5 w-3.5" />
                                Đợt đã đóng — hiển thị dữ liệu lưu trữ
                            </div>
                        )}
                    </CardContent>
                </Card>

                {/* Job Selector */}
                <Card className={`bg-neutral-900 border-neutral-800 transition-opacity ${!selectedCampaign ? "opacity-50" : ""}`}>
                    <CardContent className="p-5">
                        <div className="flex items-center gap-2 mb-3 text-sm font-semibold text-neutral-300 uppercase tracking-wider">
                            <Briefcase className="h-4 w-4" /> VỊ TRÍ TUYỂN DỤNG
                        </div>
                        <select
                            className="w-full h-10 bg-neutral-800 border border-neutral-700 rounded-md px-3 text-sm text-white focus:outline-none focus:ring-1 focus:ring-primary disabled:opacity-50"
                            value={selectedJob}
                            onChange={e => setSelectedJob(e.target.value)}
                            disabled={!selectedCampaign || loadingJobs}
                        >
                            <option value="">— Chọn vị trí —</option>
                            {jobs.map(j => (
                                <option key={j.id} value={j.id}>{j.tieu_de}</option>
                            ))}
                        </select>
                        {loadingJobs && <p className="text-xs text-neutral-500 mt-2">Đang tải vị trí...</p>}
                        {!loadingJobs && selectedCampaign && jobs.length === 0 && (
                            <p className="text-xs text-neutral-500 mt-2">Chưa có vị trí nào trong đợt này.</p>
                        )}
                    </CardContent>
                </Card>
            </div>

            {/* Results Area */}
            <Card className="bg-neutral-900 border-neutral-800 overflow-hidden">
                <CardContent className="p-0">
                    {loadingRank ? (
                        <div className="flex flex-col items-center justify-center py-20 gap-3">
                            <Loader2 className="h-8 w-8 text-primary animate-spin" />
                            <p className="text-sm text-neutral-400">
                                {isArchiveMode ? "Đang tải dữ liệu lưu trữ..." : "Đang chạy AHP xếp hạng..."}
                            </p>
                        </div>
                    ) : rankError ? (
                        <div className="flex flex-col items-center justify-center py-20 gap-3 text-center px-4">
                            <AlertCircle className="h-10 w-10 text-orange-500/60" />
                            <p className="text-sm text-neutral-400 max-w-md">{rankError}</p>
                        </div>
                    ) : candidatesWithStatus.length === 0 ? (
                        <div className="flex flex-col items-center justify-center py-20 gap-3">
                            <Users className="h-10 w-10 text-neutral-700" />
                            <p className="text-sm text-neutral-500">
                                {!selectedCampaign
                                    ? "Vui lòng chọn đợt tuyển dụng để bắt đầu"
                                    : !selectedJob
                                        ? "Vui lòng chọn vị trí tuyển dụng để xem bảng xếp hạng"
                                        : "Chưa có ứng viên"}
                            </p>
                        </div>
                    ) : (
                        <>
                            {/* Toolbar */}
                            <div className="flex flex-wrap items-center gap-3 p-4 border-b border-neutral-800">
                                {/* Search */}
                                <div className="relative flex-1 min-w-[200px]">
                                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-neutral-500" />
                                    <input
                                        className="w-full h-9 bg-neutral-800 border border-neutral-700 rounded-md pl-9 pr-3 text-sm text-white placeholder:text-neutral-500 focus:outline-none focus:ring-1 focus:ring-primary"
                                        placeholder="Tìm ứng viên..."
                                        value={searchQuery}
                                        onChange={e => setSearchQuery(e.target.value)}
                                    />
                                </div>

                                {/* Filter */}
                                <div className="flex gap-1">
                                    {(["all", "top10", "reserve"] as const).map(f => (
                                        <button
                                            key={f}
                                            onClick={() => setFilter(f)}
                                            className={`px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${filter === f
                                                ? "bg-primary text-black"
                                                : "bg-neutral-800 text-neutral-400 hover:bg-neutral-700"
                                                }`}
                                        >
                                            {f === "all" ? "Tất cả" : f === "top10" ? "Top 10" : "Dự bị"}
                                        </button>
                                    ))}
                                </div>

                                <span className="text-xs text-neutral-500">
                                    {filteredAndSorted.length} ứng viên
                                </span>
                            </div>

                            {/* Table */}
                            <div className="overflow-x-auto">
                                <table className="w-full text-sm">
                                    <thead>
                                        <tr className="border-b border-neutral-800 text-xs text-neutral-500 uppercase tracking-wider">
                                            <th className="px-4 py-3 text-left cursor-pointer select-none hover:text-white transition-colors" onClick={() => toggleSort("rank")}>
                                                <div className="flex items-center gap-1">Hạng <ArrowUpDown className="h-3 w-3" /></div>
                                            </th>
                                            <th className="px-4 py-3 text-left">Họ tên</th>
                                            <th className="px-4 py-3 text-center cursor-pointer select-none hover:text-white transition-colors" onClick={() => toggleSort("ahp_score")}>
                                                <div className="flex items-center gap-1 justify-center">Điểm AHP <ArrowUpDown className="h-3 w-3" /></div>
                                            </th>
                                            <th className="px-4 py-3 text-center">Kỹ thuật</th>
                                            <th className="px-4 py-3 text-center">Học vấn</th>
                                            <th className="px-4 py-3 text-center">Ngoại ngữ</th>
                                            <th className="px-4 py-3 text-center">Tích cực</th>
                                            <th className="px-4 py-3 text-center">Nhóm</th>
                                            {!isArchiveMode && <th className="px-4 py-3 text-center">CV</th>}
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {filteredAndSorted.map((candidate, idx) => (
                                            <tr
                                                key={candidate.don_id || idx}
                                                className="border-b border-neutral-800/50 hover:bg-neutral-800/30 transition-colors"
                                            >
                                                <td className="px-4 py-3 text-center">
                                                    <span className={`inline-flex h-7 w-7 items-center justify-center rounded-full text-xs font-bold ${candidate.rank <= 3
                                                        ? "bg-primary/20 text-primary"
                                                        : candidate.rank <= 10
                                                            ? "bg-blue-500/10 text-blue-400"
                                                            : "bg-neutral-800 text-neutral-400"
                                                        }`}>
                                                        {candidate.rank}
                                                    </span>
                                                </td>
                                                <td className="px-4 py-3 text-white font-medium">{candidate.candidate_name}</td>
                                                <td className="px-4 py-3 text-center">
                                                    <span className="text-primary font-semibold">{candidate.ahp_score.toFixed(4)}</span>
                                                </td>
                                                <td className="px-4 py-3 text-center text-neutral-400">{(candidate.scores.ky_thuat ?? 0).toFixed(1)}</td>
                                                <td className="px-4 py-3 text-center text-neutral-400">{(candidate.scores.hoc_van ?? 0).toFixed(1)}</td>
                                                <td className="px-4 py-3 text-center text-neutral-400">{(candidate.scores.ngoai_ngu ?? 0).toFixed(1)}</td>
                                                <td className="px-4 py-3 text-center text-neutral-400">{(candidate.scores.tich_cuc ?? 0).toFixed(1)}</td>
                                                <td className="px-4 py-3 text-center">
                                                    <span className={`text-xs px-2 py-1 rounded-md font-medium ${candidate.status === "top10"
                                                        ? "bg-green-500/15 text-green-400"
                                                        : "bg-neutral-800 text-neutral-500"
                                                        }`}>
                                                        {candidate.status === "top10" ? "Top 10" : "Dự bị"}
                                                    </span>
                                                </td>
                                                {!isArchiveMode && (
                                                    <td className="px-4 py-3 text-center">
                                                        <button
                                                            className="text-neutral-500 hover:text-primary transition-colors"
                                                            onClick={() => setPdfInfo({
                                                                url: `http://localhost:8000/api/cv/view/${candidate.don_id}`,
                                                                name: candidate.candidate_name
                                                            })}
                                                            title="Xem CV"
                                                        >
                                                            <FileText className="h-4 w-4" />
                                                        </button>
                                                    </td>
                                                )}
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </>
                    )}
                </CardContent>
            </Card>

            {/* PDF Viewer */}
            {pdfInfo && !isArchiveMode && (
                <PdfViewer 
                    url={pdfInfo.url} 
                    candidateName={pdfInfo.name} 
                    onClose={() => setPdfInfo(null)} 
                />
            )}
        </div>
    )
}
