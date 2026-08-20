---
name: archify
description: Use when making architecture diagrams. Build Archify HTML.
version: 2.15.0
author: tt-a1i / Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [architecture-diagram, workflow-diagram, sequence-diagram, dataflow, lifecycle, html, svg]
    related_skills: [flowchart-diagrams, architecture-diagram, markdown-viewer]
---

# Archify

Use Archify to create polished, verifiable diagrams as standalone HTML with inline SVG, theme switching, optional motion, and export.

## When to Use

Use this skill when the user asks to:

- visualize architecture, infrastructure, cloud, security, or network topology
- draw workflows, runbooks, CI/CD, approval gates, or tool-call flows
- convert sequence diagrams, request lifecycles, state machines, or data pipelines
- beautify or modernize Mermaid flowchart/sequence/state input
- produce an explorable HTML diagram rather than a static screenshot

Do not use it for unrelated general docs or when the user only wants a plain text explanation.

## Core Workflow

1. Pick the diagram type first:
   - `architecture`
   - `workflow`
   - `sequence`
   - `dataflow`
   - `lifecycle`

2. Gather only the minimum evidence needed.
   - For fresh diagrams, use the user prompt and relevant source files.
   - For real codebases, inspect the repository first and keep labels faithful to the code.
   - For Mermaid input, preserve meaning but author fresh Archify JSON.

3. Draft the candidate before deep implementation work.
   - Start with one clear main path.
   - Keep side branches short.
   - Use sparse labels.
   - Prefer at most 12 primary nodes unless the user explicitly wants density.

4. Validate early and often.
   - Run validation after each meaningful edit.
   - Fix only the diagnosed issue before moving on.
   - Do not hand off a candidate that has not passed validation.

5. Deliver the final HTML only after validation passes.
   - If the user wants a preview, open the generated HTML locally.
   - If the user wants export, produce the requested format after the HTML is correct.

## Practical Guidance

### Diagram selection

- `architecture`: services, components, clouds, boundaries, trust zones
- `workflow`: processes, approvals, automation, runbooks, CI/CD
- `sequence`: request/response chains, async calls, lifecycle traces
- `dataflow`: pipelines, ETL/ELT, lineage, consumers
- `lifecycle`: state changes, retries, terminal states

### Mermaid handling

If the user pastes Mermaid:

- `flowchart` / `graph` → usually `workflow`
- `sequenceDiagram` → `sequence`
- `stateDiagram` → `lifecycle`
- preserve semantic meaning, but rewrite into Archify JSON rather than styling Mermaid directly

### Style defaults

- use `meta.quality_profile = "showcase"` unless the user explicitly wants dense/compact output
- omit optional visual presets unless asked
- keep labels readable and faithful
- do not invent a subtitle unless the user asked for one

## Common Pitfalls

1. **Too many nodes too early**
   Start small and expand only when the layout is proven.

2. **Overusing routing controls**
   Prefer natural layout first; only add geometry hints after a specific collision.

3. **Losing semantic accuracy**
   Keep product names, protocol names, and code identifiers exact.

4. **Skipping validation**
   Validation is part of the workflow, not optional polish.

5. **Returning a sketch instead of a deliverable**
   The goal is a usable HTML artifact, not just advice.

## Verification Checklist

- [ ] Diagram type chosen
- [ ] Evidence gathered if the diagram must reflect real code
- [ ] Candidate written before deep repair work
- [ ] Validation run and passed
- [ ] HTML deliverable produced if requested

## Notes

For the full upstream implementation, see the source repository:
https://github.com/tt-a1i/archify

If the user wants the full upstream authoring contract, you can inspect:
- `archify/SKILL.md`
- `archify/schemas/`
- `archify/examples/`
- `archify/references/`

