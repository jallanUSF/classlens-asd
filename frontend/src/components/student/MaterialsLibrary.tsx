"use client";

import { useEffect, useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import {
  BookOpen,
  FileText,
  Eye,
  CheckCircle,
  Clock,
} from "lucide-react";
import { MaterialViewer } from "@/components/materials/MaterialViewer";

interface Material {
  id: string;
  student_id: string;
  goal_id: string;
  material_type: string;
  created_date: string;
  status: string;
  content: Record<string, unknown>;
}

interface Props {
  studentId: string;
  studentName?: string;
}

const TYPE_LABELS: Record<string, { label: string; icon: typeof FileText }> = {
  lesson_plan: { label: "Lesson Plan", icon: BookOpen },
  tracking_sheet: { label: "Tracking Sheet", icon: FileText },
  social_story: { label: "Social Story", icon: BookOpen },
  visual_schedule: { label: "Visual Schedule", icon: FileText },
  parent_comm: { label: "Parent Letter", icon: FileText },
  admin_report: { label: "Admin Report", icon: FileText },
  first_then: { label: "First-Then Board", icon: FileText },
};

const STATUS_STYLES: Record<string, { class: string; icon: typeof Clock }> = {
  draft: { class: "bg-warning/10 text-warning-foreground", icon: Clock },
  approved: { class: "bg-success/10 text-success-foreground", icon: CheckCircle },
};

export function MaterialsLibrary({ studentId, studentName }: Props) {
  const [materials, setMaterials] = useState<Material[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string | null>(null);
  const [viewingMaterial, setViewingMaterial] = useState<Material | null>(null);

  useEffect(() => {
    const ac = new AbortController();
    fetch(`/api/students/${studentId}/materials`, { signal: ac.signal })
      .then((r) => (r.ok ? r.json() : []))
      .then((data) => {
        setMaterials(data);
        setLoading(false);
      })
      .catch((err) => {
        if (err.name !== "AbortError") setLoading(false);
      });
    return () => ac.abort();
  }, [studentId]);

  if (loading) {
    return (
      <div className="space-y-2">
        <Skeleton className="h-16 w-full" />
        <Skeleton className="h-16 w-full" />
      </div>
    );
  }

  if (materials.length === 0) {
    return (
      <div className="text-center py-6">
        <BookOpen className="h-8 w-8 text-muted-foreground mx-auto mb-2" />
        <p className="text-sm text-muted-foreground">
          No materials generated yet. Ask the assistant to create lesson plans, social stories, and more.
        </p>
      </div>
    );
  }

  // Unique types for filter chips
  const types = [...new Set(materials.map((m) => m.material_type))];
  const filtered = filter
    ? materials.filter((m) => m.material_type === filter)
    : materials;

  return (
    <div className="space-y-3">
      {/* Filter chips */}
      {types.length > 1 && (
        <div className="flex gap-2 flex-wrap">
          <Badge
            variant={filter === null ? "default" : "outline"}
            className="cursor-pointer text-xs"
            onClick={() => setFilter(null)}
          >
            All ({materials.length})
          </Badge>
          {types.map((t) => {
            const info = TYPE_LABELS[t];
            const count = materials.filter((m) => m.material_type === t).length;
            return (
              <Badge
                key={t}
                variant={filter === t ? "default" : "outline"}
                className="cursor-pointer text-xs"
                onClick={() => setFilter(t)}
              >
                {info?.label || t} ({count})
              </Badge>
            );
          })}
        </div>
      )}

      {/* Material cards */}
      {/* Material Viewer Sheet */}
      <MaterialViewer
        material={viewingMaterial}
        studentName={studentName || "Student"}
        open={viewingMaterial !== null}
        onOpenChange={(open) => {
          if (!open) setViewingMaterial(null);
        }}
        onApprove={(id) => {
          setMaterials((prev) =>
            prev.map((m) => (m.id === id ? { ...m, status: "approved" } : m))
          );
          setViewingMaterial(null);
        }}
        onRegenerate={() => {
          setViewingMaterial(null);
        }}
      />

      {filtered.map((mat) => {
        const typeInfo = TYPE_LABELS[mat.material_type] || {
          label: mat.material_type,
          icon: FileText,
        };
        const statusInfo = STATUS_STYLES[mat.status] || STATUS_STYLES.draft;
        const TypeIcon = typeInfo.icon;
        const StatusIcon = statusInfo.icon;

        return (
          <Card key={mat.id}>
            <CardContent className="p-3">
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded bg-primary/10 flex items-center justify-center shrink-0">
                  <TypeIcon className="h-4 w-4 text-primary" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium truncate">
                      {typeInfo.label}
                    </span>
                    <Badge
                      variant="secondary"
                      className={`text-[10px] px-1.5 py-0 h-4 gap-0.5 ${statusInfo.class}`}
                    >
                      <StatusIcon className="h-2.5 w-2.5" />
                      {mat.status}
                    </Badge>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    {mat.goal_id ? `Goal: ${mat.goal_id} · ` : ""}
                    {mat.created_date}
                  </p>
                </div>
                <Button
                  size="sm"
                  variant="outline"
                  className="text-xs h-7 gap-1"
                  onClick={() => setViewingMaterial(mat)}
                >
                  <Eye className="h-3 w-3" />
                  View
                </Button>
              </div>
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
}
