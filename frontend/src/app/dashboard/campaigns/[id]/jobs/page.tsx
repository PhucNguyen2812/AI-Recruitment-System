"use client"

import * as React from "react"
import { useParams, useRouter } from "next/navigation"
import { Plus, Trash2, Settings, Loader2, Brain, AlertTriangle, CheckCircle2, ChevronLeft, Info, Save, TrendingUp, Star } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import axios from "@/lib/axios"

// ─── AHP HELPERS ─────────────────────────────────────────────────────────────
const CRITERIA_KEYS = ["ky_thuat", "hoc_van", "ngoai_ngu", "tich_cuc"]
const CRITERIA_LABELS = ["Kỹ thuật", "Học vấn", "Ngoại ngữ", "Tích cực"]

function getPairs(): [number, number][] {
    const pairs: [number, number][] = []
    for (let i = 0; i < CRITERIA_KEYS.length; i++)
        for (let j = i + 1; j < CRITERIA_KEYS.length; j++)
            pairs.push([i, j])
    return pairs
}
const PAIRS = getPairs()

function sliderToRatio(val: number): number {
    if (val === 0) return 1
    if (val > 0) return val + 1
    return 1 / (Math.abs(val) + 1)
}

function buildMatrix(sliderValues: number[]): number[][] {
    const n = CRITERIA_KEYS.length
    const matrix = Array.from({ length: n }, () => Array(n).fill(1))
    PAIRS.forEach(([i, j], idx) => {
        const ratio = sliderToRatio(sliderValues[idx])
        matrix[i][j] = ratio
        matrix[j][i] = 1 / ratio
    })
    return matrix
}

function ratioToSlider(ratio: number): number {
    if (Math.abs(ratio - 1) < 0.001) return 0
    if (ratio > 1) return Math.round(ratio - 1)
    return -Math.round(1 / ratio - 1)
}

function matrixToSliders(savedMatrix: number[][]): number[] {
    return PAIRS.map(([i, j]) => ratioToSlider(savedMatrix[i][j]))
}

function calcCRandWeights(matrix: number[][]): { cr: number; weights: number[] } {
    const n = matrix.length
    const colSums = Array(n).fill(0)
    for (let j = 0; j < n; j++) for (let i = 0; i < n; i++) colSums[j] += matrix[i][j]
    const weights = Array(n).fill(0)
    for (let i = 0; i < n; i++) {
        let rowSum = 0
        for (let j = 0; j < n; j++) rowSum += matrix[i][j] / colSums[j]
        weights[i] = rowSum / n
    }
    let lambdaMax = 0
    for (let i = 0; i < n; i++) {
        let rowDot = 0
        for (let j = 0; j < n; j++) rowDot += matrix[i][j] * weights[j]
        lambdaMax += rowDot / weights[i]
    }
    lambdaMax /= n
    const CI = (lambdaMax - n) / (n - 1)
    const RI_TABLE: Record<number, number> = { 1: 0, 2: 0, 3: 0.58, 4: 0.9, 5: 1.12, 6: 1.24 }
    const RI = RI_TABLE[n] ?? 1
    const cr = RI === 0 ? 0 : CI / RI
    return { cr, weights }
}


// ─── TYPES ────────────────────────────────────────────────────────────────────
type Job = {
    id: string
    tieu_de: string
    trang_thai: string
    ahp_weights?: {
        weights: Record<string, number>
        matrix: number[][]
    } | null
}

type CandidateRankItem = {
    don_id: string
    candidate_name: string
    rank: number
    ahp_score: number
    scores: Record<string, number>
}

