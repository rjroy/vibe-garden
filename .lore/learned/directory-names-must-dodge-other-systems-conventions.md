---
title: Directory names in a plugin must dodge other systems' conventions
date: 2026-04-25
status: approved
tags: [naming, plugin-development, gitignore]
modules: [lore-development]
---

A plugin lives inside other people's projects. Its directory names share
namespace with every language ecosystem the project might use. Names that look
fine in isolation collide:

- `build/` — gitignored by Python, CMake, npm, Gradle, Maven, Rust, Go templates.
  Files inside are silently invisible to git.
- `dist/`, `target/`, `out/`, `node_modules/` — same problem.
- `cache/`, `tmp/` — often ignored or scrubbed.

There is no mechanical check for this. Picking a name is a judgment call that
has to consider what other systems do with that word. The instinct is to name
for what the directory means inside the plugin; the discipline is to also ask
what the name means outside it.

Caught when `/tend migrate` produced `.lore/build/` and the root `.gitignore`'s
`build/` line (Python boilerplate) hid all 86 migrated files from git.
