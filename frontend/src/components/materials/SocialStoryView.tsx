"use client";

import { BookOpen } from "lucide-react";

interface Scene {
  page?: number;
  text?: string;
  sentence_type?: string;
  illustration_note?: string;
}

interface SocialStoryContent {
  title?: string;
  scenes?: Scene[];
  target_behavior?: string;
  interest_theme?: string;
}

interface Props {
  content: SocialStoryContent;
  studentName: string;
  date: string;
}

const SENTENCE_TYPE_COLORS: Record<string, string> = {
  descriptive: "bg-blue-50 text-blue-700 print:bg-blue-50",
  perspective: "bg-purple-50 text-purple-700 print:bg-purple-50",
  directive: "bg-green-50 text-green-700 print:bg-green-50",
  affirmative: "bg-amber-50 text-amber-700 print:bg-amber-50",
  cooperative: "bg-teal-50 text-teal-700 print:bg-teal-50",
  control: "bg-rose-50 text-rose-700 print:bg-rose-50",
};

export function SocialStoryView({ content, studentName, date }: Props) {
  return (
    <div className="material-print-content space-y-5">
      {/* Header */}
      <div className="border-b-2 border-primary pb-3">
        <div className="flex items-center gap-2">
          <BookOpen className="h-5 w-5 text-primary" />
          <h1 className="text-xl font-semibold text-primary">
            {content.title || "My Social Story"}
          </h1>
        </div>
        <div className="flex gap-6 mt-1 text-sm text-muted-foreground">
          <span>For: <strong className="text-foreground">{studentName}</strong></span>
          <span>Date: <strong className="text-foreground">{date}</strong></span>
        </div>
        {content.target_behavior && (
          <p className="text-xs text-muted-foreground mt-1">
            Target behavior: {content.target_behavior}
          </p>
        )}
      </div>

      {/* Scenes — picture-book style */}
      {content.scenes && content.scenes.length > 0 ? (
        <div className="space-y-4">
          {content.scenes.map((scene, i) => (
            <div
              key={i}
              className="border border-border rounded-lg p-4 space-y-2 page-break-inside-avoid"
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-muted-foreground">
                  Page {scene.page ?? i + 1}
                </span>
                {scene.sentence_type && (
                  <span
                    className={`text-[10px] px-2 py-0.5 rounded-full font-medium ${
                      SENTENCE_TYPE_COLORS[scene.sentence_type] ||
                      "bg-muted text-muted-foreground"
                    }`}
                  >
                    {scene.sentence_type}
                  </span>
                )}
              </div>

              {/* Illustration placeholder */}
              <div className="bg-muted/50 rounded-md h-24 flex items-center justify-center print:bg-gray-50">
                <p className="text-xs text-muted-foreground italic">
                  {scene.illustration_note || "Illustration area"}
                </p>
              </div>

              {/* Story text — large for readability */}
              <p className="text-base leading-relaxed">{scene.text}</p>
            </div>
          ))}
        </div>
      ) : (
        <p className="text-sm text-muted-foreground">No scenes defined.</p>
      )}
    </div>
  );
}
