"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Headphones,
  Play,
  Pause,
  Download,
  RefreshCw,
  Loader2,
  AlertTriangle,
  ChevronDown,
  ChevronUp,
  Brain,
} from "lucide-react";
import { consumeSseJob } from "@/lib/sseJob";
import { sanitizeThinking } from "@/lib/sanitizeThinking";
import { formatTime } from "@/lib/formatTime";

interface ScriptLine {
  speaker: "host" | "guest";
  text: string;
}

interface PodcastData {
  student_id: string;
  title: string;
  script: ScriptLine[];
  language: string;
  generated_date: string;
  audio_url: string;
  thinking?: string;
}

interface Props {
  studentId: string;
  /** ISO date string of the most recent student profile update, for stale detection. */
  lastUpdated?: string | null;
}

export function PodcastBriefing({ studentId, lastUpdated }: Props) {
  const [data, setData] = useState<PodcastData | null>(null);
  const [loading, setLoading] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState("Analyzing student data…");
  const [error, setError] = useState<string | null>(null);
  const [initialLoad, setInitialLoad] = useState(true);

  // Player state
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);

  // UI toggles
  const [showScript, setShowScript] = useState(false);
  const [showThinking, setShowThinking] = useState(false);

  // Load cached podcast on mount
  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const res = await fetch(`/api/students/${studentId}/podcast`);
        if (res.ok) {
          const payload = (await res.json()) as PodcastData;
          if (!cancelled) setData(payload);
        }
      } catch {
        // Silent — empty state will render
      } finally {
        if (!cancelled) setInitialLoad(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [studentId]);

  const generate = useCallback(async () => {
    // Pause any playing audio before regenerating
    if (audioRef.current && !audioRef.current.paused) {
      const confirmed = window.confirm(
        "This will replace the current briefing. Continue?",
      );
      if (!confirmed) return;
      audioRef.current.pause();
    }
    setLoading(true);
    setError(null);
    setLoadingMessage("Analyzing student data…");
    try {
      const res = await fetch(`/api/students/${studentId}/podcast/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: "{}",
      });
      const result = await consumeSseJob<PodcastData>(res, {
        onHeartbeat: (msg) => setLoadingMessage(msg),
      });
      setData(result);
      // Force audio element to reload fresh MP3 (cache-bust via key change)
      setCurrentTime(0);
      setDuration(0);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to generate briefing.",
      );
    } finally {
      setLoading(false);
    }
  }, [studentId]);

  const togglePlay = useCallback(() => {
    const el = audioRef.current;
    if (!el) return;
    if (el.paused) {
      el.play().catch(() => {
        setError("Unable to play audio. Please try again.");
      });
    } else {
      el.pause();
    }
  }, []);

  const handleDownload = useCallback(() => {
    if (!data) return;
    // Download via anchor click — preserves Content-Disposition filename on backend side
    const a = document.createElement("a");
    a.href = data.audio_url;
    // Sanitize title into a filename-safe slug
    const safeTitle = data.title
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "_")
      .replace(/^_+|_+$/g, "")
      .slice(0, 60);
    a.download = `${safeTitle || studentId}.mp3`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  }, [data, studentId]);

  // Stale detection: is student data newer than the briefing?
  const isStale =
    data && lastUpdated && lastUpdated > data.generated_date ? true : false;

  // === Render states ===

  if (initialLoad) {
    return (
      <div className="rounded-lg border bg-card p-4">
        <div className="h-6 w-32 animate-pulse rounded bg-muted" />
      </div>
    );
  }

  if (loading) {
    return (
      <div className="rounded-lg border border-primary/20 bg-primary/5 p-6 text-center">
        <Loader2 className="h-6 w-6 mx-auto text-primary animate-spin mb-2" />
        <p className="text-sm text-muted-foreground animate-pulse">
          {loadingMessage}
        </p>
        <p className="text-xs text-muted-foreground mt-1">
          Gemma is writing a dialogue script, then synthesizing audio.
        </p>
      </div>
    );
  }

  if (error && !data) {
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

  if (!data) {
    // Empty state — no precomputed, trigger generation
    return (
      <div className="rounded-lg border border-dashed border-muted-foreground/30 p-6 text-center">
        <Headphones className="h-8 w-8 mx-auto text-muted-foreground/50 mb-2" />
        <p className="text-sm text-muted-foreground mb-3">
          Generate a 2-minute audio briefing on this student&apos;s progress.
        </p>
        <Button onClick={generate} className="min-h-[44px]">
          <Headphones className="h-4 w-4 mr-2" />
          Generate Briefing
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {/* Stale banner */}
      {isStale && (
        <div className="rounded-lg border border-amber-300 bg-amber-50 p-3 flex items-center gap-3">
          <AlertTriangle className="h-4 w-4 shrink-0 text-amber-700" />
          <p className="text-sm text-amber-900 flex-1">
            New data available since this briefing was generated.
          </p>
          <Button
            size="sm"
            className="bg-amber-600 hover:bg-amber-700 text-white min-h-[44px]"
            onClick={generate}
          >
            <RefreshCw className="h-3.5 w-3.5 mr-1.5" />
            Update Briefing
          </Button>
        </div>
      )}

      {/* Player row */}
      <div className="rounded-lg border bg-card p-4">
        <div className="flex items-center gap-3 flex-wrap">
          <Headphones className="h-5 w-5 shrink-0 text-primary" />
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium truncate">{data.title}</p>
            <p className="text-xs text-muted-foreground">
              Generated {data.generated_date}
            </p>
          </div>
          <Badge variant="outline" className="text-[11px] shrink-0">
            {data.script.length} lines
          </Badge>
        </div>

        <div className="mt-3 flex items-center gap-3">
          <Button
            size="sm"
            variant="default"
            className="min-h-[44px] min-w-[44px]"
            onClick={togglePlay}
            aria-label={isPlaying ? "Pause briefing" : "Play briefing"}
          >
            {isPlaying ? (
              <Pause className="h-4 w-4" />
            ) : (
              <Play className="h-4 w-4" />
            )}
          </Button>
          <div className="flex-1 flex items-center gap-2">
            <span className="text-xs text-muted-foreground tabular-nums w-10">
              {formatTime(currentTime)}
            </span>
            <div className="flex-1 h-1.5 bg-muted rounded-full overflow-hidden">
              <div
                className="h-full bg-primary transition-all"
                style={{
                  width: duration
                    ? `${Math.min(100, (currentTime / duration) * 100)}%`
                    : "0%",
                }}
              />
            </div>
            <span className="text-xs text-muted-foreground tabular-nums w-10 text-right">
              {formatTime(duration)}
            </span>
          </div>
          <Button
            size="sm"
            variant="outline"
            className="min-h-[44px]"
            onClick={handleDownload}
            aria-label="Download briefing as MP3"
          >
            <Download className="h-4 w-4" />
          </Button>
          <Button
            size="sm"
            variant="ghost"
            className="min-h-[44px]"
            onClick={generate}
            disabled={loading}
            aria-label="Regenerate briefing"
          >
            <RefreshCw className="h-4 w-4" />
          </Button>
        </div>

        <audio
          ref={audioRef}
          src={data.audio_url}
          preload="metadata"
          onPlay={() => setIsPlaying(true)}
          onPause={() => setIsPlaying(false)}
          onEnded={() => setIsPlaying(false)}
          onLoadedMetadata={(e) => setDuration(e.currentTarget.duration || 0)}
          onTimeUpdate={(e) => setCurrentTime(e.currentTarget.currentTime)}
        />
      </div>

      {/* Script toggle */}
      <div>
        <Button
          size="sm"
          variant="ghost"
          className="text-xs text-muted-foreground gap-1.5 min-h-[44px]"
          onClick={() => setShowScript((v) => !v)}
          aria-expanded={showScript}
        >
          {showScript ? (
            <ChevronUp className="h-3.5 w-3.5" />
          ) : (
            <ChevronDown className="h-3.5 w-3.5" />
          )}
          {showScript ? "Hide" : "Show"} Script
        </Button>
        {showScript && (
          <div className="mt-2 rounded-lg border overflow-hidden">
            {data.script.map((line, i) => (
              <div
                key={i}
                className={`px-3 py-2 text-sm ${
                  i % 2 === 0 ? "bg-muted/50" : "bg-card"
                }`}
              >
                <span className="font-semibold capitalize mr-2">
                  {line.speaker}:
                </span>
                <span>{line.text}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Thinking trace */}
      {data.thinking && (
        <div>
          <Button
            size="sm"
            variant="ghost"
            className="text-xs text-muted-foreground gap-1.5 min-h-[44px]"
            onClick={() => setShowThinking((v) => !v)}
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
    </div>
  );
}
