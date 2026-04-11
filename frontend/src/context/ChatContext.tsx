"use client";

import {
  createContext,
  useContext,
  useState,
  useCallback,
  type ReactNode,
} from "react";
import { useChat, type ChatMessage } from "@/hooks/useChat";

interface ChatContextValue {
  messages: ChatMessage[];
  sendMessage: (text: string) => Promise<void>;
  isStreaming: boolean;
  /** Set the active student (updates context for the chat API) */
  setActiveStudent: (id: string | null) => void;
  activeStudentId: string | null;
  /** Add a system/context message from outside the chat */
  addContextMessage: (text: string) => void;
  /** Pre-fill the input box text */
  prefillInput: (text: string) => void;
  pendingInput: string;
  clearPendingInput: () => void;
  /** Upload a work image and run the capture pipeline */
  uploadWork: (file: File, studentId: string, workType?: string, subject?: string) => Promise<void>;
}

const ChatContext = createContext<ChatContextValue | null>(null);

export function ChatProvider({ children }: { children: ReactNode }) {
  const [activeStudentId, setActiveStudentId] = useState<string | null>(null);
  const [pendingInput, setPendingInput] = useState("");

  const { messages, sendMessage, isStreaming, addContextMessage, uploadWork } = useChat({
    studentId: activeStudentId,
  });

  const setActiveStudent = useCallback((id: string | null) => {
    setActiveStudentId(id);
  }, []);

  const prefillInput = useCallback((text: string) => {
    setPendingInput(text);
  }, []);

  const clearPendingInput = useCallback(() => {
    setPendingInput("");
  }, []);

  return (
    <ChatContext.Provider
      value={{
        messages,
        sendMessage,
        isStreaming,
        setActiveStudent,
        activeStudentId,
        addContextMessage,
        prefillInput,
        pendingInput,
        clearPendingInput,
        uploadWork,
      }}
    >
      {children}
    </ChatContext.Provider>
  );
}

export function useChatContext() {
  const ctx = useContext(ChatContext);
  if (!ctx) throw new Error("useChatContext must be used within ChatProvider");
  return ctx;
}
