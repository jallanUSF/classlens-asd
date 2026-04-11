"use client";

import { useRef } from "react";
import { Camera, FileText, Mail } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useChatContext } from "@/context/ChatContext";

interface Props {
  studentName: string;
  studentId: string;
}

export function QuickActions({ studentName, studentId }: Props) {
  const { prefillInput, uploadWork, isStreaming } = useChatContext();
  const fileRef = useRef<HTMLInputElement>(null);

  function handleFileSelect(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    uploadWork(file, studentId);
    // Reset so the same file can be selected again
    e.target.value = "";
  }

  return (
    <div className="sticky bottom-0 bg-background/95 backdrop-blur-sm border-t border-border py-3 -mx-6 px-6">
      <input
        ref={fileRef}
        type="file"
        accept="image/*"
        className="hidden"
        onChange={handleFileSelect}
      />
      <div className="flex gap-3">
        <Button
          className="gap-2"
          disabled={isStreaming}
          onClick={() => fileRef.current?.click()}
        >
          <Camera className="h-4 w-4" />
          Scan Work
        </Button>
        <Button
          variant="outline"
          className="gap-2"
          onClick={() =>
            prefillInput(`Generate a lesson plan for ${studentName}`)
          }
        >
          <FileText className="h-4 w-4" />
          Generate Material
        </Button>
        <Button
          variant="outline"
          className="gap-2"
          onClick={() =>
            prefillInput(`Write a parent update for ${studentName}`)
          }
        >
          <Mail className="h-4 w-4" />
          Write Parent Note
        </Button>
      </div>
    </div>
  );
}
