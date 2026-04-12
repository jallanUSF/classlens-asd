/**
 * Clean Gemma's thinking-trace text for display.
 *
 * Gemma's thinking mode output contains LaTeX math notation like
 * `$\rightarrow$`, `$27/60 = 45\%$`, `$5 + 5 + 5 = 15$`. Without a math
 * renderer those tokens show up as literal text in the Why? panel, which
 * looks like garbage. This helper converts the common macros to unicode
 * equivalents, strips `$...$` inline-math delimiters, and unescapes the
 * LaTeX percent/dollar/underscore escapes Gemma emits.
 *
 * We deliberately keep this a simple text transform rather than pulling in
 * KaTeX or MathJax — the thinking trace is narrative prose with occasional
 * arithmetic, not real math content.
 */

const MACRO_MAP: Record<string, string> = {
  rightarrow: "→",
  leftarrow: "←",
  Rightarrow: "⇒",
  Leftarrow: "⇐",
  leftrightarrow: "↔",
  uparrow: "↑",
  downarrow: "↓",
  times: "×",
  div: "÷",
  cdot: "·",
  pm: "±",
  mp: "∓",
  leq: "≤",
  geq: "≥",
  neq: "≠",
  approx: "≈",
  infty: "∞",
  Delta: "Δ",
  sum: "∑",
  alpha: "α",
  beta: "β",
  gamma: "γ",
  delta: "δ",
  sigma: "σ",
  mu: "μ",
  pi: "π",
};

export function sanitizeThinking(raw: string): string {
  if (!raw) return raw;

  let out = raw;

  // Replace `\macro` tokens (inside or outside math delimiters) with unicode.
  // Handles `$\rightarrow$`, `\rightarrow`, `$a \times b$`, etc.
  for (const [macro, glyph] of Object.entries(MACRO_MAP)) {
    const re = new RegExp(`\\\\${macro}\\b`, "g");
    out = out.replace(re, glyph);
  }

  // Strip inline-math delimiters `$...$` (LaTeX), keeping the inner text.
  // Guard against the dollar literal on its own (e.g. currency) by requiring
  // at least one non-dollar character between the delimiters.
  out = out.replace(/\$([^$\n]+?)\$/g, "$1");

  // Unescape common LaTeX escapes Gemma emits for reserved chars.
  out = out.replace(/\\%/g, "%");
  out = out.replace(/\\\$/g, "$");
  out = out.replace(/\\_/g, "_");
  out = out.replace(/\\&/g, "&");
  out = out.replace(/\\#/g, "#");

  return out;
}
