"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { Upload, UserPlus, Sparkles } from "lucide-react";
import { useChatContext } from "@/context/ChatContext";

interface ProfilePreview {
  name?: string;
  grade?: number;
  asd_level?: number;
  communication_level?: string;
  interests?: string[];
}

const LEVEL_STYLES: Record<number, string> = {
  1: "bg-level-1 text-level-1-foreground",
  2: "bg-level-2 text-level-2-foreground",
  3: "bg-level-3 text-level-3-foreground",
};

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
        const res = await fetch("/api/documents/upload", {
          method: "POST",
          body: formData,
        });
        if (res.ok) {
          addContextMessage(
            `I've received the IEP document (**${file.name}**). I'll use this to extract goals and accommodations. Let me know the student's name and grade to continue.`,
          );
        }
      } catch {
        addContextMessage("There was an issue uploading the file. Please try again.");
      } finally {
        setUploading(false);
      }
    },
    [preview.name, addContextMessage],
  );

  async function handleCreateProfile() {
    if (!preview.name) return;

    const profile = {
      student_id: preview.name.toLowerCase() + "_" + new Date().getFullYear(),
      name: preview.name,
      grade: preview.grade || 3,
      asd_level: preview.asd_level || 2,
      communication_level: preview.communication_level || "verbal",
      interests: preview.interests || [],
      iep_goals: [],
    };

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
                    <span>Grade {preview.grade}</span>
                  ) : (
                    <span className="italic">Grade?</span>
                  )}
                  {preview.asd_level && (
                    <Badge
                      variant="secondary"
                      className={`text-[10px] px-1.5 py-0 h-4 ${LEVEL_STYLES[preview.asd_level] || ""}`}
                    >
                      Level {preview.asd_level}
                    </Badge>
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
