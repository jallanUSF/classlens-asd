"use client";

import { useRef, useEffect, useState } from "react";
import { Send, Sparkles, Paperclip } from "lucide-react";
import { ScrollArea } from "@/components/ui/scroll-area";

import { useChatContext } from "@/context/ChatContext";
import { ChatMessage } from "./ChatMessage";

export function ChatPanel() {
  const {
    messages,
    sendMessage,
    isStreaming,
    pendingInput,
    clearPendingInput,
    uploadWork,
    activeStudentId,
  } = useChatContext();
  const [input, setInput] = useState("");
  const scrollRef = useRef<HTMLDivElement>(null);
  const chatFileRef = useRef<HTMLInputElement>(null);

  // Pick up pre-filled input from context (e.g. quick actions)
  useEffect(() => {
    if (pendingInput) {
      setInput(pendingInput);
      clearPendingInput();
    }
  }, [pendingInput, clearPendingInput]);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!input.trim() || isStreaming) return;
    const text = input.trim();
    setInput("");
    sendMessage(text);
  }

  return (
    <aside className="w-full md:w-80 border-l border-border bg-chat-bg flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b border-border bg-card">
        <div className="flex items-center gap-2">
          <Sparkles className="h-4 w-4 text-primary" />
          <h2 className="font-semibold text-base">ClassLens Assistant</h2>
        </div>
        <p className="text-xs text-muted-foreground mt-0.5">
          Powered by Gemma 4
        </p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto" ref={scrollRef}>
        <div className="p-4 space-y-4">
          {messages.map((msg) => (
            <ChatMessage key={msg.id} message={msg} />
          ))}
        </div>
      </div>

      {/* Input */}
      <form
        onSubmit={handleSubmit}
        className="p-3 border-t border-border bg-card"
      >
        <input
          ref={chatFileRef}
          type="file"
          accept="image/*"
          className="hidden"
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (file && activeStudentId) {
              uploadWork(file, activeStudentId);
            }
            e.target.value = "";
          }}
        />
        <div className="flex gap-2">
          <button
            type="button"
            disabled={isStreaming || !activeStudentId}
            onClick={() => chatFileRef.current?.click()}
            title={activeStudentId ? "Attach work image" : "Select a student first"}
            className="inline-flex items-center justify-center rounded-lg border border-input bg-background min-h-[44px] min-w-[44px] hover:bg-accent transition-colors disabled:opacity-50 disabled:cursor-not-allowed focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-1"
          >
            <Paperclip className="h-4 w-4" />
          </button>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about a student..."
            disabled={isStreaming}
            className="flex-1 rounded-lg border border-input bg-background px-3 py-2.5 text-sm min-h-[44px] placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={isStreaming}
            className="inline-flex items-center justify-center rounded-lg bg-primary text-primary-foreground min-h-[44px] min-w-[44px] hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-1"
          >
            <Send className="h-4 w-4" />
          </button>
        </div>
      </form>
    </aside>
  );
}
