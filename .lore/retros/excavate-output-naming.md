---
title: Excavate Output Naming
date: 2026-01-28
status: complete
tags: [excavate, naming, artifact-structure, reference-docs]
modules: [lore-development]
---

# Retro: Excavate Output Naming

## Summary

The excavate skill saves documents to `.lore/specs/` but produces reference documentation, not specifications.

## The Problem

Excavate documents existing implementations by tracing code. The output describes what IS, not what SHOULD BE. These are reference documents, useful for onboarding and navigation, but they're not specifications in the traditional sense.

A specification defines requirements and success criteria before implementation. A reference document captures how something already works.

## What Should Change

1. Change `artifact_path` in SKILL.md frontmatter from `.lore/specs` to `.lore/reference`
2. Update all path references in SKILL.md from `.lore/specs/` to `.lore/reference/`
3. Update the excavation index template to reference `../reference/` instead of `../specs/`

## Affected Files

- `skills/excavate/SKILL.md` - frontmatter and all internal references

## Lesson Learned

Name artifacts by what they ARE, not by what they look like. Excavated documents look similar to specs (structured, detailed) but serve a different purpose (documenting reality vs defining intent).
