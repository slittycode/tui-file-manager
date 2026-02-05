# Agent Operating Guide (Non-Kiro)

## Purpose
This document defines how any non-Kiro agent (Codex, Gemini, Copilot, or others) should operate in this repo. It is intentionally strict to prevent scope creep and accidental changes outside the project.

## Scope And Constraints
- Operate only within this repository directory.
- Do not read, write, or execute outside the repo folder unless the human explicitly approves.
- Do not add new dependencies or frameworks without explicit approval.
- Do not run network calls unless explicitly approved.
- Prefer small, reversible changes and keep diffs focused.

## Repo Facts (Current State)
- Language: Python.
- UI: Textual (TUI).
- Entry point: `main.py` calls `FileManagerApp` from `app.py`.
- Core UI logic lives in `app.py`.
- `TODO.md` defines the roadmap and is the source of truth for future work.

## Desired Direction (From Repo Roadmap)
- Fix dual-pane layout issues.
- Improve file preview (syntax highlighting).
- Add file operations (copy, move, delete, rename).
- Add keyboard shortcuts for operations.
- Add a status bar with file info.
- Add search/filter, bookmarks, and tabs.

## Current Limitations
- No file operations yet.
- Preview is text-only with a 1MB size limit.
- Synchronous filesystem reads can block the UI on slow paths.
- Test coverage is minimal.

## Working Style
- Read `README.md` and `TODO.md` before making changes.
- Keep UI behavior consistent with help text and key bindings.
- Prefer safe filesystem handling with clear error states.
- Keep behavior predictable and avoid “magic” features.

## Output Expectations
- If you make changes, summarize what changed and list the files touched.
- If you add tests, run them and report the command used.

## Non-Negotiables
- Stay within the repo folder.
- Follow this document first if other instructions conflict.

