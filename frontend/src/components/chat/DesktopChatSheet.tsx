"use client";

import { useEffect, useState } from "react";
import { MessageSquare } from "lucide-react";
import {
  Sheet,
  SheetContent,
  SheetTrigger,
} from "@/components/ui/sheet";
import { ChatPanel } from "./ChatPanel";

const STORAGE_KEY = "chat-panel-open";

export function DesktopChatSheet() {
  const [open, setOpen] = useState(false);
  const [hydrated, setHydrated] = useState(false);

  // Read persisted state on mount
  useEffect(() => {
    try {
      const stored = window.localStorage.getItem(STORAGE_KEY);
      if (stored === "true") setOpen(true);
    } catch {
      // localStorage unavailable — ignore
    }
    setHydrated(true);
  }, []);

  // Persist state on change (after hydration, to avoid overwriting)
  useEffect(() => {
    if (!hydrated) return;
    try {
      window.localStorage.setItem(STORAGE_KEY, String(open));
    } catch {
      // ignore
    }
  }, [open, hydrated]);

  return (
    <Sheet open={open} onOpenChange={setOpen}>
      <SheetTrigger
        render={
          <button
            type="button"
            aria-label="Open assistant"
            className="hidden md:flex fixed top-4 right-4 z-40 items-center justify-center w-11 h-11 rounded-full bg-primary text-primary-foreground shadow-md hover:bg-primary/90 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
          >
            <MessageSquare className="h-5 w-5" />
          </button>
        }
      />
      <SheetContent
        side="right"
        className="w-full sm:max-w-md p-0 flex flex-col"
      >
        <ChatPanel />
      </SheetContent>
    </Sheet>
  );
}
