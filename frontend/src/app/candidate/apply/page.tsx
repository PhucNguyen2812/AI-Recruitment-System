"use client"

import * as React from "react"
import { useRouter } from "next/navigation"
import { Upload, FileText, X, AlertCircle, CheckCircle2, Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"



const MAX_SIZE_MB = 5
const MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024

export default function CandidateApplyPage() {
    const router = useRouter()
    const [file, setFile] = React.useState<File | null>(null)
    const [fileError, setFileError] = React.useState<string | null>(null)
    const [position, setPosition] = React.useState("")
    const [fullName, setFullName] = React.useState("")
    const [email, setEmail] = React.useState("")
    const [dragging, setDragging] = React.useState(false)
    const [uploading, setUploading] = React.useState(false)
    const [uploadProgress, setUploadProgress] = React.useState(0)
    const [uploadSuccess, setUploadSuccess] = React.useState(false)
    const [serverError, setServerError] = React.useState<string | null>(null)
    const [jobPositions, setJobPositions] = React.useState<{id: string, tieu_de: string}[]>([])
    const inputRef = React.useRef<HTMLInputElement>(null)

    React.useEffect(() => {
        const fetchJobs = async () => {
            try {
                const res = await fetch("http://localhost:8000/api/jobs/open")
                if (res.ok) {
                    const data = await res.json()
                    setJobPositions(data)
                }
            } catch (err) {
                console.error("Failed to fetch open jobs", err)
            }
        }
        fetchJobs()
    }, [])

    const validateFile = (f: File): string | null => {
        if (f.type !== "application/pdf" && !f.name.toLowerCase().endsWith(".pdf")) {
            return "Chỉ chấp nhận file PDF. Vui lòng chọn lại."
        }
        if (f.size > MAX_SIZE_BYTES) {
            return `File quá lớn (${(f.size / 1024 / 1024).toFixed(1)} MB). Giới hạn: ${MAX_SIZE_MB} MB.`
        }
        return null
    }

    const handleFileSelect = (f: File) => {
        const err = validateFile(f)
        if (err) {
            setFileError(err)
            setFile(null)
        } else {
            setFileError(null)
            setFile(f)
        }
    }

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault()
        setDragging(false)
        const droppedFile = e.dataTransfer.files[0]
        if (droppedFile) handleFileSelect(droppedFile)
    }

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const selected = e.target.files?.[0]
        if (selected) handleFileSelect(selected)
    }

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        if (!file || !position || !fullName || !email) return

        setUploading(true)
        setUploadProgress(0)
        setServerError(null)

        // Simulate progress
        const interval = setInterval(() => {
            setUploadProgress((prev) => {
                if (prev >= 90) {
                    clearInterval(interval)
                    return 90
                }
                return prev + 10
            })
        }, 150)

        try {
            const formData = new FormData()
            formData.append("file", file)
            formData.append("job_id", position)
            formData.append("candidate_name", fullName)
            formData.append("candidate_email", email)

            const res = await fetch("http://localhost:8000/api/cv/upload", {
                method: "POST",
                body: formData,
            })

            clearInterval(interval)
            setUploadProgress(100)

            if (!res.ok) {
                const data = await res.json().catch(() => ({}))
                throw new Error(data?.detail || `Lỗi server: ${res.status}`)
            }

            const data = await res.json()
            const applicationId = data?.id || data?.application_id || "unknown"
            localStorage.setItem("application_id", String(applicationId))
            localStorage.setItem("applicant_name", fullName)
            localStorage.setItem("applicant_position", position)

            setUploadSuccess(true)
            setTimeout(() => {
                router.push("/candidate/status")
            }, 2000)
        } catch (err: unknown) {
            clearInterval(interval)
            setUploadProgress(0)
            if (err instanceof Error) {
                setServerError(err.message)
            } else {
                setServerError("Không thể kết nối tới server. Vui lòng thử lại sau.")
            }
        } finally {
            setUploading(false)
        }
    }

    const removeFile = () => {
        setFile(null)
        setFileError(null)
        if (inputRef.current) inputRef.current.value = ""
    }

    if (uploadSuccess) {
        return (
            <div className="flex min-h-[calc(100vh-112px)] items-center justify-center px-4">
                <div className="text-center">
                    <div className="flex items-center justify-center mb-4">
                        <div className="h-16 w-16 rounded-full bg-green-500/15 border border-green-500/30 flex items-center justify-center">
                            <CheckCircle2 className="h-8 w-8 text-green-400" />
                        </div>
                    </div>
                    <h2 className="text-2xl font-bold text-white mb-2">Nộp CV thành công!</h2>
                    <p className="text-neutral-400 text-sm mb-1">Hồ sơ đã được ghi nhận vào hệ thống.</p>
                    <p className="text-neutral-500 text-xs">Bạn có thể dùng Email đã đăng ký để tra cứu trạng thái.</p>
                    <p className="text-neutral-500 justify-content flex text-xs mt-2 animate-pulse">Đang chuyển hướng sang trang theo dõi...</p>
                </div>
            </div>
        )
    }

    return (
        <div className="flex min-h-[calc(100vh-112px)] items-start justify-center px-4 py-12">
            <div className="w-full max-w-2xl space-y-6">
                {/* Page title */}
                <div className="text-center">
                    <h1 className="text-3xl font-bold text-white tracking-tight">Nộp hồ sơ ứng tuyển</h1>
                    <p className="text-neutral-400 mt-2 text-sm">
                        Chỉ chấp nhận file PDF · Tối đa {MAX_SIZE_MB} MB · Tối đa 5 trang
                    </p>
                </div>

                <Card className="bg-neutral-900 border-neutral-800 shadow-2xl">
                    <CardHeader className="border-b border-neutral-800">
                        <CardTitle className="text-base text-white">Thông tin ứng viên</CardTitle>
                        <CardDescription className="text-xs">Vui lòng điền đầy đủ thông tin trước khi nộp CV.</CardDescription>
                    </CardHeader>
                    <CardContent className="pt-6">
                        <form onSubmit={handleSubmit} className="space-y-5">
                            {/* Name */}
                            <div className="space-y-1.5">
                                <Label htmlFor="fullName" className="text-sm text-neutral-300">Họ và tên <span className="text-red-400">*</span></Label>
                                <Input
                                    id="fullName"
                                    type="text"
                                    placeholder="Nguyễn Văn A"
                                    value={fullName}
                                    onChange={(e) => setFullName(e.target.value)}
                                    required
                                    className="bg-neutral-950 border-neutral-700 focus-visible:ring-primary text-white placeholder:text-neutral-600"
                                />
                            </div>

                            {/* Email */}
                            <div className="space-y-1.5">
                                <Label htmlFor="email" className="text-sm text-neutral-300">Email <span className="text-red-400">*</span></Label>
                                <Input
                                    id="email"
                                    type="email"
                                    placeholder="example@email.com"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    required
                                    className="bg-neutral-950 border-neutral-700 focus-visible:ring-primary text-white placeholder:text-neutral-600"
                                />
                            </div>

                            {/* Position */}
                            <div className="space-y-1.5">
                                <Label htmlFor="position" className="text-sm text-neutral-300">Vị trí ứng tuyển <span className="text-red-400">*</span></Label>
                                <select
                                    id="position"
                                    value={position}
                                    onChange={(e) => setPosition(e.target.value)}
                                    required
                                    className="w-full h-10 rounded-md border border-neutral-700 bg-neutral-950 px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-primary/60 appearance-none cursor-pointer"
                                >
                                    <option value="" disabled className="text-neutral-500">— Chọn vị trí —</option>
                                    {jobPositions.map((j) => (
                                        <option key={j.id} value={j.id} className="text-white bg-neutral-900">
                                            {j.tieu_de}
                                        </option>
                                    ))}
                                </select>
                            </div>

                            {/* File Upload */}
                            <div className="space-y-1.5">
                                <Label className="text-sm text-neutral-300">File CV (PDF) <span className="text-red-400">*</span></Label>

                                {!file ? (
                                    <div
                                        onClick={() => inputRef.current?.click()}
                                        onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
                                        onDragLeave={() => setDragging(false)}
                                        onDrop={handleDrop}
                                        className={`flex flex-col items-center justify-center border-2 border-dashed rounded-xl h-36 cursor-pointer transition-all duration-200 ${dragging
                                                ? "border-primary bg-primary/10 scale-[1.01]"
                                                : "border-neutral-700 hover:border-neutral-500 hover:bg-neutral-800/30"
                                            }`}
                                    >
                                        <Upload className="h-8 w-8 text-neutral-500 mb-2" />
                                        <p className="text-sm text-neutral-400">
                                            Kéo thả hoặc <span className="text-primary underline">nhấp để chọn file</span>
                                        </p>
                                        <p className="text-xs text-neutral-600 mt-1">PDF · Tối đa {MAX_SIZE_MB}MB</p>
                                    </div>
                                ) : (
                                    <div className="flex items-center justify-between border border-neutral-700 bg-neutral-800/50 rounded-lg px-4 py-3">
                                        <div className="flex items-center space-x-3">
                                            <div className="h-9 w-9 flex items-center justify-center rounded-lg bg-red-500/15 border border-red-500/30">
                                                <FileText className="h-4 w-4 text-red-400" />
                                            </div>
                                            <div>
                                                <p className="text-sm text-white font-medium truncate max-w-[280px]">{file.name}</p>
                                                <p className="text-xs text-neutral-500">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                                            </div>
                                        </div>
                                        <button type="button" onClick={removeFile} className="p-1.5 rounded-md hover:bg-neutral-700 text-neutral-400 hover:text-white transition-colors">
                                            <X className="h-4 w-4" />
                                        </button>
                                    </div>
                                )}

                                <input
                                    ref={inputRef}
                                    type="file"
                                    accept="application/pdf,.pdf"
                                    className="hidden"
                                    onChange={handleInputChange}
                                />

                                {fileError && (
                                    <div className="flex items-center space-x-2 text-red-400 text-xs mt-1">
                                        <AlertCircle className="h-3.5 w-3.5 flex-shrink-0" />
                                        <span>{fileError}</span>
                                    </div>
                                )}
                            </div>

                            {/* Upload Progress */}
                            {uploading && (
                                <div className="space-y-1">
                                    <div className="flex items-center justify-between text-xs text-neutral-400">
                                        <span>Đang tải lên...</span>
                                        <span>{uploadProgress}%</span>
                                    </div>
                                    <div className="h-1.5 w-full bg-neutral-800 rounded-full overflow-hidden">
                                        <div
                                            className="h-full bg-primary rounded-full transition-all duration-200 shadow-[0_0_8px_rgba(255,255,255,0.3)]"
                                            style={{ width: `${uploadProgress}%` }}
                                        />
                                    </div>
                                </div>
                            )}

                            {/* Server Error */}
                            {serverError && (
                                <div className="flex items-start space-x-2 bg-red-500/10 border border-red-500/30 rounded-lg px-4 py-3">
                                    <AlertCircle className="h-4 w-4 text-red-400 flex-shrink-0 mt-0.5" />
                                    <p className="text-sm text-red-300">{serverError}</p>
                                </div>
                            )}

                            {/* Submit */}
                            <Button
                                type="submit"
                                className="w-full h-11 font-semibold"
                                disabled={!file || !position || !fullName || !email || uploading}
                            >
                                {uploading ? (
                                    <>
                                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                                        Đang nộp hồ sơ...
                                    </>
                                ) : (
                                    "Nộp hồ sơ"
                                )}
                            </Button>
                        </form>
                    </CardContent>
                </Card>
            </div>
        </div>
    )
}
