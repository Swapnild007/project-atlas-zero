# Bring Your Own Key (BYOK) design

Status: design approved for implementation; not yet a working UI.

## Settings

AI & Models > Connections:
- Provider dropdown: OpenAI, Gemini, Groq, OpenRouter, Mistral; extensible registry.
- Model selector populated from a vetted per-provider catalog; optional custom model ID.
- Password-masked API key field; never prefill or return stored secrets to the UI.
- Test connection, Connect, Disconnect, and Clear session actions.
- Clear indication of whether a key is session-only or stored on device.
- Explain that API usage may incur charges billed by the selected provider.

## Security boundary

No shared API keys in source code, GitHub, CI, or public static assets.
Browser-only mode: session-memory credentials only; no localStorage, IndexedDB, cookies, URL parameters, analytics, logs, or service worker caches for secrets. Refresh clears them. Direct browser-to-provider calls are allowed only when the provider explicitly supports safe browser requests and CORS; otherwise disable this path.

Preferred production mode: authenticated backend proxy with TLS. The browser submits a key over TLS for the active session. The backend keeps the key only in memory, associates it with the authenticated session, never persists it, and sends requests to a fixed provider allowlist. Never accept an arbitrary endpoint URL, to prevent SSRF and key exfiltration. Enforce rate limits, payload limits, session expiry, redaction, and CSRF protections where cookie authentication is used. A multi-instance deployment needs session affinity or a dedicated secure ephemeral store; do not imply process memory works across instances. No provider switching with user content without explicit opt-in.

Android mode: optional Android Keystore-backed encrypted local credential storage, requiring explicit opt-in; key must not be backed up or included in crash reports.

## Provider interface

Provider adapters implement validate_config, list_models, and generate(messages, config, credential).
Errors are standardized: missing_credentials, authentication_failed, rate_limited, unavailable, invalid_model, invalid_response.
Provider and model choice is explicit. Automatic fallback must be opt-in and show the target provider before sharing message content.

## Acceptance criteria

1. No secret appears in repository, app bundles, HTTP responses, logs, traces, browser storage, or crash reports.
2. A session-only key is removed on disconnect, expiration, and process termination.
3. Missing/invalid keys produce actionable errors without exposing credentials.
4. At least two adapters pass contract tests with fake transports, including Unicode messages and error mapping.
5. Test connection is opt-in and uses a minimal request with no conversation history.
6. Browser UI is not considered complete until end-to-end tests cover connect, send, receive, disconnect, and failed requests.
7. Live provider tests require private runtime credentials, never GitHub Actions secrets.
