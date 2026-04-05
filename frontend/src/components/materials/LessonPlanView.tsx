"use client";

import { CheckSquare } from "lucide-react";

interface LessonPlanContent {
  title?: string;
  objective?: string;
  warm_up?: string;
  main_activity?: string;
  materials_needed?: string[];
  scaffolding_notes?: string;
  assessment?: string;
  interest_theme?: string;
  duration?: string;
}

interface Props {
  content: LessonPlanContent;
  studentName: string;
  goalId: string;
  date: string;
}

export function LessonPlanView({ content, studentName, goalId, date }: Props) {
  return (
    <div className="material-print-content space-y-5">
      {/* Header */}
      <div className="border-b-2 border-primary pb-3">
        <h1 className="text-xl font-semibold text-primary">
          {content.title || "Lesson Plan"}
        </h1>
        <div className="flex flex-wrap gap-x-6 gap-y-1 mt-1 text-sm text-muted-foreground">
          <span>Student: <strong className="text-foreground">{studentName}</strong></span>
          <span>Goal: <strong className="text-foreground">{goalId}</strong></span>
          <span>Date: <strong className="text-foreground">{date}</strong></span>
          {content.duration && <span>Duration: <strong className="text-foreground">{content.duration}</strong></span>}
        </div>
        {content.interest_theme && (
          <p className="text-xs text-muted-foreground mt-1">
            Interest theme: {content.interest_theme}
          </p>
        )}
      </div>

      {/* Objective */}
      {content.objective && (
        <section>
          <h2 className="text-sm font-semibold uppercase tracking-wide text-primary mb-1">
            Objective
          </h2>
          <p className="text-sm">{content.objective}</p>
        </section>
      )}

      {/* Warm-up */}
      {content.warm_up && (
        <section>
          <h2 className="text-sm font-semibold uppercase tracking-wide text-primary mb-1">
            Warm-Up
          </h2>
          <p className="text-sm">{content.warm_up}</p>
        </section>
      )}

      {/* Main Activity */}
      {content.main_activity && (
        <section>
          <h2 className="text-sm font-semibold uppercase tracking-wide text-primary mb-1">
            Main Activity
          </h2>
          <p className="text-sm whitespace-pre-line">{content.main_activity}</p>
        </section>
      )}

      {/* Materials Needed */}
      {content.materials_needed && content.materials_needed.length > 0 && (
        <section>
          <h2 className="text-sm font-semibold uppercase tracking-wide text-primary mb-1">
            Materials Needed
          </h2>
          <ul className="space-y-1">
            {content.materials_needed.map((item, i) => (
              <li key={i} className="flex items-center gap-2 text-sm">
                <CheckSquare className="h-3.5 w-3.5 text-muted-foreground shrink-0" />
                {item}
              </li>
            ))}
          </ul>
        </section>
      )}

      {/* Scaffolding Notes */}
      {content.scaffolding_notes && (
        <section>
          <h2 className="text-sm font-semibold uppercase tracking-wide text-primary mb-1">
            Scaffolding Notes
          </h2>
          <p className="text-sm whitespace-pre-line">{content.scaffolding_notes}</p>
        </section>
      )}

      {/* Assessment */}
      {content.assessment && (
        <section>
          <h2 className="text-sm font-semibold uppercase tracking-wide text-primary mb-1">
            Assessment
          </h2>
          <p className="text-sm">{content.assessment}</p>
        </section>
      )}
    </div>
  );
}
