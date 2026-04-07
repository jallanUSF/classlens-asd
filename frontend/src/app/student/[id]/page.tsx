"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Separator } from "@/components/ui/separator";
import { useChatContext } from "@/context/ChatContext";
import { GoalCard } from "@/components/student/GoalCard";
import { AlertBanner } from "@/components/student/AlertBanner";
import { RecentWork } from "@/components/student/RecentWork";
import { MaterialsLibrary } from "@/components/student/MaterialsLibrary";
import { QuickActions } from "@/components/student/QuickActions";

interface IEPGoal {
  goal_id: string;
  domain: string;
  description: string;
  target_pct: number;
  current_pct: number;
  trial_history: { date: string; pct: number }[];
}

interface StudentProfile {
  student_id: string;
  name: string;
  grade: number;
  asd_level: number;
  communication_level: string;
  interests: string[];
  iep_goals: IEPGoal[];
}

interface Alert {
  id: string;
  student_id: string;
  alert_type: string;
  goal_id: string;
  title: string;
  detail: string;
  suggested_action: string;
}

const LEVEL_STYLES: Record<number, string> = {
  1: "bg-level-1 text-level-1-foreground",
  2: "bg-level-2 text-level-2-foreground",
  3: "bg-level-3 text-level-3-foreground",
};

export default function StudentDetailPage() {
  const params = useParams<{ id: string }>();
  const [student, setStudent] = useState<StudentProfile | null>(null);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { setActiveStudent, prefillInput, addContextMessage } =
    useChatContext();

  useEffect(() => {
    async function load() {
      const [studentRes, alertsRes] = await Promise.all([
        fetch(`/api/students/${params.id}`),
        fetch("/api/alerts"),
      ]);

      if (!studentRes.ok) {
        setError(
          studentRes.status === 404 ? "Student not found" : "Failed to load",
        );
        setLoading(false);
        return;
      }

      const studentData: StudentProfile = await studentRes.json();
      setStudent(studentData);

      if (alertsRes.ok) {
        const allAlerts: Alert[] = await alertsRes.json();
        setAlerts(allAlerts.filter((a) => a.student_id === params.id));
      }

      setLoading(false);

      // Update chat context
      setActiveStudent(params.id);
      addContextMessage(
        `Now looking at **${studentData.name}** — Grade ${studentData.grade === 0 ? "K" : studentData.grade}, ${studentData.iep_goals.length} IEP goals. ${
          alerts.length > 0
            ? `${alerts.length} alert(s) need attention.`
            : "How can I help?"
        }`,
      );
    }
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [params.id]);

  if (loading) {
    return (
      <div className="max-w-3xl mx-auto p-6 space-y-6">
        <Skeleton className="h-10 w-64" />
        <Skeleton className="h-32 w-full" />
        <Skeleton className="h-48 w-full" />
      </div>
    );
  }

  if (error || !student) {
    return (
      <div className="max-w-3xl mx-auto p-6">
        <Card>
          <CardContent className="p-8 text-center">
            <p className="text-muted-foreground">
              {error || "Student not found"}
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  function handleScanWork(goalId: string) {
    prefillInput(
      `Scan work for ${student!.name} on goal ${goalId}`,
    );
  }

  function handleGenerateMaterials(goalId: string) {
    prefillInput(
      `Generate materials for ${student!.name} on goal ${goalId}`,
    );
  }

  function handleAskAssistant(detail: string) {
    prefillInput(
      `Help me with this: ${detail}`,
    );
  }

  return (
    <div className="max-w-3xl mx-auto p-6 space-y-6 pb-20">
      {/* Student Header */}
      <div>
        <div className="flex items-center gap-3">
          <h1 className="text-2xl font-semibold">{student.name}</h1>
          <Badge
            variant="secondary"
            className={LEVEL_STYLES[student.asd_level] || ""}
          >
            Level {student.asd_level}
          </Badge>
        </div>
        <p className="text-muted-foreground mt-1">
          Grade {student.grade === 0 ? "K" : student.grade} &middot;{" "}
          {student.communication_level.charAt(0).toUpperCase() +
            student.communication_level.slice(1)}{" "}
          &middot; Interests: {student.interests.join(", ") || "None listed"}
        </p>
      </div>

      {/* Alert Banner */}
      {alerts.length > 0 && (
        <AlertBanner
          alerts={alerts}
          onGenerateMaterials={handleGenerateMaterials}
          onAskAssistant={handleAskAssistant}
        />
      )}

      <Separator />

      {/* IEP Goals */}
      <section>
        <h2 className="text-lg font-semibold mb-3">IEP Goals</h2>
        {student.iep_goals.length === 0 ? (
          <p className="text-sm text-muted-foreground">
            No goals defined yet.
          </p>
        ) : (
          <div className="space-y-3">
            {student.iep_goals.map((goal) => (
              <GoalCard
                key={goal.goal_id}
                goal={goal}
                onScanWork={handleScanWork}
              />
            ))}
          </div>
        )}
      </section>

      <Separator />

      {/* Recent Work */}
      <section>
        <h2 className="text-lg font-semibold mb-3">Recent Work</h2>
        <RecentWork studentId={student.student_id} />
      </section>

      <Separator />

      {/* Materials Library */}
      <section>
        <h2 className="text-lg font-semibold mb-3">Materials</h2>
        <MaterialsLibrary studentId={student.student_id} studentName={student.name} />
      </section>

      {/* Quick Actions sticky footer */}
      <QuickActions studentName={student.name} />
    </div>
  );
}
