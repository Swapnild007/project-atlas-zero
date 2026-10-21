# Atlas Zero product ownership decisions

Status: active engineering plan, not a claim of completed features.

## Mission
A general-purpose AI assistant that answers, researches, creates, analyzes, and takes explicitly authorized actions. SaaS and website creation are examples, not the sole product.

## Architecture decisions
- Python standard-library backend for the current zero-cost prototype.
- BYOK model adapters: Gemini, OpenAI, Groq, OpenRouter, Mistral. No developer-owned shared key.
- Curated public tool registry; never fetch arbitrary URLs.
- Local-only HTTP server until real user authentication, tenancy isolation, abuse controls, and deployment security are implemented.
- SQLite for local conversation persistence. No cloud sync by default.
- Mobile-first accessible web UI after backend release gates; avoid shipping inert controls.
- Explicit user consent before cross-provider data sharing, external writes, deployment, or paid operations.

## Prioritized delivery
P0: repeatable offline tests, secret redaction, credential boundary, authenticated local access, conversation isolation.
P1: provider-neutral model selection, tools with reliable citations, user-visible error states, chat send/receive.
P2: working settings and mobile-first interface, conversation history and deletion, end-to-end tests.
P3: files, documents, research, code tasks, MCP, and optional deployment integrations.

## Known risks
- Optional ATLAS_ACCESS_TOKEN is a single local bearer token, NOT multi-user authentication.
- Current session IDs are user-selected and do NOT provide tenancy isolation.
- SQLite stores message content unencrypted.
- BYOK keys are carried in request bodies and must only be used on trusted local loopback until a secure deployment design is implemented.
- External model availability, pricing, quotas and terms vary.
- No live provider or public tool network verification is claimed.

## Release rule
No public deployment or claim of production readiness until security review, isolation, end-to-end checks, and live integration verification succeed.
