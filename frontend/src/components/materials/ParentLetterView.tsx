"use client";

import { Star, Home } from "lucide-react";

interface ParentLetterContent {
  greeting?: string;
  highlights?: string[];
  try_at_home?: string[];
  closing?: string;
  teacher_name?: string;
}

interface Props {
  content: ParentLetterContent;
  studentName: string;
  date: string;
  language?: string;
}

export function ParentLetterView({ content, studentName, date, language = "en" }: Props) {
  const isNonEnglish = language !== "en";
  return (
    <div
      className="material-print-content space-y-5 max-w-xl"
      lang={language}
      dir={isNonEnglish ? "ltr" : undefined}
    >
      {/* Header */}
      <div className="border-b-2 border-primary pb-3">
        <h1 className="text-xl font-semibold text-primary">
          Progress Update — {studentName}
        </h1>
        <p className="text-sm text-muted-foreground mt-1">{date}</p>
      </div>

      {/* Greeting */}
      <p className="text-sm">
        {content.greeting || `Dear ${studentName}'s family,`}
      </p>

      {/* Highlights */}
      {content.highlights && content.highlights.length > 0 && (
        <section>
          <h2 className="text-sm font-semibold uppercase tracking-wide text-primary mb-2">
            This Week&apos;s Highlights
          </h2>
          <ul className="space-y-2">
            {content.highlights.map((item, i) => (
              <li key={i} className="flex items-start gap-2 text-sm">
                <Star className="h-3.5 w-3.5 text-warning mt-0.5 shrink-0" />
                {item}
              </li>
            ))}
          </ul>
        </section>
      )}

      {/* Try at Home */}
      {content.try_at_home && content.try_at_home.length > 0 && (
        <section className="bg-muted/50 rounded-lg p-4 print:bg-gray-50">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-primary mb-2">
            Try at Home
          </h2>
          <ul className="space-y-2">
            {content.try_at_home.map((item, i) => (
              <li key={i} className="flex items-start gap-2 text-sm">
                <Home className="h-3.5 w-3.5 text-success mt-0.5 shrink-0" />
                {item}
              </li>
            ))}
          </ul>
        </section>
      )}

      {/* Closing */}
      <div className="text-sm space-y-3 pt-2">
        <p>{content.closing || "Thank you for your partnership in supporting your child's growth!"}</p>
        <div>
          <p className="font-medium">{content.teacher_name || "Your child's teacher"}</p>
          <p className="text-muted-foreground text-xs">ClassLens ASD</p>
        </div>
      </div>
    </div>
  );
}
