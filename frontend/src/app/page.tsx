import Link from "next/link"
import { ArrowRight, FileText, Search, UserCheck, ShieldCheck } from "lucide-react"

export default function Home() {
  return (
    <div className="flex flex-col min-h-screen bg-black">
      {/* Header with HR login link */}
      <header className="flex items-center justify-between px-6 py-4 border-b border-neutral-800 bg-neutral-950/50 backdrop-blur-md sticky top-0 z-50">
        <div className="flex items-center gap-2">
          <div className="h-8 w-8 rounded-lg bg-primary/20 flex items-center justify-center border border-primary/30">
            <UserCheck className="h-4 w-4 text-primary" />
          </div>
          <span className="text-white font-bold tracking-tight text-lg">AHB</span>
        </div>
        <Link
          href="/login"
          className="text-sm font-medium text-neutral-400 hover:text-white transition-colors flex items-center gap-2 px-3 py-1.5 rounded-md hover:bg-neutral-800/60 border border-transparent hover:border-neutral-700/50"
        >
          <ShieldCheck className="h-4 w-4" />
          Dành cho HR
        </Link>
      </header>

      {/* Main Content */}
      <main className="flex-1 flex flex-col items-center justify-center px-4 py-16 text-center space-y-12">

        {/* Hero Section */}
        <div className="max-w-3xl space-y-6 animate-in fade-in slide-in-from-bottom-6 duration-1000">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 border border-primary/20 text-primary text-xs font-semibold uppercase tracking-wider mb-2">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-primary"></span>
            </span>
            Tuyển dụng thông minh
          </div>
          <h1 className="text-4xl md:text-6xl font-extrabold text-white tracking-tight text-balance leading-tight">
            Khởi đầu sự nghiệp với <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-emerald-400">Công ty AHB</span>
          </h1>
          <p className="text-lg md:text-xl text-neutral-400 max-w-2xl mx-auto font-medium text-balance">
            Hệ thống đánh giá ứng viên minh bạch và khách quan. Nộp hồ sơ của bạn ngay hôm nay để trở thành một phần của chúng tôi.
          </p>
        </div>

        {/* Action Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl w-full animate-in fade-in slide-in-from-bottom-8 duration-1000 delay-150 fill-mode-both">

          {/* Apply Card */}
          <Link href="/candidate/apply" className="group block">
            <div className="flex flex-col h-full text-left p-8 rounded-3xl bg-neutral-900 border border-neutral-800 hover:border-primary/50 transition-all duration-300 hover:shadow-[0_0_30px_-5px_rgba(var(--primary),0.3)] hover:-translate-y-1">
              <div className="h-14 w-14 rounded-2xl bg-primary/10 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300 group-hover:bg-primary border border-primary/20 group-hover:border-primary">
                <FileText className="h-7 w-7 text-primary group-hover:text-black transition-colors" />
              </div>
              <h3 className="text-2xl font-bold text-white mb-2 group-hover:text-primary transition-colors">Nộp hồ sơ ứng tuyển</h3>
              <p className="text-neutral-400 mb-8 flex-1">
                Gửi CV của bạn cho các vị trí đang mở. AI sẽ quét và phản hồi sơ bộ ngay lập tức.
              </p>
              <div className="flex items-center text-sm font-semibold text-white group-hover:text-primary transition-colors">
                Bắt đầu ngay <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />
              </div>
            </div>
          </Link>

          {/* Track Card */}
          <Link href="/candidate/status" className="group block">
            <div className="flex flex-col h-full text-left p-8 rounded-3xl bg-neutral-900 border border-neutral-800 hover:border-blue-500/50 transition-all duration-300 hover:shadow-[0_0_30px_-5px_rgba(59,130,246,0.2)] hover:-translate-y-1">
              <div className="h-14 w-14 rounded-2xl bg-blue-500/10 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300 group-hover:bg-blue-500 border border-blue-500/20 group-hover:border-blue-500">
                <Search className="h-7 w-7 text-blue-400 group-hover:text-white transition-colors" />
              </div>
              <h3 className="text-2xl font-bold text-white mb-2 group-hover:text-blue-400 transition-colors">Theo dõi tiến độ</h3>
              <p className="text-neutral-400 mb-8 flex-1">
                Bạn đã nộp CV? Tra cứu trạng thái và xem quá trình đánh giá từ hệ thống AI của chúng tôi.
              </p>
              <div className="flex items-center text-sm font-semibold text-white group-hover:text-blue-400 transition-colors">
                Kiểm tra ngay <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />
              </div>
            </div>
          </Link>

        </div>
      </main>

      {/* Footer */}
      <footer className="py-8 text-center border-t border-neutral-800/50 text-neutral-600 text-sm">
        <p>Được thực hiện bởi nhóm 23</p>
      </footer>
    </div>
  )
}
