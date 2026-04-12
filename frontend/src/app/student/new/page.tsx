"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { LevelBadge } from "@/components/ui/LevelBadge";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { Upload, UserPlus, Sparkles } from "lucide-react";
import { useChatContext } from "@/context/ChatContext";
import { consumeSseJob } from "@/lib/sseJob";

interface ExtractedGoal {
  goal_id: string;
  domain?: string;
  description: string;
  baseline?: string;
  target?: string;
  measurement_method?: string;
}

interface IepExtraction {
  student_name?: string;
  grade?: number | null;
  asd_level?: number | null;
  communication_level?: string;
  interests?: string[];
  iep_goals?: ExtractedGoal[];
  accommodations?: string[];
  notes?: string;
}

interface ProfilePreview {
  name?: string;
  grade?: number;
  asd_level?: number;
  communication_level?: string;
  interests?: string[];
  iep_goals?: ExtractedGoal[];
  accommodations?: string[];
}

export default function NewStudentPage() {
  const router = useRouter();
  const { setActiveStudent, addContextMessage, messages, sendMessage } =
    useChatContext();
  const [preview, setPreview] = useState<ProfilePreview>({});
  const [uploading, setUploading] = useState(false);
  const [createdId, setCreatedId] = useState<string | null>(null);

  // On mount, set chat context for new student flow
  useEffect(() => {
    setActiveStudent(null);
    addContextMessage(
      "Let's set up a new student! Tell me their **first name** and **grade**, and I'll guide you through the rest. You can also drop an IEP document below.",
    );
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Watch chat messages for profile data mentions
  useEffect(() => {
    const lastAssistant = [...messages]
      .reverse()
      .find((m) => m.role === "assistant");
    if (!lastAssistant) return;

    const text = lastAssistant.content.toLowerCase();

    // Simple extraction from assistant acknowledgments
    const nameMatch = text.match(
      /(?:name(?:'s| is)?|setting up|for)\s+(\w+)/i,
    );
    if (nameMatch && !preview.name) {
      setPreview((p) => ({ ...p, name: nameMatch[1] }));
    }

    const gradeMatch = text.match(/grade\s+(\d)/i);
    if (gradeMatch) {
      setPreview((p) => ({ ...p, grade: parseInt(gradeMatch[1]) }));
    }

    const levelMatch = text.match(/level\s+(\d)/i);
    if (levelMatch) {
      setPreview((p) => ({ ...p, asd_level: parseInt(levelMatch[1]) }));
    }
  }, [messages, preview.name]);

  const handleFileUpload = useCallback(
    async (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (!file) return;

      setUploading(true);
      const formData = new FormData();
      formData.append("file", file);
      formData.append("student_id", preview.name?.toLowerCase() || "new_student");
      formData.append("doc_type", "iep_pdf");

      try {
        const res = await fetch("/api/documents/upload/stream", {
          method: "POST",
          body: formData,
        });
        const payload = await consumeSseJob<{ extraction?: IepExtraction }>(res);
        const extraction: IepExtraction = payload.extraction ?? {};
        const goals = extraction.iep_goals ?? [];
        const accommodations = extraction.accommodations ?? [];

        // Merge extracted fields into the preview — don't overwrite values
        // the user already supplied via chat.
        setPreview((p) => ({
          ...p,
          name: p.name || extraction.student_name || p.name,
          grade:
            p.grade ??
            (typeof extraction.grade === "number" ? extraction.grade : undefined),
          asd_level:
            p.asd_level ??
            (typeof extraction.asd_level === "number"
              ? extraction.asd_level
              : undefined),
          communication_level:
            p.communication_level || extraction.communication_level || undefined,
          interests:
            p.interests && p.interests.length > 0
              ? p.interests
              : extraction.interests ?? [],
          iep_goals: goals,
          accommodations: accommodations,
        }));

        addContextMessage(
          `I extracted **${goals.length} IEP goals** and **${accommodations.length} accommodations** from ${file.name}. Review them below and tell me the student's name to continue.`,
        );
      } catch {
        addContextMessage(
          `I couldn't process ${file.name}. The server returned an error — please try again or upload a different file.`,
        );
      } finally {
        setUploading(false);
      }
    },
    [preview.name, addContextMessage],
  );

  const [createError, setCreateError] = useState<string | null>(null);

  async function handleCreateProfile() {
    if (!preview.name) return;

    setCreateError(null);

    const profile = {
      student_id: preview.name.toLowerCase() + "_" + new Date().getFullYear(),
      name: preview.name,
      grade: preview.grade || 3,
      asd_level: preview.asd_level || 2,
      communication_level: preview.communication_level || "verbal",
      interests: preview.interests || [],
      iep_goals: [],
    };

    try {
      const res = await fetch("/api/students", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(profile),
      });

      if (res.ok) {
        setCreatedId(profile.student_id);
        addContextMessage(
          `**${preview.name}**'s profile has been created! Redirecting to their page now. You can add IEP goals there.`,
        );
        setTimeout(() => router.push(`/student/${profile.student_id}`), 1500);
      } else {
        setCreateError("Could not create the profile. Please try again.");
      }
    } catch {
      setCreateError("Network error — check your connection and try again.");
    }
  }

  const hasEnoughInfo = !!preview.name;

  return (
    <div className="max-w-xl mx-auto p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-semibold flex items-center gap-2">
          <UserPlus className="h-6 w-6 text-primary" />
          New Student
        </h1>
        <p className="text-muted-foreground mt-1">
          The assistant will guide you through setup. Just chat naturally.
        </p>
      </div>

      <Separator />

      {/* Profile Preview Card — builds in real time */}
      <Card>
        <CardContent className="p-4">
          <h3 className="text-sm font-medium text-muted-foreground mb-3">
            Profile Preview
          </h3>
          <div className="space-y-2">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
                <span className="text-lg font-semibold text-primary">
                  {preview.name ? preview.name[0].toUpperCase() : "?"}
                </span>
              </div>
              <div>
                <p className="font-medium">
                  {preview.name || "Name pending..."}
                </p>
                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                  {preview.grade ? (
                    <span>Grade {preview.grade === 0 ? "K" : preview.grade}</span>
                  ) : (
                    <span className="italic">Grade?</span>
                  )}
                  {preview.asd_level && (
                    <LevelBadge
                      level={preview.asd_level}
                      format="long"
                      className="text-[10px] px-1.5 py-0 h-4"
                    />
                  )}
                </div>
              </div>
            </div>
            {preview.interests && preview.interests.length > 0 && (
              <p className="text-xs text-muted-foreground">
                Interests: {preview.interests.join(", ")}
              </p>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Extracted IEP Content — only shows after a successful upload */}
      {((preview.iep_goals && preview.iep_goals.length > 0) ||
        (preview.accommodations && preview.accommodations.length > 0)) && (
        <Card>
          <CardContent className="p-4 space-y-4">
            <h3 className="text-sm font-medium text-muted-foreground flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-primary" />
              Extracted from IEP
            </h3>

            {preview.iep_goals && preview.iep_goals.length > 0 && (
              <div className="space-y-2">
                <p className="text-xs uppercase tracking-wide text-muted-foreground">
                  IEP Goals ({preview.iep_goals.length})
                </p>
                <ul className="space-y-1.5">
                  {preview.iep_goals.map((goal, idx) => (
                    <li
                      key={`${goal.goal_id}-${idx}`}
                      className="text-sm leading-snug"
                    >
                      <span className="font-mono text-xs text-primary">
                        {goal.goal_id}
                      </span>{" "}
                      <span className="text-muted-foreground">—</span>{" "}
                      <span>{goal.description}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {preview.accommodations && preview.accommodations.length > 0 && (
              <div className="space-y-2">
                <p className="text-xs uppercase tracking-wide text-muted-foreground">
                  Accommodations ({preview.accommodations.length})
                </p>
                <ul className="list-disc list-inside space-y-1">
                  {preview.accommodations.map((acc, idx) => (
                    <li key={idx} className="text-sm">
                      {acc}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* IEP Document Drop Zone */}
      <Card>
        <CardContent className="p-4">
          <label className="block cursor-pointer">
            <div className="border-2 border-dashed border-border rounded-lg p-6 text-center hover:border-primary/50 transition-colors">
              <Upload className="h-8 w-8 text-muted-foreground mx-auto mb-2" />
              <p className="text-sm font-medium">
                {uploading ? "Uploading..." : "Drop IEP document here"}
              </p>
              <p className="text-xs text-muted-foreground mt-1">
                PDF or image — I&apos;ll extract goals and accommodations
              </p>
            </div>
            <input
              type="file"
              accept=".pdf,.png,.jpg,.jpeg"
              className="hidden"
              onChange={handleFileUpload}
              disabled={uploading}
            />
          </label>
        </CardContent>
      </Card>

      {/* Create Profile Button */}
      {hasEnoughInfo && !createdId && (
        <div className="space-y-2">
          <div className="flex gap-3">
            <Button className="gap-2" onClick={handleCreateProfile}>
              <Sparkles className="h-4 w-4" />
              Create {preview.name}&apos;s Profile
            </Button>
            <Button
              variant="outline"
              onClick={() =>
                sendMessage(
                  `I'm setting up ${preview.name}. What else should I know about them?`,
                )
              }
            >
              Tell me more first
            </Button>
          </div>
          {createError && (
            <p className="text-sm text-destructive" role="alert">
              {createError}
            </p>
          )}
        </div>
      )}

      {createdId && (
        <Card>
          <CardContent className="p-4 bg-success/10 text-center">
            <p className="text-sm font-medium text-success-foreground">
              Profile created! Redirecting...
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
