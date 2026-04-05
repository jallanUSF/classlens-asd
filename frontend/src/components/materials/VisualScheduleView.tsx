"use client";

import { CalendarCheck, Square, CheckSquare } from "lucide-react";

interface ScheduleStep {
  step_number?: number;
  label?: string;
  icon_note?: string;
  is_first_then?: boolean;
}

interface VisualScheduleContent {
  title?: string;
  steps?: ScheduleStep[];
  first_then?: { first: string; then: string };
}

interface Props {
  content: VisualScheduleContent;
  studentName: string;
  date: string;
}

export function VisualScheduleView({ content, studentName, date }: Props) {
  return (
    <div className="material-print-content space-y-5">
      {/* Header */}
      <div className="border-b-2 border-primary pb-3">
        <div className="flex items-center gap-2">
          <CalendarCheck className="h-5 w-5 text-primary" />
          <h1 className="text-xl font-semibold text-primary">
            {content.title || "My Schedule"}
          </h1>
        </div>
        <div className="flex gap-6 mt-1 text-sm text-muted-foreground">
          <span>For: <strong className="text-foreground">{studentName}</strong></span>
          <span>Date: <strong className="text-foreground">{date}</strong></span>
        </div>
      </div>

      {/* First-Then board */}
      {content.first_then && (
        <div className="grid grid-cols-2 gap-3">
          <div className="border-2 border-primary rounded-lg p-4 text-center">
            <p className="text-xs font-semibold uppercase tracking-wide text-primary mb-2">
              First
            </p>
            <p className="text-lg font-medium">{content.first_then.first}</p>
          </div>
          <div className="border-2 border-success rounded-lg p-4 text-center">
            <p className="text-xs font-semibold uppercase tracking-wide text-success mb-2">
              Then
            </p>
            <p className="text-lg font-medium">{content.first_then.then}</p>
          </div>
        </div>
      )}

      {/* Sequential steps */}
      {content.steps && content.steps.length > 0 && (
        <div className="space-y-2">
          {content.steps.map((step, i) => (
            <div
              key={i}
              className="flex items-center gap-3 border border-border rounded-lg p-3"
            >
              {/* Checkbox for teacher to mark complete */}
              <Square className="h-5 w-5 text-muted-foreground shrink-0 print:block" />

              {/* Step number */}
              <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center shrink-0">
                <span className="text-sm font-semibold text-primary">
                  {step.step_number ?? i + 1}
                </span>
              </div>

              {/* Icon placeholder */}
              <div className="w-12 h-12 rounded-md bg-muted/50 flex items-center justify-center shrink-0 print:bg-gray-50">
                <span className="text-[9px] text-muted-foreground text-center leading-tight">
                  {step.icon_note || "icon"}
                </span>
              </div>

              {/* Label */}
              <span className="text-base font-medium">{step.label}</span>
            </div>
          ))}
        </div>
      )}

      {!content.steps?.length && !content.first_then && (
        <p className="text-sm text-muted-foreground">No schedule steps defined.</p>
      )}
    </div>
  );
}
