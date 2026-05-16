"use client"

import { useState } from "react"
import { Lock, AlertCircle } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Checkbox } from "@/components/ui/checkbox"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { cn } from "@/lib/utils"

interface SignatureDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  title?: string
  description?: string
  meaning: string
  onConfirm: (signature: string) => void | Promise<void>
  isLoading?: boolean
  requireReauth?: boolean
  className?: string
}

export function SignatureDialog({
  open,
  onOpenChange,
  title = "Electronic Signature",
  description,
  meaning,
  onConfirm,
  isLoading = false,
  requireReauth = false,
  className,
}: SignatureDialogProps) {
  const [signature, setSignature] = useState("")
  const [confirmed, setConfirmed] = useState(false)
  const [error, setError] = useState("")

  const handleConfirm = async () => {
    setError("")
    if (!signature.trim()) {
      setError("Signature is required")
      return
    }
    if (!confirmed) {
      setError("Please confirm your understanding")
      return
    }
    await onConfirm(signature.trim())
    setSignature("")
    setConfirmed(false)
  }

  const handleOpenChange = (next: boolean) => {
    if (!next) {
      setSignature("")
      setConfirmed(false)
      setError("")
    }
    onOpenChange(next)
  }

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className={cn("sm:max-w-md", className)}>
        <DialogHeader>
          <div className="flex items-center gap-2">
            <Lock className="h-5 w-5 text-muted-foreground" />
            <DialogTitle>{title}</DialogTitle>
          </div>
          <DialogDescription>
            {description ?? "Sign with your credentials to authorize this action. This constitutes a legally binding electronic signature per 21 CFR Part 11."}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-2">
          <div className="rounded-md border bg-muted/30 p-3">
            <p className="text-xs text-muted-foreground uppercase tracking-wider font-medium">
              Signature Meaning
            </p>
            <p className="text-sm font-medium mt-1">{meaning}</p>
          </div>

          {requireReauth && (
            <div className="flex items-start gap-2 rounded-md border border-amber-200 bg-amber-50 p-3 dark:bg-amber-950/30 dark:border-amber-800">
              <AlertCircle className="h-4 w-4 text-amber-600 mt-0.5 shrink-0" />
              <p className="text-xs text-amber-800 dark:text-amber-200">
                Re-authentication required. Enter your current password to proceed.
              </p>
            </div>
          )}

          <div className="space-y-1.5">
            <Label htmlFor="sig-input">Signature / Passphrase</Label>
            <Input
              id="sig-input"
              type="password"
              value={signature}
              onChange={(e) => setSignature(e.target.value)}
              placeholder="Enter your e-signature passphrase"
              autoComplete="off"
            />
          </div>

          <div className="flex items-start gap-2">
            <Checkbox
              id="sig-confirm"
              checked={confirmed}
              onCheckedChange={(v) => setConfirmed(v === true)}
            />
            <Label htmlFor="sig-confirm" className="text-sm font-normal leading-tight">
              I confirm that I have reviewed the content and understand the meaning of this signature ({meaning}).
            </Label>
          </div>

          {error && (
            <p className="text-xs text-destructive">{error}</p>
          )}
        </div>

        <DialogFooter className="gap-2">
          <Button variant="outline" onClick={() => handleOpenChange(false)}>
            Cancel
          </Button>
          <Button onClick={handleConfirm} disabled={isLoading}>
            {isLoading ? "Signing..." : "Sign & Confirm"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
