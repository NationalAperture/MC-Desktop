Overlay: Code Generation (≤300 words)

Goal: Produce production‑ready code with tests and minimal tokens.

Rules

Scaffolding: generate only touched files; reference existing modules via stable interfaces.

SOLID & Hex: create/extend ports; adapters for DB/HTTP/queue; avoid framework leakage into domain.

API Design: document inputs/outputs; validate; choose clear names; add examples in docstrings.

Tests First (lightweight): outline 2–4 critical cases; then implement; include one property‑based test if pure logic.

Diff First: prefer a unified diff from repo root. Mark new files with # new file: headers.

Config: constants via config/env; no magic numbers.

Errors: explicit error types; remediation suggestion.

Deliverables

Unified diff + test files + one‑line run command.

Brief rationale (≤60 words) capturing key trade‑offs.

If info missing

Ask 3 quick questions (paths, interfaces, constraints). Default to safe interfaces and stubs if no reply.