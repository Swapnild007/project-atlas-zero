# Project Atlas Zero

**Experimental milestone-scale AI ecosystem. Not production-ready.**

Atlas Zero is intended to combine multimodel intelligence, research, creation, automation, files, coding, voice, memory, and connected tools. These are product goals, not claims that every capability is available.

## Implemented components (pending full-suite verification)
- Local Python HTTP server with a mobile-first web chat workspace at http://127.0.0.1:8080/
- Functional chat Send and New Chat controls; model and provider selection; in-memory BYOK credentials
- Gemini, OpenAI, Groq, OpenRouter, and Mistral adapters
- Local SQLite conversation history
- Curated Wikipedia search tool supporting English, Hindi, and Marathi
- Local API endpoints: GET /health, /providers, /tools; POST /chat, /tools/run
- Automated offline tests

## Run locally
Requires Python 3.11+.

```bash
python -m atlas_zero.server
```

Open http://127.0.0.1:8080/ in the same computer's browser. In Settings choose a provider and enter your own API key. No API key is needed to display the interface. You may alternatively configure GEMINI_API_KEY in your local environment.

Optional local API protection: set ATLAS_ACCESS_TOKEN before starting the server and enter that same token in Settings.

Run offline tests:

```bash
python -m unittest discover -s tests -v
```

Optional live Gemini check (requires a configured key):

```bash
python -m scripts.live_smoke
```

## Security and release limits
- Binds only to loopback. Do not expose this server to the internet or route through a public proxy.
- The optional shared access token is not user authentication or multi-tenant isolation.
- Conversation content persists in unencrypted local SQLite. Do not enter sensitive information.
- BYOK keys stay in browser-tab memory but are transmitted to the trusted local backend for provider requests.
- No production authentication, secure multiuser tenancy, public deployment, autonomous coding execution, or universal tool support.
- API quotas, costs, and availability depend on individual providers.
- The latest commits have not been independently verified by a full local test run or live API smoke test.

The name Atlas Zero is provisional. This project is independent and has no claimed government endorsement.
