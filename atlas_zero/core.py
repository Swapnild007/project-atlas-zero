import json
import os
import sqlite3
import urllib.error
import urllib.request
from pathlib import Path

SYSTEM_INSTRUCTION = "You are an accurate, respectful multilingual AI assistant built for users in India. Acknowledge uncertainty. Never invent sources or tool results."

class ProviderError(Exception):
    pass

def gemini_reply(messages, api_key=None, model=None, transport=None):
    key = api_key if api_key is not None else os.getenv("GEMINI_API_KEY", "")
    if not key:
        raise ProviderError("provider_not_configured")
    model = model or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    if not model.replace("-", "").replace(".", "").isalnum():
        raise ProviderError("invalid_model")
    payload = {
        "system_instruction": {"parts": [{"text": SYSTEM_INSTRUCTION}]},
        "contents": [{"role": "model" if m["role"] == "assistant" else "user", "parts": [{"text": m["content"]}]} for m in messages],
        "generationConfig": {"temperature": 0.4},
    }
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json", "x-goog-api-key": key}, method="POST")
    try:
        if transport is not None:
            result = transport(req)
        else:
            with urllib.request.urlopen(req, timeout=35) as response:
                result = json.load(response)
        text = "".join(p.get("text", "") for c in result.get("candidates", []) for p in c.get("content", {}).get("parts", []))
        if not text.strip():
            raise ProviderError("empty_provider_response")
        return text
    except urllib.error.HTTPError as exc:
        if exc.code == 429:
            raise ProviderError("provider_rate_limited") from exc
        raise ProviderError("provider_http_error") from exc
    except urllib.error.URLError as exc:
        raise ProviderError("provider_unreachable") from exc

class ConversationStore:
    def __init__(self, path=None):
        self.path = str(path or os.getenv("ATLAS_DB", "atlas-zero.sqlite3"))
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.execute("CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY, session_id TEXT NOT NULL, role TEXT NOT NULL, content TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP)")
            db.execute("CREATE INDEX IF NOT EXISTS idx_session ON messages(session_id, id)")

    def connect(self):
        return sqlite3.connect(self.path)

    def history(self, session_id, limit=40):
        with self.connect() as db:
            rows = db.execute("SELECT role, content FROM (SELECT id, role, content FROM messages WHERE session_id=? ORDER BY id DESC LIMIT ?) ORDER BY id", (session_id, limit)).fetchall()
        return [{"role": r, "content": c} for r, c in rows]

    def append_turn(self, session_id, user_message, assistant_message):
        # A conversation turn must be persisted atomically.
        with self.connect() as db:
            db.execute("INSERT INTO messages(session_id, role, content) VALUES(?,?,?)", (session_id, "user", user_message))
            db.execute("INSERT INTO messages(session_id, role, content) VALUES(?,?,?)", (session_id, "assistant", assistant_message))

def chat(store, session_id, message, provider=gemini_reply):
    if not isinstance(session_id, str) or not 1 <= len(session_id) <= 100 or not session_id.replace("-", "").replace("_", "").isalnum():
        raise ValueError("invalid_session_id")
    if not isinstance(message, str) or not 1 <= len(message.strip()) <= 12000:
        raise ValueError("invalid_message")
    history = store.history(session_id)
    answer = provider(history + [{"role": "user", "content": message}])
    if not isinstance(answer, str) or not answer.strip():
        raise ProviderError("empty_provider_response")
    store.append_turn(session_id, message, answer)
    return {"session_id": session_id, "reply": answer}
