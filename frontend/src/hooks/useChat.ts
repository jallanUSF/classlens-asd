"use client";

import { useState, useCallback, useRef } from "react";

export interface ChatMessage {
  id: string;
  role: "assistant" | "user";
  content: string;
  /** Optional action card embedded in the message */
  action?: {
    type: "material_generated" | "profile_created" | "work_captured";
    label: string;
    studentId?: string;
    materialId?: string;
  };
  isLoading?: boolean;
}

interface UseChatOptions {
  studentId?: string | null;
}

let msgCounter = 0;
function nextId() {
  return `msg-${++msgCounter}-${Date.now()}`;
}

const WELCOME: ChatMessage = {
  id: "welcome",
  role: "assistant",
  content:
    "Hi! I'm your ClassLens assistant — think of me as an experienced IEP co-teacher. Select a student to get started, or ask me anything about your class.",
};

export function useChat({ studentId }: UseChatOptions = {}) {
  const [messages, setMessages] = useState<ChatMessage[]>([WELCOME]);
  const [isStreaming, setIsStreaming] = useState(false);
  const historyRef = useRef<{ role: string; content: string }[]>([]);

  const sendMessage = useCallback(
    async (text: string) => {
      const userMsg: ChatMessage = {
        id: nextId(),
        role: "user",
        content: text,
      };

      const loadingMsg: ChatMessage = {
        id: nextId(),
        role: "assistant",
        content: "",
        isLoading: true,
      };

      setMessages((prev) => [...prev, userMsg, loadingMsg]);
      setIsStreaming(true);

      // Build conversation history for the API
      const history = [...historyRef.current, { role: "user", content: text }];

      try {
        const res = await fetch("/api/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            message: text,
            student_id: studentId ?? null,
            conversation_history: historyRef.current,
          }),
        });

        if (!res.ok) {
          throw new Error(`Chat request failed: ${res.status}`);
        }

        const data = await res.json();
        const responseText: string = data.content || "I couldn't generate a response.";

        // Detect action cards in the response
        const action = detectAction(responseText);

        const assistantMsg: ChatMessage = {
          id: loadingMsg.id,
          role: "assistant",
          content: responseText,
          action,
        };

        setMessages((prev) =>
          prev.map((m) => (m.id === loadingMsg.id ? assistantMsg : m)),
        );

        // Update history ref
        historyRef.current = [
          ...history,
          { role: "assistant", content: responseText },
        ];
      } catch {
        setMessages((prev) =>
          prev.map((m) =>
            m.id === loadingMsg.id
              ? {
                  ...m,
                  content:
                    "Sorry, I had trouble connecting. Please try again.",
                  isLoading: false,
                }
              : m,
          ),
        );
      } finally {
        setIsStreaming(false);
      }
    },
    [studentId],
  );

  const addContextMessage = useCallback((text: string) => {
    setMessages((prev) => {
      // Deduplicate: skip if the last assistant message has the same content
      const lastAssistant = [...prev].reverse().find((m) => m.role === "assistant");
      if (lastAssistant && lastAssistant.content === text) return prev;
      const msg: ChatMessage = {
        id: nextId(),
        role: "assistant",
        content: text,
      };
      return [...prev, msg];
    });
  }, []);

  const uploadWork = useCallback(
    async (file: File, targetStudentId: string, workType = "worksheet", subject = "general") => {
      const userMsg: ChatMessage = {
        id: nextId(),
        role: "user",
        content: `📎 Scanning: ${file.name}`,
      };
      const loadingMsg: ChatMessage = {
        id: nextId(),
        role: "assistant",
        content: "",
        isLoading: true,
      };
      setMessages((prev) => [...prev, userMsg, loadingMsg]);
      setIsStreaming(true);

      try {
        const formData = new FormData();
        formData.append("image", file);
        formData.append("student_id", targetStudentId);
        formData.append("work_type", workType);
        formData.append("subject", subject);

        const res = await fetch("/api/capture", {
          method: "POST",
          body: formData,
        });

        if (!res.ok) {
          throw new Error(`Upload failed: ${res.status}`);
        }

        const result = await res.json();

        // Build a human-readable summary from pipeline results
        const transcription = result.transcription || {};
        const goals = result.goal_mapping?.matched_goals || [];
        const alerts = result.alerts || [];

        let summary = `I've scanned and analyzed **${file.name}**.\n\n`;

        const rawText = transcription.transcribed_text || transcription.raw_text;
        if (rawText) {
          summary += `**What I see:** ${rawText.slice(0, 300)}\n\n`;
        }
        const itemsTotal = transcription.items_completed ?? transcription.total_items;
        const itemsCorrect = transcription.items_correct ?? transcription.correct_items;
        if (itemsTotal != null) {
          summary += `**Items:** ${itemsCorrect ?? 0}/${itemsTotal} correct`;
          if (transcription.accuracy_pct != null) summary += ` (${transcription.accuracy_pct}%)`;
          else if (transcription.work_quality) summary += ` (${transcription.work_quality})`;
          summary += "\n\n";
        }
        if (goals.length > 0) {
          summary += "**Matched IEP Goals:**\n";
          for (const g of goals) {
            summary += `- ${g.goal_id}: ${g.successes}/${g.trials} (${g.percentage}%)\n`;
          }
          summary += "\n";
        }
        if (alerts.length > 0) {
          summary += "⚠️ **Alerts:**\n";
          for (const a of alerts) {
            summary += `- ${a.alert_message || a.progress_note}\n`;
          }
          summary += "\n";
        }
        summary += "Trial data has been recorded. Want me to generate materials or dig deeper into any goal?";

        const assistantMsg: ChatMessage = {
          id: loadingMsg.id,
          role: "assistant",
          content: summary,
          action: { type: "work_captured", label: "Work Captured & Analyzed" },
        };

        setMessages((prev) =>
          prev.map((m) => (m.id === loadingMsg.id ? assistantMsg : m)),
        );

        historyRef.current = [
          ...historyRef.current,
          { role: "user", content: `Scanned work: ${file.name}` },
          { role: "assistant", content: summary },
        ];
      } catch {
        setMessages((prev) =>
          prev.map((m) =>
            m.id === loadingMsg.id
              ? { ...m, content: "Sorry, I had trouble processing that image. Please try again.", isLoading: false }
              : m,
          ),
        );
      } finally {
        setIsStreaming(false);
      }
    },
    [],
  );

  const clearHistory = useCallback(() => {
    historyRef.current = [];
    setMessages([WELCOME]);
  }, []);

  return { messages, sendMessage, isStreaming, addContextMessage, clearHistory, uploadWork };
}

function detectAction(
  text: string,
): ChatMessage["action"] | undefined {
  const lower = text.toLowerCase();
  if (lower.includes("lesson plan") && (lower.includes("generated") || lower.includes("created") || lower.includes("here's"))) {
    return { type: "material_generated", label: "Lesson Plan Ready" };
  }
  if (lower.includes("profile") && (lower.includes("created") || lower.includes("set up"))) {
    return { type: "profile_created", label: "Student Profile Created" };
  }
  if (lower.includes("captured") || lower.includes("scanned")) {
    return { type: "work_captured", label: "Work Captured" };
  }
  return undefined;
}
