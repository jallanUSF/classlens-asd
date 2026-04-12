"use client";

import { useState, useCallback } from "react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  TrendingUp,
  AlertTriangle,
  Minus,
  Trophy,
  Brain,
  ChevronDown,
  ChevronUp,
  Loader2,
} from "lucide-react";
import { consumeSseJob } from "@/lib/sseJob";
import { sanitizeThinking } from "@/lib/sanitizeThinking";

interface GoalTrajectory {
  goal_id: string;
  domain: string;
  status: "on_track" | "at_risk" | "stalled" | "met";
  current_pct: number;
  target_pct: number;
  baseline_pct: number;
  trend_summary: string;
  confidence: "high" | "moderate" | "low";
  iep_meeting_note: string;
}

interface TrajectoryData {
  student_id: string;
  summary: string;
  goals: GoalTrajectory[];
  cross_goal_patterns: string | null;
  recommended_priority: string;
  thinking: string;
}

interface Props {
  studentId: string;
}

const STATUS_CONFIG: Record<
  string,
  { label: string; color: string; icon: typeof TrendingUp }
> = {
  on_track: { label: "On Track", color: "bg-emerald-100 text-emerald-800", icon: TrendingUp },
  at_risk: { label: "At Risk", color: "bg-amber-100 text-amber-800", icon: AlertTriangle },
  stalled: { label: "Stalled", color: "bg-red-100 text-red-800", icon: Minus },
  met: { label: "Target Met", color: "bg-blue-100 text-blue-800", icon: Trophy },
};

const CONFIDENCE_STYLE: Record<string, string> = {
  high: "bg-emerald-50 text-emerald-700 border-emerald-200",
  moderate: "bg-amber-50 text-amber-700 border-amber-200",
  low: "bg-red-50 text-red-700 border-red-200",
};

