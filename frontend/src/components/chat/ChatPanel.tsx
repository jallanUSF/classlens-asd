"use client";

import { useState } from "react";
import { Send, Sparkles } from "lucide-react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Button } from "@/components/ui/button";

interface Message {
  role: "assistant" | "user";
  content: string;
}

const WELCOME_MESSAGE: Message = {
  role: "assistant",
  content:
    "Hi! I'm your ClassLens assistant — think of me as an experienced IEP co-teacher. Select a student to get started, or ask me anything about your class.",
};

export function ChatPanel() {
  const [messages, setMessages] = useState<Message[]>([WELCOME_MESSAGE]);
  const [input, setInput] = useState("");

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!input.trim()) return;

    const userMsg: Message = { role: "user", content: input.trim() };
    setMessages((prev) => [
      ...prev,
      userMsg,
      {
        role: "assistant",
        content:
          "I'm not connected to the backend yet — streaming integration is coming in Sprint 3. For now, explore the student sidebar and dashboard!",
      },
    ]);
    setInput("");
  }

  return (
    <aside className="w-80 border-l border-border bg-chat-bg flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b border-border bg-card">
        <div className="flex items-center gap-2">
          <Sparkles className="h-4 w-4 text-primary" />
          <h2 className="font-semibold text-sm">ClassLens Assistant</h2>
        </div>
        <p className="text-xs text-muted-foreground mt-0.5">
          Powered by Gemma 4
        </p>
      </div>

      {/* Messages */}
      <ScrollArea className="flex-1">
        <div className="p-4 space-y-4">
          {messages.map((msg, i) => (
            <div
              key={i}
              className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`
                  max-w-[85%] rounded-xl px-3.5 py-2.5 text-sm leading-relaxed
                  ${msg.role === "user"
                    ? "bg-primary text-primary-foreground"
                    : "bg-card text-foreground shadow-sm"
                  }
                `}
              >
                {msg.content}
              </div>
            </div>
          ))}
        </div>
      </ScrollArea>

      {/* Input */}
      <form onSubmit={handleSubmit} className="p-3 border-t border-border bg-card">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about a student..."
            className="flex-1 rounded-lg border border-input bg-background px-3 py-2 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
          />
          <Button type="submit" size="icon" disabled={!input.trim()}>
            <Send className="h-4 w-4" />
          </Button>
        </div>
      </form>
    </aside>
  );
}
