"use client";

import Link from "next/link";
import { useMonitoringPoints } from "@/lib/hooks/queries/qms";
import { useQuery } from "@tanstack/react-query";
import { envMonitoringApi } from "@/lib/api/services/qms";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { AlertTriangle, ChevronLeft } from "lucide-react";
import { format } from "date-fns";

export default function ExcursionsPage() {
  const { data: pointsPage } = useMonitoringPoints({ page: 1, page_size: 100 });
  const points = pointsPage?.items ?? [];

  // Fetch excursions for all active points that have had excursions
  const excursionQueries = useQuery({
    queryKey: ["all-excursions", points.map((p) => p.id)],
    queryFn: async () => {
      if (points.length === 0) return [];
      const results = await Promise.all(
        points.map(async (p) => {
          try {
            const excs = await envMonitoringApi.listExcursions(p.id);
            return excs.map((e) => ({ ...e, point: p }));
          } catch { return []; }
        })
      );
      return results.flat().sort((a, b) => new Date(b.recorded_at).getTime() - new Date(a.recorded_at).getTime());
    },
    enabled: points.length > 0,
  });

  const excursions = excursionQueries.data ?? [];

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center gap-4">
        <Link href="/qms/em">
          <Button variant="ghost" size="sm" className="-ml-2"><ChevronLeft className="w-4 h-4 mr-1" />EM Dashboard</Button>
        </Link>
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">All Excursions</h1>
          <p className="text-sm text-gray-500 mt-1">All alert and action limit exceedances across monitoring points</p>
        </div>
      </div>

      <Card className="border border-gray-200">
        <CardContent className="p-0">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="text-left px-4 py-3 font-medium text-gray-600">Point</th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">Location</th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">Value</th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">Type</th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">Recorded At</th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">Notes</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {excursionQueries.isLoading ? (
                <tr><td colSpan={6} className="px-4 py-10 text-center text-gray-400">Loading…</td></tr>
              ) : excursions.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-4 py-12 text-center">
                    <AlertTriangle className="w-8 h-8 text-gray-300 mx-auto mb-2" />
                    <p className="text-gray-400 text-sm">No excursions recorded</p>
                  </td>
                </tr>
              ) : excursions.map((ex) => (
                <tr key={ex.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3">
                    <Link href={`/qms/em/points/${ex.point_id}`} className="text-blue-600 hover:underline font-medium">
                      {(ex as { point?: { point_id: string } }).point?.point_id ?? ex.point_id}
                    </Link>
                  </td>
                  <td className="px-4 py-3 text-gray-600">{(ex as { point?: { location: string } }).point?.location ?? "—"}</td>
                  <td className="px-4 py-3 font-mono font-semibold text-red-700">{ex.value}</td>
                  <td className="px-4 py-3">
                    <Badge className={`text-xs ${ex.status === "action_limit_exceeded" ? "bg-red-100 text-red-700" : "bg-yellow-100 text-yellow-700"}`}>
                      {ex.status.replace(/_/g, " ")}
                    </Badge>
                  </td>
                  <td className="px-4 py-3 text-gray-600">{format(new Date(ex.recorded_at), "PPp")}</td>
                  <td className="px-4 py-3 text-gray-500">{ex.notes ?? "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardContent>
      </Card>
    </div>
  );
}