export function TrajectoryReport({ studentId }: Props) {
  const [data, setData] = useState<TrajectoryData | null>(null);
  const [loading, setLoading] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState("Analyzing semester data…");
  const [error, setError] = useState<string | null>(null);
  const [showThinking, setShowThinking] = useState(false);
  const [expandedGoal, setExpandedGoal] = useState<string | null>(null);

  const generate = useCallback(async () => {
    setLoading(true);
    setError(null);
    setLoadingMessage("Analyzing semester data…");
    try {
      const res = await fetch(`/api/students/${studentId}/trajectory/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: "{}",
      });
      const result = await consumeSseJob<TrajectoryData>(res, {
        onHeartbeat: (msg) => setLoadingMessage(msg),
      });
      setData(result);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to generate trajectory report.",
      );
    } finally {
      setLoading(false);
    }
  }, [studentId]);

  // Not yet generated — show the trigger button
  if (!data && !loading && !error) {
    return (
      <div className="rounded-lg border border-dashed border-muted-foreground/30 p-6 text-center">
        <TrendingUp className="h-8 w-8 mx-auto text-muted-foreground/50 mb-2" />
        <p className="text-sm text-muted-foreground mb-3">
          Generate a full-semester trajectory report for the IEP team meeting.
        </p>
        <Button onClick={generate} className="min-h-[44px]">
          <Brain className="h-4 w-4 mr-2" />
          Generate Trajectory Report
        </Button>
      </div>
    );
  }

  // Loading state
  if (loading) {
    return (
      <div className="rounded-lg border border-primary/20 bg-primary/5 p-6 text-center">
        <Loader2 className="h-6 w-6 mx-auto text-primary animate-spin mb-2" />
        <p className="text-sm text-muted-foreground animate-pulse">
          {loadingMessage}
        </p>
        <p className="text-xs text-muted-foreground mt-1">
          Gemma is analyzing all trial data across every goal…
        </p>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="rounded-lg border border-destructive/30 bg-destructive/5 p-4">
        <p className="text-sm text-destructive">{error}</p>
        <Button
          size="sm"
          variant="outline"
          className="mt-2 min-h-[44px]"
          onClick={generate}
        >
          Retry
        </Button>
      </div>
    );
  }

  if (!data) return null;

  return (
    <div className="space-y-4">
      {/* Executive Summary */}
      <div className="rounded-lg border bg-card p-4">
        <p className="text-sm leading-relaxed">{data.summary}</p>
      </div>

      {/* Per-goal trajectories */}
      <div className="space-y-2">
        {data.goals.map((goal) => {
          const config = STATUS_CONFIG[goal.status] || STATUS_CONFIG.on_track;
          const Icon = config.icon;
          const isExpanded = expandedGoal === goal.goal_id;

          return (
            <div
              key={goal.goal_id}
              className="rounded-lg border bg-card overflow-hidden"
            >
              <button
                className="w-full flex items-center gap-3 p-3 text-left hover:bg-muted/50 transition-colors min-h-[44px] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                onClick={() =>
                  setExpandedGoal(isExpanded ? null : goal.goal_id)
                }
                aria-expanded={isExpanded}
              >
                <Icon className="h-4 w-4 shrink-0" />
                <div className="flex-1 min-w-0">
                  <span className="text-sm font-medium">
                    {goal.goal_id} — {goal.domain.replace(/_/g, " ")}
                  </span>
                </div>
                <Badge
                  variant="secondary"
                  className={`text-xs shrink-0 ${config.color}`}
                >
                  {config.label}
                </Badge>
                <span className="text-xs text-muted-foreground tabular-nums shrink-0">
                  {goal.baseline_pct}% → {goal.current_pct}% / {goal.target_pct}%
                </span>
                {isExpanded ? (
                  <ChevronUp className="h-4 w-4 shrink-0 text-muted-foreground" />
                ) : (
                  <ChevronDown className="h-4 w-4 shrink-0 text-muted-foreground" />
                )}
              </button>
              {isExpanded && (
                <div className="border-t px-3 py-3 space-y-3">
                  {/* Trend summary */}
                  <p className="text-sm text-muted-foreground leading-relaxed">
                    {goal.trend_summary}
                  </p>

                  {/* Confidence badge */}
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-muted-foreground">Confidence:</span>
                    <Badge
                      variant="outline"
                      className={`text-xs ${CONFIDENCE_STYLE[goal.confidence] || ""}`}
                    >
                      {goal.confidence}
                    </Badge>
                  </div>

                  {/* IEP meeting note */}
                  <div className="rounded-md bg-muted/50 p-3">
                    <p className="text-[11px] font-semibold uppercase tracking-wide text-muted-foreground mb-1">
                      IEP Meeting Talking Point
                    </p>
                    <p className="text-sm">{goal.iep_meeting_note}</p>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Cross-goal patterns */}
      {data.cross_goal_patterns && (
        <div className="rounded-lg border bg-card p-4">
          <p className="text-[11px] font-semibold uppercase tracking-wide text-muted-foreground mb-1">
            Cross-Goal Patterns
          </p>
          <p className="text-sm leading-relaxed">{data.cross_goal_patterns}</p>
        </div>
      )}

      {/* Recommended priority */}
      {data.recommended_priority && (
        <div className="rounded-lg border border-primary/20 bg-primary/5 p-4">
          <p className="text-[11px] font-semibold uppercase tracking-wide text-primary/70 mb-1">
            Recommended Priority
          </p>
          <p className="text-sm leading-relaxed">{data.recommended_priority}</p>
        </div>
      )}

      {/* Thinking trace (collapsible) */}
      {data.thinking && (
        <div>
          <Button
            size="sm"
            variant="ghost"
            className="text-xs text-muted-foreground gap-1.5 min-h-[44px]"
            onClick={() => setShowThinking(!showThinking)}
            aria-expanded={showThinking}
          >
            <Brain className="h-3.5 w-3.5" />
            {showThinking ? "Hide" : "Show"} Gemma&apos;s reasoning
          </Button>
          {showThinking && (
            <div className="mt-2 rounded-md border bg-muted/30 p-3">
              <p className="text-xs text-muted-foreground italic whitespace-pre-wrap">
                {sanitizeThinking(data.thinking)}
              </p>
            </div>
          )}
        </div>
      )}

      {/* Regenerate */}
      <div className="flex justify-end">
        <Button
          size="sm"
          variant="outline"
          className="text-xs min-h-[44px]"
          onClick={generate}
          disabled={loading}
        >
          Regenerate Report
        </Button>
      </div>
    </div>
  );
}
