---
name: work-prd
description: Use when a PM needs to create or revise a LUKUKU-standard PRD from a Slack request, bounded project scope, source document, and verified project history.
metadata:
  version: 0.1.0
  author: hak2881
license: MIT
---

# Work PRD

Create a reviewable PRD from verified project history without turning historical discussion into approved scope.

Accepted inputs:

- `$work-prd <Slack permalink>`
- `$work-prd <project>`: inspect the project's request history and ask the user to select a bounded scope when more than one candidate exists.
- `$work-prd <project> <scope>`
- `$work-prd <document path or URL>`

Read [references/history-resolution.md](references/history-resolution.md) before selecting evidence and [references/prd-contract.md](references/prd-contract.md) before authoring the document.

## Workflow

1. Resolve the canonical project with `history_find_projects`, explicit source links, customer identity, and repository mappings. If multiple project identities materially change the result, ask the user instead of choosing one.
2. Load `history_project_context`, including current `policy_snapshots`, and search the project history for explicit request, decision, document, and source-link clusters before selecting a scope. Treat reviewed policy as a constraint on requirements, while reopening its authority source if the new request may change that policy. For a project-only invocation, load project history before asking the user to choose, then present independently releasable candidate outcomes with their source labels. Do not group candidates by keyword alone.
3. Establish one bounded PRD scope. A project name alone is not permission to merge unrelated requests. When the source history contains multiple possible releases or changes, ask which candidate belongs in this PRD. After selection, use `history_search` again for the chosen scope and build a claim ledger containing the proposed PRD section, claim, source, timestamp or version, authority, status, and conflicts.
4. Reopen every material primary source needed to support the current scope. Read complete Slack threads and current document versions. Refresh current code, Shopify, browser, or Admin evidence only when the as-is behavior or a platform constraint changes the requirement or acceptance criteria.
5. Apply the source and conflict rules in `history-resolution.md`. Historical implementation proves what existed, not what the customer currently requests. Do not reuse a cancelled, replaced, or superseded decision as current scope.
6. Draft the eight sections in `prd-contract.md`. Every functional requirement uses a stable `FR-NNN` ID and one of `확정 | 확인 필요 | 보류`. An explicit observable completion criterion is used as written; an agent-authored criterion stays visibly proposed and confirmation-required. Every unresolved decision that can change scope or acceptance appears in section 7.2.
7. Copy `assets/lukuku-prd-template.html` and `assets/lukuku-prd-template.css` into a versioned output directory under `~/.local/share/work-research-agent/prd/<project-slug>/`. Derive `<project-slug>` only from letters, numbers, `_`, and `-`; resolve the destination and verify it remains inside the PRD root before writing. Escape source text as HTML instead of inserting source-provided markup. Replace the template placeholders without changing the section order, field meanings, or LUKUKU visual system. Remove unused sample rows and leave no placeholder tokens in a completed draft.
8. Resolve this skill's installed directory, then validate with `python3 <skill-dir>/scripts/render_prd.py --validate-only <html>` and render with `python3 <skill-dir>/scripts/render_prd.py <html> <pdf>`. Do not assume the current directory or executable file mode. If Chrome or Chromium is unavailable, return the complete HTML and the renderer's exact installation message rather than claiming that a PDF was created. Visually inspect every rendered page for Korean text, table overflow, page breaks, and header/footer consistency. If any page fails, revise and rerender; return a PDF path only after every page passes.
9. Record each generated version through `history_record_document` with a unique external key, source URI, version, content hash, and captured time. Record newly verified claims through `history_record_evidence` and connect the PRD or individual requirements to their sources with `history_link_sources`. Namespace requirement keys as `<document-external-key>#FR-NNN`; never link a bare `FR-NNN` key.
10. Return the PM review summary, clickable HTML and PDF paths, bounded source coverage, unresolved decisions, and document status. Never post the PRD to Slack automatically.

## Responsibility boundary

The initial document status is `초안` unless an authoritative source explicitly supplies another status. Do not mark a PRD approved from silence, prior implementation, or successful rendering.

Do not create work items, TODOs, engineering estimates, branches, or product-code changes. A draft PRD is not implementation approval. After PM review, route feasibility, estimates, dependencies, and developer work-item creation to `$dev-plan <PRD path>`.

Do not overwrite an earlier PRD. Identify the predecessor by the same document number or explicit scope lineage in `project_documents` and `source_links`, not by the highest version in the whole project. A new scope starts at `v0.1`. A revision increments the draft version only after comparing with its explicit predecessor. Record a `prd_version` source link from the new external key to the predecessor key, and populate the change-history row with the changed requirement IDs, reason, reviewer or decision source, and source location. Use `v1.0` or an approved status only after an authoritative approval.

## Bundled standard

The plugin includes the reusable HTML/CSS implementation of the LUKUKU PRD standard. The original reference PDF is not required at runtime and is not stored in the history database. Project history supplies content and provenance; the bundled assets supply document structure and presentation.
