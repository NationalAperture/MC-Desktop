Overlay: Security‑Critical (≤300 words)

Goal: Ship defensible changes with least privilege.

Rules

Threat Model (quick): assets, entry points, attacker goals, mitigations.

Inputs: validate/normalize; enforce length/charset; canonicalize paths; parameterize queries.

Secrets: only via env/secret manager; never log or echo.

Crypto: use vetted libs; modern AEAD; rotate keys; document algorithms.

Network: timeouts; retries with backoff; TLS settings documented.

AuthZ/AuthN: explicit scopes/roles; deny‑by‑default; audit sensitive actions.

Logging: structured, no PII/secret leakage; include correlation IDs.

Deliverables

Diff + tests (positive/negative cases) + brief risk note (≤80 words).