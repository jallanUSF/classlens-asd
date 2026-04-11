"use client";

import { ArrowDown, Sparkles } from "lucide-react";
import ReactMarkdown from "react-markdown";

interface Props {
  content: string | Record<string, unknown>;
  studentName: string;
  date: string;
}

/**
 * The Material Forge emits first_then boards as a raw Markdown string (unlike
 * the structured JSON the other material types return). This renderer splits
 * the markdown on the FIRST / THEN / teacher-notes section markers and places
 * each chunk in its own themed card, so the teacher sees a real first-then
 * visual instead of a raw-text dump.
 */
export function FirstThenView({ content, studentName, date }: Props) {
  const raw = typeof content === "string" ? content : JSON.stringify(content, null, 2);

  const sections = splitSections(raw);

  return (
    <div className="material-print-content space-y-5">
      <header className="border-b border-border pb-3">
        <div className="flex items-center gap-2">
          <Sparkles className="h-4 w-4 text-primary" />
          <h2 className="text-lg font-semibold">First-Then Board</h2>
        </div>
        <p className="text-xs text-muted-foreground mt-1">
          {studentName} · {date}
        </p>
      </header>

      {sections.header && (
        <div className="prose prose-sm max-w-none text-muted-foreground">
          <ReactMarkdown>{sections.header}</ReactMarkdown>
        </div>
      )}

      <div className="rounded-xl border-2 border-primary/30 bg-primary/5 p-5 space-y-1">
        <p className="text-[11px] uppercase tracking-widest text-primary font-semibold">
          First
        </p>
        <div className="prose prose-sm max-w-none">
          <ReactMarkdown>{sections.first || "_No first task specified._"}</ReactMarkdown>
        </div>
      </div>

      <div className="flex justify-center">
        <ArrowDown className="h-8 w-8 text-primary" aria-hidden="true" />
      </div>

      <div className="rounded-xl border-2 border-accent/40 bg-accent/10 p-5 space-y-1">
        <p className="text-[11px] uppercase tracking-widest text-accent-foreground font-semibold">
          Then
        </p>
        <div className="prose prose-sm max-w-none">
          <ReactMarkdown>{sections.then || "_No reinforcer specified._"}</ReactMarkdown>
        </div>
      </div>

      {sections.notes && (
        <div className="rounded-lg border border-border bg-muted/30 p-4">
          <p className="text-[11px] uppercase tracking-wide text-muted-foreground font-semibold mb-2">
            Teacher Notes
          </p>
          <div className="prose prose-sm max-w-none">
            <ReactMarkdown>{sections.notes}</ReactMarkdown>
          </div>
        </div>
      )}
    </div>
  );
}

interface Sections {
  header: string;
  first: string;
  then: string;
  notes: string;
}

/**
 * Pull FIRST / THEN / teacher-notes sections out of the Material Forge's
 * markdown output. The prompt doesn't pin an exact schema, so we match on
 * common headings the model emits: "FIRST SECTION" / "FIRST:" / "THEN SECTION"
 * / "THEN:" / "Teacher" / "Implementation Notes".
 */
function splitSections(raw: string): Sections {
  const firstIdx = findHeading(raw, /\bfirst\b/i);
  const thenIdx = findHeading(raw, /\bthen\b/i, firstIdx + 1);
  const notesIdx = findHeading(raw, /(teacher|implementation).{0,30}notes?/i, thenIdx + 1);

  const end = raw.length;
  const header = firstIdx >= 0 ? raw.slice(0, firstIdx).trim() : raw.trim();
  const first =
    firstIdx >= 0
      ? raw.slice(firstIdx, thenIdx >= 0 ? thenIdx : notesIdx >= 0 ? notesIdx : end).trim()
      : "";
  const then =
    thenIdx >= 0 ? raw.slice(thenIdx, notesIdx >= 0 ? notesIdx : end).trim() : "";
  const notes = notesIdx >= 0 ? raw.slice(notesIdx, end).trim() : "";

  return {
    header: header,
    first: stripSectionHeading(first, /\bfirst\b/i),
    then: stripSectionHeading(then, /\bthen\b/i),
    notes: notes,
  };
}

function findHeading(text: string, pattern: RegExp, from = 0): number {
  // Find the earliest line at-or-after `from` whose trimmed form contains the
  // pattern AND looks like a heading (starts with **, #, or is uppercase-ish).
  const lines = text.split("\n");
  let cursor = 0;
  for (let i = 0; i < lines.length; i++) {
    const lineStart = cursor;
    cursor += lines[i].length + 1;
    if (lineStart < from) continue;
    const line = lines[i].trim();
    if (!pattern.test(line)) continue;
    const looksLikeHeading =
      /^(\*\*|##?#?|\[)/.test(line) ||
      /^[^a-z]*$/.test(line.replace(/[^\w\s]/g, "").trim());
    if (looksLikeHeading) return lineStart;
  }
  return -1;
}

function stripSectionHeading(chunk: string, pattern: RegExp): string {
  const lines = chunk.split("\n");
  // Drop lines that are just the "FIRST"/"THEN" heading markers so we don't
  // render them twice (once as a card label, once as body text).
  while (lines.length > 0) {
    const line = lines[0].trim();
    if (!line) {
      lines.shift();
      continue;
    }
    const stripped = line.replace(/[\*#\[\]:\s🦖⬇️💧👋💪🔢]/gu, "").trim();
    if (pattern.test(line) && stripped.toLowerCase().replace(/[^a-z]/g, "").length <= 10) {
      lines.shift();
      continue;
    }
    break;
  }
  return lines.join("\n").trim();
}
