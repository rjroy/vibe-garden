---
title: mind-reader design principles
date: 2026-04-25
status: current
tags: [mind-reader, design-principles, nudges, ux]
modules: [mind-reader]
---

# mind-reader Design Principles

## Nudges observe, they do not prescribe

Every nudge message ends in a question ("Long session?", "Everything okay?", "Burning the midnight oil?") and reports the user's own baseline back to them ("your p95 is 30"). A nudge never tells the user what to do.

**Why:** the design framing was explicit from the start: "It's not actionable advice. It's a mirror." Prescriptive messages ("you should checkpoint", "take a break") shift the plugin from observation to nagging, which the user will silence — and a silenced plugin observes nothing.

**How to apply:** when adding a new check, the message must be baseline-relative and end in a question. If the observation can't be phrased as a question, the check probably isn't ready. Telling the user something they already feel ("you've been at this a while") only earns its keep when it's anchored to their own data ("you've been at this a while — your p95 is 30").
