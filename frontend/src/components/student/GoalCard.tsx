"use client";

import { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  TrendingUp,
  TrendingDown,
  Minus,
  ChevronDown,
  ChevronUp,
  Camera,
} from "lucide-react";
import { ProgressMiniChart } from "./PlotlyChart";

interface IEPGoal {
  goal_id: string;
  domain: string;
  description: string;
  target_pct: number;
  current_pct: number;
  target_display?: string;
  target_unit?: "percent" | "count_per_day";
  target_value?: number;
  trial_history: { date: string; pct: number }[];
}

interface Props {
  goal: IEPGoal;
  onScanWork?: (goalId: string) => void;
}

function getTrend(history: { pct: number }[]): "up" | "down" | "flat" {
  if (history.length < 2) return "flat";
  const recent = history.slice(-3);
  const first = recent[0].pct;
  const last = recent[recent.length - 1].pct;
  if (last - first > 5) return "up";
  if (first - last > 5) return "down";
  return "flat";
}

const TREND_ICONS = { up: TrendingUp, down: TrendingDown, flat: Minus };
const TREND_COLORS = {
  up: "text-success",
  down: "text-destructive",
  flat: "text-muted-foreground",
};

export function GoalCard({ goal, onScanWork }: Props) {
  const [expanded, setExpanded] = useState(false);
  const trend = getTrend(goal.trial_history);
  const TrendIcon = TREND_ICONS[trend];
  const progressRatio = Math.min(
    100,
    (goal.current_pct / goal.target_pct) * 100,
  );

  const lastThree = goal.trial_history.slice(-3);

  return (
    <Card>
      <CardContent className="p-4">
        {/* Summary row — always visible */}
        <button
          type="button"
          onClick={() => setExpanded(!expanded)}
          className="w-full text-left rounded-md focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
        >
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
            <div className="text-right shrink-0 flex items-center gap-2">
              <div>
                <div className="flex items-center gap-1">
                  <span className="text-xl font-semibold">
                    {goal.current_pct}%
                  </span>
                  <TrendIcon
                    className={`h-4 w-4 ${TREND_COLORS[trend]}`}
                  />
                </div>
                <p className="text-xs text-muted-foreground">
                  Target: {goal.target_display ?? `${goal.target_pct}%`}
                </p>
              </div>
              {expanded ? (
                <ChevronUp className="h-4 w-4 text-muted-foreground" />
              ) : (
                <ChevronDown className="h-4 w-4 text-muted-foreground" />
              )}
            </div>
          </div>
        </button>

        {/* Mini progress bar */}
        <div className="mt-3 h-1.5 bg-muted rounded-full overflow-hidden">
          <div
            className="h-full bg-primary rounded-full transition-all"
            style={{ width: `${progressRatio}%` }}
          />
        </div>

        {/* Expanded details */}
        {expanded && (
          <div className="mt-4 space-y-3 border-t border-border pt-3">
            {/* Plotly mini-chart */}
            <ProgressMiniChart
              history={goal.trial_history}
              targetPct={goal.target_pct}
            />

            {/* Last 3 sessions */}
            {lastThree.length > 0 && (
              <div>
                <p className="text-xs font-medium text-muted-foreground mb-1">
                  Last {lastThree.length} sessions
                </p>
                <div className="flex gap-2">
                  {lastThree.map((s, i) => (
                    <div
                      key={i}
                      className="bg-muted rounded-md px-2 py-1 text-xs"
                    >
                      <span className="font-medium">{s.pct}%</span>
                      <span className="text-muted-foreground ml-1">
                        {s.date}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Action button */}
            {onScanWork && (
              <Button
                size="sm"
                variant="outline"
                className="gap-2 text-xs"
                onClick={(e) => {
                  e.stopPropagation();
                  onScanWork(goal.goal_id);
                }}
              >
                <Camera className="h-3 w-3" />
                Scan Work for This Goal
              </Button>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
