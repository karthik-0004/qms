"use client"

import { useState, lazy, Suspense } from "react"
import { useRouter } from "next/navigation"
import { ArrowLeft, BookOpen, Home, Plus, Search, ChevronLeft, ChevronRight } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Skeleton } from "@/components/ui/skeleton"
import { useCourses, useCreateCourse } from "@/lib/hooks/queries/qms"
import type { Course } from "@/lib/api/services/qms"
import { toast } from "sonner"
import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import { createCourseSchema, type CreateCourseInput } from "@/validators/qms/training.validator"

const Dialog = lazy(() => import("@/components/ui/dialog").then((m) => ({ default: m.Dialog })));
const DialogContent = lazy(() => import("@/components/ui/dialog").then((m) => ({ default: m.DialogContent })));
const DialogDescription = lazy(() => import("@/components/ui/dialog").then((m) => ({ default: m.DialogDescription })));
const DialogFooter = lazy(() => import("@/components/ui/dialog").then((m) => ({ default: m.DialogFooter })));
const DialogHeader = lazy(() => import("@/components/ui/dialog").then((m) => ({ default: m.DialogHeader })));
const DialogTitle = lazy(() => import("@/components/ui/dialog").then((m) => ({ default: m.DialogTitle })));
const DialogTrigger = lazy(() => import("@/components/ui/dialog").then((m) => ({ default: m.DialogTrigger })));

const ACTIVE_CONFIG = {
  active: { label: "Active", color: "bg-green-100 text-green-700" },
  inactive: { label: "Inactive", color: "bg-slate-100 text-slate-600" },
} as const;

const PAGE_SIZE = 10;

