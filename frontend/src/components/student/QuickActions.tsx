"use client";

import { Camera, FileText, Mail } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useChatContext } from "@/context/ChatContext";

interface Props {
  studentName: string;
}

export function QuickActions({ studentName }: Props) {
  const { prefillInput } = useChatContext();

  return (
    <div className="sticky bottom-0 bg-background/95 backdrop-blur-sm border-t border-border py-3 -mx-6 px-6">
      <div className="flex gap-3">
        <Button
          className="gap-2"
          onClick={() =>
            prefillInput(`Scan work for ${studentName}`)
          }
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