// ─── PAGE ─────────────────────────────────────────────────────────────────────
export default function JobsPage() {
    const { id: campaignId } = useParams()
    const router = useRouter()

    const [jobs, setJobs] = React.useState<Job[]>([])
    const [positions, setPositions] = React.useState<any[]>([])
    const [loading, setLoading] = React.useState(true)

    // Create form
    const [showCreate, setShowCreate] = React.useState(false)
    const [tieuDe, setTieuDe] = React.useState("")
    const [idViTri, setIdViTri] = React.useState("")
    const [moTa, setMoTa] = React.useState("")
    const [yeuCau, setYeuCau] = React.useState("")

    // Selected job + active tab
    const [selectedJobId, setSelectedJobId] = React.useState<string | null>(null)
    const [activeTab, setActiveTab] = React.useState<"config" | "ranking">("config")

    // AHP Config State
    const [sliderValues, setSliderValues] = React.useState<number[]>(Array(PAIRS.length).fill(0))
    const [configLoading, setConfigLoading] = React.useState(false)
    const [configResult, setConfigResult] = React.useState<string | null>(null)
    const [configError, setConfigError] = React.useState<string | null>(null)

    // Ranking State
    const [rankLoading, setRankLoading] = React.useState(false)
    const [rankResult, setRankResult] = React.useState<{
        top_10: CandidateRankItem[]
        reserve_20: CandidateRankItem[]
        total_ranked: number
        weights: Record<string, number>
    } | null>(null)
    const [rankError, setRankError] = React.useState<string | null>(null)

    React.useEffect(() => {
        fetchJobsAndPositions()
    }, [campaignId])

    const fetchJobsAndPositions = async () => {
        setLoading(true)
        try {
            const token = localStorage.getItem("token")
            const [jobsRes, posRes] = await Promise.all([
                axios.get(`/api/jobs/my?campaign_id=${campaignId}`, { headers: { Authorization: `Bearer ${token}` } }),
                axios.get(`/api/positions/`, { headers: { Authorization: `Bearer ${token}` } }),
            ])
            setJobs(jobsRes.data)
            setPositions(posRes.data)
        } catch (error) {
            console.error("Failed to fetch data", error)
        } finally {
            setLoading(false)
        }
    }

    const handleCreateJob = async () => {
        if (!tieuDe || !idViTri) return alert("Vui lòng nhập Tên tin và chọn Vị trí!")
        try {
            const token = localStorage.getItem("token")
            await axios.post("/api/jobs/", {
                tieu_de: tieuDe, id_vi_tri: idViTri, campaign_id: campaignId,
                mo_ta: moTa, yeu_cau: yeuCau, trang_thai: "dang_mo",
            }, { headers: { Authorization: `Bearer ${token}` } })
            setShowCreate(false); setTieuDe(""); setIdViTri(""); setMoTa(""); setYeuCau("")
            fetchJobsAndPositions()
        } catch (err: any) {
            alert(err.response?.data?.detail || "Đã xảy ra lỗi!")
        }
    }

    const handleDeleteJob = async (id: string) => {
        if (!window.confirm("Xóa job này và toàn bộ hồ sơ?")) return
        try {
            await axios.delete(`/api/jobs/${id}`, { headers: { Authorization: `Bearer ${localStorage.getItem("token")}` } })
            fetchJobsAndPositions()
            if (selectedJobId === id) setSelectedJobId(null)
        } catch {
            alert("Lỗi khi xóa job.")
        }
    }

    const selectJob = (job: Job) => {
        if (selectedJobId === job.id) { setSelectedJobId(null); return }
        setSelectedJobId(job.id)
        setActiveTab("config")
        setConfigResult(null); setConfigError(null)
        setRankResult(null); setRankError(null)
        // Khôi phục thanh trượt từ ma trận đã lưu
        if (job.ahp_weights?.matrix) {
            setSliderValues(matrixToSliders(job.ahp_weights.matrix))
        } else {
            setSliderValues(Array(PAIRS.length).fill(0))
        }
    }

    // ── AHP Config: Live calculation ──────────────────────────────────────────
    const matrix = buildMatrix(sliderValues)
    const { cr, weights } = calcCRandWeights(matrix)
    const crValid = cr <= 0.1

    const handleSaveConfig = async () => {
        if (!selectedJobId || !crValid) return
        setConfigLoading(true); setConfigResult(null); setConfigError(null)
        try {
            const token = localStorage.getItem("token")
            const res = await axios.post("/api/ai/ahp/config", {
                job_id: selectedJobId,
                matrix: matrix,
            }, { headers: { Authorization: `Bearer ${token}` } })
            setConfigResult(`✓ Đã lưu cấu hình AHP! CR = ${res.data.consistency?.cr?.toFixed(4) ?? cr.toFixed(4)}`)
            fetchJobsAndPositions() // refresh to show ahp_weights set
        } catch (err: any) {
            setConfigError(err.response?.data?.detail || err.message)
        } finally {
            setConfigLoading(false)
        }
    }

    // ── Ranking ────────────────────────────────────────────────────────────────
    const handleRunRank = async () => {
        if (!selectedJobId) return
        setRankLoading(true); setRankResult(null); setRankError(null)
        try {
            const token = localStorage.getItem("token")
            const res = await axios.post("/api/ai/ahp/rank", {
                job_id: selectedJobId,
            }, { headers: { Authorization: `Bearer ${token}` } })
            setRankResult(res.data)
        } catch (err: any) {
            setRankError(err.response?.data?.detail || err.message)
        } finally {
            setRankLoading(false)
        }
    }

    // ── Helper: tính Sum cột cho ma trận tiêu chí ───────────────────────────
    const colSums = React.useMemo(() => {
        const n = CRITERIA_KEYS.length
        const sums = Array(n).fill(0)
        for (let j = 0; j < n; j++)
            for (let i = 0; i < n; i++)
                sums[j] += matrix[i][j]
        return sums
    }, [matrix])

    // ── Helper: normalized matrix & weights (chuẩn hóa) ──────────────────────
    const normalizedMatrix = React.useMemo(() => {
        const n = CRITERIA_KEYS.length
        return matrix.map(row => row.map((val: number, j: number) => colSums[j] === 0 ? 0 : val / colSums[j]))
    }, [matrix, colSums])

    // ── Helper: top candidates cho ma trận phương án ──────────────────────────
    const topCandidates = rankResult?.top_10?.slice(0, 5) ?? []

    // Build pairwise alternatives matrix for a given criterion key
    const buildAltMatrix = (criterionKey: string) => {
        const n = topCandidates.length
        if (n === 0) return []
        const mat: number[][] = []
        for (let i = 0; i < n; i++) {
            const row: number[] = []
            for (let j = 0; j < n; j++) {
                const si = topCandidates[i].scores[criterionKey] || 0.01
                const sj = topCandidates[j].scores[criterionKey] || 0.01
                row.push(si / sj)
            }
            mat.push(row)
        }
        return mat
    }

    // Tên ngắn cho ứng viên trong bảng phương án
    const candidateShortNames = topCandidates.map(c => {
        const parts = c.candidate_name.split(" ")
        return parts.length > 1 ? parts[parts.length - 1] : parts[0]
    })

    // Màu ô: đường chéo = cam, header = xanh primary
    const cellBg = (i: number, j: number) => i === j ? "bg-amber-500 text-black font-bold" : "bg-sky-600/80 text-white"
    const headerBg = "bg-sky-700 text-white font-semibold"

    const selectedJob = jobs.find(j => j.id === selectedJobId)

    return (
        <div className="space-y-6 max-w-5xl mx-auto">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <Button variant="outline" size="icon" onClick={() => router.push("/dashboard/campaigns")}
                        className="h-9 w-9 bg-neutral-900 border-neutral-800">
                        <ChevronLeft className="h-4 w-4" />
                    </Button>
                    <div>
                        <h2 className="text-2xl font-bold text-white">Vị trí tuyển dụng trong đợt</h2>
                        <p className="text-sm text-neutral-400 mt-1">Quản lý Job, cấu hình AHP và xếp hạng ứng viên.</p>
                    </div>
                </div>
                <Button onClick={() => setShowCreate(!showCreate)} className="bg-primary text-black hover:bg-primary/90">
                    <Plus className="h-4 w-4 mr-2" />Thêm Job
                </Button>
            </div>

            {/* Create form */}
            {showCreate && (
                <Card className="bg-neutral-900 border-neutral-800 shadow-xl">
                    <CardHeader className="border-b border-neutral-800 pb-4">
                        <CardTitle className="text-lg text-white">Thêm tin tuyển dụng mới</CardTitle>
                    </CardHeader>
                    <CardContent className="pt-4 space-y-4">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <label className="text-xs text-neutral-400 font-medium">Tên tin tuyển dụng *</label>
                                <Input value={tieuDe} onChange={e => setTieuDe(e.target.value)}
                                    placeholder="Vd: Tuyển thực tập sinh ReactJS"
                                    className="border-neutral-700 bg-neutral-800 text-white" />
                            </div>
                            <div className="space-y-2">
                                <label className="text-xs text-neutral-400 font-medium">Vị trí *</label>
                                <select className="w-full h-10 border border-neutral-700 bg-neutral-800 px-3 py-2 rounded-md text-sm text-white focus:outline-none"
                                    value={idViTri} onChange={e => setIdViTri(e.target.value)}>
                                    <option value="" disabled>-- Chọn Vị trí --</option>
                                    {positions.map(p => <option key={p.id} value={p.id}>{p.ten} ({p.ma})</option>)}
                                </select>
                            </div>
                            <div className="space-y-2 md:col-span-2">
                                <label className="text-xs text-neutral-400 font-medium">Mô tả chi tiết</label>
                                <Input value={moTa} onChange={e => setMoTa(e.target.value)}
                                    placeholder="Vd: Tham gia dự án lớn với khách hàng Nhật Bản..."
                                    className="border-neutral-700 bg-neutral-800 text-white" />
                            </div>
                            <div className="space-y-2 md:col-span-2">
                                <label className="text-xs text-neutral-400 font-medium">Yêu cầu</label>
                                <Input value={yeuCau} onChange={e => setYeuCau(e.target.value)}
                                    placeholder="Vd: Biết ReactJS, TypeScript..."
                                    className="border-neutral-700 bg-neutral-800 text-white" />
                            </div>
                        </div>
                        <div className="flex justify-end pt-2">
                            <Button onClick={handleCreateJob}>Lưu Tin Tuyển Dụng</Button>
                        </div>
                    </CardContent>
                </Card>
            )}

            {/* Job list */}
            {loading ? (
                <div className="text-center text-neutral-500 py-10">Đang tải...</div>
            ) : jobs.length === 0 ? (
                <div className="text-center text-neutral-500 py-10 border border-dashed border-neutral-800 rounded-lg">
                    Đợt này chưa có tin tuyển dụng nào.
                </div>
            ) : (
                <div className="grid grid-cols-1 gap-4">
                    {jobs.map(job => (
                        <Card key={job.id}
                            className={`bg-neutral-900 border-neutral-800 transition-colors ${selectedJobId === job.id ? "ring-1 ring-primary border-primary/50" : ""}`}>
                            {/* Job row */}
                            <div className="p-4 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                                <div>
                                    <h3 className="text-lg font-bold text-white">{job.tieu_de}</h3>
                                    <div className="flex items-center gap-3 mt-1">
                                        <span className="text-sm text-neutral-400">
                                            {job.trang_thai === "dang_mo" ? "Đang nhận CV" : "Đã đóng"}
                                        </span>
                                        {job.ahp_weights && (
                                            <span className="text-xs text-green-400 bg-green-400/10 px-2 py-0.5 rounded-full flex items-center gap-1">
                                                <CheckCircle2 className="h-3 w-3" /> AHP đã cấu hình
                                            </span>
                                        )}
                                    </div>
                                </div>
                                <div className="flex items-center gap-3">
                                    <Button variant="outline" onClick={() => selectJob(job)}
                                        className={`h-9 text-xs border-primary/20 hover:bg-primary/10 transition-colors ${selectedJobId === job.id ? "bg-primary/20 text-primary hover:bg-primary/30" : "text-neutral-300"}`}>
                                        <Settings className="h-4 w-4 mr-2" />Quản lý AHP
                                    </Button>
                                    <Button variant="outline"
                                        className="h-9 w-9 p-0 border-red-900/40 text-red-500 hover:bg-red-500/10 hover:text-red-400"
                                        onClick={() => handleDeleteJob(job.id)}>
                                        <Trash2 className="h-4 w-4" />
                                    </Button>
                                </div>
                            </div>

                            {/* Expanded panel */}
                            {selectedJobId === job.id && (
                                <div className="border-t border-neutral-800 bg-neutral-950/40">
                                    {/* Tabs */}
                                    <div className="flex border-b border-neutral-800">
                                        {[
                                            { key: "config", icon: <Settings className="h-3.5 w-3.5" />, label: "Cấu hình AHP" },
                                            { key: "ranking", icon: <TrendingUp className="h-3.5 w-3.5" />, label: "Xếp hạng & Phân tích" },
                                        ].map(tab => (
                                            <button key={tab.key}
                                                onClick={() => setActiveTab(tab.key as any)}
                                                className={`flex items-center gap-2 px-5 py-3 text-xs font-medium transition-colors border-b-2 -mb-px ${
                                                    activeTab === tab.key
                                                        ? "border-primary text-primary"
                                                        : "border-transparent text-neutral-500 hover:text-neutral-300"
                                                }`}>
                                                {tab.icon}{tab.label}
                                            </button>
                                        ))}
                                    </div>

                                    {/* ── TAB: AHP Config ─────────────────────────────────── */}
                                    {activeTab === "config" && (
                                        <div className="p-5">
                                            <div className="flex items-start gap-3 bg-neutral-900/60 border border-neutral-800 rounded-xl px-4 py-3 mb-5">
                                                <Info className="h-4 w-4 text-neutral-500 flex-shrink-0 mt-0.5" />
                                                <p className="text-xs text-neutral-400">
                                                    Điều chỉnh thanh trượt để so sánh tầm quan trọng giữa 2 tiêu chí. Sau khi lưu, cấu hình này sẽ áp dụng lâu dài cho <strong className="text-white">{selectedJob?.tieu_de}</strong>.
                                                </p>
                                            </div>

                                            <div className="flex flex-col lg:flex-row gap-6">
                                                {/* Sliders */}
                                                <div className="flex-1 space-y-4">
                                                    {/* CR badge */}
                                                    <div className="bg-neutral-900 border border-neutral-800 rounded-lg p-3">
                                                        <div className="flex items-center justify-between mb-2">
                                                            <div className="flex items-center gap-2">
                                                                {crValid
                                                                    ? <CheckCircle2 className="h-4 w-4 text-green-400" />
                                                                    : <AlertTriangle className="h-4 w-4 text-red-400" />}
                                                                <span className="text-sm font-medium text-white">
                                                                    Chỉ số nhất quán CR: {cr.toFixed(4)}
                                                                </span>
                                                            </div>
                                                            <span className={`text-xs px-2 py-0.5 rounded-full ${crValid ? "bg-green-400/10 text-green-400" : "bg-red-400/10 text-red-400"}`}>
                                                                {crValid ? "Hợp lệ (< 0.1)" : "Không hợp lệ"}
                                                            </span>
                                                        </div>
                                                        <div className="h-1.5 w-full bg-neutral-800 rounded-full overflow-hidden">
                                                            <div className={`h-full rounded-full transition-all ${crValid ? "bg-green-500" : "bg-red-500"}`}
                                                                style={{ width: `${Math.min(cr * 200, 100)}%` }} />
                                                        </div>
                                                    </div>

                                                    {PAIRS.map(([i, j], idx) => {
                                                        const val = sliderValues[idx]
                                                        return (
                                                            <div key={idx} className="space-y-1">
                                                                <div className="flex justify-between text-xs mb-1">
                                                                    <span className={val > 0 ? "text-white font-medium" : "text-neutral-500"}>{CRITERIA_LABELS[i]}</span>
                                                                    <span className={val < 0 ? "text-white font-medium" : "text-neutral-500"}>{CRITERIA_LABELS[j]}</span>
                                                                </div>
                                                                <input type="range" min={-8} max={8} step={1} value={val}
                                                                    onChange={(e) => {
                                                                        const next = [...sliderValues]
                                                                        next[idx] = Number(e.target.value)
                                                                        setSliderValues(next)
                                                                    }}
                                                                    className="w-full h-1.5 appearance-none bg-neutral-800 rounded-full accent-primary cursor-pointer" />
                                                            </div>
                                                        )
                                                    })}
                                                </div>

                                                {/* Weights preview + save */}
                                                <div className="w-full lg:w-64 space-y-4">
                                                    <div className="bg-neutral-900 border border-neutral-800 rounded-lg p-3">
                                                        <h5 className="text-xs font-semibold text-white mb-3">Trọng số hiện tại</h5>
                                                        <div className="space-y-2">
                                                            {CRITERIA_LABELS.map((c, i) => (
                                                                <div key={c} className="flex flex-col gap-1">
                                                                    <div className="flex justify-between text-[11px] text-neutral-400">
                                                                        <span>{c}</span>
                                                                        <span className="text-white font-mono">{(weights[i] * 100).toFixed(1)}%</span>
                                                                    </div>
                                                                    <div className="h-1 w-full bg-neutral-800 rounded-full overflow-hidden">
                                                                        <div className="h-full rounded-full transition-all"
                                                                            style={{ width: `${(weights[i] * 100).toFixed(1)}%`, backgroundColor: ["#22d3ee", "#a78bfa", "#34d399", "#fb923c"][i] }} />
                                                                    </div>
                                                                </div>
                                                            ))}
                                                        </div>
                                                    </div>

                                                    <Button onClick={handleSaveConfig}
                                                        disabled={!crValid || configLoading}
                                                        className="w-full h-10 bg-primary text-black hover:bg-primary/90">
                                                        {configLoading
                                                            ? <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                                                            : <Save className="h-4 w-4 mr-2" />}
                                                        Lưu cấu hình AHP
                                                    </Button>
                                                    {configResult && <div className="text-xs text-green-400 bg-green-400/10 p-2 rounded">{configResult}</div>}
                                                    {configError && <div className="text-xs text-red-400 bg-red-400/10 p-2 rounded">{configError}</div>}
                                                </div>
                                            </div>

                                            {/* ═══ MA TRẬN TIÊU CHÍ (hiển thị ở tab Config) ═══ */}
                                            <div className="bg-neutral-900 border border-neutral-800 rounded-xl p-5 mt-5">
                                                <h5 className="text-sm font-semibold text-white mb-1">Ma trận so sánh cặp tiêu chí</h5>
                                                <p className="text-xs text-neutral-500 mb-4">Ma trận pairwise comparison giữa 4 tiêu chí đánh giá (đường chéo = 1)</p>
                                                <div className="overflow-x-auto">
                                                    <table className="w-full text-xs border-collapse">
                                                        <thead>
                                                            <tr>
                                                                <th className={`${headerBg} px-3 py-2 border border-neutral-700 text-left`}></th>
                                                                {CRITERIA_LABELS.map(label => (
                                                                    <th key={label} className={`${headerBg} px-3 py-2 border border-neutral-700 text-center min-w-[80px]`}>{label}</th>
                                                                ))}
                                                                <th className={`${headerBg} px-3 py-2 border border-neutral-700 text-center min-w-[80px]`}>Trọng số</th>
                                                            </tr>
                                                        </thead>
                                                        <tbody>
                                                            {CRITERIA_LABELS.map((rowLabel, i) => (
                                                                <tr key={rowLabel}>
                                                                    <td className={`${headerBg} px-3 py-2 border border-neutral-700 text-left`}>{rowLabel}</td>
                                                                    {matrix[i].map((val: number, j: number) => (
                                                                        <td key={j} className={`${cellBg(i, j)} px-3 py-2 border border-neutral-700 text-center font-mono`}>
                                                                            {val.toFixed(2)}
                                                                        </td>
                                                                    ))}
                                                                    <td className="bg-emerald-600/80 text-white px-3 py-2 border border-neutral-700 text-center font-mono font-bold">
                                                                        {(weights[i] * 100).toFixed(1)}%
                                                                    </td>
                                                                </tr>
                                                            ))}
                                                            <tr>
                                                                <td className="bg-neutral-800 text-amber-400 px-3 py-2 border border-neutral-700 font-bold">Sum</td>
                                                                {colSums.map((s: number, j: number) => (
                                                                    <td key={j} className="bg-neutral-800 text-amber-400 px-3 py-2 border border-neutral-700 text-center font-mono font-bold">
                                                                        {s.toFixed(2)}
                                                                    </td>
                                                                ))}
                                                                <td className="bg-neutral-800 text-amber-400 px-3 py-2 border border-neutral-700 text-center font-mono font-bold">100%</td>
                                                            </tr>
                                                        </tbody>
                                                    </table>
                                                </div>
                                                <p className="text-[10px] text-neutral-500 mt-2">CR = {cr.toFixed(4)} — {crValid ? "✓ Nhất quán (< 0.1)" : "✗ Không nhất quán"}</p>
                                            </div>
                                        </div>
                                    )}

                                    {/* ── TAB: Ranking & Analytics ──────────────────────── */}
                                    {activeTab === "ranking" && (
                                        <div className="p-5 space-y-6">
                                            {/* CTA */}
                                            {!selectedJob?.ahp_weights && (
                                                <div className="flex items-center gap-3 bg-amber-400/10 border border-amber-400/20 rounded-lg px-4 py-3">
                                                    <AlertTriangle className="h-4 w-4 text-amber-400 flex-shrink-0" />
                                                    <p className="text-xs text-amber-300">Chưa cấu hình AHP. Hãy qua Tab <strong>"Cấu hình AHP"</strong> thiết lập và lưu trước khi xếp hạng.</p>
                                                </div>
                                            )}

                                            <div className="flex items-center justify-between">
                                                <div>
                                                    <h4 className="text-sm font-semibold text-white">Xếp hạng ứng viên</h4>
                                                    <p className="text-xs text-neutral-400 mt-0.5">Sử dụng trọng số AHP đã lưu để tính điểm và xếp hạng các hồ sơ đã qua lọc RF.</p>
                                                </div>
                                                <Button onClick={handleRunRank} disabled={rankLoading}
                                                    className="h-10 px-5 bg-violet-600 hover:bg-violet-500 text-white">
                                                    {rankLoading
                                                        ? <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                                                        : <Brain className="h-4 w-4 mr-2" />}
                                                    Thực hiện Xếp hạng AHP
                                                </Button>
                                            </div>

                                            {rankError && (
                                                <div className="flex items-start gap-3 bg-red-400/10 border border-red-400/20 rounded-lg px-4 py-3">
                                                    <AlertTriangle className="h-4 w-4 text-red-400 flex-shrink-0 mt-0.5" />
                                                    <p className="text-xs text-red-300">{rankError}</p>
                                                </div>
                                            )}

                                            {rankResult && (
                                                <>
                                                    <div className="text-sm text-green-400 bg-green-400/10 border border-green-400/20 rounded-lg px-4 py-3">
                                                        ✓ Đã xếp hạng <strong>{rankResult.total_ranked}</strong> ứng viên — Top {rankResult.top_10.length} + {rankResult.reserve_20.length} dự bị.
                                                    </div>

                                                    {/* ═══ MA TRẬN PHƯƠNG ÁN (Alternatives per Criterion) ═══ */}
                                                    {topCandidates.length > 0 && (
                                                        <div className="bg-neutral-900 border border-neutral-800 rounded-xl p-5">
                                                            <h5 className="text-sm font-semibold text-white mb-1">Ma trận so sánh cặp các phương án theo từng tiêu chí</h5>
                                                            <p className="text-xs text-neutral-500 mb-4">So sánh tỉ lệ điểm thô giữa Top {topCandidates.length} ứng viên cho mỗi tiêu chí. Kiểm tra CR · {'<'}10%</p>
                                                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                                                {CRITERIA_KEYS.map((key, cIdx) => {
                                                                    const altMat = buildAltMatrix(key)
                                                                    if (altMat.length === 0) return null
                                                                    // Compute column sums
                                                                    const altColSums = Array(altMat.length).fill(0)
                                                                    for (let j = 0; j < altMat.length; j++)
                                                                        for (let i = 0; i < altMat.length; i++)
                                                                            altColSums[j] += altMat[i][j]
                                                                    return (
                                                                        <div key={key} className="border border-neutral-700 rounded-lg overflow-hidden">
                                                                            <div className={`${headerBg} px-3 py-1.5 text-xs`}>{CRITERIA_LABELS[cIdx]}</div>
                                                                            <div className="overflow-x-auto">
                                                                                <table className="w-full text-[11px] border-collapse">
                                                                                    <thead>
                                                                                        <tr>
                                                                                            <th className="bg-sky-800/60 text-neutral-300 px-2 py-1.5 border border-neutral-700 text-left"></th>
                                                                                            {candidateShortNames.map((name, j) => (
                                                                                                <th key={j} className="bg-sky-800/60 text-neutral-300 px-2 py-1.5 border border-neutral-700 text-center font-medium">{name}</th>
                                                                                            ))}
                                                                                        </tr>
                                                                                    </thead>
                                                                                    <tbody>
                                                                                        {candidateShortNames.map((rowName, i) => (
                                                                                            <tr key={i}>
                                                                                                <td className="bg-sky-800/60 text-neutral-300 px-2 py-1.5 border border-neutral-700 font-medium">{rowName}</td>
                                                                                                {altMat[i].map((val, j) => (
                                                                                                    <td key={j} className={`${cellBg(i, j)} px-2 py-1.5 border border-neutral-700 text-center font-mono`}>
                                                                                                        {val >= 100 ? val.toFixed(0) : val >= 10 ? val.toFixed(1) : val.toFixed(2)}
                                                                                                    </td>
                                                                                                ))}
                                                                                            </tr>
                                                                                        ))}
                                                                                        <tr>
                                                                                            <td className="bg-neutral-800 text-amber-400 px-2 py-1 border border-neutral-700 font-bold text-[10px]">Sum</td>
                                                                                            {altColSums.map((s: number, j: number) => (
                                                                                                <td key={j} className="bg-neutral-800 text-amber-400 px-2 py-1 border border-neutral-700 text-center font-mono font-bold text-[10px]">
                                                                                                    {s.toFixed(2)}
                                                                                                </td>
                                                                                            ))}
                                                                                        </tr>
                                                                                    </tbody>
                                                                                </table>
                                                                            </div>
                                                                        </div>
                                                                    )
                                                                })}
                                                            </div>
                                                        </div>
                                                    )}

                                                    {/* Top 10 table */}
                                                    <div className="bg-neutral-900 border border-neutral-800 rounded-xl overflow-hidden">
                                                        <div className="px-4 py-3 border-b border-neutral-800 flex items-center gap-2">
                                                            <Star className="h-4 w-4 text-amber-400" />
                                                            <h5 className="text-sm font-semibold text-white">Top 10 Ứng viên</h5>
                                                        </div>
                                                        <div className="divide-y divide-neutral-800">
                                                            {rankResult.top_10.map(c => (
                                                                <div key={c.don_id} className="px-4 py-3 flex items-center justify-between hover:bg-neutral-800/30 transition-colors">
                                                                    <div className="flex items-center gap-3">
                                                                        <span className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold ${c.rank <= 3 ? "bg-amber-400 text-black" : "bg-neutral-800 text-neutral-300"}`}>
                                                                            {c.rank}
                                                                        </span>
                                                                        <span className="text-sm text-white">{c.candidate_name}</span>
                                                                    </div>
                                                                    <div className="flex items-center gap-4">
                                                                        {CRITERIA_LABELS.map((label, i) => (
                                                                            <div key={label} className="hidden md:flex flex-col items-center text-center">
                                                                                <span className="text-[10px] text-neutral-500">{label}</span>
                                                                                <span className="text-xs text-white font-mono">{c.scores[CRITERIA_KEYS[i]]?.toFixed(1)}</span>
                                                                            </div>
                                                                        ))}
                                                                        <div className="flex flex-col items-end">
                                                                            <span className="text-[10px] text-neutral-500">AHP</span>
                                                                            <span className="text-sm font-mono font-bold text-primary">{c.ahp_score.toFixed(3)}</span>
                                                                        </div>
                                                                    </div>
                                                                </div>
                                                            ))}
                                                        </div>
                                                    </div>

                                                    {/* Reserve 20 */}
                                                    {rankResult.reserve_20.length > 0 && (
                                                        <details className="group">
                                                            <summary className="cursor-pointer text-xs text-neutral-400 hover:text-neutral-200 transition-colors list-none flex items-center gap-2">
                                                                <span className="w-4 h-4 rounded bg-neutral-800 flex items-center justify-center text-neutral-400 group-open:rotate-90 transition-transform">▶</span>
                                                                Xem {rankResult.reserve_20.length} ứng viên dự bị
                                                            </summary>
                                                            <div className="mt-3 bg-neutral-900 border border-neutral-800 rounded-xl divide-y divide-neutral-800 overflow-hidden">
                                                                {rankResult.reserve_20.map(c => (
                                                                    <div key={c.don_id} className="px-4 py-2.5 flex items-center justify-between">
                                                                        <div className="flex items-center gap-3">
                                                                            <span className="w-6 h-6 rounded-full bg-neutral-800 flex items-center justify-center text-xs text-neutral-400">{c.rank}</span>
                                                                            <span className="text-sm text-neutral-300">{c.candidate_name}</span>
                                                                        </div>
                                                                        <span className="text-xs font-mono text-neutral-400">{c.ahp_score.toFixed(3)}</span>
                                                                    </div>
                                                                ))}
                                                            </div>
                                                        </details>
                                                    )}
                                                </>
                                            )}
                                        </div>
                                    )}
                                </div>
                            )}
                        </Card>
                    ))}
                </div>
            )}
        </div>
    )
}
