import axios from 'axios';

const axiosInstance = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor: Tự động gắn Token vào header Authorization
axiosInstance.interceptors.request.use(
  (config) => {
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem("token");
      if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor: Xử lý lỗi 401 Unauthorized
axiosInstance.interceptors.response.use(
  (response) => response,
  (error) => {
    // Chỉ redirect nếu gặp lỗi 401 và không phải đang ở trang login
    if (error.response?.status === 401) {
      // Only perform client-side redirect if window is defined
      if (typeof window !== 'undefined' && !window.location.pathname.includes('/login')) {
        localStorage.clear();
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export default axiosInstance;
