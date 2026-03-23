"use client"

import * as React from "react"
import { Plus, Calendar, Briefcase, Trash2, X, Loader2, Pencil, Lock, AlertTriangle } from "lucide-react"
import { Button } from "@/components/ui/button"
import { useRouter } from "next/navigation"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import axios from "@/lib/axios"

export default function CampaignsPage() {
    const [campaigns, setCampaigns] = React.useState<any[]>([])
    const router = useRouter()
    const [loading, setLoading] = React.useState(true)
    const [showCreate, setShowCreate] = React.useState(false)

    // Create form states
    const [tieuDe, setTieuDe] = React.useState("")
    const [moTa, setMoTa] = React.useState("")
    const [ngayBatDau, setNgayBatDau] = React.useState("")
    const [ngayKetThuc, setNgayKetThuc] = React.useState("")

    // Edit form states
    const [editingId, setEditingId] = React.useState<string | null>(null)
    const [editTieuDe, setEditTieuDe] = React.useState("")
    const [editMoTa, setEditMoTa] = React.useState("")
    const [editNgayKetThuc, setEditNgayKetThuc] = React.useState("")

    // Loading states
    const [closingId, setClosingId] = React.useState<string | null>(null)
    const [savingEdit, setSavingEdit] = React.useState(false)

    // Today's date for min validation
    const todayStr = new Date().toISOString().slice(0, 16)

    React.useEffect(() => {
        fetchCampaigns()
    }, [])

    const fetchCampaigns = async () => {
        setLoading(true)
        try {
            const res = await axios.get("/api/campaigns/my")
            setCampaigns(res.data)
        } catch (error) {
            console.error("Failed to load campaigns", error)
        } finally {
            setLoading(false)
        }
    }

    const handleCreate = async () => {
        if (!tieuDe || !ngayBatDau || !ngayKetThuc) return alert("Vui lòng nhập đủ thông tin bắt buộc")
        
        // Frontend validation
        const startDate = new Date(ngayBatDau)
        const endDate = new Date(ngayKetThuc)
        const today = new Date()
        today.setHours(0, 0, 0, 0)
        
        if (startDate < today) {
            return alert("Ngày bắt đầu không được nhỏ hơn ngày hôm nay.")
        }
        if (endDate <= startDate) {
            return alert("Ngày kết thúc phải sau ngày bắt đầu.")
        }

        try {
            const token = localStorage.getItem("token")
            await axios.post("/api/campaigns/", {
                tieu_de: tieuDe,
                mo_ta: moTa,
                ngay_bat_dau: new Date(ngayBatDau).toISOString(),
                ngay_ket_thuc: new Date(ngayKetThuc).toISOString(),
                trang_thai: "dang_mo"
            }, {
                headers: { "Authorization": `Bearer ${token}` }
            })
            setShowCreate(false)
            setTieuDe("")
            setMoTa("")
            setNgayBatDau("")
            setNgayKetThuc("")
            fetchCampaigns()
        } catch (error: any) {
            console.error("Lỗi khi tạo đợt tuyển dụng", error)
            const detail = error.response?.data?.detail
            if (Array.isArray(detail)) {
                alert(detail.map((d: any) => d.msg).join("\n"))
            } else {
                alert(detail || "Đã xảy ra lỗi khi tạo đợt tuyển dụng!")
            }
        }
    }

    const handleDelete = async (id: string) => {
        const confirmDelete = window.confirm("Bạn có chắc chắn muốn xóa đợt tuyển dụng này? Toàn bộ dữ liệu liên quan sẽ bị xóa!")
        if (!confirmDelete) return
        
        try {
            const token = localStorage.getItem("token")
            await axios.delete(`/api/campaigns/${id}`, {
                headers: { "Authorization": `Bearer ${token}` }
            })
            fetchCampaigns()
        } catch (error) {
            console.error("Lỗi xóa đợt tuyển dụng", error)
            alert("Lỗi khi xóa đợt tuyển dụng.")
        }
    }

    // ── Đóng sớm Campaign ──
    const handleCloseEarly = async (id: string, title: string) => {
        const confirmed = window.confirm(
            `⚠️ ĐÓNG SỚM ĐỢT TUYỂN DỤNG\n\n` +
            `Đợt: "${title}"\n\n` +
            `Hành động này sẽ:\n` +
            `• Lưu trữ kết quả xếp hạng Top 30 (nếu có)\n` +
            `• Xóa toàn bộ CV và dữ liệu cá nhân ứng viên\n` +
            `• Đóng tất cả vị trí tuyển dụng trong đợt\n\n` +
            `Bạn có chắc chắn muốn tiếp tục?`
        )
        if (!confirmed) return

        setClosingId(id)
        try {
            const token = localStorage.getItem("token")
            const res = await axios.post(`/api/campaigns/${id}/close-early`, null, {
                headers: { "Authorization": `Bearer ${token}` }
            })
            alert(`✅ ${res.data.message}`)
            fetchCampaigns()
        } catch (error: any) {
            console.error("Lỗi đóng sớm đợt tuyển dụng", error)
            alert(error.response?.data?.detail || "Lỗi khi đóng đợt tuyển dụng.")
        } finally {
            setClosingId(null)
        }
    }

    // ── Chỉnh sửa Campaign ──
    const startEditing = (campaign: any) => {
        setEditingId(campaign.id)
        setEditTieuDe(campaign.tieu_de)
        setEditMoTa(campaign.mo_ta || "")
        // Format datetime-local from ISO
        const endDate = new Date(campaign.ngay_ket_thuc)
        setEditNgayKetThuc(endDate.toISOString().slice(0, 16))
    }

    const cancelEditing = () => {
        setEditingId(null)
        setEditTieuDe("")
        setEditMoTa("")
        setEditNgayKetThuc("")
    }

    const handleSaveEdit = async () => {
        if (!editingId) return
        
        // Validate
        if (!editTieuDe.trim()) {
            return alert("Tên đợt tuyển dụng không được để trống.")
        }
        
        if (editNgayKetThuc) {
            const newEnd = new Date(editNgayKetThuc)
            if (newEnd < new Date()) {
                return alert("Ngày kết thúc mới không được nhỏ hơn thời điểm hiện tại.")
            }
        }

        setSavingEdit(true)
        try {
            const token = localStorage.getItem("token")
            const updateData: any = {
                tieu_de: editTieuDe.trim(),
                mo_ta: editMoTa.trim() || null,
            }
            if (editNgayKetThuc) {
                updateData.ngay_ket_thuc = new Date(editNgayKetThuc).toISOString()
            }
            
            await axios.put(`/api/campaigns/${editingId}`, updateData, {
                headers: { "Authorization": `Bearer ${token}` }
            })
            cancelEditing()
            fetchCampaigns()
        } catch (error: any) {
            console.error("Lỗi cập nhật đợt tuyển dụng", error)
            const detail = error.response?.data?.detail
            if (Array.isArray(detail)) {
                alert(detail.map((d: any) => d.msg).join("\n"))
            } else {
                alert(detail || "Lỗi khi cập nhật đợt tuyển dụng.")
            }
        } finally {
            setSavingEdit(false)
        }
    }

    return (
        <div className="space-y-6 max-w-5xl mx-auto">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold text-white">Quản lý Tuyển Dụng (Campaigns)</h2>
                    <p className="text-sm text-neutral-400 mt-1">Tạo và quản lý các đợt tuyển dụng, thời hạn và việc tự động đóng đơn.</p>
                </div>
                <Button onClick={() => setShowCreate(!showCreate)} className="bg-primary text-black hover:bg-primary/90">
                    <Plus className="h-4 w-4 mr-2" />
                    Thêm Đợt Tuyển Dụng
                </Button>
            </div>

            {showCreate && (
                <Card className="bg-neutral-900 border-neutral-800 shadow-xl">
                    <CardHeader className="border-b border-neutral-800 pb-4">
                        <CardTitle className="text-lg text-white">Tạo đợt tuyển dụng mới</CardTitle>
                    </CardHeader>
                    <CardContent className="pt-4 space-y-4">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <label className="text-xs text-neutral-400 font-medium">Tên đợt tuyển dụng *</label>
                                <Input 
                                    placeholder="Vd: Tuyển Thực tập sinh CNTT 2026" 
                                    className="h-10 border-neutral-700 bg-neutral-800 text-white placeholder:text-neutral-500"
                                    value={tieuDe}
                                    onChange={(e) => setTieuDe(e.target.value)}
                                />
                            </div>
                            <div className="space-y-2">
                                <label className="text-xs text-neutral-400 font-medium">Mô tả ngắn</label>
                                <Input 
                                    placeholder="Vd: Khu vực Hà Nội & HCM" 
                                    className="h-10 border-neutral-700 bg-neutral-800 text-white placeholder:text-neutral-500"
                                    value={moTa}
                                    onChange={(e) => setMoTa(e.target.value)}
                                />
                            </div>
                            <div className="space-y-2">
                                <label className="text-xs text-neutral-400 font-medium">Ngày bắt đầu *</label>
                                <Input 
                                    type="datetime-local" 
                                    className="h-10 border-neutral-700 bg-neutral-800 text-white"
                                    value={ngayBatDau}
                                    onChange={(e) => setNgayBatDau(e.target.value)}
                                    min={todayStr}
                                />
                                <p className="text-[10px] text-neutral-500">Không được chọn ngày trong quá khứ</p>
                            </div>
                            <div className="space-y-2">
                                <label className="text-xs text-neutral-400 font-medium">Ngày kết thúc (Auto-close) *</label>
                                <Input 
                                    type="datetime-local" 
                                    className="h-10 border-neutral-700 bg-neutral-800 text-white"
                                    value={ngayKetThuc}
                                    onChange={(e) => setNgayKetThuc(e.target.value)}
                                    min={ngayBatDau || todayStr}
                                />
                            </div>
                        </div>
                        <div className="flex justify-end gap-2 pt-2">
                            <Button variant="ghost" onClick={() => setShowCreate(false)} className="text-neutral-400">
                                Hủy
                            </Button>
                            <Button onClick={handleCreate}>
                                Lưu Đợt Tuyển Dụng
                            </Button>
                        </div>
                    </CardContent>
                </Card>
            )}

            {loading ? (
                <div className="text-center text-neutral-500 py-10">Đang tải dữ liệu...</div>
            ) : campaigns.length === 0 ? (
                <div className="text-center text-neutral-500 py-10 border border-dashed border-neutral-800 rounded-lg">
                    Chưa có đợt tuyển dụng nào. Hãy tạo đợt mới!
                </div>
            ) : (
                <div className="grid grid-cols-1 gap-4">
                    {campaigns.map(campaign => {
                        const isClosed = campaign.trang_thai === 'da_dong'
                        const isEditing = editingId === campaign.id
                        const isClosing = closingId === campaign.id

                        return (
                            <Card key={campaign.id} className={`bg-neutral-900 border-neutral-800 overflow-hidden transition-all ${isClosed ? "opacity-70" : ""}`}>
                                <div className="flex flex-col md:flex-row border-b border-neutral-800">
                                    <div className="p-5 flex-1 border-r border-neutral-800/50">
                                        {isEditing ? (
                                            /* ── EDIT MODE ── */
                                            <div className="space-y-3">
                                                <div className="flex items-center gap-2 mb-1">
                                                    <Pencil className="h-4 w-4 text-primary" />
                                                    <span className="text-xs font-semibold text-primary uppercase tracking-wider">Chỉnh sửa</span>
                                                </div>
                                                <div className="space-y-2">
                                                    <label className="text-xs text-neutral-400">Tên đợt tuyển dụng</label>
                                                    <Input
                                                        value={editTieuDe}
                                                        onChange={(e) => setEditTieuDe(e.target.value)}
                                                        className="h-9 border-neutral-700 bg-neutral-800 text-white text-sm"
                                                    />
                                                </div>
                                                <div className="space-y-2">
                                                    <label className="text-xs text-neutral-400">Mô tả</label>
                                                    <Input
                                                        value={editMoTa}
                                                        onChange={(e) => setEditMoTa(e.target.value)}
                                                        placeholder="Mô tả ngắn..."
                                                        className="h-9 border-neutral-700 bg-neutral-800 text-white text-sm"
                                                    />
                                                </div>
                                                <div className="space-y-2">
                                                    <label className="text-xs text-neutral-400">Ngày kết thúc</label>
                                                    <Input
                                                        type="datetime-local"
                                                        value={editNgayKetThuc}
                                                        onChange={(e) => setEditNgayKetThuc(e.target.value)}
                                                        min={todayStr}
                                                        className="h-9 border-neutral-700 bg-neutral-800 text-white text-sm"
                                                    />
                                                </div>
                                                <div className="flex items-center gap-2 text-[10px] text-neutral-600 mt-1">
                                                    <Lock className="h-3 w-3" />
                                                    Ngày bắt đầu và trạng thái không thể chỉnh sửa
                                                </div>
                                                <div className="flex gap-2 pt-1">
                                                    <Button size="sm" onClick={handleSaveEdit} disabled={savingEdit} className="h-8 text-xs">
                                                        {savingEdit ? <Loader2 className="h-3 w-3 animate-spin mr-1" /> : null}
                                                        Lưu
                                                    </Button>
                                                    <Button size="sm" variant="ghost" onClick={cancelEditing} className="h-8 text-xs text-neutral-400">
                                                        Hủy
                                                    </Button>
                                                </div>
                                            </div>
                                        ) : (
                                            /* ── VIEW MODE ── */
                                            <>
                                                <div className="flex justify-between items-start mb-2">
                                                    <h3 className="text-lg font-bold text-white">{campaign.tieu_de}</h3>
                                                    <span className={`text-xs px-2 py-1 rounded-md font-semibold ${
                                                        isClosed 
                                                            ? 'bg-red-500/20 text-red-400' 
                                                            : 'bg-green-500/20 text-green-400'
                                                    }`}>
                                                        {isClosed ? 'Đã đóng' : 'Đang mở'}
                                                    </span>
                                                </div>
                                                <p className="text-sm text-neutral-400 mb-4">{campaign.mo_ta || "Không có mô tả"}</p>
                                                
                                                <div className="flex items-center gap-4 text-xs text-neutral-500">
                                                    <div className="flex items-center gap-1.5">
                                                        <Calendar className="h-3.5 w-3.5" />
                                                        Bắt đầu: {new Date(campaign.ngay_bat_dau).toLocaleDateString("vi-VN")}
                                                    </div>
                                                    <div className="flex items-center gap-1.5 text-orange-400/80">
                                                        <Calendar className="h-3.5 w-3.5" />
                                                        {isClosed ? "Đã đóng" : "Đóng tự động"}: {new Date(campaign.ngay_ket_thuc).toLocaleDateString("vi-VN")}
                                                    </div>
                                                </div>
                                            </>
                                        )}
                                    </div>
                                    <div className="p-5 w-full md:w-52 bg-neutral-950/30 flex flex-col justify-center gap-2.5">
                                        <Button 
                                            variant="outline" 
                                            className="w-full justify-start h-9 text-xs border-neutral-700 hover:bg-neutral-800" 
                                            onClick={() => router.push(`/dashboard/campaigns/${campaign.id}/jobs`)}
                                        >
                                            <Briefcase className="h-3.5 w-3.5 mr-2" />
                                            Vị trí tuyển dụng
                                        </Button>

                                        {!isClosed && (
                                            <>
                                                <Button 
                                                    variant="outline" 
                                                    className="w-full justify-start h-9 text-xs border-neutral-700 hover:bg-neutral-800" 
                                                    onClick={() => startEditing(campaign)}
                                                    disabled={isEditing}
                                                >
                                                    <Pencil className="h-3.5 w-3.5 mr-2" />
                                                    Chỉnh sửa
                                                </Button>

                                                <Button 
                                                    variant="outline" 
                                                    className="w-full justify-start h-9 text-xs border-orange-900/40 text-orange-400 hover:bg-orange-900/20 hover:text-orange-300" 
                                                    onClick={() => handleCloseEarly(campaign.id, campaign.tieu_de)}
                                                    disabled={isClosing}
                                                >
                                                    {isClosing ? (
                                                        <Loader2 className="h-3.5 w-3.5 mr-2 animate-spin" />
                                                    ) : (
                                                        <AlertTriangle className="h-3.5 w-3.5 mr-2" />
                                                    )}
                                                    {isClosing ? "Đang đóng..." : "Đóng sớm"}
                                                </Button>
                                            </>
                                        )}

                                        <Button 
                                            variant="outline" 
                                            className="w-full justify-start h-9 text-xs border-red-900/40 text-red-400 hover:bg-red-900/20 hover:text-red-300" 
                                            onClick={() => handleDelete(campaign.id)}
                                        >
                                            <Trash2 className="h-3.5 w-3.5 mr-2" />
                                            Xóa đợt
                                        </Button>
                                    </div>
                                </div>
                            </Card>
                        )
                    })}
                </div>
            )}
        </div>
    )
}
