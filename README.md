# Project Atlas Zero

Early-stage experimental software. **Work in progress.**

This repository contains an initial Python backend for experimenting with AI-assisted conversations. The implementation is incomplete and is **not ready for production use**.

## Current contents

- Local HTTP endpoints: `GET /health` and `POST /chat`
- A Gemini API adapter requiring your own API key
- SQLite conversation history
- Automated unit and HTTP tests

These components have been committed to the repository. Passing CI and live provider integration have not yet been independently verified.

## Run locally

Requires Python 3.11+.

```bash
export GEMINI_API_KEY="your-api-key"
python -m atlas_zero.server
```

In a second terminal:

```bash
curl http://127.0.0.1:8080/health

curl http://127.0.0.1:8080/chat \
  -H 'Content-Type: application/json' \
  -d '{"session_id":"demo","message":"Hello"}'
```

Run tests:

```bash
python -m unittest discover -s tests -v
```

## Important limitations

- The HTTP server binds to localhost and has no user authentication.
- Conversation data is stored locally in SQLite without application-level encryption.
- Model requests require a separately configured Gemini API key and are subject to provider limits.
- No public deployment, agent tool execution, MCP, RAG, or production security controls are provided yet.
- Do not enter sensitive personal information or expose this server to the public internet.

## Development status

Development is ongoing. Functionality and interfaces may change. Issues and test results will guide subsequent changes.

## Project name

"Project Atlas Zero" is a temporary development name, not a finalized public brand.

This is an independent experimental project and has no claimed government affiliation or endorsement.
