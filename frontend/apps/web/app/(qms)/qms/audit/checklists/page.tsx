"use client";

import { useState } from "react";
import Link from "next/link";
import { useAuditChecklists } from "@/lib/hooks/queries/qms";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ChevronLeft, BookOpen, Plus, ChevronDown, ChevronRight } from "lucide-react";
import { format } from "date-fns";

export default function AuditChecklistsPage() {
  const { data: checklists = [], isLoading } = useAuditChecklists();
  const [expanded, setExpanded] = useState<Set<string>>(new Set());

  function toggle(id: string) {
    setExpanded((s) => {
      const n = new Set(s);
      n.has(id) ? n.delete(id) : n.add(id);
      return n;
    });
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center gap-3">
        <Link href="/qms/audit">
          <Button variant="ghost" size="sm">
            <ChevronLeft className="w-4 h-4 mr-1" />
            Dashboard
          </Button>
        </Link>
        <div>
          <h1 className="text-xl font-semibold text-gray-900">Audit Checklists</h1>
          <p className="text-sm text-gray-500">Reusable checklist templates for audits</p>
        </div>
        <div className="ml-auto">
          <Button size="sm" className="bg-blue-600 hover:bg-blue-700 text-white" disabled>
            <Plus className="w-4 h-4 mr-2" />
            New Checklist
          </Button>
        </div>
      </div>

      {isLoading ? (
        <div className="text-center py-12 text-gray-400 text-sm">Loading…</div>
      ) : checklists.length === 0 ? (
        <div className="text-center py-12">
          <BookOpen className="w-10 h-10 text-gray-300 mx-auto mb-3" />
          <p className="text-gray-500 text-sm">No checklists yet</p>
          <p className="text-gray-400 text-xs mt-1">Create reusable audit checklists based on standards like ISO 9001</p>
        </div>
      ) : (
        <div className="space-y-3">
          {checklists.map((cl) => (
            <Card key={cl.id} className="border border-gray-200">
              <CardHeader className="pb-2 pt-4 px-5 cursor-pointer" onClick={() => toggle(cl.id)}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    {expanded.has(cl.id) ? (
                      <ChevronDown className="w-4 h-4 text-gray-400" />
                    ) : (
                      <ChevronRight className="w-4 h-4 text-gray-400" />
                    )}
                    <div>
                      <CardTitle className="text-sm font-semibold text-gray-900">{cl.name}</CardTitle>
                      {cl.criteria && (
                        <p className="text-xs text-gray-500 mt-0.5">{cl.criteria}</p>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge className="text-xs bg-gray-100 text-gray-600">
                      {cl.items.length} items
                    </Badge>
                    <Badge className={`text-xs ${cl.is_active ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-500"}`}>
                      {cl.is_active ? "Active" : "Inactive"}
                    </Badge>
                    <span className="text-xs text-gray-400">
                      {format(new Date(cl.created_at), "MMM d, yyyy")}
                    </span>
                  </div>
                </div>
              </CardHeader>
              {expanded.has(cl.id) && (
                <CardContent className="px-5 pb-4">
                  {cl.description && (
                    <p className="text-sm text-gray-600 mb-3">{cl.description}</p>
                  )}
                  {cl.items.length === 0 ? (
                    <p className="text-xs text-gray-400">No items</p>
                  ) : (
                    <div className="border border-gray-200 rounded overflow-hidden">
                      <table className="w-full text-xs">
                        <thead className="bg-gray-50">
                          <tr>
                            <th className="text-left px-3 py-2 font-medium text-gray-500 w-16">Clause</th>
                            <th className="text-left px-3 py-2 font-medium text-gray-500">Question</th>
                            <th className="text-left px-3 py-2 font-medium text-gray-500">Expected Evidence</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-100">
                          {cl.items
                            .slice()
                            .sort((a, b) => a.sort_order - b.sort_order)
                            .map((item) => (
                              <tr key={item.id}>
                                <td className="px-3 py-2 text-gray-500">{item.iso_clause ?? "—"}</td>
                                <td className="px-3 py-2 text-gray-800">{item.question}</td>
                                <td className="px-3 py-2 text-gray-500">{item.expected_evidence ?? "—"}</td>
                              </tr>
                            ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                </CardContent>
              )}
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
