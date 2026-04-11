"use client";

import { AlertTriangle, X, FileText, Sparkles, Brain } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useState, useCallback } from "react";

interface Alert {
  id: string;
  alert_type: string;
  goal_id: string;
  title: string;
  detail: string;
  suggested_action: string;
}

interface Analysis {
  thinking: string;
  output: string;
}

interface Props {
  alerts: Alert[];
  onGenerateMaterials?: (goalId: string) => void;
  onAskAssistant?: (detail: string) => void;
}

export function AlertBanner({
  alerts,
  onGenerateMaterials,
  onAskAssistant,
}: Props) {
  const [dismissed, setDismissed] = useState<Set<string>>(new Set());
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [loadingId, setLoadingId] = useState<string | null>(null);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [analyses, setAnalyses] = useState<Record<string, Analysis>>({});

  const visible = alerts.filter((a) => !dismissed.has(a.id));

  const dismiss = useCallback((id: string) => {
    setDismissed((prev) => {
      const next = new Set(prev);
      next.add(id);
      return next;
    });
    // Fire-and-forget dismiss on backend
    fetch(`/api/alerts/${id}/dismiss`, { method: "PUT" }).catch(() => {});
  }, []);

  const runAnalyze = useCallback(async (alertId: string) => {
    setLoadingId(alertId);
    setErrors((prev) => {
      if (!prev[alertId]) return prev;
      const next = { ...prev };
      delete next[alertId];
      return next;
    });
    try {
      const res = await fetch(`/api/alerts/${alertId}/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: "{}",
      });
      if (!res.ok) {
        throw new Error(`Request failed: ${res.status}`);
      }
      const data = (await res.json()) as Analysis;
      setAnalyses((prev) => ({
        ...prev,
        [alertId]: { thinking: data.thinking ?? "", output: data.output ?? "" },
      }));
      setExpandedId(alertId);
    } catch (err) {
      setErrors((prev) => ({
        ...prev,
        [alertId]:
          err instanceof Error
            ? err.message
            : "Couldn't analyze this alert — try again.",
      }));
      setExpandedId(alertId);
    } finally {
      setLoadingId((prev) => (prev === alertId ? null : prev));
    }
  }, []);

  const handleWhy = useCallback(
    (alertId: string) => {
      // Toggle: if already expanded for this alert, collapse.
      if (expandedId === alertId) {
        setExpandedId(null);
        return;
      }
      // If we already have a cached analysis, just expand.
      if (analyses[alertId]) {
        setExpandedId(alertId);
        return;
      }
      void runAnalyze(alertId);
    },
    [expandedId, analyses, runAnalyze],
  );

  if (visible.length === 0) return null;

  return (
    <div className="space-y-2">
      {visible.map((alert) => {
        const isExpanded = expandedId === alert.id;
        const isLoading = loadingId === alert.id;
        const analysis = analyses[alert.id];
        const error = errors[alert.id];

        return (
          <div
            key={alert.id}
            className="bg-warning/10 border border-warning/30 rounded-lg p-3"
          >
            <div className="flex items-start gap-2">
              <AlertTriangle className="h-4 w-4 text-warning mt-0.5 shrink-0" />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium">{alert.title}</p>
                <p className="text-xs text-muted-foreground mt-0.5 break-words">
                  {alert.detail}
                </p>
                <div className="flex flex-wrap gap-2 mt-2">
                  <Button
                    size="sm"
                    variant="outline"
                    className="text-xs min-h-[44px] gap-1.5"
                    onClick={() => handleWhy(alert.id)}
                    disabled={isLoading}
                    aria-expanded={isExpanded}
                    aria-controls={`alert-analysis-${alert.id}`}
                  >
                    <Brain className="h-3.5 w-3.5" />
                    {isLoading ? "Thinking…" : "Why?"}
                  </Button>
                  {onGenerateMaterials ? (
                    <Button
                      size="sm"
                      variant="outline"
                      className="text-xs min-h-[44px] gap-1.5"
                      onClick={() => onGenerateMaterials(alert.goal_id)}
                    >
                      <FileText className="h-3.5 w-3.5" />
                      Generate Materials
                    </Button>
                  ) : null}
                  {onAskAssistant ? (
                    <Button
                      size="sm"
                      variant="outline"
                      className="text-xs min-h-[44px] gap-1.5"
                      onClick={() =>
                        onAskAssistant(
                          `${alert.title}: ${alert.detail}. ${alert.suggested_action}`,
                        )
                      }
                    >
                      <Sparkles className="h-3.5 w-3.5" />
                      Ask Assistant
                    </Button>
                  ) : null}
                </div>
                {isExpanded ? (
                  <div
                    id={`alert-analysis-${alert.id}`}
                    className="mt-3 rounded-md border border-warning/20 bg-background/60 p-3"
                  >
                    {isLoading ? (
                      <p className="text-xs text-muted-foreground italic animate-pulse">
                        Gemma is thinking…
                      </p>
                    ) : error ? (
                      <div className="space-y-2">
                        <p className="text-xs text-destructive">
                          Couldn&apos;t analyze this alert — try again.
                        </p>
                        <Button
                          size="sm"
                          variant="outline"
                          className="text-xs min-h-[36px]"
                          onClick={() => runAnalyze(alert.id)}
                        >
                          Retry
                        </Button>
                      </div>
                    ) : analysis ? (
                      <div className="space-y-3">
                        {analysis.thinking ? (
                          <div>
                            <p className="text-[11px] font-semibold uppercase tracking-wide text-muted-foreground">
                              Gemma&apos;s reasoning
                            </p>
                            <p className="mt-1 text-xs text-muted-foreground italic whitespace-pre-wrap">
                              {analysis.thinking}
                            </p>
                          </div>
                        ) : null}
                        <div>
                          <p className="text-[11px] font-semibold uppercase tracking-wide text-muted-foreground">
                            Analysis
                          </p>
                          <p className="mt-1 text-sm whitespace-pre-wrap">
                            {analysis.output || "No analysis returned."}
                          </p>
                        </div>
                      </div>
                    ) : null}
                  </div>
                ) : null}
              </div>
              <button
                onClick={() => dismiss(alert.id)}
                className="text-muted-foreground hover:text-foreground min-h-[44px] min-w-[44px] flex items-center justify-center rounded-md focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
          </div>
        );
      })}
    </div>
  );
}
