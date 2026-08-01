# JARVIS PRO – Developer V2

Developer V2 is a modular software engineering subsystem for JARVIS PRO.

## Goals

- Stable architecture
- Modular design
- Easy testing
- Independent subsystems
- No circular dependencies
- Clean public API
- AI-agnostic generation pipeline
- Maintainable codebase

---

## Design Principles

1. One responsibility per module.
2. Public interfaces remain stable.
3. No module performs another module's work.
4. Every phase is independently testable.
5. Analysis precedes planning.
6. Planning precedes generation.
7. Generation precedes validation.
8. Validation precedes workspace operations.
9. Workspace is the only layer that writes files.
10. Integration with JARVIS occurs only after the subsystem is complete.

---

## Development Phases

Phase 0 – Foundation

Phase 1 – Core Models

Phase 2 – Analyzer

Phase 3 – Planner

Phase 4 – Prompt Builder

Phase 5 – Generator

Phase 6 – Validator

Phase 7 – Workspace

Phase 8 – Editing

Phase 9 – Memory

Phase 10 – Integration

Phase 11 – Advanced Features

---

## Public API

DeveloperAPI

This is the only class exposed to JARVIS.

No other module may import internal Developer components directly.

---

## Internal Flow

User Request
      ↓
Analyzer
      ↓
Planner
      ↓
Prompt Builder
      ↓
Generator
      ↓
Validator
      ↓
Workspace
      ↓
Developer Result

---

## Rules

- No circular imports.
- No hidden global state.
- Stable interfaces after each phase.
- Clear separation of concerns.
- Every phase must pass its tests before proceeding.
- Do not modify completed phases to add unrelated functionality.