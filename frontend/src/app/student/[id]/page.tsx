"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Separator } from "@/components/ui/separator";
import { Button } from "@/components/ui/button";
import {
  Camera,
  FileText,
  Mail,
  TrendingUp,
  TrendingDown,
  Minus,
} from "lucide-react";

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

const LEVEL_STYLES: Record<number, string> = {
  1: "bg-level-1 text-level-1-foreground",
  2: "bg-level-2 text-level-2-foreground",
  3: "bg-level-3 text-level-3-foreground",
};

function getTrend(history: { pct: number }[]): "up" | "down" | "flat" {
  if (history.length < 2) return "flat";
  const recent = history.slice(-3);
  const first = recent[0].pct;
  const last = recent[recent.length - 1].pct;
  if (last - first > 5) return "up";
  if (first - last > 5) return "down";
  return "flat";
}

const TREND_ICONS = {
  up: TrendingUp,
  down: TrendingDown,
  flat: Minus,
};

const TREND_COLORS = {
  up: "text-success",
  down: "text-destructive",
  flat: "text-muted-foreground",
};

export default function StudentDetailPage() {
  const params = useParams<{ id: string }>();
  const [student, setStudent] = useState<StudentProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      const res = await fetch(`/api/students/${params.id}`);
      if (!res.ok) {
        setError(res.status === 404 ? "Student not found" : "Failed to load");
        setLoading(false);
        return;
      }
      setStudent(await res.json());
      setLoading(false);
    }
    load();
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
            <p className="text-muted-foreground">{error || "Student not found"}</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto p-6 space-y-6">
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
          Grade {student.grade} &middot;{" "}
          {student.communication_level.charAt(0).toUpperCase() +
            student.communication_level.slice(1)}{" "}
          &middot; Interests: {student.interests.join(", ") || "None listed"}
        </p>
      </div>

      <Separator />

      {/* IEP Goals */}
      <section>
        <h2 className="text-lg font-semibold mb-3">IEP Goals</h2>
        {student.iep_goals.length === 0 ? (
          <p className="text-sm text-muted-foreground">No goals defined yet.</p>
        ) : (
          <div className="space-y-3">
            {student.iep_goals.map((goal) => {
              const trend = getTrend(goal.trial_history);
              const TrendIcon = TREND_ICONS[trend];
              return (
                <Card key={goal.goal_id}>
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <Badge variant="outline" className="text-xs">
                            {goal.domain.replace("_", " ")}
                          </Badge>
                          <span className="text-xs text-muted-foreground">
                            {goal.goal_id}
                          </span>
                        </div>
                        <p className="text-sm">{goal.description}</p>
                      </div>
                      <div className="text-right shrink-0">
                        <div className="flex items-center gap-1">
                          <span className="text-xl font-semibold">
                            {goal.current_pct}%
                          </span>
                          <TrendIcon
                            className={`h-4 w-4 ${TREND_COLORS[trend]}`}
                          />
                        </div>
                        <p className="text-xs text-muted-foreground">
                          Target: {goal.target_pct}%
                        </p>
                      </div>
                    </div>
                    {/* Mini progress bar */}
                    <div className="mt-3 h-1.5 bg-muted rounded-full overflow-hidden">
                      <div
                        className="h-full bg-primary rounded-full transition-all"
                        style={{
                          width: `${Math.min(100, (goal.current_pct / goal.target_pct) * 100)}%`,
                        }}
                      />
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        )}
      </section>

      {/* Quick Actions (sticky footer comes in Sprint 3, inline for now) */}
      <Separator />
      <div className="flex gap-3">
        <Button className="gap-2">
          <Camera className="h-4 w-4" />
          Scan Work
        </Button>
        <Button variant="outline" className="gap-2">
          <FileText className="h-4 w-4" />
          Generate Material
        </Button>
        <Button variant="outline" className="gap-2">
          <Mail className="h-4 w-4" />
          Write Parent Note
        </Button>
      </div>
    </div>
  );
}
