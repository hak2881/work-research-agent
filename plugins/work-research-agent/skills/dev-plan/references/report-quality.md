# Evidence-first report quality

Use this standard for PM planning reports and developer implementation reports. The MUSA B2C tax-interface draft is the quality benchmark for information density and decision clarity, not a fixed visual template.

## Start from truth

- Put the decision before detail: state the purpose, verified conclusion, remaining decision, and next action before supporting material.
- Separate facts, proposals, and unknowns visibly. Never promote a suggestion or generated report sentence into an accepted requirement.
- Every material statement must trace to an original source, current repository SHA, observed runtime or platform result, or an explicit engineering proposal label.
- A generated HTML report is a navigation and communication artifact. Recheck original Slack, document, code, API, and runtime evidence before planning or implementing from it.

## Match the document to the decision

- Include only sections that help the reader decide, approve, implement, or verify the requested work. Do not copy the benchmark's section count, headings, table count, colors, or field taxonomy when they do not fit the request.
- Prefer a short inline answer when the conclusion and material evidence remain clear. Use HTML only when structure materially improves comprehension.
- Do not add architecture diagrams, option matrices, schedules, risks, estimates, or field catalogs unless the request and evidence require them.
- Avoid repeating the same conclusion in the summary, note, table, and footer. Link detail back to one concise conclusion.

## Parse dense source documents faithfully

- Use a format-aware reader for HTML, PDF, spreadsheets, slides, images, and word-processing files, and preserve heading and table topology, merged headers, row groups, footnotes, formulas versus displayed values, intentionally empty versus inherited cells, and image-only annotations when they affect meaning.
- Assign stable row identifiers from the source structure, such as page/table/row, sheet/range, section/field, or an explicit source key. Carry those identifiers into extracted mappings and evidence records.
- Perform rendered-view spot checks against the extracted mapping, including the beginning and end of each material table and every row where status, source, requirement level, or interpretation changes. For spreadsheets, inspect both the rendered sheet and relevant formulas; for PDFs or images, compare text extraction with the rendered page.
- Label OCR output, truncated content, ambiguous merged cells, and uncertain row associations as `unverified`. Do not normalize them into facts or silently fill blanks from neighboring rows.

## Build scannable evidence

- Use a compact title and metadata line, a short purpose or conclusion callout, then the minimum supporting sections.
- Show a structure or flow before a large mapping only when it explains how the rows relate.
- Use tables for comparable facts such as fields, options, dependencies, criteria, or source mappings. Each row should represent one atomic item.
- Choose columns by the decision. A data-contract table may use `필드 | 타입 | 구분 | 원천 | 설명 | 비고`; another request should use different columns when those are more useful.
- When status matters, use a small consistent vocabulary such as `필수 | 조건부 | 파생`, `확정 | 제안 | 미확인`, or `pass | fail | unverified`, and define it from evidence.
- Split a large table by entity, layer, or decision when that improves reading. Do not split it merely to make more sections.

## Keep the presentation restrained

- Optimize for information density: readable type, strong heading hierarchy, restrained colors, clear borders, adequate spacing, responsive table overflow, and print-safe layout.
- Use visual emphasis to encode meaning, not decoration. Keep one primary accent and a small number of status colors with readable contrast.
- Keep HTML self-contained and passive. Follow the owning skill's path, escaping, link, privacy, and file-permission rules.

## Quality gate

Before delivery, verify the content against the request and original sources, check that omitted sections are genuinely unnecessary, and confirm that labels distinguish sourced facts from engineering judgment. Render the HTML and visually verify desktop readability, narrow-screen behavior, table overflow, print output when relevant, and the absence of clipping, overlap, broken characters, empty blocks, or decorative noise. If visual polish conflicts with evidence or brevity, preserve evidence and brevity.
