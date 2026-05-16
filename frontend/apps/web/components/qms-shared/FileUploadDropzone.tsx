"use client"

import { useCallback, useState } from "react"
import { Upload, File, X, AlertCircle, CheckCircle2, Loader2 } from "lucide-react"
import { cn } from "@/lib/utils"

type VirusScanStatus = "pending" | "clean" | "infected" | "error"

interface UploadedFile {
  id: string
  name: string
  size: number
  progress: number
  virusScan: VirusScanStatus
  error?: string
}

interface FileUploadDropzoneProps {
  onFilesSelected: (files: File[]) => void
  accept?: string[]
  maxSize?: number
  multiple?: boolean
  className?: string
}

const MAX_SIZE_MB = 100

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

const virusStatusIcon: Record<VirusScanStatus, { icon: typeof AlertCircle; className: string }> = {
  pending: { icon: Loader2, className: "text-muted-foreground animate-spin" },
  clean: { icon: CheckCircle2, className: "text-emerald-500" },
  infected: { icon: AlertCircle, className: "text-red-500" },
  error: { icon: AlertCircle, className: "text-amber-500" },
}

export function FileUploadDropzone({
  onFilesSelected,
  accept,
  maxSize = MAX_SIZE_MB * 1024 * 1024,
  multiple = false,
  className,
}: FileUploadDropzoneProps) {
  const [files, setFiles] = useState<UploadedFile[]>([])
  const [dragOver, setDragOver] = useState(false)

  const addFiles = useCallback(
    (incoming: File[]) => {
      const mapped: UploadedFile[] = incoming.map((f) => ({
        id: crypto.randomUUID(),
        name: f.name,
        size: f.size,
        progress: 0,
        virusScan: "pending" as VirusScanStatus,
      }))
      setFiles((prev) => (multiple ? [...prev, ...mapped] : mapped))
      onFilesSelected(incoming)
    },
    [multiple, onFilesSelected],
  )

  const removeFile = useCallback((id: string) => {
    setFiles((prev) => prev.filter((f) => f.id !== id))
  }, [])

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault()
      setDragOver(false)
      const dropped = Array.from(e.dataTransfer.files)
      if (dropped.length > 0) addFiles(dropped)
    },
    [addFiles],
  )

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      if (e.target.files && e.target.files.length > 0) {
        addFiles(Array.from(e.target.files))
      }
    },
    [addFiles],
  )

  return (
    <div className={cn("space-y-3", className)}>
      <div
        onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        onClick={() => document.getElementById("file-drop-input")?.click()}
        className={cn(
          "flex flex-col items-center justify-center gap-2 rounded-lg border-2 border-dashed p-8 text-center cursor-pointer transition-colors",
          dragOver
            ? "border-blue-400 bg-blue-50 dark:bg-blue-950"
            : "border-slate-300 hover:border-slate-400 dark:border-slate-700 dark:hover:border-slate-600",
        )}
      >
        <Upload className="h-8 w-8 text-muted-foreground" />
        <div>
          <p className="text-sm font-medium">
            Drop files here or click to browse
          </p>
          <p className="text-xs text-muted-foreground mt-1">
            Max {MAX_SIZE_MB} MB
            {accept ? ` · ${accept.join(", ")}` : ""}
          </p>
        </div>
        <input
          id="file-drop-input"
          type="file"
          multiple={multiple}
          accept={accept?.join(",")}
          onChange={handleChange}
          className="hidden"
        />
      </div>

      {files.length > 0 && (
        <ul className="space-y-2">
          {files.map((f) => {
            const statusInfo = virusStatusIcon[f.virusScan]
            return (
              <li
                key={f.id}
                className="flex items-center gap-3 rounded-md border p-3 text-sm"
              >
                <File className="h-5 w-5 shrink-0 text-muted-foreground" />
                <div className="flex-1 min-w-0">
                  <p className="truncate font-medium">{f.name}</p>
                  <p className="text-xs text-muted-foreground">{formatSize(f.size)}</p>
                </div>
                <statusInfo.icon className={cn("h-4 w-4 shrink-0", statusInfo.className)} />
                <button
                  type="button"
                  onClick={(e) => { e.stopPropagation(); removeFile(f.id) }}
                  className="shrink-0 text-muted-foreground hover:text-destructive transition-colors"
                >
                  <X className="h-4 w-4" />
                </button>
              </li>
            )
          })}
        </ul>
      )}
    </div>
  )
}
