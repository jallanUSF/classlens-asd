"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetDescription,
} from "@/components/ui/sheet";
import { Printer, CheckCircle, RefreshCw, X } from "lucide-react";
import { LessonPlanView } from "./LessonPlanView";
import { ParentLetterView } from "./ParentLetterView";
import { AdminReportView } from "./AdminReportView";
import { SocialStoryView } from "./SocialStoryView";
import { TrackingSheetView } from "./TrackingSheetView";
import { VisualScheduleView } from "./VisualScheduleView";
import { FirstThenView } from "./FirstThenView";
import { consumeSseJob } from "@/lib/sseJob";

interface Material {
  id: string;
  student_id: string;
  goal_id: string;
  material_type: string;
  created_date: string;
  status: string;
  content: Record<string, unknown>;
  language?: string;
}

// Hoisted outside the component so the array identity is stable and
// mapping over it never re-creates per render.
const LANGUAGES: ReadonlyArray<{ code: string; label: string }> = [
  { code: "en", label: "EN" },
  { code: "es", label: "ES" },
  { code: "vi", label: "VI" },
  { code: "zh", label: "ZH" },
];

interface Props {
  material: Material | null;
  studentName: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onApprove?: (materialId: string) => void;
  onRegenerate?: (materialId: string) => void;
}

const TYPE_TITLES: Record<string, string> = {
  lesson_plan: "Lesson Plan",
  parent_comm: "Parent Letter",
  admin_report: "Admin Report",
  social_story: "Social Story",
  tracking_sheet: "Tracking Sheet",
  visual_schedule: "Visual Schedule",
  first_then: "First-Then Board",
};