export default function CoursesPage() {
  const router = useRouter();
  const [search, setSearch] = useState("");
  const [departmentFilter, setDepartmentFilter] = useState("");
  const [mandatoryFilter, setMandatoryFilter] = useState<"" | "mandatory">("");
  const [page, setPage] = useState(1);
  const [dialogOpen, setDialogOpen] = useState(false);

  const { data, isLoading: loading } = useCourses({
    page,
    page_size: PAGE_SIZE,
    department: departmentFilter || undefined,
    is_mandatory: mandatoryFilter === "mandatory" ? true : undefined,
  });

  const createCourse = useCreateCourse();

  const courses: Course[] = data?.items ?? [];
  const totalItems = data?.total ?? 0;
  const totalPages = Math.max(1, Math.ceil(totalItems / PAGE_SIZE));
  const filtered = courses.filter((c) => {
    const q = search.trim().toLowerCase();
    if (!q) return true;
    return (
      c.course_code.toLowerCase().includes(q) ||
      c.title.toLowerCase().includes(q) ||
      (c.department ?? "").toLowerCase().includes(q)
    );
  });
  const paginated = filtered;

  const form = useForm<CreateCourseInput>({
    resolver: zodResolver(createCourseSchema),
    defaultValues: {
      course_code: "",
      title: "",
      course_type: "online",
      department: "",
      description: "",
      duration_hours: undefined,
      passing_score: 80,
      requires_certification: false,
      recurrence_days: undefined,
      is_mandatory: false,
    },
  });

  const onSubmit = (values: CreateCourseInput) => {
    createCourse.mutate(values, {
      onSuccess: () => {
        toast.success("Course created successfully");
        setDialogOpen(false);
        form.reset();
      },
      onError: (error: any) => {
        const errorMessage = error?.response?.data?.detail || error?.message || "Failed to create course";
        toast.error(errorMessage);
      },
    });
  };

  return (
    <div className="space-y-6 p-6 max-w-7xl mx-auto">
      <div className="flex items-center gap-2 text-sm">
        <Button variant="ghost" size="sm" onClick={() => router.push("/dashboard")} className="h-7 px-2 text-muted-foreground hover:text-foreground">
          <ArrowLeft className="h-4 w-4 mr-1" /> Back
        </Button>
        <span className="text-muted-foreground">/</span>
        <Button variant="ghost" size="sm" onClick={() => router.push("/qms/training")} className="h-7 px-2 text-muted-foreground hover:text-foreground">
          <Home className="h-4 w-4 mr-1" /> Training
        </Button>
        <span className="text-muted-foreground">/</span>
        <span className="text-foreground font-medium">Courses</span>
      </div>

      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
            <BookOpen className="h-6 w-6" />
            Training Courses
          </h1>
          <p className="text-muted-foreground text-sm mt-1">Course catalog and management</p>
        </div>
        <Suspense fallback={<Button size="sm" className="gap-1.5"><Plus className="h-4 w-4" />New Course</Button>}>
          <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
            <DialogTrigger asChild>
              <Button size="sm" className="gap-1.5"><Plus className="h-4 w-4" />New Course</Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Create New Course</DialogTitle>
                <DialogDescription>Add a new course to your training catalog.</DialogDescription>
              </DialogHeader>
              <form onSubmit={form.handleSubmit(onSubmit)}>
                <div className="space-y-4 py-4">
                  <div className="space-y-2">
                    <Label htmlFor="course_code">Course Code</Label>
                    <Input id="course_code" placeholder="TRN-001" aria-invalid={!!form.formState.errors.course_code} {...form.register("course_code")} />
                    {form.formState.errors.course_code?.message && <p className="text-xs text-destructive">{form.formState.errors.course_code.message}</p>}
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="title">Title</Label>
                    <Input id="title" placeholder="Course title" aria-invalid={!!form.formState.errors.title} {...form.register("title")} />
                    {form.formState.errors.title?.message && <p className="text-xs text-destructive">{form.formState.errors.title.message}</p>}
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="department">Department</Label>
                    <Input id="department" placeholder="e.g. QA, Production" {...form.register("department")} />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="course_type">Course Type</Label>
                    <select id="course_type" className="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm" {...form.register("course_type")}>
                      <option value="online">Online</option>
                      <option value="classroom">Classroom</option>
                      <option value="blended">Blended</option>
                      <option value="document_read">Document Read</option>
                    </select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="duration_hours">Duration (hours)</Label>
                    <Input id="duration_hours" type="number" min={0} step={0.5} {...form.register("duration_hours")} />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="passing_score">Passing Score</Label>
                    <Input id="passing_score" type="number" min={0} max={100} step={1} {...form.register("passing_score")} />
                  </div>
                  <div className="flex items-center gap-2">
                    <input id="requires_certification" type="checkbox" className="h-4 w-4 rounded border border-input" {...form.register("requires_certification")} />
                    <Label htmlFor="requires_certification">Requires certification</Label>
                  </div>
                  <div className="flex items-center gap-2">
                    <input id="is_mandatory" type="checkbox" className="h-4 w-4 rounded border border-input" {...form.register("is_mandatory")} />
                    <Label htmlFor="is_mandatory">Mandatory</Label>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="description">Description</Label>
                    <Input id="description" placeholder="Optional description" {...form.register("description")} />
                  </div>
                </div>
                <DialogFooter>
                  <Button type="button" variant="outline" onClick={() => setDialogOpen(false)} disabled={createCourse.isPending}>Cancel</Button>
                  <Button type="submit" disabled={createCourse.isPending}>{createCourse.isPending ? "Creating..." : "Create Course"}</Button>
                </DialogFooter>
              </form>
            </DialogContent>
          </Dialog>
        </Suspense>
      </div>

      <Card>
        <CardContent className="pt-4">
          <div className="flex flex-col sm:flex-row gap-3">
            <div className="relative flex-1">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input placeholder="Search by code, title, department..." className="pl-8" value={search} onChange={(e) => { setSearch(e.target.value); setPage(1); }} />
            </div>
            <Input placeholder="Filter department..." value={departmentFilter} onChange={(e) => { setDepartmentFilter(e.target.value); setPage(1); }} className="sm:max-w-[220px]" />
            <select value={mandatoryFilter} onChange={(e) => { setMandatoryFilter(e.target.value as "" | "mandatory"); setPage(1); }} className="h-9 rounded-md border border-input bg-background px-3 text-sm sm:max-w-[180px]">
              <option value="">All Courses</option>
              <option value="mandatory">Mandatory Only</option>
            </select>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-0"><CardTitle className="text-sm font-medium text-muted-foreground">{loading ? "Loading..." : `${totalItems} courses`}</CardTitle></CardHeader>
        <CardContent className="pt-2">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left text-muted-foreground">
                  <th className="pb-2 pr-4 font-medium">Code</th>
                  <th className="pb-2 pr-4 font-medium">Title</th>
                  <th className="pb-2 pr-4 font-medium hidden sm:table-cell">Department</th>
                  <th className="pb-2 pr-4 font-medium hidden md:table-cell">Type</th>
                  <th className="pb-2 pr-4 font-medium hidden lg:table-cell">Duration</th>
                  <th className="pb-2 pr-4 font-medium hidden md:table-cell">Mandatory</th>
                  <th className="pb-2 pr-4 font-medium">Status</th>
                  <th className="pb-2 pr-4 font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {loading ? Array.from({ length: PAGE_SIZE }).map((_, i) => (
                  <tr key={i} className="border-b">{Array.from({ length: 8 }).map((_, j) => (<td key={j} className="py-3 pr-4"><Skeleton className="h-4 w-20" /></td>))}</tr>
                )) : paginated.map((c) => {
                  const cfg = c.is_active ? ACTIVE_CONFIG.active : ACTIVE_CONFIG.inactive;
                  return (
                    <tr key={c.id} className="border-b last:border-0 hover:bg-muted/30 transition-colors cursor-pointer" onClick={() => router.push(`/qms/training/courses/${c.id}`)}>
                      <td className="py-3 pr-4 font-mono font-semibold text-xs">{c.course_code}</td>
                      <td className="py-3 pr-4 font-medium max-w-[200px] truncate">{c.title}</td>
                      <td className="py-3 pr-4 text-muted-foreground hidden sm:table-cell">{c.department ?? "—"}</td>
                      <td className="py-3 pr-4 capitalize text-muted-foreground hidden md:table-cell">{c.course_type.replace(/_/g, " ")}</td>
                      <td className="py-3 pr-4 text-muted-foreground hidden lg:table-cell">{c.duration_hours ? `${c.duration_hours}h` : "—"}</td>
                      <td className="py-3 pr-4 hidden md:table-cell">{c.is_mandatory ? "Yes" : "No"}</td>
                      <td className="py-3 pr-4"><span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${cfg.color}`}>{cfg.label}</span></td>
                      <td className="py-3 pr-4">
                        <Button variant="ghost" size="sm" onClick={(e) => { e.stopPropagation(); router.push(`/qms/training/courses/${c.id}`); }}>View</Button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          {!loading && totalItems > PAGE_SIZE && (
            <div className="flex items-center justify-between mt-4 pt-4 border-t">
              <p className="text-xs text-muted-foreground">Page {page} of {totalPages}</p>
              <div className="flex gap-2">
                <Button variant="outline" size="sm" onClick={() => setPage((p) => Math.max(1, p - 1))} disabled={page === 1}><ChevronLeft className="h-4 w-4" /></Button>
                <Button variant="outline" size="sm" onClick={() => setPage((p) => Math.min(totalPages, p + 1))} disabled={page === totalPages}><ChevronRight className="h-4 w-4" /></Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
