"use client"

import * as React from "react"
import { Plus, Trash2, Code } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import axios from "@/lib/axios"

export default function PositionsPage() {
    const [positions, setPositions] = React.useState<any[]>([])
    const [loading, setLoading] = React.useState(true)
    const [showCreate, setShowCreate] = React.useState(false)

    // Form states
    const [ten, setTen] = React.useState("")
    const [ma, setMa] = React.useState("")
    const [moTa, setMoTa] = React.useState("")

    React.useEffect(() => {
        fetchPositions()
    }, [])

    const fetchPositions = async () => {
        setLoading(true)
        try {
            const token = localStorage.getItem("token")
            const res = await axios.get("/api/positions/", {
                headers: { "Authorization": `Bearer ${token}` }
            })
            setPositions(res.data)
        } catch (error) {
            console.error("Failed to load positions", error)
        } finally {
            setLoading(false)
        }
    }

    const handleCreate = async () => {
        if (!ten || !ma) return alert("Vui lòng nhập tên và mã vị trí (code)")
        
        try {
            const token = localStorage.getItem("token")
            await axios.post("/api/positions/", {
                ten,
                ma,
                mo_ta: moTa
            }, {
                headers: { "Authorization": `Bearer ${token}` }
            })
            setShowCreate(false)
            setTen("")
            setMa("")
            setMoTa("")
            fetchPositions()
        } catch (error: any) {
            console.error("Lỗi khi tạo vị trí", error)
            alert(error.response?.data?.detail || "Đã xảy ra lỗi khi tạo vị trí!")
        }
    }

    const handleDelete = async (id: string) => {
        const confirmDelete = window.confirm("Bạn có chắc chắn muốn xóa vị trí này?")
        if (!confirmDelete) return
        
        try {
            const token = localStorage.getItem("token")
            await axios.delete(`/api/positions/${id}`, {
                headers: { "Authorization": `Bearer ${token}` }
            })
            fetchPositions()
        } catch (error) {
            console.error("Lỗi xóa vị trí", error)
            alert("Lỗi khi xóa vị trí.")
        }
    }

    return (
        <div className="space-y-6 max-w-4xl mx-auto">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold text-white">Vị trí Tuyển Dụng (Positions)</h2>
                    <p className="text-sm text-neutral-400 mt-1">Quản lý các chức danh / vị trí tuyển dụng có thể chọn trong đợt tuyển dụng.</p>
                </div>
                <Button onClick={() => setShowCreate(!showCreate)} className="bg-primary text-black hover:bg-primary/90">
                    <Plus className="h-4 w-4 mr-2" />
                    Thêm Vị trí
                </Button>
            </div>

            {showCreate && (
                <Card className="bg-neutral-900 border-neutral-800 shadow-xl">
                    <CardHeader className="border-b border-neutral-800 pb-4">
                        <CardTitle className="text-lg text-white">Thêm Vị trí Tuyển dụng</CardTitle>
                    </CardHeader>
                    <CardContent className="pt-4 space-y-4">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <label className="text-xs text-neutral-400 font-medium">Tên hiển thị *</label>
                                <Input 
                                    placeholder="Vd: Lập trình viên Backend" 
                                    className="h-10 border-neutral-700 bg-neutral-800 text-white placeholder:text-neutral-500"
                                    value={ten}
                                    onChange={(e) => setTen(e.target.value)}
                                />
                            </div>
                            <div className="space-y-2">
                                <label className="text-xs text-neutral-400 font-medium">Mã (Code, dùng cho model AI) *</label>
                                <Input 
                                    placeholder="Vd: backend_dev" 
                                    className="h-10 border-neutral-700 bg-neutral-800 text-white placeholder:text-neutral-500"
                                    value={ma}
                                    onChange={(e) => setMa(e.target.value)}
                                />
                                <p className="text-[10px] text-orange-400">Lưu ý: Mã này dùng để map với mô hình phân loại (RF Model).</p>
                            </div>
                            <div className="space-y-2 md:col-span-2">
                                <label className="text-xs text-neutral-400 font-medium">Mô tả (Không bắt buộc)</label>
                                <Input 
                                    placeholder="Vd: Tham gia phát triển hệ thống lõi..." 
                                    className="h-10 border-neutral-700 bg-neutral-800 text-white placeholder:text-neutral-500"
                                    value={moTa}
                                    onChange={(e) => setMoTa(e.target.value)}
                                />
                            </div>
                        </div>
                        <div className="flex justify-end pt-2">
                            <Button onClick={handleCreate}>
                                Lưu Vị trí
                            </Button>
                        </div>
                    </CardContent>
                </Card>
            )}

            {loading ? (
                <div className="text-center text-neutral-500 py-10">Đang tải dữ liệu...</div>
            ) : positions.length === 0 ? (
                <div className="text-center text-neutral-500 py-10 border border-dashed border-neutral-800 rounded-lg">
                    Chưa có vị trí nào. Hãy thêm vị trí!
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {positions.map(pos => (
                        <Card key={pos.id} className="bg-neutral-900 border-neutral-800 relative group">
                            <CardContent className="p-5">
                                <div className="absolute top-3 right-3 opacity-0 group-hover:opacity-100 transition-opacity">
                                    <button 
                                        className="text-neutral-500 hover:text-red-400 transition-colors"
                                        onClick={() => handleDelete(pos.id)}
                                        title="Xóa vị trí"
                                    >
                                        <Trash2 className="h-4 w-4" />
                                    </button>
                                </div>
                                <h3 className="text-white font-bold leading-tight pr-6">{pos.ten}</h3>
                                <div className="flex items-center gap-1.5 mt-2 text-xs text-neutral-400 bg-neutral-950 w-max px-2 py-1 rounded inline-flex">
                                    <Code className="h-3.5 w-3.5 text-primary/70" />
                                    <code>{pos.ma}</code>
                                </div>
                                {pos.mo_ta && (
                                    <p className="mt-3 text-sm text-neutral-500 line-clamp-2">{pos.mo_ta}</p>
                                )}
                            </CardContent>
                        </Card>
                    ))}
                </div>
            )}
        </div>
    )
}
