"use client";

import { ClipboardList } from "lucide-react";

interface TrackingSheetContent {
  title?: string;
  goal_text?: string;
  measurement_criteria?: string;
  columns?: string[];
  rows?: Record<string, string>[];
  target_value?: string;
  notes_section?: boolean;
}

interface Props {
  content: TrackingSheetContent;
  studentName: string;
  goalId: string;
  date: string;
}

export function TrackingSheetView({
  content,
  studentName,
  goalId,
  date,
}: Props) {
  const columns = content.columns || ["Date", "Trial 1", "Trial 2", "Trial 3", "Result", "Notes"];
  const rows = content.rows || [];

  // Generate empty rows for printing if none provided
  const printRows =
    rows.length > 0
      ? rows
      : Array.from({ length: 10 }, () =>
          Object.fromEntries(columns.map((c) => [c, ""]))
        );

  return (
    <div className="material-print-content space-y-5">
      {/* Header */}
      <div className="border-b-2 border-primary pb-3">
        <div className="flex items-center gap-2">
          <ClipboardList className="h-5 w-5 text-primary" />
          <h1 className="text-xl font-semibold text-primary">
            {content.title || "Data Tracking Sheet"}
          </h1>
        </div>
        <div className="flex flex-wrap gap-x-6 gap-y-1 mt-1 text-sm text-muted-foreground">
          <span>Student: <strong className="text-foreground">{studentName}</strong></span>
          <span>Goal: <strong className="text-foreground">{goalId}</strong></span>
          <span>Date: <strong className="text-foreground">{date}</strong></span>
        </div>
      </div>

      {/* Goal & Criteria */}
      {content.goal_text && (
        <section>
          <h2 className="text-sm font-semibold uppercase tracking-wide text-primary mb-1">
            Goal
          </h2>
          <p className="text-sm">{content.goal_text}</p>
        </section>
      )}
      {content.measurement_criteria && (
        <section>
          <h2 className="text-sm font-semibold uppercase tracking-wide text-primary mb-1">
            Measurement Criteria
          </h2>
          <p className="text-sm">{content.measurement_criteria}</p>
        </section>
      )}
      {content.target_value && (
        <p className="text-xs text-muted-foreground">
          Target: <strong>{content.target_value}</strong>
        </p>
      )}

      {/* Data Grid */}
      <div className="overflow-x-auto">
        <table className="w-full text-sm border-collapse">
          <thead>
            <tr>
              {columns.map((col) => (
                <th
                  key={col}
                  className="border border-border bg-muted/50 px-2 py-1.5 text-left text-xs font-semibold uppercase tracking-wide print:bg-gray-100"
                >
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {printRows.map((row, i) => (
              <tr key={i}>
                {columns.map((col) => (
                  <td
                    key={col}
                    className="border border-border px-2 py-2 text-sm min-w-[4rem]"
                  >
                    {row[col] || <span>&nbsp;</span>}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Notes section */}
      {(content.notes_section !== false) && (
        <section>
          <h2 className="text-sm font-semibold uppercase tracking-wide text-primary mb-1">
            Notes
          </h2>
          <div className="border border-border rounded-md h-24 print:h-32" />
        </section>
      )}
    </div>
  );
}
