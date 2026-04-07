"use client";

import { useEffect, useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

import { Skeleton } from "@/components/ui/skeleton";
import {
  AlertTriangle,
  TrendingDown,
  BookOpen,
  Eye,
  Sparkles,
} from "lucide-react";
import Link from "next/link";
import { useChatContext } from "@/context/ChatContext";

interface Alert {
  id: string;
  student_id: string;
  alert_type: string;
  title: string;
  detail: string;
  suggested_action: string;
  severity: string;
}

interface StudentSummary {
  student_id: string;
  name: string;
  grade: number;
  asd_level: number;
  goal_count: number;
  session_count: number;
}

const ALERT_ICONS: Record<string, typeof AlertTriangle> = {
  plateau: AlertTriangle,
  regression: TrendingDown,
};

function getGreeting(): string {
  const hour = new Date().getHours();
  if (hour < 12) return "Good morning";
  if (hour < 17) return "Good afternoon";
  return "Good evening";
}

export default function DashboardPage() {
  const [students, setStudents] = useState<StudentSummary[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const { prefillInput, setActiveStudent } = useChatContext();

  useEffect(() => {
    async function load() {
      const [studentsRes, alertsRes] = await Promise.all([
        fetch("/api/students"),
        fetch("/api/alerts"),
      ]);
      if (studentsRes.ok) setStudents(await studentsRes.json());
      if (alertsRes.ok) setAlerts(await alertsRes.json());
      setLoading(false);
    }
    load();
  }, []);

  const totalGoals = students.reduce((sum, s) => sum + s.goal_count, 0);
  const totalSessions = students.reduce((sum, s) => sum + s.session_count, 0);

  if (loading) {
    return (
      <div className="max-w-3xl mx-auto p-6 space-y-6">
        <Skeleton className="h-10 w-80" />
        <Skeleton className="h-24 w-full" />
        <Skeleton className="h-48 w-full" />
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto p-6 space-y-8">
      {/* Greeting */}
      <div>
        <h1 className="text-2xl font-semibold text-foreground">
          {getGreeting()}!
        </h1>
        <p className="text-muted-foreground mt-1">
          You have{" "}
          <span className="font-medium text-foreground">
            {students.length} students
          </span>
          ,{" "}
          <span className="font-medium text-foreground">
            {totalGoals} active goals
          </span>
          , and{" "}
          <span className="font-medium text-foreground">
            {totalSessions} sessions
          </span>{" "}
          recorded.
        </p>
      </div>

      {/* Needs Attention */}
      {alerts.length > 0 && (
        <section>
          <h2 className="text-lg font-semibold mb-3 flex items-center gap-2">
            <AlertTriangle className="h-4 w-4 text-warning" />
            Needs Attention
          </h2>
          <div className="space-y-3">
            {alerts.map((alert) => {
              const Icon = ALERT_ICONS[alert.alert_type] || AlertTriangle;
              return (
                <Card key={alert.id} className="border-l-4 border-l-warning">
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex items-start gap-3">
                        <Icon className="h-4 w-4 text-warning mt-0.5 shrink-0" />
                        <div>
                          <p className="font-medium text-sm">{alert.title}</p>
                          <p className="text-xs text-muted-foreground mt-0.5">
                            {alert.detail}
                          </p>
                        </div>
                      </div>
                      <div className="flex flex-col sm:flex-row gap-2 shrink-0">
                        <Link
                          href={`/student/${alert.student_id}`}
                          className="inline-flex items-center justify-center gap-1 rounded-md border border-input bg-background px-3 min-h-[44px] text-sm font-medium hover:bg-accent hover:text-accent-foreground transition-colors"
                        >
                          <Eye className="h-3.5 w-3.5" />
                          View
                        </Link>
                        <button
                          type="button"
                          className="inline-flex items-center justify-center gap-1 rounded-md px-3 min-h-[44px] text-sm font-medium hover:bg-accent hover:text-accent-foreground transition-colors"
                          onClick={() => {
                            setActiveStudent(alert.student_id);
                            prefillInput(`Help with: ${alert.title} — ${alert.detail}`);
                          }}
                        >
                          <Sparkles className="h-3.5 w-3.5" />
                          Ask Assistant
                        </button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </section>
      )}

      {/* Quick Overview */}
      <section>
        <h2 className="text-lg font-semibold mb-3 flex items-center gap-2">
          <BookOpen className="h-4 w-4 text-primary" />
          Your Students
        </h2>
        {students.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {students.map((s) => (
              <Link key={s.student_id} href={`/student/${s.student_id}`}>
                <Card className="hover:border-primary/30 transition-colors cursor-pointer">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium">{s.name}</p>
                        <p className="text-xs text-muted-foreground">
                          Grade {s.grade === 0 ? "K" : s.grade} &middot; {s.goal_count} goals &middot;{" "}
                          {s.session_count} sessions
                        </p>
                      </div>
                      <Badge
                        variant="secondary"
                        className={`text-xs ${
                          s.asd_level === 1
                            ? "bg-level-1 text-level-1-foreground"
                            : s.asd_level === 2
                              ? "bg-level-2 text-level-2-foreground"
                              : "bg-level-3 text-level-3-foreground"
                        }`}
                      >
                        Level {s.asd_level}
                      </Badge>
                    </div>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
        ) : (
          <Card>
            <CardContent className="p-8 text-center">
              <p className="text-muted-foreground mb-4">
                No students yet. Add your first student to get started.
              </p>
              <Link
                href="/student/new"
                className="inline-flex items-center justify-center rounded-md bg-primary text-primary-foreground px-4 min-h-[44px] text-sm font-medium hover:bg-primary/90 transition-colors"
              >
                Add Student
              </Link>
            </CardContent>
          </Card>
        )}
      </section>
    </div>
  );
}
