"use client";

import { Shield } from "lucide-react";

interface GoalReport {
  goal_id: string;
  domain?: string;
  present_level?: string;
  target?: string;
  current_pct?: number;
  target_pct?: number;
  trend?: string;
  recommendation?: string;
}

interface AdminReportContent {
  title?: string;
  executive_summary?: string;
  goals?: GoalReport[];
  accommodations?: string[];
  next_steps?: string;
}

interface Props {
  content: AdminReportContent;
  studentName: string;
  date: string;
}

export function AdminReportView({ content, studentName, date }: Props) {
  return (
    <div className="material-print-content space-y-5">
      {/* Confidential header */}
      <div className="flex items-center gap-2 text-xs text-destructive font-semibold uppercase tracking-widest">
        <Shield className="h-3.5 w-3.5" />
        Confidential — IEP Team Use Only
      </div>

      {/* Header */}
      <div className="border-b-2 border-primary pb-3">
        <h1 className="text-xl font-semibold text-primary">
          {content.title || "IEP Progress Report"}
        </h1>
        <div className="flex gap-6 mt-1 text-sm text-muted-foreground">
          <span>Student: <strong className="text-foreground">{studentName}</strong></span>
          <span>Date: <strong className="text-foreground">{date}</strong></span>
        </div>
      </div>

      {/* Executive Summary */}
      {content.executive_summary && (
        <section>
          <h2 className="text-sm font-semibold uppercase tracking-wide text-primary mb-1">
            Executive Summary
          </h2>
          <p className="text-sm">{content.executive_summary}</p>
        </section>
      )}

      {/* Goal-by-Goal */}
      {content.goals && content.goals.length > 0 && (
        <section>
          <h2 className="text-sm font-semibold uppercase tracking-wide text-primary mb-3">
            Goal Progress
          </h2>
          <div className="space-y-4">
            {content.goals.map((g, i) => (
              <div
                key={i}
                className="border border-border rounded-lg p-3 space-y-2"
              >
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">
                    {g.goal_id}
                    {g.domain && (
                      <span className="text-muted-foreground font-normal ml-2">
                        ({g.domain.replace("_", " ")})
                      </span>
                    )}
                  </span>
                  {g.current_pct != null && g.target_pct != null && (
                    <span className="text-sm font-semibold">
                      {g.current_pct}% / {g.target_pct}%
                    </span>
                  )}
                </div>
                {g.present_level && (
                  <p className="text-xs">
                    <strong>Present Level:</strong> {g.present_level}
                  </p>
                )}
                {g.target && (
                  <p className="text-xs">
                    <strong>Target:</strong> {g.target}
                  </p>
                )}
                {g.trend && (
                  <p className="text-xs">
                    <strong>Trend:</strong> {g.trend}
                  </p>
                )}
                {g.recommendation && (
                  <p className="text-xs">
                    <strong>Recommendation:</strong> {g.recommendation}
                  </p>
                )}
                {/* Progress bar */}
                {g.current_pct != null && g.target_pct != null && (
                  <div className="h-1.5 bg-muted rounded-full overflow-hidden">
                    <div
                      className="h-full bg-primary rounded-full"
                      style={{
                        width: `${Math.min(100, (g.current_pct / g.target_pct) * 100)}%`,
                      }}
                    />
                  </div>
                )}
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Accommodations */}
      {content.accommodations && content.accommodations.length > 0 && (
        <section>
          <h2 className="text-sm font-semibold uppercase tracking-wide text-primary mb-1">
            Accommodations
          </h2>
          <ul className="list-disc list-inside text-sm space-y-1">
            {content.accommodations.map((a, i) => (
              <li key={i}>{a}</li>
            ))}
          </ul>
        </section>
      )}

      {/* Next Steps */}
      {content.next_steps && (
        <section>
          <h2 className="text-sm font-semibold uppercase tracking-wide text-primary mb-1">
            Next Steps
          </h2>
          <p className="text-sm whitespace-pre-line">{content.next_steps}</p>
        </section>
      )}

      {/* Signature line */}
      <div className="border-t border-border pt-4 mt-6">
        <div className="flex gap-12">
          <div className="text-sm">
            <p className="border-b border-foreground w-48 mb-1">&nbsp;</p>
            <p className="text-xs text-muted-foreground">Teacher Signature</p>
          </div>
          <div className="text-sm">
            <p className="border-b border-foreground w-32 mb-1">&nbsp;</p>
            <p className="text-xs text-muted-foreground">Date</p>
          </div>
        </div>
      </div>
    </div>
  );
}
