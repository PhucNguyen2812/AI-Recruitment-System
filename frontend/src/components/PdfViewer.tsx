"use client"

import * as React from "react"
import { X, Download, ZoomIn, ZoomOut, ExternalLink } from "lucide-react"

interface PdfViewerProps {
    url: string
    candidateName: string
    onClose: () => void
}

export default function PdfViewer({ url, candidateName, onClose }: PdfViewerProps) {
    const [zoom, setZoom] = React.useState(100)
    const [loading, setLoading] = React.useState(true)

    const increaseZoom = () => setZoom((z) => Math.min(z + 25, 200))
    const decreaseZoom = () => setZoom((z) => Math.max(z - 25, 50))

    return (
        <div className="fixed inset-0 z-50 flex">
            {/* Backdrop */}
            <div
                className="absolute inset-0 bg-black/60 backdrop-blur-sm"
                onClick={onClose}
            />

            {/* Panel */}
            <div className="relative ml-auto flex flex-col w-full max-w-2xl h-full bg-neutral-950 border-l border-neutral-800 shadow-2xl z-10">
                {/* Header */}
                <div className="flex items-center justify-between px-4 py-3 border-b border-neutral-800 bg-neutral-900/80">
                    <div>
                        <p className="text-sm font-semibold text-white truncate max-w-xs">{candidateName}</p>
                        <p className="text-xs text-neutral-500">CV gốc</p>
                    </div>
                    <div className="flex items-center gap-1">
                        {/* Zoom */}
                        <button
                            onClick={decreaseZoom}
                            className="p-1.5 rounded-md hover:bg-neutral-800 text-neutral-400 hover:text-white transition-colors"
                            title="Thu nhỏ"
                        >
                            <ZoomOut className="h-4 w-4" />
                        </button>
                        <span className="text-xs text-neutral-500 w-12 text-center">{zoom}%</span>
                        <button
                            onClick={increaseZoom}
                            className="p-1.5 rounded-md hover:bg-neutral-800 text-neutral-400 hover:text-white transition-colors"
                            title="Phóng to"
                        >
                            <ZoomIn className="h-4 w-4" />
                        </button>

                        {/* Open in new tab */}
                        <a
                            href={url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="p-1.5 rounded-md hover:bg-neutral-800 text-neutral-400 hover:text-white transition-colors ml-1"
                            title="Mở trong tab mới"
                        >
                            <ExternalLink className="h-4 w-4" />
                        </a>

                        {/* Download */}
                        <a
                            href={url}
                            download={`${candidateName}_CV.pdf`}
                            className="p-1.5 rounded-md hover:bg-neutral-800 text-neutral-400 hover:text-white transition-colors"
                            title="Tải về"
                        >
                            <Download className="h-4 w-4" />
                        </a>

                        {/* Close */}
                        <button
                            onClick={onClose}
                            className="p-1.5 rounded-md hover:bg-neutral-800 text-neutral-400 hover:text-white transition-colors ml-1"
                            title="Đóng"
                        >
                            <X className="h-4 w-4" />
                        </button>
                    </div>
                </div>

                {/* PDF Iframe */}
                <div className="flex-1 overflow-auto bg-neutral-900 relative">
                    {loading && (
                        <div className="absolute inset-0 flex items-center justify-center bg-neutral-950">
                            <div className="text-center">
                                <div className="h-8 w-8 rounded-full border-2 border-primary border-t-transparent animate-spin mx-auto mb-3" />
                                <p className="text-xs text-neutral-500">Đang tải PDF...</p>
                            </div>
                        </div>
                    )}
                    <iframe
                        src={`${url}#toolbar=0&navpanes=0`}
                        className="w-full h-full border-none"
                        style={{
                            transform: `scale(${zoom / 100})`,
                            transformOrigin: "top center",
                            height: zoom !== 100 ? `${10000 / zoom}%` : "100%",
                        }}
                        title={`CV của ${candidateName}`}
                        onLoad={() => setLoading(false)}
                    />
                </div>
            </div>
        </div>
    )
}
