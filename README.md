# Project Atlas Zero

**Mission:** Build in India. Serve India. Compete globally.

An open, headless-first Indian AI agent platform. Public brand name is provisional pending trademark clearance.

## Current scope
- Python standard-library HTTP API
- Hosted Gemini model adapter (bring your own key)
- SQLite-backed conversation history
- Deterministic offline tests
- Future: Indian-language evaluations, MCP gateway, RAG, agent orchestration and secure execution

## Quick start
Requires Python 3.11+.

```bash
export GEMINI_API_KEY="your-key"
python -m atlas_zero.server
```

Health: `GET http://localhost:8080/health`

Chat:
```bash
curl -s http://localhost:8080/chat -H 'Content-Type: application/json' -d '{"message":"नमस्कार!","session_id":"demo"}'
```

Tests:
```bash
python -m unittest discover -s tests -v
```

Do not expose this development server to the public internet. Authentication, abuse prevention, hosted persistence and production security are future release gates.

## Release policy
A feature is complete only after automated tests and real acceptance checks pass. No claims of Government of India endorsement or official affiliation.
