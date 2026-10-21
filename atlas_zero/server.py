import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from .core import ConversationStore, ProviderError, chat

class Handler(BaseHTTPRequestHandler):
    store = None

    def send_json(self, status, data):
        body = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/health":
            return self.send_json(200, {"status": "ok", "service": "atlas-zero"})
        self.send_json(404, {"error": "not_found"})

    def do_POST(self):
        if self.path != "/chat":
            return self.send_json(404, {"error": "not_found"})
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= 16000:
                return self.send_json(413, {"error": "invalid_body_size"})
            if self.headers.get("Content-Type", "").split(";", 1)[0].strip().lower() != "application/json":
                return self.send_json(415, {"error": "unsupported_media_type"})
            payload = json.loads(self.rfile.read(length))
            if not isinstance(payload, dict):
                return self.send_json(400, {"error": "invalid_request"})
            result = chat(self.store, payload.get("session_id"), payload.get("message"))
            self.send_json(200, result)
        except (ValueError, AttributeError, TypeError, json.JSONDecodeError) as exc:
            self.send_json(400, {"error": "invalid_request", "detail": str(exc)})
        except ProviderError as exc:
            self.send_json(503, {"error": str(exc)})
        except Exception:
            self.send_json(500, {"error": "internal_error"})

def main():
    Handler.store = ConversationStore()
    port = int(os.getenv("PORT", "8080"))
    print(f"Atlas Zero listening on localhost:{port}", flush=True)
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()

if __name__ == "__main__":
    main()
