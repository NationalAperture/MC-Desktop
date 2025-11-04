Overlay: Refactor & Migrations (≤300 words)

Goal: Improve design without changing behavior.

Rules

Safety: introduce seams; write characterization tests before moving code.

SOLID: split god objects; extract interfaces; invert dependencies.

Migrations: for DB, generate migration scripts + rollback plan; annotate risk.

Compatibility: preserve public APIs; deprecate with adapters and warnings.

Diff Clarity: grouped commits or sections (extract → move → delete). Keep functions <30 LOC where feasible.

Deliverables

Diff, tests (characterization + updated unit), migration scripts, and a 3–5 bullet rationale.

If risk detected

Ask “Challenge & Clarify” then proceed with safest path if no response.