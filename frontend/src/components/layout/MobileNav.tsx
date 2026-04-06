"use client";

import { useState, useCallback, useEffect } from "react";
import { Menu, X, Sparkles } from "lucide-react";
import { StudentSidebar } from "@/components/sidebar/StudentSidebar";
import { ChatPanel } from "@/components/chat/ChatPanel";

export function MobileNav() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [chatOpen, setChatOpen] = useState(false);

  const openSidebar = useCallback(() => {
    setChatOpen(false);
    setSidebarOpen(true);
  }, []);

  const closeSidebar = useCallback(() => setSidebarOpen(false), []);

  const openChat = useCallback(() => {
    setSidebarOpen(false);
    setChatOpen(true);
  }, []);

  const closeChat = useCallback(() => setChatOpen(false), []);

  // Lock body scroll when an overlay is open
  useEffect(() => {
    if (sidebarOpen || chatOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }
    return () => {
      document.body.style.overflow = "";
    };
  }, [sidebarOpen, chatOpen]);

  return (
    <>
      {/* Hamburger button — top-left, mobile only */}
      <button
        onClick={openSidebar}
        className="fixed top-3 left-3 z-50 md:hidden flex items-center justify-center w-10 h-10 rounded-lg bg-card border border-border shadow-sm"
        aria-label="Open navigation"
      >
        <Menu className="h-5 w-5 text-foreground" />
      </button>

      {/* Chat FAB — bottom-right, mobile only */}
      {!chatOpen && (
        <button
          onClick={openChat}
          className="fixed bottom-5 right-5 z-50 md:hidden flex items-center justify-center w-14 h-14 rounded-full bg-primary text-white shadow-lg"
          aria-label="Open assistant"
        >
          <Sparkles className="h-6 w-6" />
        </button>
      )}

      {/* Sidebar overlay — mobile only */}
      {sidebarOpen && (
        <div className="fixed inset-0 z-50 md:hidden">
          {/* Backdrop */}
          <div
            className="absolute inset-0 bg-black/40"
            onClick={closeSidebar}
          />
          {/* Sidebar panel */}
          <div className="absolute inset-y-0 left-0 w-72 animate-slide-in-left">
            <div className="relative h-full">
              <button
                onClick={closeSidebar}
                className="absolute top-3 right-3 z-10 flex items-center justify-center w-8 h-8 rounded-md hover:bg-accent"
                aria-label="Close navigation"
              >
                <X className="h-5 w-5 text-foreground" />
              </button>
              <StudentSidebar />
            </div>
          </div>
        </div>
      )}

      {/* Chat overlay — mobile only */}
      {chatOpen && (
        <div className="fixed inset-0 z-50 md:hidden">
          {/* Backdrop */}
          <div
            className="absolute inset-0 bg-black/40"
            onClick={closeChat}
          />
          {/* Chat panel — near full screen */}
          <div className="absolute inset-2 top-4 rounded-xl overflow-hidden shadow-2xl animate-slide-in-bottom">
            <div className="relative h-full">
              <button
                onClick={closeChat}
                className="absolute top-3 right-3 z-10 flex items-center justify-center w-8 h-8 rounded-md hover:bg-accent bg-card/80"
                aria-label="Close assistant"
              >
                <X className="h-5 w-5 text-foreground" />
              </button>
              <ChatPanel />
            </div>
          </div>
        </div>
      )}
    </>
  );
}
