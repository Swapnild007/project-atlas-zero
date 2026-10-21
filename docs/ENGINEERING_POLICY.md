# Blocker-resistant engineering policy

Atlas Zero must make progress without silently weakening privacy, security, correctness, or user consent.

## Dependency classification
- Essential: identity and access controls before public deployment, request validation, data isolation, tested send/receive flow.
- Replaceable: AI providers, model catalogs, deployment platforms, optional cloud databases.
- Optional: voice, research integrations, device actions, premium UI effects.

## Fallback contract
1. Detect the unavailable dependency and return a structured, actionable error.
2. Prefer an explicitly configured alternative only with user-approved routing.
3. Never claim a simulated response came from a live model.
4. Never retry endlessly or silently incur cost. Bound attempts and apply backoff.
5. Never downgrade transport security or send credentials to arbitrary endpoints.
6. Preserve pending user text locally when a request fails; allow an explicit retry.
7. Do not claim live verification until it has actually run.

## Delivery gates
- Offline unit and HTTP tests runnable without credentials or network.
- Provider contract tests use injected transports and fake credentials.
- Live tests are optional, run only in a private trusted runtime.
- The interface is not releasable until connect, send, response, errors, retry, and disconnect pass end-to-end checks.
- Public hosting requires authentication, abuse controls, secrets handling, and isolation between users.
- Document each remaining blocker and the smallest user action, if any, that is truly necessary.

## Initial implementation sequence
1. Provider-neutral request/response interface and mock adapters.
2. OpenAI-compatible adapter (OpenAI, Groq, OpenRouter, Mistral) with fixed provider base URLs.
3. BYOK session boundary and model selection API.
4. Accessible mobile-first settings and chat UI with real send/receive integration.
5. Automated end-to-end tests, then optional live provider checks.
