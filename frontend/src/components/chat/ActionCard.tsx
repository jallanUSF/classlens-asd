import { FileText, UserPlus, Camera, ExternalLink } from "lucide-react";
import { Button } from "@/components/ui/button";
import type { ChatMessage } from "@/hooks/useChat";

type Action = NonNullable<ChatMessage["action"]>;

const ACTION_CONFIG: Record<
  Action["type"],
  { icon: typeof FileText; color: string; borderColor: string }
> = {
  material_generated: {
    icon: FileText,
    color: "text-primary",
    borderColor: "border-l-primary",
  },
  profile_created: {
    icon: UserPlus,
    color: "text-success",
    borderColor: "border-l-success",
  },
  work_captured: {
    icon: Camera,
    color: "text-chart-4",
    borderColor: "border-l-[var(--chart-4)]",
  },
};

interface Props {
  action: Action;
}

export function ActionCard({ action }: Props) {
  const config = ACTION_CONFIG[action.type];
  const Icon = config.icon;

  return (
    <div
      className={`bg-card rounded-lg border border-border border-l-4 ${config.borderColor} p-3 shadow-sm`}
    >
      <div className="flex items-center gap-2 mb-2">
        <Icon className={`h-4 w-4 ${config.color}`} />
        <span className="text-sm font-medium">{action.label}</span>
      </div>
      <div className="flex gap-2">
        <Button size="sm" variant="outline" className="text-xs h-7 gap-1">
          <ExternalLink className="h-3 w-3" />
          View
        </Button>
        {action.type === "material_generated" && (
          <>
            <Button size="sm" className="text-xs h-7">
              Approve
            </Button>
            <Button size="sm" variant="outline" className="text-xs h-7">
              Edit
            </Button>
          </>
        )}
      </div>
    </div>
  );
}
