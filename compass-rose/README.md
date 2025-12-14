# Compass Rose

A Claude Code plugin for project management using GitHub Projects.

## Overview

Compass Rose provides skills, commands, and agents to help users and Claude manage a project together. It uses GitHub's project functionality (`gh project ...`) to track work items.

## Purpose

Compass Rose complements [Spiral Grove](../spiral-grove/) (the Spec-Driven Development plugin) by providing a place for:

- **Tasks/Bugs**: Small, actionable items like "the input box is too big" or "when refresh is hit during a refresh the server crashes"
- **Feature Ideas**: Larger questions that may eventually need a full spec, like "add functionality for different rule-based RPG systems into the engine"

While Spiral Grove handles the structured development workflow (Spec → Plan → Tasks → Implementation), Compass Rose manages the backlog of work items that feed into that process.

## Requirements

- GitHub CLI (`gh`) installed and authenticated
- A GitHub Project linked to your repository

## Configuration

Each repository using Compass Rose must define which GitHub Project it uses. (Configuration details TBD during spec phase.)

## Installation

```bash
/plugin install compass-rose@vibe-garden
```

## Status

**v0.1.0** - Initial project setup. Spec phase next.
