/**
 * Consume a server-sent-events job stream from one of the streaming Gemma
 * endpoints (/api/alerts/{id}/analyze/stream, /api/documents/upload/stream,
 * /api/materials/generate/stream).
 *
 * Frame contract (matches backend/routers/_sse.py::run_streaming_job):
 *   - {"status": "working", "message": "..."}  ← heartbeat, called via onHeartbeat
 *   - {"result": <any>}                         ← resolves the returned promise
 *   - {"error": "..."}                          ← rejects the returned promise
 *   - {"done": true}                            ← stream terminator
 *
 * The backend sends heartbeats every few seconds so proxies (notably the
 * Turbopack dev proxy) keep the socket open during 30-75s Gemma calls.
 */
export async function consumeSseJob<T>(
  response: Response,
  options: { onHeartbeat?: (message: string) => void; signal?: AbortSignal } = {},
): Promise<T> {
  if (!response.ok || !response.body) {
    throw new Error(`Stream request failed: ${response.status}`);
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let finalResult: T | undefined;
  let finalError: string | null = null;
  let done = false;

  try {
    while (!done) {
      if (options.signal?.aborted) {
        throw new DOMException("Aborted", "AbortError");
      }
      const { value, done: streamDone } = await reader.read();
      if (streamDone) break;
      buffer += decoder.decode(value, { stream: true });

      const frames = buffer.split("\n\n");
      buffer = frames.pop() ?? "";

      for (const frame of frames) {
        const line = frame.trimStart();
        if (!line.startsWith("data:")) continue;
        const payload = line.slice(5).trim();
        if (!payload) continue;

        let parsed: {
          status?: string;
          message?: string;
          result?: T;
          error?: string;
          done?: boolean;
        };
        try {
          parsed = JSON.parse(payload);
        } catch {
          continue;
        }

        if (parsed.error) {
          finalError = parsed.error;
          continue;
        }
        if (parsed.result !== undefined) {
          finalResult = parsed.result;
          continue;
        }
        if (parsed.status === "working") {
          options.onHeartbeat?.(parsed.message ?? "Working…");
          continue;
        }
        if (parsed.done) {
          done = true;
          break;
        }
      }
    }
  } finally {
    try {
      reader.releaseLock();
    } catch {
      // Reader may already be closed.
    }
  }

  if (finalError) {
    throw new Error(finalError);
  }
  if (finalResult === undefined) {
    throw new Error("Stream ended without a result frame");
  }
  return finalResult;
}
