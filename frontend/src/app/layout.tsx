import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { StudentSidebar } from "@/components/sidebar/StudentSidebar";
import { ChatPanel } from "@/components/chat/ChatPanel";
import { ChatProvider } from "@/context/ChatContext";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "ClassLens ASD",
  description:
    "AI-powered IEP progress tracking for special education teachers",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${inter.variable} h-full antialiased`}>
      <body className="h-full flex">
        <ChatProvider>
          <StudentSidebar />
          <main className="flex-1 overflow-y-auto">{children}</main>
          <ChatPanel />
        </ChatProvider>
      </body>
    </html>
  );
}
