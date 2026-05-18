# HTML Base Template

This is the canonical HTML shell that all lore-development skills copy as their starting point.

**How to use**: Copy the full HTML block below verbatim. Fill in the `<meta>` tag values, update the title in `<head>` and `<header>`, and replace the `<main>` placeholder content with artifact-specific sections.

**Annotation re-embed rule**: When regenerating an artifact that already exists on disk, you MUST read the existing file, extract all `<div class="user-note">` elements, and re-embed them in the regenerated artifact. User notes must never be lost on regeneration. Remove a note only after you have explicitly acted on its content.

---

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>[Document Title]</title>

  <!-- Lore frontmatter -- all skills populate these -->
  <meta name="lore-title"   content="[Document title]">
  <meta name="lore-date"    content="YYYY-MM-DD">
  <meta name="lore-status"  content="[status]">
  <meta name="lore-tags"    content="[tag1, tag2, tag3]">
  <meta name="lore-modules" content="[module1, module2]">
  <meta name="lore-related" content="[.lore/path/to/related.html]">

  <!-- Type-specific fields: include only the ones relevant to this artifact type -->
  <!-- Spec:  <meta name="lore-req-prefix" content="AUTH"> -->
  <!-- Notes: <meta name="lore-source"     content=".lore/work/plans/some-plan.html"> -->
  <!-- Task:  <meta name="lore-source"     content=".lore/work/plans/some-plan.html"> -->
  <!-- Task:  <meta name="lore-sequence"   content="1"> -->

  <style>
    /* =====================================================================
       BASE RESET & TYPOGRAPHY
       ===================================================================== */
    *, *::before, *::after { box-sizing: border-box; }

    :root {
      --font-body: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      --font-mono: "SF Mono", "Fira Code", "Fira Mono", "Roboto Mono", Menlo, Courier, monospace;

      --color-bg:           #f9f9f8;
      --color-surface:      #ffffff;
      --color-border:       #e5e4e0;
      --color-text:         #1c1b19;
      --color-text-muted:   #6b6a65;
      --color-accent:       #3b6ef0;
      --color-accent-light: #eef2fe;

      --color-user-note-bg:     #fffbeb;
      --color-user-note-border: #f59e0b;
      --color-user-note-text:   #92400e;

      --color-open-q-bg:     #fef3c7;
      --color-open-q-border: #fbbf24;

      --color-req-id-bg:   #eff6ff;
      --color-req-id-text: #1d4ed8;

      --radius:   6px;
      --max-width: 800px;
    }

    html { font-size: 16px; }

    body {
      font-family: var(--font-body);
      background: var(--color-bg);
      color: var(--color-text);
      line-height: 1.65;
      margin: 0;
      padding: 2rem 1rem 4rem;
    }

    /* =====================================================================
       LAYOUT
       ===================================================================== */
    header, main {
      max-width: var(--max-width);
      margin: 0 auto;
    }

    /* =====================================================================
       HEADER
       ===================================================================== */
    header {
      background: var(--color-surface);
      border: 1px solid var(--color-border);
      border-radius: var(--radius);
      padding: 1.25rem 1.5rem 1rem;
      margin-bottom: 1.5rem;
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
    }

    header h1 {
      margin: 0;
      font-size: 1.4rem;
      font-weight: 700;
      color: var(--color-text);
    }

    .meta-bar {
      display: flex;
      flex-wrap: wrap;
      gap: 0.5rem;
      align-items: center;
      font-size: 0.8rem;
      color: var(--color-text-muted);
    }

    .meta-bar .badge {
      display: inline-block;
      background: var(--color-accent-light);
      color: var(--color-accent);
      border-radius: 999px;
      padding: 0.15em 0.6em;
      font-size: 0.75rem;
      font-weight: 500;
    }

    .meta-bar .sep { color: var(--color-border); }

    .header-actions {
      display: flex;
      justify-content: flex-end;
    }

    /* =====================================================================
       COPY-AS-PROMPT BUTTON
       Single button per artifact. Lives in the header only.
       Clicking copies: Add a user note to "[title]": 
       ===================================================================== */
    .copy-prompt-btn {
      appearance: none;
      background: transparent;
      border: 1px solid var(--color-border);
      border-radius: var(--radius);
      color: var(--color-text-muted);
      cursor: pointer;
      font-family: var(--font-body);
      font-size: 0.75rem;
      padding: 0.25em 0.75em;
      transition: border-color 0.15s, color 0.15s;
    }
    .copy-prompt-btn:hover {
      border-color: var(--color-accent);
      color: var(--color-accent);
    }
    .copy-prompt-btn.copied {
      border-color: #22c55e;
      color: #16a34a;
    }

    /* =====================================================================
       MAIN CONTENT
       ===================================================================== */
    main { display: flex; flex-direction: column; gap: 1.25rem; }

    /* =====================================================================
       SECTIONS
       ===================================================================== */
    section {
      background: var(--color-surface);
      border: 1px solid var(--color-border);
      border-radius: var(--radius);
      padding: 1.25rem 1.5rem;
    }

    section h2 {
      margin: 0 0 0.75rem;
      font-size: 1rem;
      font-weight: 700;
      color: var(--color-text);
      text-transform: uppercase;
      letter-spacing: 0.05em;
      font-size: 0.8rem;
    }

    section h3 {
      margin: 1rem 0 0.5rem;
      font-size: 0.95rem;
      font-weight: 600;
    }

    section p { margin: 0 0 0.75rem; }
    section p:last-child { margin-bottom: 0; }

    section ul, section ol {
      margin: 0 0 0.75rem;
      padding-left: 1.5rem;
    }
    section li { margin-bottom: 0.25rem; }

    /* =====================================================================
       OPEN QUESTIONS -- visually highlighted
       ===================================================================== */
    section#open-questions {
      background: var(--color-open-q-bg);
      border-color: var(--color-open-q-border);
    }

    /* =====================================================================
       USER NOTES -- ephemeral, amber tint
       These are short-lived. Claude reads and removes after acting on them.
       ===================================================================== */
    .user-note {
      background: var(--color-user-note-bg);
      border: 1px solid var(--color-user-note-border);
      border-radius: var(--radius);
      color: var(--color-user-note-text);
      font-size: 0.9rem;
      margin: 0.75rem 0;
      padding: 0.75rem 1rem;
    }

    .user-note::before {
      content: "📝 User note: ";
      font-weight: 600;
    }

    /* =====================================================================
       REQUIREMENT IDs -- spec artifacts
       ===================================================================== */
    span.req-id {
      background: var(--color-req-id-bg);
      color: var(--color-req-id-text);
      border-radius: 4px;
      font-family: var(--font-mono);
      font-size: 0.78rem;
      font-weight: 600;
      padding: 0.1em 0.4em;
    }

    /* =====================================================================
       COLLAPSIBLE SECTIONS -- work artifacts (brainstorm, spec, plan)
       ===================================================================== */
    details {
      border: 1px solid var(--color-border);
      border-radius: var(--radius);
      margin-bottom: 0.5rem;
    }

    summary {
      cursor: pointer;
      font-weight: 600;
      font-size: 0.9rem;
      padding: 0.6rem 0.75rem;
      list-style: none;
      user-select: none;
    }
    summary::-webkit-details-marker { display: none; }
    summary::before {
      content: "▸ ";
      font-size: 0.75em;
      opacity: 0.6;
    }
    details[open] > summary::before { content: "▾ "; }
    details > *:not(summary) { padding: 0.5rem 0.75rem 0.75rem; }

    /* =====================================================================
       CODE
       ===================================================================== */
    code {
      font-family: var(--font-mono);
      font-size: 0.85em;
      background: #f1f0ee;
      border-radius: 3px;
      padding: 0.1em 0.35em;
    }

    pre {
      background: #f1f0ee;
      border: 1px solid var(--color-border);
      border-radius: var(--radius);
      font-family: var(--font-mono);
      font-size: 0.85rem;
      overflow-x: auto;
      padding: 1rem;
    }
    pre code { background: none; padding: 0; }

    /* =====================================================================
       LINKS
       ===================================================================== */
    a { color: var(--color-accent); text-decoration: none; }
    a:hover { text-decoration: underline; }

    /* =====================================================================
       RESPONSIVE
       ===================================================================== */
    @media (max-width: 600px) {
      body { padding: 1rem 0.75rem 3rem; }
      header, section { padding: 1rem; }
    }
  </style>
