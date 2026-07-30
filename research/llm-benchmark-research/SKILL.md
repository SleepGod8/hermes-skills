---
name: llm-benchmark-research
description: Research and compare LLM capabilities for specific domains (coding, reasoning, etc.) using live benchmark leaderboards. Covers data sources, browser-based extraction techniques, and structured presentation formats.
version: 1.0.0
tags: [llm, benchmark, research, model-comparison, coding, livebench, swe-bench]
---

# LLM Benchmark Research

When the user asks "which model is best for X" or "compare coding/reasoning/math models", this skill provides the workflow for gathering current, authoritative benchmark data and presenting it in a structured, actionable format.

## Key Data Sources

| Source | URL | Best For | Notes |
|--------|-----|----------|-------|
| **LiveBench** | https://livebench.ai | General capability (coding, reasoning, math, agentic) | Contamination-free, refreshed every 6 months. Has Coding + Agentic Coding subcategories. |
| **SWE-bench Verified** | https://www.swebench.com/verified.html | Real-world bug-fixing (agentic) | Gold standard for agentic coding. JS-rendered, requires browser. |
| **Aider Polyglot** | https://aider.chat/docs/leaderboards/ | Multi-language code editing | Good for refactoring/editing benchmarks. |
| **Chatbot Arena** | https://lmarena.ai | Human preference (coding subset available) | Subjective but large sample size. |

## Workflow

### Step 1: Identify the domain
Ask the user what kind of capability they care about: pure code generation, agentic coding (tool-using), reasoning, math, or general-purpose.

### Step 2: Navigate to LiveBench (primary source)
```
browser_navigate(url="https://livebench.ai/")
```
- Click "Leaderboard" if needed
- Select the latest release date
- Click the relevant category button (Coding, Agentic Coding, Reasoning, etc.)
- Use `browser_snapshot` to get the visible table

### Step 3: Extract full data via browser_console
When the page only shows partial rows, use JavaScript to extract all table data:

```javascript
(function() {
  var rows = document.querySelectorAll('table tbody tr');
  var result = [];
  for (var i = 0; i < rows.length; i++) {
    var cells = rows[i].querySelectorAll('td');
    if (cells.length > 1) {
      result.push(cells[1].textContent.trim() + ' | ' + cells[2].textContent.trim());
    }
  }
  return result.join('\n');
})()
```

Call this via `browser_console(expression="...")`. Slice with `.slice(N, M)` for pagination.

### Step 4: Cross-reference with domain knowledge
- Claude models: strong code generation, weaker at agentic coding
- GPT models: strong agentic coding, balanced across categories
- Open-weight models: Kimi K3, GLM-5.2, Qwen 3.6 are strong contenders
- Cost-effectiveness: check the "Cost per successful task" column

### Step 5: Present structured analysis
Use this format (the user prefers it):

1. **🏆 TOP ranking table** — sorted by the primary metric, with cost and open-source columns
2. **🤖 Sub-domain breakdown** — e.g., agentic coding separately if relevant
3. **💰 Cost-effectiveness table** — score ÷ cost for value ranking
4. **🎯 Scenario-based recommendations** — "if you want X, use Y"
5. **📝 User's current setup evaluation** — how their existing models stack up

Mark indicators: 🥇🥈🥉 for podium, ⭐ for standout value, 🏷️ for open-source, 💸 for expensive.

## Pitfalls

- **LiveBench page is JS-rendered**: `curl` won't work. Must use `browser_navigate` + `browser_snapshot` or `browser_console`.
- **Category filter buttons may not visually update**: After clicking a category button, the table header changes but the snapshot may appear identical. Always check the column headers (`columnheader` elements) to confirm the filter applied.
- **`browser_console` JS syntax limitations**: Arrow functions (`() => {}`) and template literals (backtick strings) can cause `SyntaxError: Unexpected end of input` or parse failures when passed as `expression` strings. Always wrap extraction logic in a classic `(function() { ... })()` IIFE and use string concatenation (`+`) instead of template literals:
  ```javascript
  // ✅ WORKS
  (function() { var rows = document.querySelectorAll('table tbody tr'); var r = []; for (var i = 0; i < rows.length; i++) { var c = rows[i].querySelectorAll('td'); if (c.length > 1) r.push(c[1].textContent.trim() + ' | ' + c[2].textContent.trim()); } return r.join('\n'); })()
  
  // ❌ BREAKS in browser_console expression
  (() => { ... })()
  ```
- **GitHub raw URLs are blocked in China**: If behind the GFW, use the proxy at `http://127.0.0.1:12450` for GitHub API calls. SWE-bench data lives in `swe-bench/experiments` repo.
- **SWE-bench also JS-rendered**: Same browser requirement.

## References

- `references/livebench-coding-2026-07.md` — LiveBench 2026-06-25 coding leaderboard snapshot (current as of July 2026)
