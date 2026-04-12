"use client";

import { useState, useRef, useCallback, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Mic,
  Square,
  Play,
  Send,
  Loader2,
  AlertCircle,
  CheckCircle,
  Keyboard,
} from "lucide-react";
import { consumeSseJob } from "@/lib/sseJob";

interface VoiceCaptureResult {
  transcription?: string;
  work_type?: string;
  subject?: string;
  student_work?: {
    task_description?: string;
    correct_responses?: number | null;
    total_responses?: number | null;
    accuracy_pct?: number | null;
    independence_level?: string | null;
    behavior_notes?: string;
  };
  confidence?: number;
  error?: string;
  fallback?: string;
}

interface Props {
  studentId: string;
  onCaptureComplete?: (result: VoiceCaptureResult) => void;
}

type CaptureMode = "idle" | "recording" | "preview" | "submitting" | "done" | "text";

export function VoiceCapture({ studentId, onCaptureComplete }: Props) {
  const [mode, setMode] = useState<CaptureMode>("idle");
  const [audioSupported, setAudioSupported] = useState<boolean | null>(null);
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [textInput, setTextInput] = useState("");
  const [result, setResult] = useState<VoiceCaptureResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loadingMessage, setLoadingMessage] = useState("Processing…");
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  // Check if voice capture is supported
  useEffect(() => {
    fetch("/api/capture/voice/supported")
      .then((r) => r.json())
      .then((data) => setAudioSupported(data.supported))
      .catch(() => setAudioSupported(false));
  }, []);

  const startRecording = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream, {
        mimeType: MediaRecorder.isTypeSupported("audio/webm;codecs=opus")
          ? "audio/webm;codecs=opus"
          : "audio/webm",
      });
      chunksRef.current = [];

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data);
      };

      recorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: "audio/webm" });
        setAudioBlob(blob);
        setAudioUrl(URL.createObjectURL(blob));
        setMode("preview");
        // Stop all tracks to release the mic
        stream.getTracks().forEach((t) => t.stop());
      };

      mediaRecorderRef.current = recorder;
      recorder.start();
      setMode("recording");
    } catch {
      setError("Could not access microphone. Please check browser permissions.");
    }
  }, []);

  const stopRecording = useCallback(() => {
    mediaRecorderRef.current?.stop();
  }, []);

  const submitAudio = useCallback(async () => {
    if (!audioBlob) return;
    setMode("submitting");
    setError(null);
    setLoadingMessage("Processing voice observation…");

    try {
      // Convert blob to base64
      const buffer = await audioBlob.arrayBuffer();
      const b64 = btoa(
        new Uint8Array(buffer).reduce((s, b) => s + String.fromCharCode(b), ""),
      );

      const res = await fetch("/api/capture/voice/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          student_id: studentId,
          audio_b64: b64,
          media_type: "audio/webm",
        }),
      });

      const data = await consumeSseJob<VoiceCaptureResult>(res, {
        onHeartbeat: (msg) => setLoadingMessage(msg),
      });

      setResult(data);
      setMode("done");
      onCaptureComplete?.(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Voice capture failed.");
      setMode("preview");
    }
  }, [audioBlob, studentId, onCaptureComplete]);

  const submitText = useCallback(async () => {
    if (!textInput.trim()) return;
    setMode("submitting");
    setError(null);
    setLoadingMessage("Processing observation…");

    try {
      const res = await fetch("/api/capture/voice/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          student_id: studentId,
          audio_b64: "",
          media_type: "audio/webm",
          text_fallback: textInput.trim(),
        }),
      });

      const data = await consumeSseJob<VoiceCaptureResult>(res, {
        onHeartbeat: (msg) => setLoadingMessage(msg),
      });

      setResult(data);
      setMode("done");
      onCaptureComplete?.(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Capture failed.");
      setMode("text");
    }
  }, [textInput, studentId, onCaptureComplete]);

  const reset = useCallback(() => {
    setMode("idle");
    setAudioBlob(null);
    if (audioUrl) URL.revokeObjectURL(audioUrl);
    setAudioUrl(null);
    setTextInput("");
    setResult(null);
    setError(null);
  }, [audioUrl]);

  // Done state — show extracted data
  if (mode === "done" && result) {
    const work = result.student_work;
    return (
      <div className="rounded-lg border bg-card p-4 space-y-3">
        <div className="flex items-center gap-2">
          <CheckCircle className="h-4 w-4 text-emerald-600" />
          <span className="text-sm font-medium">Observation captured</span>
        </div>
        {result.transcription && (
          <div className="rounded-md bg-muted/50 p-3">
            <p className="text-[11px] font-semibold uppercase tracking-wide text-muted-foreground mb-1">
              Transcription
            </p>
            <p className="text-sm">{result.transcription}</p>
          </div>
        )}
        {work && (
          <div className="grid grid-cols-2 gap-2 text-sm">
            {work.task_description && (
              <div className="col-span-2">
                <span className="text-muted-foreground">Activity: </span>
                {work.task_description}
              </div>
            )}
            {work.accuracy_pct != null && (
              <div>
                <span className="text-muted-foreground">Accuracy: </span>
                <span className="font-medium">{work.accuracy_pct}%</span>
                {work.correct_responses != null && work.total_responses != null && (
                  <span className="text-muted-foreground">
                    {" "}({work.correct_responses}/{work.total_responses})
                  </span>
                )}
              </div>
            )}
            {work.independence_level && (
              <div>
                <span className="text-muted-foreground">Independence: </span>
                <Badge variant="outline" className="text-xs">
                  {work.independence_level.replace(/_/g, " ")}
                </Badge>
              </div>
            )}
            {work.behavior_notes && (
              <div className="col-span-2">
                <span className="text-muted-foreground">Notes: </span>
                {work.behavior_notes}
              </div>
            )}
          </div>
        )}
        <Button size="sm" variant="outline" className="min-h-[44px]" onClick={reset}>
          Record Another
        </Button>
      </div>
    );
  }

  return (
    <div className="rounded-lg border border-dashed border-muted-foreground/30 p-4 space-y-3">
      {error && (
        <div className="flex items-center gap-2 text-sm text-destructive">
          <AlertCircle className="h-4 w-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Idle state — text-first. Audio path kept dormant for V2 (Gemma 4 E4B
          on-device via LiteRT-LM; enabled automatically when the backend
          reports audioSupported=true, e.g., once VOICE_AUDIO_ENABLED=1). */}
      {mode === "idle" && (
        <div className="flex flex-col items-center gap-3">
          <Keyboard className="h-8 w-8 text-muted-foreground/50" />
          <p className="text-sm text-muted-foreground text-center">
            Type a quick observation. One or two sentences is plenty.
          </p>
          <div className="flex gap-2">
            <Button
              className="min-h-[44px] gap-2"
              onClick={() => setMode("text")}
            >
              <Keyboard className="h-4 w-4" />
              Type Observation
            </Button>
            {audioSupported === true && (
              <Button
                variant="outline"
                onClick={startRecording}
                className="min-h-[44px] gap-2"
              >
                <Mic className="h-4 w-4" />
                Record
              </Button>
            )}
          </div>
        </div>
      )}

      {/* Recording state */}
      {mode === "recording" && (
        <div className="flex flex-col items-center gap-3">
          <div className="relative">
            <Mic className="h-8 w-8 text-destructive" />
            <span className="absolute -top-1 -right-1 h-3 w-3 rounded-full bg-destructive animate-pulse" />
          </div>
          <p className="text-sm font-medium text-destructive">Recording…</p>
          <Button
            variant="destructive"
            className="min-h-[44px] gap-2"
            onClick={stopRecording}
          >
            <Square className="h-4 w-4" />
            Stop
          </Button>
        </div>
      )}

      {/* Preview state */}
      {mode === "preview" && audioUrl && (
        <div className="flex flex-col items-center gap-3">
          <audio src={audioUrl} controls className="w-full max-w-sm" />
          <div className="flex gap-2">
            <Button
              variant="outline"
              className="min-h-[44px] gap-2"
              onClick={reset}
            >
              Re-record
            </Button>
            <Button className="min-h-[44px] gap-2" onClick={submitAudio}>
              <Send className="h-4 w-4" />
              Submit
            </Button>
          </div>
        </div>
      )}

      {/* Text input mode */}
      {mode === "text" && (
        <div className="space-y-3">
          <textarea
            placeholder="Type your observation… e.g., 'Marcus completed the coin sort. Got 4 out of 5. He was dysregulated at the start but recovered well.'"
            value={textInput}
            onChange={(e) => setTextInput(e.target.value)}
            rows={3}
            className="w-full resize-none rounded-md border border-input bg-background px-3 py-2 text-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          />
          <div className="flex gap-2 justify-end">
            <Button
              variant="outline"
              className="min-h-[44px]"
              onClick={reset}
            >
              Cancel
            </Button>
            <Button
              className="min-h-[44px] gap-2"
              onClick={submitText}
              disabled={!textInput.trim()}
            >
              <Send className="h-4 w-4" />
              Submit
            </Button>
          </div>
        </div>
      )}

      {/* Submitting state */}
      {mode === "submitting" && (
        <div className="flex flex-col items-center gap-2 py-4">
          <Loader2 className="h-6 w-6 text-primary animate-spin" />
          <p className="text-sm text-muted-foreground animate-pulse">
            {loadingMessage}
          </p>
        </div>
      )}
    </div>
  );
}
