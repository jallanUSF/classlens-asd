"use client";

import dynamic from "next/dynamic";

// Dynamic import to avoid SSR issues with Plotly
const Plot = dynamic(() => import("react-plotly.js"), { ssr: false });

interface DataPoint {
  date: string;
  pct: number;
}

interface Props {
  history: DataPoint[];
  targetPct: number;
  /** Height in pixels */
  height?: number;
}

export function ProgressMiniChart({ history, targetPct, height = 140 }: Props) {
  if (history.length === 0) {
    return (
      <p className="text-xs text-muted-foreground py-4 text-center">
        No session data yet
      </p>
    );
  }

  const dates = history.map((h) => h.date);
  const values = history.map((h) => h.pct);

  return (
    <Plot
      data={[
        {
          x: dates,
          y: values,
          type: "scatter",
          mode: "lines+markers",
          line: { color: "var(--primary)", width: 2, shape: "spline" },
          marker: { size: 5, color: "var(--primary)" },
          name: "Progress",
        },
        {
          x: [dates[0], dates[dates.length - 1]],
          y: [targetPct, targetPct],
          type: "scatter",
          mode: "lines",
          line: { color: "var(--success)", width: 1.5, dash: "dash" },
          name: "Target",
        },
      ]}
      layout={{
        height,
        margin: { t: 10, r: 10, b: 30, l: 35 },
        paper_bgcolor: "transparent",
        plot_bgcolor: "transparent",
        font: { family: "Inter, sans-serif", size: 11, color: "#6B7C8D" },
        xaxis: {
          showgrid: false,
          tickformat: "%b %d",
          tickfont: { size: 10 },
        },
        yaxis: {
          range: [0, 105],
          showgrid: true,
          gridcolor: "#E2E8F0",
          ticksuffix: "%",
          tickfont: { size: 10 },
        },
        showlegend: false,
      }}
      config={{ displayModeBar: false, responsive: true }}
      style={{ width: "100%" }}
    />
  );
}
