"use client";

import { useEffect, useState } from "react";
import { usePathname } from "next/navigation";
import Link from "next/link";
import { Users, Plus, AlertTriangle } from "lucide-react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";

import { Skeleton } from "@/components/ui/skeleton";

interface StudentSummary {
  student_id: string;
  name: string;
  grade: number;
  asd_level: number;
  communication_level: string;
  interests: string[];
  goal_count: number;
  session_count: number;
  last_session_date: string | null;
}

interface Alert {
  student_id: string;
  alert_type: string;
}

const LEVEL_STYLES: Record<number, string> = {
  1: "bg-level-1 text-level-1-foreground",
  2: "bg-level-2 text-level-2-foreground",
  3: "bg-level-3 text-level-3-foreground",
};

export function StudentSidebar() {
  const pathname = usePathname();
  const [students, setStudents] = useState<StudentSummary[]>([]);
  const [alertCounts, setAlertCounts] = useState<Record<string, number>>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [studentsRes, alertsRes] = await Promise.all([
          fetch("/api/students"),
          fetch("/api/alerts"),
        ]);
        if (studentsRes.ok) {
          setStudents(await studentsRes.json());
        }
        if (alertsRes.ok) {
          const alerts: Alert[] = await alertsRes.json();
          const counts: Record<string, number> = {};
          for (const a of alerts) {
            counts[a.student_id] = (counts[a.student_id] || 0) + 1;
          }
          setAlertCounts(counts);
        }
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  // Sort: students with alerts first, then alphabetical
  const sorted = [...students].sort((a, b) => {
    const aAlerts = alertCounts[a.student_id] || 0;
    const bAlerts = alertCounts[b.student_id] || 0;
    if (aAlerts && !bAlerts) return -1;
    if (!aAlerts && bAlerts) return 1;
    return a.name.localeCompare(b.name);
  });

  const activeId = pathname.startsWith("/student/")
    ? pathname.split("/")[2]
    : null;

  return (
    <aside className="w-full md:w-60 border-r border-border bg-card flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b border-border">
        <Link href="/" className="flex items-center gap-2 text-primary font-semibold text-lg rounded-md focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2">
          <Users className="h-5 w-5" />
          ClassLens
        </Link>
      </div>

      {/* Student list */}
      <ScrollArea className="flex-1">
        <div className="p-2">
          {loading ? (
            <div className="space-y-2 p-2">
              {[1, 2, 3].map((i) => (
                <Skeleton key={i} className="h-14 w-full rounded-lg" />
              ))}
            </div>
          ) : sorted.length === 0 ? (
            <p className="text-sm text-muted-foreground p-3">
              No students yet. Add one to get started.
            </p>
          ) : (
            <nav className="space-y-1">
              {sorted.map((s) => {
                const isActive = activeId === s.student_id;
                const alerts = alertCounts[s.student_id] || 0;
                return (
                  <Link
                    key={s.student_id}
                    href={`/student/${s.student_id}`}
                    className={`
                      flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm transition-colors
                      focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-1
                      ${isActive
                        ? "bg-primary/10 text-primary font-medium"
                        : "text-foreground hover:bg-accent"
                      }
                    `}
                  >
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="truncate font-medium">{s.name}</span>
                        {alerts > 0 && (
                          <AlertTriangle className="h-3.5 w-3.5 text-warning shrink-0" />
                        )}
                      </div>
                      <div className="flex items-center gap-2 mt-0.5">
                        <span className="text-xs text-muted-foreground">
                          Grade {s.grade === 0 ? "K" : s.grade}
                        </span>
                        <Badge
                          variant="secondary"
                          className={`text-[10px] px-1.5 py-0 h-4 ${LEVEL_STYLES[s.asd_level] || ""}`}
                        >
                          L{s.asd_level}
                        </Badge>
                      </div>
                    </div>
                  </Link>
                );
              })}
            </nav>
          )}
        </div>
      </ScrollArea>

      {/* Add Student */}
      <div className="p-3 border-t border-border">
        <Link
          href="/student/new"
          className="inline-flex items-center justify-start gap-2 w-full rounded-md border border-input bg-background px-4 py-2 text-sm font-medium hover:bg-accent hover:text-accent-foreground transition-colors min-h-[44px] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-1"
        >
          <Plus className="h-4 w-4" />
          Add Student
        </Link>
      </div>
    </aside>
  );
}
