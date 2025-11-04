# agent.md

> Entry point for codex to load **multiple agent guides** from `/AGENTS`.

This file tells codex *how* to compose prompts from the shared base guide and one (or more, in rare cases) role‑specific overlays—while keeping token usage in the Goldilocks zone.

## Directory layout

```
AGENTS/
  BASE.md            # shared rules (SOLID, token policy, review gates)
  codegen.md         # overlay for code generation
  refactor.md        # overlay for refactors/migrations
  research.md        # overlay for web/browsing research
  security.md        # overlay for high‑risk work
  manifest.yaml      # role→overlay mapping (optional but recommended)
AGENTS.md            # comprehensive operating guide (the one you created earlier)
agent.md             # ← this file (entry point)
```

## Composition rules (read carefully)

* Always load **`AGENTS/BASE.md`** first.
* Load **exactly one overlay** per task from `AGENTS/*.md` (e.g., `codegen.md`).
* Only add a second overlay for documented, high‑value cases (e.g., `security.md` + `codegen.md`).
* If an overlay conflicts with `BASE.md`, **the overlay wins**. Keep conflicts rare; prefer “extends” phrasing.
* Token policy: keep overlays **≤300 words**; keep `BASE.md` **≤800 words**.

## Role selection

Codex selects the overlay using the following precedence (first match wins):

1. **Env var**: `AGENTS_ROLE` (e.g., `codegen`, `refactor`, `research`, `security`).
2. **Manifest** (`AGENTS/manifest.yaml`), matching any of the `when` tags to the task label or user instruction.
3. **Heuristics**: inspect the ask; if uncertain, ask the user 3 tightly scoped questions, then default to `codegen` if no reply.

### Example `AGENTS/manifest.yaml`

```yaml
roles:
  codegen:
    path: AGENTS/codegen.md
    when: ["generate_code", "write_tests", "new_api"]
  refactor:
    path: AGENTS/refactor.md
    when: ["refactor", "migrate", "extract_module"]
  research:
    path: AGENTS/research.md
    when: ["investigate", "compare", "web_search"]
  security:
    path: AGENTS/security.md
    when: ["secrets", "auth", "crypto", "injection"]
```

## Loader contract (what codex should do)

1. **Read** `AGENTS/BASE.md`.
2. **Select** an overlay (`AGENTS/<role>.md`).
3. **Compose** the system prompt as: `AGENTS.md (summary header) + BASE.md + overlay header + overlay`.
4. **Cache** the composed system message for the session; do **not** resend it each turn.
5. **Echo** a one‑line header in the first response with the chosen role and version (e.g., `AGENTS v1.2 · overlay=codegen`).

> If any referenced file is missing: codex must ask for the file or proceed with `BASE.md` only (and state that it did).

## Minimal composition syntax (optional helper)

Codex MAY use the following markers in this file to locate includes if you don’t have a custom loader yet:

```
<!-- codex:includes
AGENTS/BASE.md
AGENTS/{ROLE}.md   # ROLE comes from AGENTS_ROLE, manifest, or heuristics
-->
```

A client that understands `codex:includes` can replace `{ROLE}` at runtime and load the two files.

## Token‑smart guidance for codex

* Do **not** inline the full text of `AGENTS.md` when `BASE.md` + overlay already encode the rules. Reference it when helpful.
* Prefer **diffs** over full files in outputs; include tests.
* Use the “Challenge & Clarify” pattern (≤80 words) when the ask seems risky or unclear; otherwise proceed.

## Quick check (self‑review for codex)

* Did I load `BASE.md` + exactly one overlay?
* Did I keep the prompt small (no redundant sections)?
* Did I announce the chosen role once, then stay quiet about it?
* If uncertain, did I ask 3 short, high‑leverage questions?

---

**Place this `agent.md` at the repo root** (next to `AGENTS.md`). Codex should read this file first to discover `/AGENTS`, then assemble its system prompt accordingly.
