"use client";

import { useState, useRef, useCallback } from "react";
import { useRouter } from "next/navigation";
import { ArrowLeft, FileText, PenLine, Upload, Save } from "lucide-react";
import { useForm } from "react-hook-form";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { toast } from "sonner";
import { useCreateDocument } from "@/lib/hooks/queries/qms";
import { documentsApi } from "@/lib/api/services/qms";
import { handleApiError } from "@/lib/api/client";

const DOC_TYPES = ["SOP", "Work Instruction", "Policy", "Form", "Record", "Manual", "Template"];

type AuthoringMode = "editor" | "upload";

interface FormValues {
  doc_number: string;
  title: string;
  doc_type: string;
  description: string;
  department: string;
  tags: string;
}

export default function CreateDocumentPage() {
  const router = useRouter();
  const createDoc = useCreateDocument();
  const [authoringMode, setAuthoringMode] = useState<AuthoringMode>("upload");
  const [isSaving, setIsSaving] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [editorContent, setEditorContent] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<FormValues>({
    defaultValues: {
      doc_number: "",
      title: "",
      doc_type: "SOP",
      description: "",
      department: "",
      tags: "",
    },
  });

  const selectedDocType = watch("doc_type");

  const onSubmit = useCallback(async (values: FormValues) => {
    setIsSaving(true);
    try {
      const tags = values.tags
        ? values.tags.split(",").map((t) => t.trim()).filter(Boolean)
        : undefined;

      const doc = await createDoc.mutateAsync({
        doc_number: values.doc_number,
        title: values.title,
        doc_type: values.doc_type,
        description: values.description || undefined,
        department: values.department || undefined,
        tags,
      });

      if (authoringMode === "editor" && editorContent) {
        await documentsApi.saveContent(doc.id, {
          authoring_mode: "editor",
          html_snapshot: editorContent,
          content_ast: { blocks: [] },
        });
      } else if (authoringMode === "upload" && selectedFile) {
        const formData = new FormData();
        formData.append("file", selectedFile);
        await documentsApi.uploadFile(doc.id, formData);
      }

      toast.success("Document created successfully");
      router.push(`/qms/documents/${doc.id}`);
    } catch (err) {
      handleApiError(err, "Failed to create document");
    } finally {
      setIsSaving(false);
    }
  }, [authoringMode, editorContent, selectedFile, createDoc, router]);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
      <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-6 flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => router.back()}>
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <div>
            <h1 className="text-2xl font-semibold text-gray-900 dark:text-gray-100">
              Create New Document
            </h1>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Fill in the document metadata, choose your authoring mode, and save.
            </p>
          </div>
        </div>

        <form onSubmit={handleSubmit(onSubmit)}>
          {/* Authoring Mode */}
          <Card className="mb-6">
            <CardContent className="pt-6">
              <Label className="mb-3 block text-sm font-medium">Authoring Mode</Label>
              <RadioGroup
                value={authoringMode}
                onValueChange={(v) => setAuthoringMode(v as AuthoringMode)}
                className="flex gap-6"
              >
                <div className="flex items-center gap-2">
                  <RadioGroupItem value="upload" id="mode-upload" />
                  <Label htmlFor="mode-upload" className="flex items-center gap-2 cursor-pointer">
                    <Upload className="h-4 w-4" />
                    File Upload (Mode B)
                  </Label>
                </div>
                <div className="flex items-center gap-2">
                  <RadioGroupItem value="editor" id="mode-editor" />
                  <Label htmlFor="mode-editor" className="flex items-center gap-2 cursor-pointer">
                    <PenLine className="h-4 w-4" />
                    Editor (Mode A)
                  </Label>
                </div>
              </RadioGroup>
            </CardContent>
          </Card>

          {/* Three-column layout */}
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
            {/* Left: Main form */}
            <div className="lg:col-span-2 space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Document Information</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                    <div className="space-y-2">
                      <Label htmlFor="doc_number">Document Number</Label>
                      <Input
                        id="doc_number"
                        placeholder="Auto-generated if left empty"
                        {...register("doc_number")}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="doc_type">Document Type *</Label>
                      <Select
                        value={selectedDocType}
                        onValueChange={(v) => {
                          const nativeInput = document.querySelector<HTMLInputElement>("input[name='doc_type']");
                          if (nativeInput) {
                            const nativeSetter = Object.getOwnPropertyDescriptor(
                              window.HTMLInputElement.prototype,
                              "value"
                            )?.set;
                            nativeSetter?.call(nativeInput, v);
                            nativeInput.dispatchEvent(new Event("input", { bubbles: true }));
                          }
                        }}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Select type" />
                        </SelectTrigger>
                        <SelectContent>
                          {DOC_TYPES.map((t) => (
                            <SelectItem key={t} value={t}>{t}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                      <input type="hidden" {...register("doc_type", { required: true })} />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="title">Title *</Label>
                    <Input
                      id="title"
                      placeholder="Document title"
                      {...register("title", { required: true })}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="description">Description</Label>
                    <Textarea
                      id="description"
                      placeholder="Brief description of the document"
                      rows={4}
                      {...register("description")}
                    />
                  </div>

                  {/* Editor / Upload area */}
                  {authoringMode === "editor" && (
                    <div className="space-y-2">
                      <Label>Content (HTML)</Label>
                      <Textarea
                        placeholder="Paste or type HTML content..."
                        rows={12}
                        value={editorContent}
                        onChange={(e) => setEditorContent(e.target.value)}
                        className="font-mono text-sm"
                      />
                    </div>
                  )}

                  {authoringMode === "upload" && (
                    <div className="space-y-2">
                      <Label>File Attachment</Label>
                      <div
                        className="flex cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed border-gray-300 p-8 hover:border-blue-400 dark:border-gray-600 dark:hover:border-blue-500"
                        onClick={() => fileInputRef.current?.click()}
                      >
                        <FileText className="mb-2 h-8 w-8 text-gray-400" />
                        <p className="text-sm text-gray-500 dark:text-gray-400">
                          {selectedFile ? selectedFile.name : "Click to upload a file"}
                        </p>
                        <p className="text-xs text-gray-400">PDF, DOCX, XLSX — max 50 MB</p>
                        <input
                          ref={fileInputRef}
                          type="file"
                          className="hidden"
                          onChange={(e) => setSelectedFile(e.target.files?.[0] ?? null)}
                        />
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>

            {/* Right: Settings sidebar */}
            <div className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Settings</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="department">Department</Label>
                    <Input
                      id="department"
                      placeholder="e.g. Quality, Operations"
                      {...register("department")}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="tags">Tags</Label>
                    <Input
                      id="tags"
                      placeholder="Comma-separated tags"
                      {...register("tags")}
                    />
                    <p className="text-xs text-gray-400">
                      e.g. ISO-9001, audit, training
                    </p>
                  </div>

                  <Button
                    type="submit"
                    className="w-full"
                    disabled={isSaving}
                  >
                    <Save className="mr-2 h-4 w-4" />
                    {isSaving ? "Saving..." : "Create Document"}
                  </Button>
                </CardContent>
              </Card>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}