</head>
<body>

<!--
  ANNOTATION RE-EMBED RULE:
  When regenerating this artifact from a newer spec/plan/etc., you MUST first read the
  existing file on disk, extract every <div class="user-note"> element, and re-embed
  each one in the regenerated output at the closest contextually appropriate location.
  User notes must NEVER be discarded on regeneration.
  Remove a user note only after you have explicitly acted on its content.
-->

<header>
  <h1>[Document Title]</h1>
  <div class="meta-bar">
    <span class="badge">[status]</span>
    <span class="sep">·</span>
    <span>[YYYY-MM-DD]</span>
    <span class="sep">·</span>
    <span>[tag1, tag2, tag3]</span>
  </div>
  <div class="header-actions">
    <button class="copy-prompt-btn" onclick="copyPrompt(this)">Copy as Prompt</button>
  </div>
</header>

<main>
  <!--
    SKILL CONTENT GOES HERE.
    
    Replace this comment block with artifact-specific <section> elements.
    
    Use canonical cross-skill IDs where they apply:
      <section id="context">      — background and framing
      <section id="summary">      — key findings or decisions (one paragraph overview)
      <section id="open-questions"> — unresolved questions
      <section id="next-steps">   — optional: where this leads
    
    Add type-specific sections with their own IDs, e.g.:
      <section id="requirements"> — for specs
      <section id="approaches">   — for designs
      <section id="decision">     — for designs
      <section id="steps">        — for plans
    
    User notes are placed inline as <div class="user-note"> elements.
    They are ephemeral: Claude reads and removes them after acting.
    Example:
      <div class="user-note">Reconsider the third approach — it has a latency issue.</div>
    
    Example section:
      <section id="context">
        <h2>Context</h2>
        <p>Background and framing for this artifact.</p>
      </section>
  -->
