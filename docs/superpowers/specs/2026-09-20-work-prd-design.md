# Work PRD Skill Design

## Goal

Add `$work-prd` to turn a bounded Slack request, project scope, or source document into a versioned PRD using the LUKUKU PRD standard structure and evidence from local project history plus freshly checked primary sources.

## Boundaries

- The skill authors a PRD; it does not estimate effort, approve implementation, create developer TODOs, or modify product code.
- A project name without a bounded scope is insufficient when history contains multiple unrelated requests. The skill asks for the target scope instead of merging them.
- Stored history guides source discovery. Material requirements are checked against the relevant Slack thread, document, current platform state, or current code before they are stated as confirmed.
- Completed behavior and current code describe the as-is state; neither becomes a new requirement without an authoritative request.

## Source model

Each material PRD statement is classified as confirmed, needs confirmation, or held. Superseded and conflicting decisions remain visible in the internal claim ledger but are not silently promoted into current requirements. Every FR maps to one or more source references, and every unresolved decision that can change scope or acceptance appears in section 7.2.

## Standard document

The generated document retains the LUKUKU standard sections:

1. Document information and revision history
2. Background and goals
3. Included and excluded scope
4. Users and main business flow
5. Functional requirements, details, and optional technical explanation
6. Quality and constraints
7. Prerequisites and unresolved items
8. Overall acceptance criteria and related documents

The plugin ships an HTML/CSS template that reproduces the supplied standard's hierarchy, tables, typography, green accent, headers, footers, and A4 print layout. The source PDF is not bundled. Completed PRDs are editable HTML plus a shareable PDF rendered through an available Chrome or Chromium executable. Content may expand beyond seven pages rather than being compressed.

## Storage

Output lives below `~/.local/share/work-research-agent/prd/<project>/` with a sanitized scope, version, and unique suffix. Each version is recorded with `history_record_document`; supporting claims and document-to-source relationships use existing evidence and source-link tools. Draft PRDs do not create work items. `$dev-plan` consumes a reviewed PRD and owns feasibility, estimates, work-item decomposition, and acceptance-criterion persistence.

## Validation

- Distribution tests require the skill, references, assets, and renderer in both source and packaged plugin trees.
- Contract tests require scope resolution, source authority, conflict handling, section coverage, and the no-TODO/no-estimate boundary.
- The renderer validates required section markers, refuses accidental overwrite, creates a PDF with Chrome, and reports a clear HTML-only fallback when no supported browser exists.
- A sample PRD is rendered and visually checked for Korean text, table overflow, page breaks, header/footer consistency, and A4 output.
