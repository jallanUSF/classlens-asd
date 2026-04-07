"use client";

import { AlertTriangle, X, FileText, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useState } from "react";

interface Alert {
  id: string;
  alert_type: string;
  goal_id: string;
  title: string;
  detail: string;
  suggested_action: string;
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

  const visible = alerts.filter((a) => !dismissed.has(a.id));
  if (visible.length === 0) return null;

  function dismiss(id: string) {
    setDismissed((prev) => new Set([...prev, id]));
    // Fire-and-forget dismiss on backend
    fetch(`/api/alerts/${id}/dismiss`, { method: "PUT" }).catch(() => {});
  }

  return (
    <div className="space-y-2">
      {visible.map((alert) => (
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
                {onGenerateMaterials && (
                  <Button
                    size="sm"
                    variant="outline"
                    className="text-xs min-h-[44px] gap-1.5"
                    onClick={() => onGenerateMaterials(alert.goal_id)}
                  >
                    <FileText className="h-3.5 w-3.5" />
                    Generate Materials
                  </Button>
                )}
                {onAskAssistant && (
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
                )}
              </div>
            </div>
            <button
              onClick={() => dismiss(alert.id)}
              className="text-muted-foreground hover:text-foreground min-h-[44px] min-w-[44px] flex items-center justify-center rounded-md focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}