</main>

<script>
  function copyPrompt(btn) {
    const titleMeta = document.querySelector('meta[name="lore-title"]');
    const title = titleMeta ? titleMeta.getAttribute('content') : document.title;
    const prompt = 'Add a user note to "' + title + '": ';
    navigator.clipboard.writeText(prompt).then(function() {
      btn.textContent = 'Copied!';
      btn.classList.add('copied');
      setTimeout(function() {
        btn.textContent = 'Copy as Prompt';
        btn.classList.remove('copied');
      }, 2000);
    }).catch(function() {
      // Fallback: select a hidden textarea
      var ta = document.createElement('textarea');
      ta.value = prompt;
      ta.style.position = 'fixed';
      ta.style.opacity = '0';
      document.body.appendChild(ta);
      ta.select();
      document.execCommand('copy');
      document.body.removeChild(ta);
      btn.textContent = 'Copied!';
      btn.classList.add('copied');
      setTimeout(function() {
        btn.textContent = 'Copy as Prompt';
        btn.classList.remove('copied');
      }, 2000);
    });
  }
</script>

</body>
</html>
```

---

## Field Reference

All `<meta name="lore-*">` tags correspond to the schema defined in `frontmatter-schema.md`.

| Meta tag | YAML equivalent | Notes |
|---|---|---|
| `lore-title` | `title:` | Required |
| `lore-date` | `date:` | Required, YYYY-MM-DD |
| `lore-status` | `status:` | Required, type-specific values |
| `lore-tags` | `tags:` | Comma-separated |
| `lore-modules` | `modules:` | Comma-separated, optional |
| `lore-related` | `related:` | Comma-separated paths, optional |
| `lore-req-prefix` | `req-prefix:` | Specs only, optional |
| `lore-source` | `source:` | Notes and tasks, required |
| `lore-sequence` | `sequence:` | Tasks only, required |

## Richness by Artifact Type

Scale interactivity to the artifact:

- **Simple** (retro, learned entry, research): Clean structured sections, no collapsibles.
- **Standard** (brainstorm, design, issue): Sections with possible collapsibles for long content.
- **Rich** (spec, plan): Collapsible sections, `span.req-id` callouts, dependency indicators in plans.
- **Reference** (vision, distilled): Clean structured layout, no interactivity needed.
