// Quick smoke test for sanitizeThinking — run with:
//   cd frontend && npx tsx scripts/test_sanitize_thinking.ts
// Exits 0 on pass, non-zero on fail.

import { sanitizeThinking } from "../src/lib/sanitizeThinking";

const cases = [
  {
    name: "rightarrow macro in math delimiters",
    input: "45% $\\rightarrow$ Target: 70%",
    expect: "45% → Target: 70%",
  },
  {
    name: "times macro with arithmetic",
    input: "Total Trials: $10 \\times 6 = 60$",
    expect: "Total Trials: 10 × 6 = 60",
  },
  {
    name: "escaped percent in math",
    input: "$27/60 = 45\\%$",
    expect: "27/60 = 45%",
  },
  {
    name: "multiple macros on one line",
    input: "Trend: 50% $\\rightarrow$ 45% $\\rightarrow$ 40% (declining)",
    expect: "Trend: 50% → 45% → 40% (declining)",
  },
  {
    name: "macro without $ delimiters",
    input: "Gemma said \\rightarrow next step",
    expect: "Gemma said → next step",
  },
  {
    name: "standalone dollar is preserved",
    input: "The iPad costs $300 at Best Buy.",
    expect: "The iPad costs $300 at Best Buy.",
  },
  {
    name: "leq / geq macros",
    input: "Target: $\\leq 1$/day and success $\\geq 80\\%$",
    expect: "Target: ≤ 1/day and success ≥ 80%",
  },
  {
    name: "empty string",
    input: "",
    expect: "",
  },
];

let failed = 0;
for (const c of cases) {
  const got = sanitizeThinking(c.input);
  const ok = got === c.expect;
  console.log(`  ${ok ? "PASS" : "FAIL"}  ${c.name}`);
  if (!ok) {
    console.log(`    input:  ${JSON.stringify(c.input)}`);
    console.log(`    expect: ${JSON.stringify(c.expect)}`);
    console.log(`    got:    ${JSON.stringify(got)}`);
    failed++;
  }
}

console.log(`\n${cases.length - failed}/${cases.length} passed`);
process.exit(failed === 0 ? 0 : 1);
