import { Sparkles, User } from "lucide-react";
import type { ChatMessage as ChatMessageType } from "@/hooks/useChat";
import { ActionCard } from "./ActionCard";

interface Props {
  message: ChatMessageType;
}

export function ChatMessage({ message }: Props) {
  const isUser = message.role === "user";

  if (message.isLoading) {
    return (
      <div className="flex justify-start">
        <div className="max-w-[85%] rounded-xl px-3.5 py-2.5 text-sm bg-card text-foreground shadow-sm">
          <div className="flex items-center gap-2">
            <div className="flex gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-primary animate-bounce [animation-delay:0ms]" />
              <span className="w-1.5 h-1.5 rounded-full bg-primary animate-bounce [animation-delay:150ms]" />
              <span className="w-1.5 h-1.5 rounded-full bg-primary animate-bounce [animation-delay:300ms]" />
            </div>
            <span className="text-xs text-muted-foreground">Thinking...</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div className="flex gap-2 max-w-[85%]">
        {!isUser && (
          <div className="w-6 h-6 rounded-full bg-primary/10 flex items-center justify-center shrink-0 mt-0.5">
            <Sparkles className="h-3 w-3 text-primary" />
          </div>
        )}
        <div>
          <div
            className={`
              rounded-xl px-3.5 py-2.5 text-sm leading-relaxed
              ${isUser
                ? "bg-primary text-primary-foreground"
                : "bg-card text-foreground shadow-sm"
              }
            `}
          >
            {formatContent(message.content)}
          </div>
          {message.action && (
            <div className="mt-2">
              <ActionCard action={message.action} />
            </div>
          )}
        </div>
        {isUser && (
          <div className="w-6 h-6 rounded-full bg-muted flex items-center justify-center shrink-0 mt-0.5">
            <User className="h-3 w-3 text-muted-foreground" />
          </div>
        )}
      </div>
    </div>
  );
}

/** Simple markdown-like formatting: **bold** and line breaks */
function formatContent(text: string) {
  const parts = text.split(/(\*\*[^*]+\*\*)/g);
  return (
    <span>
      {parts.map((part, i) => {
        if (part.startsWith("**") && part.endsWith("**")) {
          return (
            <strong key={i} className="font-semibold">
              {part.slice(2, -2)}
            </strong>
          );
        }
        // Handle line breaks
        const lines = part.split("\n");
        return lines.map((line, j) => (
          <span key={`${i}-${j}`}>
            {j > 0 && <br />}
            {line}
          </span>
        ));
      })}
    </span>
  );
}
