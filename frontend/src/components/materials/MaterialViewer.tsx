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
import { Printer, CheckCircle, RefreshCw, X, Brain, Flag, ShieldCheck, ShieldAlert, ShieldQuestion } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { sanitizeThinking } from "@/lib/sanitizeThinking";
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
  thinking?: string;
  confidence_score?: "high" | "review_recommended" | "flag_for_expert";
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

const CONFIDENCE_CONFIG: Record<
  string,
  { label: string; color: string; icon: typeof ShieldCheck }
> = {
  high: {
    label: "High Confidence",
    color: "bg-emerald-100 text-emerald-800 border-emerald-200",
    icon: ShieldCheck,
  },
  review_recommended: {
    label: "Review Recommended",
    color: "bg-amber-100 text-amber-800 border-amber-200",
    icon: ShieldAlert,
  },
  flag_for_expert: {
    label: "Flag for Expert",
    color: "bg-red-100 text-red-800 border-red-200",
    icon: ShieldQuestion,
  },
};

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
  const [showThinking, setShowThinking] = useState(false);
  const [flagging, setFlagging] = useState(false);

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

  const handleFlag = async () => {
    setFlagging(true);
    try {
      await fetch(
        `/api/materials/${liveMaterial.student_id}/${liveMaterial.id}/flag`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ reason: "Teacher flagged for expert review" }),
        },
      );
      setLiveMaterial((prev) =>
        prev ? { ...prev, status: "flagged" } : prev,
      );
    } finally {
      setFlagging(false);
    }
  };

  /** Extract readable text from parent letter content for translation. */
  const extractLetterText = (content: Record<string, unknown>): string => {
    // Freeform text path (non-EN fallback from MaterialForge)
    if (typeof content.text === "string" && content.text.trim()) {
      return content.text.trim();
    }
    // Structured EN path — reconstruct readable letter
    const parts: string[] = [];
    if (typeof content.greeting === "string") parts.push(content.greeting);
    if (Array.isArray(content.highlights)) {
      parts.push(content.highlights.join("\n"));
    }
    if (Array.isArray(content.try_at_home)) {
      parts.push("Try at home:\n" + (content.try_at_home as string[]).join("\n"));
    }
    if (typeof content.closing === "string") parts.push(content.closing);
    if (typeof content.teacher_name === "string") parts.push(content.teacher_name);
    return parts.join("\n\n");
  };

  const handleLanguageSelect = async (code: string) => {
    if (code === activeLanguage || regenerating) return;
    setRegenerating(true);
    try {
      // When switching away from EN, pass the current content for translation
      // so Gemma preserves student-specific details instead of regenerating.
      const approvedContent =
        code !== "en" ? extractLetterText(liveMaterial.content) : "";

      const res = await fetch("/api/materials/generate/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          student_id: liveMaterial.student_id,
          goal_id: liveMaterial.goal_id,
          material_type: "parent_comm",
          language: code,
          ...(approvedContent ? { approved_content: approvedContent } : {}),
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

        {/* Confidence badge + thinking trace */}
        {liveMaterial.confidence_score && (
          <div className="px-4 pb-2 print:hidden">
            {(() => {
              const conf =
                CONFIDENCE_CONFIG[liveMaterial.confidence_score] ??
                CONFIDENCE_CONFIG.review_recommended;
              const ConfIcon = conf.icon;
              return (
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <Badge
                      variant="outline"
                      className={`gap-1.5 ${conf.color}`}
                    >
                      <ConfIcon className="h-3.5 w-3.5" />
                      {conf.label}
                    </Badge>
                    {liveMaterial.thinking && (
                      <Button
                        size="sm"
                        variant="ghost"
                        className="text-xs text-muted-foreground gap-1 h-7"
                        onClick={() => setShowThinking(!showThinking)}
                        aria-expanded={showThinking}
                      >
                        <Brain className="h-3.5 w-3.5" />
                        {showThinking ? "Hide" : "Why?"}
                      </Button>
                    )}
                  </div>
                  {showThinking && liveMaterial.thinking && (
                    <div className="rounded-md border bg-muted/30 p-3">
                      <p className="text-[11px] font-semibold uppercase tracking-wide text-muted-foreground mb-1">
                        Gemma&apos;s reasoning
                      </p>
                      <p className="text-xs text-muted-foreground italic whitespace-pre-wrap">
                        {sanitizeThinking(liveMaterial.thinking)}
                      </p>
                    </div>
                  )}
                </div>
              );
            })()}
          </div>
        )}

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
          {liveMaterial.status !== "flagged" && (
            <Button
              size="sm"
              variant="outline"
              className="gap-1.5 text-amber-700 hover:text-amber-800"
              onClick={handleFlag}
              disabled={flagging}
            >
              <Flag className="h-3.5 w-3.5" />
              {flagging ? "Flagging…" : "Flag for Review"}
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