export function MaterialViewer({
  material,
  studentName,
  open,
  onOpenChange,
  onApprove,
  onRegenerate,
}: Props) {
  const [approving, setApproving] = useState(false);
  // Local copy so a language regenerate can swap the letter content/language
  // without needing the parent to refetch the whole materials list.
  const [liveMaterial, setLiveMaterial] = useState<Material | null>(material);
  const [regenerating, setRegenerating] = useState(false);

  // Sync when the parent picks a different material. Primitive id dep keeps
  // this from re-running on every unrelated parent re-render.
  useEffect(() => {
    setLiveMaterial(material);
  }, [material?.id]);

  if (!liveMaterial) return null;

  const activeLanguage = liveMaterial.language ?? "en";
  const isParentComm = liveMaterial.material_type === "parent_comm";

  const handleApprove = async () => {
    setApproving(true);
    try {
      const res = await fetch(
        `/api/materials/${liveMaterial.student_id}/${liveMaterial.id}/approve`,
        { method: "PUT" }
      );
      if (res.ok) {
        onApprove?.(liveMaterial.id);
      }
    } finally {
      setApproving(false);
    }
  };

  const handlePrint = () => {
    window.print();
  };

  const handleLanguageSelect = async (code: string) => {
    if (code === activeLanguage || regenerating) return;
    setRegenerating(true);
    try {
      const res = await fetch("/api/materials/generate/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          student_id: liveMaterial.student_id,
          goal_id: liveMaterial.goal_id,
          material_type: "parent_comm",
          language: code,
        }),
      });
      const fresh = await consumeSseJob<Material>(res);
      // Functional setState — avoids stale-closure surprises if the user
      // clicks another language while this promise is still in flight.
      setLiveMaterial((prev) =>
        prev
          ? {
              ...prev,
              content: fresh.content,
              language: fresh.language ?? code,
              created_date: fresh.created_date ?? prev.created_date,
            }
          : prev
      );
    } catch {
      // Swallow — the language button reverts to the previous state on error.
    } finally {
      setRegenerating(false);
    }
  };

  function renderContent() {
    if (!liveMaterial) return null;
    const c = liveMaterial.content;
    const date = liveMaterial.created_date;
    const goalId = liveMaterial.goal_id;

    switch (liveMaterial.material_type) {
      case "lesson_plan":
        return (
          <LessonPlanView
            content={c as Parameters<typeof LessonPlanView>[0]["content"]}
            studentName={studentName}
            goalId={goalId}
            date={date}
          />
        );
      case "parent_comm":
        return (
          <ParentLetterView
            content={c as Parameters<typeof ParentLetterView>[0]["content"]}
            studentName={studentName}
            date={date}
            language={activeLanguage}
          />
        );
      case "admin_report":
        return (
          <AdminReportView
            content={c as Parameters<typeof AdminReportView>[0]["content"]}
            studentName={studentName}
            date={date}
          />
        );
      case "social_story":
        return (
          <SocialStoryView
            content={c as Parameters<typeof SocialStoryView>[0]["content"]}
            studentName={studentName}
            date={date}
          />
        );
      case "tracking_sheet":
        return (
          <TrackingSheetView
            content={c as Parameters<typeof TrackingSheetView>[0]["content"]}
            studentName={studentName}
            goalId={goalId}
            date={date}
          />
        );
      case "visual_schedule":
        return (
          <VisualScheduleView
            content={c as Parameters<typeof VisualScheduleView>[0]["content"]}
            studentName={studentName}
            date={date}
          />
        );
      case "first_then":
        return (
          <FirstThenView
            content={c as string | Record<string, unknown>}
            studentName={studentName}
            date={date}
          />
        );
      default:
        return (
          <div className="text-sm text-muted-foreground">
            <p>Unknown material type: {liveMaterial.material_type}</p>
            <pre className="mt-2 text-xs bg-muted p-3 rounded overflow-auto">
              {JSON.stringify(c, null, 2)}
            </pre>
          </div>
        );
    }
  }

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent
        side="right"
        showCloseButton={false}
        className="w-full sm:max-w-2xl overflow-y-auto"
      >
        <SheetHeader className="print:hidden">
          <div className="flex items-center justify-between">
            <div>
              <SheetTitle>
                {TYPE_TITLES[liveMaterial.material_type] || liveMaterial.material_type}
              </SheetTitle>
              <SheetDescription>
                {studentName} &middot; {liveMaterial.created_date}
              </SheetDescription>
            </div>
            <Button
              variant="ghost"
              size="icon-sm"
              onClick={() => onOpenChange(false)}
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
          {isParentComm && (
            <div
              className="flex items-center gap-1.5 pt-2"
              role="group"
              aria-label="Letter language"
            >
              <span className="text-[11px] uppercase tracking-wide text-muted-foreground mr-1">
                Language
              </span>
              {LANGUAGES.map((lang) => {
                const active = lang.code === activeLanguage;
                return (
                  <Button
                    key={lang.code}
                    size="sm"
                    variant={active ? "default" : "outline"}
                    className="h-7 px-2.5 text-xs"
                    disabled={regenerating}
                    aria-pressed={active}
                    onClick={() => handleLanguageSelect(lang.code)}
                  >
                    {lang.label}
                  </Button>
                );
              })}
              {regenerating && (
                <span className="text-[11px] text-muted-foreground ml-1">
                  Translating…
                </span>
              )}
            </div>
          )}
        </SheetHeader>

        {/* Material content */}
        <div className="px-4 pb-4">{renderContent()}</div>

        {/* Footer */}
        <div className="text-center text-[10px] text-muted-foreground mt-4 px-4">
          Generated by ClassLens ASD &middot; Teacher review required
        </div>

        {/* Action buttons — hidden when printing */}
        <div className="sticky bottom-0 bg-popover border-t border-border p-3 flex gap-2 justify-end print:hidden">
          {liveMaterial.status !== "approved" && (
            <Button
              size="sm"
              variant="outline"
              className="gap-1.5"
              onClick={handleApprove}
              disabled={approving}
            >
              <CheckCircle className="h-3.5 w-3.5" />
              {approving ? "Approving..." : "Approve"}
            </Button>
          )}
          <Button
            size="sm"
            variant="outline"
            className="gap-1.5"
            onClick={() => onRegenerate?.(liveMaterial.id)}
          >
            <RefreshCw className="h-3.5 w-3.5" />
            Regenerate
          </Button>
          <Button size="sm" className="gap-1.5" onClick={handlePrint}>
            <Printer className="h-3.5 w-3.5" />
            Print
          </Button>
        </div>
      </SheetContent>
    </Sheet>
  );
}
