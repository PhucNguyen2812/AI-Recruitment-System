"use client";

import React, { useState } from "react";
import axios from "@/lib/axios";
import { Lock, User, Eye, EyeOff, Loader2, ShieldCheck } from "lucide-react";
import { useRouter } from "next/navigation";

export default function LoginPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    username: "",
    password: "",
  });
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError("");

    try {
      const response = await axios.post("/api/auth/login", {
        email: formData.username,
        mat_khau: formData.password,
      });

      // Store token
      if (response.data.access_token) {
        localStorage.setItem("token", response.data.access_token);
        localStorage.setItem("user", JSON.stringify(response.data.user || { vai_tro: response.data.vai_tro }));
        
        console.log("Login successful, token stored. Redirecting...");
        
        // Dùng replace để tránh quay lại trang login bằng nút Back
        router.replace("/dashboard/candidates");
      } else {
        throw new Error("Không nhận được token từ máy chủ.");
      }
    } catch (error: any) {
      if (typeof error.response?.data?.detail === "string") {
        setError(error.response.data.detail);
      } else if (Array.isArray(error.response?.data?.detail)) {
        setError(error.response.data.detail[0]?.msg || "Lỗi dữ liệu đầu vào không hợp lệ.");
      } else {
        setError("Sai tên đăng nhập hoặc mật khẩu.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background text-foreground flex items-center justify-center p-6">
      <div className="w-full max-w-md bg-card border border-border rounded-2xl p-8 shadow-2xl relative overflow-hidden">
        <div className="absolute top-0 left-0 w-full h-1 bg-primary"></div>
        
        <div className="flex flex-col items-center mb-8">
          <div className="bg-primary/10 p-4 rounded-2xl mb-4">
            <ShieldCheck className="text-primary w-10 h-10" />
          </div>
          <h1 className="text-2xl font-bold">Cổng Đăng Nhập Nhân Sự</h1>
          <p className="text-muted-foreground text-sm">Hệ thống quản lý tuyển dụng thông minh</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {error && (
            <div className="bg-destructive/10 border border-destructive/20 text-destructive text-sm p-4 rounded-lg flex items-center gap-2">
              <Lock className="w-4 h-4" />
              {error}
            </div>
          )}

          <div className="space-y-2">
            <label className="text-sm font-medium text-muted-foreground">Tên đăng nhập</label>
            <div className="relative">
              <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
              <input
                required
                type="text"
                name="username"
                value={formData.username}
                onChange={handleInputChange}
                className="w-full bg-background border border-border rounded-lg pl-10 pr-4 py-3 focus:ring-2 focus:ring-primary outline-none transition-all"
                placeholder="admin_hr"
              />
            </div>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-muted-foreground">Mật khẩu</label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
              <input
                required
                type={showPassword ? "text" : "password"}
                name="password"
                value={formData.password}
                onChange={handleInputChange}
                className="w-full bg-background border border-border rounded-lg pl-10 pr-12 py-3 focus:ring-2 focus:ring-primary outline-none transition-all"
                placeholder="••••••••"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
              >
                {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
              </button>
            </div>
          </div>

          <button
            disabled={isLoading}
            type="submit"
            className="w-full bg-primary text-primary-foreground font-bold py-4 rounded-xl hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg shadow-primary/25 flex items-center justify-center gap-2"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Đang xác thực...
              </>
            ) : (
              "Đăng Nhập"
            )}
          </button>
        </form>

        <div className="mt-8 pt-6 border-t border-border text-center">
          <p className="text-sm text-muted-foreground">
            Quên mật khẩu? Vui lòng liên hệ Admin hệ thống.
          </p>
        </div>
      </div>
    </div>
  );
}
