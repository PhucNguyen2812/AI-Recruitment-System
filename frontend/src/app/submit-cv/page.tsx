"use client";

import React, { useState, useEffect } from "react";
import axios from "@/lib/axios";
import { Upload, CheckCircle2, AlertCircle, FileText, Loader2 } from "lucide-react";

interface Job {
  id: string;
  label: string;
}

export default function SubmitCVPage() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    phone: "",
    jobId: "",
  });
  const [file, setFile] = useState<File | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [result, setResult] = useState<{
    success: boolean;
    message: string;
    trang_thai?: string;
  } | null>(null);

  useEffect(() => {
    const fetchJobs = async () => {
      try {
        const response = await axios.get("/api/cv/jobs");
        setJobs(response.data);
      } catch (error) {
        console.error("Error fetching jobs:", error);
      }
    };
    fetchJobs();
  }, []);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      if (selectedFile.size > 5 * 1024 * 1024) {
        alert("File size exceeds 5MB limit.");
        return;
      }
      if (selectedFile.type !== "application/pdf") {
        alert("Only PDF files are allowed.");
        return;
      }
      setFile(selectedFile);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file || !formData.jobId) return;

    setIsSubmitting(true);
    setResult(null);

    const submitData = new FormData();
    submitData.append("job_id", formData.jobId);
    submitData.append("candidate_name", formData.name);
    submitData.append("candidate_email", formData.email);
    submitData.append("candidate_phone", formData.phone);
    submitData.append("file", file);

    try {
      const response = await axios.post("/api/cv/upload", submitData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      const isRejected = response.data.trang_thai === "khong_phu_hop";
      setResult({
        success: !isRejected,
        message: response.data.message,
        trang_thai: response.data.trang_thai,
      });
    } catch (error: any) {
      setResult({
        success: false,
        message: error.response?.data?.detail || "Đã có lỗi xảy ra. Vui lòng thử lại sau.",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col items-center justify-center p-6">
      <div className="w-full max-w-2xl bg-card border border-border rounded-2xl p-8 shadow-2xl relative overflow-hidden">
        {/* Glow effect */}
        <div className="absolute -top-24 -left-24 w-48 h-48 bg-primary/20 blur-3xl rounded-full"></div>
        <div className="absolute -bottom-24 -right-24 w-48 h-48 bg-primary/20 blur-3xl rounded-full"></div>

        <div className="relative z-10">
          <h1 className="text-3xl font-bold mb-2 flex items-center gap-3">
            <FileText className="text-primary w-8 h-8" />
            Nộp Hồ Sơ Ứng Tuyển
          </h1>
          <p className="text-muted-foreground mb-8">
            Hãy để AI của chúng tôi phân tích và đánh giá tiềm năng của bạn ngay lập tức.
          </p>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <label className="text-sm font-medium text-muted-foreground">Họ và tên *</label>
                <input
                  required
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  placeholder="Nguyễn Văn A"
                  className="w-full bg-background border border-border rounded-lg px-4 py-2 focus:ring-2 focus:ring-primary outline-none transition-all"
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium text-muted-foreground">Email *</label>
                <input
                  required
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  placeholder="example@gmail.com"
                  className="w-full bg-background border border-border rounded-lg px-4 py-2 focus:ring-2 focus:ring-primary outline-none transition-all"
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium text-muted-foreground">Số điện thoại</label>
                <input
                  type="tel"
                  name="phone"
                  value={formData.phone}
                  onChange={handleInputChange}
                  placeholder="090 123 4567"
                  className="w-full bg-background border border-border rounded-lg px-4 py-2 focus:ring-2 focus:ring-primary outline-none transition-all"
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium text-muted-foreground">Vị trí ứng tuyển *</label>
                <select
                  required
                  name="jobId"
                  value={formData.jobId}
                  onChange={handleInputChange}
                  className="w-full bg-background border border-border rounded-lg px-4 py-2 focus:ring-2 focus:ring-primary outline-none transition-all appearance-none"
                >
                  <option value="">Chọn vị trí...</option>
                  {jobs.map((job) => (
                    <option key={job.id} value={job.id}>
                      {job.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-muted-foreground">Tải tệp CV (PDF, Max 5MB) *</label>
              <div
                className={`border-2 border-dashed rounded-xl p-8 transition-all flex flex-col items-center justify-center gap-4 cursor-pointer hover:border-primary/50 hover:bg-primary/5 ${
                  file ? "border-primary bg-primary/5" : "border-border"
                }`}
                onClick={() => document.getElementById("cv-upload")?.click()}
              >
                <input
                  id="cv-upload"
                  type="file"
                  accept=".pdf"
                  className="hidden"
                  onChange={handleFileChange}
                />
                {file ? (
                  <>
                    <div className="bg-primary/20 p-4 rounded-full">
                      <FileText className="text-primary w-8 h-8" />
                    </div>
                    <div className="text-center">
                      <p className="font-medium">{file.name}</p>
                      <p className="text-sm text-muted-foreground">
                        {(file.size / (1024 * 1024)).toFixed(2)} MB
                      </p>
                    </div>
                  </>
                ) : (
                  <>
                    <div className="bg-secondary p-4 rounded-full">
                      <Upload className="text-muted-foreground w-8 h-8" />
                    </div>
                    <div className="text-center">
                      <p className="font-medium">Bấm để tải tệp hoặc kéo thả</p>
                      <p className="text-sm text-muted-foreground">Hỗ trợ định dạng PDF</p>
                    </div>
                  </>
                )}
              </div>
            </div>

            <button
              disabled={isSubmitting || !file || !formData.jobId}
              type="submit"
              className="w-full bg-primary text-primary-foreground font-bold py-4 rounded-xl hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg shadow-primary/25 flex items-center justify-center gap-2"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Đang phân tích hồ sơ...
                </>
              ) : (
                "Nộp Hồ Sơ Ngay"
              )}
            </button>
          </form>
        </div>
      </div>

      {/* Result Modal */}
      {result && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-300">
          <div className="bg-card border border-border rounded-2xl p-8 max-w-md w-full shadow-2xl scale-in-center transition-transform">
            <div className="flex flex-col items-center text-center gap-4">
              {result.success ? (
                <div className="bg-green-500/20 p-4 rounded-full">
                  <CheckCircle2 className="text-green-500 w-12 h-12" />
                </div>
              ) : (
                <div className="bg-destructive/20 p-4 rounded-full">
                  <AlertCircle className="text-destructive w-12 h-12" />
                </div>
              )}
              <h2 className="text-2xl font-bold">
                {result.success ? "Nộp Thành Công!" : "Hồ Sơ Bị Từ Chối"}
              </h2>
              <p className="text-muted-foreground leading-relaxed">
                {result.message}
              </p>
              <button
                onClick={() => {
                  if (result.success) {
                    window.location.reload();
                  } else {
                    setResult(null);
                  }
                }}
                className={`mt-4 px-8 py-3 rounded-lg font-bold transition-all ${
                  result.success
                    ? "bg-green-600 hover:bg-green-700 text-white"
                    : "bg-destructive hover:bg-destructive/90 text-white"
                }`}
              >
                {result.success ? "Quay lại Trang Chủ" : "Thử lại hồ sơ khác"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
