import type { ComponentProps } from "react";
import { Circle, Triangle, Diamond } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

type BadgeProps = ComponentProps<typeof Badge>;

interface LevelBadgeProps {
  level: number;
  /** "short" renders "L1"; "long" renders "Level 1". Defaults to "short". */
  format?: "short" | "long";
  className?: string;
  variant?: BadgeProps["variant"];
}

const LEVEL_STYLES: Record<number, string> = {
  1: "bg-level-1 text-level-1-foreground",
  2: "bg-level-2 text-level-2-foreground",
  3: "bg-level-3 text-level-3-foreground",
};

const LEVEL_LABELS: Record<number, string> = {
  1: "Level 1 (requiring support)",
  2: "Level 2 (requiring substantial support)",
  3: "Level 3 (requiring very substantial support)",
};

function LevelIcon({ level, className }: { level: number; className?: string }) {
  const props = { className, "aria-hidden": true as const };
  if (level === 1) return <Circle {...props} />;
  if (level === 2) return <Triangle {...props} />;
  if (level === 3) return <Diamond {...props} />;
  return null;
}

/**
 * ASD support-level badge (L1/L2/L3).
 *
 * Colorblind-accessible: each level has a distinct shape icon (circle /
 * triangle / diamond) in addition to its color, so the three levels remain
 * distinguishable in grayscale or for users with color vision deficiency.
 */
export function LevelBadge({
  level,
  format = "short",
  className,
  variant = "secondary",
}: LevelBadgeProps) {
  const text = format === "long" ? `Level ${level}` : `L${level}`;
  const iconSize = format === "long" ? "h-3.5 w-3.5" : "h-3 w-3";
  return (
    <Badge
      variant={variant}
      className={cn(
        "inline-flex items-center gap-1",
        LEVEL_STYLES[level] ?? "",
        className,
      )}
      aria-label={LEVEL_LABELS[level] ?? `Level ${level}`}
    >
      <LevelIcon level={level} className={iconSize} />
      <span>{text}</span>
    </Badge>
  );
}
