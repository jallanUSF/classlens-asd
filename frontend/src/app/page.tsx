"use client";

import { useEffect, useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { LevelBadge } from "@/components/ui/LevelBadge";

import { Skeleton } from "@/components/ui/skeleton";
import {
  AlertTriangle,
  TrendingDown,
  BookOpen,
  Eye,
  Sparkles,
  UserPlus,
} from "lucide-react";
import { EmptyClassroom } from "@/components/illustrations/EmptyClassroom";
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
    const ac = new AbortController();
    async function load() {
      try {
        const [studentsRes, alertsRes] = await Promise.all([
          fetch("/api/students", { signal: ac.signal }),
          fetch("/api/alerts", { signal: ac.signal }),
        ]);
        const studentsData = studentsRes.ok ? await studentsRes.json() : null;
        const alertsData = alertsRes.ok ? await alertsRes.json() : null;
        if (ac.signal.aborted) return;
        if (studentsData) setStudents(studentsData);
        if (alertsData) setAlerts(alertsData);
        setLoading(false);
      } catch (err) {
        if ((err as Error).name !== "AbortError") throw err;
      }
    }
    load();
    return () => ac.abort();
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
      {/* Product explainer */}
      <Card className="bg-muted/50 border-muted">
        <CardContent className="p-4">
          <div className="flex items-start gap-3">
            <Sparkles className="h-4 w-4 text-muted-foreground mt-0.5 shrink-0" />
            <p className="text-sm text-muted-foreground">
              Photo of student work becomes structured IEP progress data. Powered by Gemma 4 with multimodal vision, function calling, and thinking mode.
            </p>
          </div>
        </CardContent>
      </Card>

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
                          className="inline-flex items-center justify-center gap-1 rounded-md border border-input bg-background px-3 min-h-[44px] text-sm font-medium hover:bg-accent hover:text-accent-foreground transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                        >
                          <Eye className="h-3.5 w-3.5" />
                          View
                        </Link>
                        <button
                          type="button"
                          className="inline-flex items-center justify-center gap-1 rounded-md px-3 min-h-[44px] text-sm font-medium hover:bg-accent hover:text-accent-foreground transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
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
            {students.map((s) => {
              const levelColor =
                s.asd_level === 1
                  ? "border-l-level-1"
                  : s.asd_level === 2
                    ? "border-l-level-2"
                    : "border-l-level-3";
              const avatarBg =
                s.asd_level === 1
                  ? "bg-level-1/15 text-level-1"
                  : s.asd_level === 2
                    ? "bg-level-2/15 text-level-2"
                    : "bg-level-3/15 text-level-3";
              return (
                <Link key={s.student_id} href={`/student/${s.student_id}`} className="rounded-xl focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2">
                  <Card className={`border-l-4 ${levelColor} hover:shadow-md hover:border-l-4 transition-all duration-200 cursor-pointer group`}>
                    <CardContent className="p-4">
                      <div className="flex items-center gap-3">
                        <div
                          className={`w-9 h-9 rounded-full ${avatarBg} flex items-center justify-center text-sm font-semibold shrink-0`}
                        >
                          {s.name.charAt(0)}
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="font-medium truncate group-hover:text-primary transition-colors">{s.name}</p>
                          <p className="text-xs text-muted-foreground">
                            Grade {s.grade === 0 ? "K" : s.grade} &middot; {s.goal_count} goals &middot;{" "}
                            {s.session_count} sessions
                          </p>
                        </div>
                        <LevelBadge
                          level={s.asd_level}
                          format="long"
                          className="text-xs shrink-0"
                        />
                      </div>
                    </CardContent>
                  </Card>
                </Link>
              );
            })}
          </div>
        ) : (
          <Card>
            <CardContent className="p-8 text-center flex flex-col items-center">
              <EmptyClassroom className="w-48 h-auto mb-5 opacity-80" />
              <h3 className="font-medium text-foreground mb-1">
                Your classroom is ready
              </h3>
              <p className="text-sm text-muted-foreground mb-5 max-w-xs">
                Add your first student to start tracking IEP goals and generating personalized materials.
              </p>
              <Link
                href="/student/new"
                className="inline-flex items-center justify-center gap-2 rounded-md bg-primary text-primary-foreground px-5 min-h-[44px] text-sm font-medium hover:bg-primary/90 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
              >
                <UserPlus className="h-4 w-4" />
                Add Your First Student
              </Link>
            </CardContent>
          </Card>
        )}
      </section>
    </div>
  );
}
