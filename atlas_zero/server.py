import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from .core import ConversationStore, ProviderError, chat
from .providers import PROVIDERS, generate
from .tools_registry import available_tools, run_tool

class Handler(BaseHTTPRequestHandler):
    store = None

    def send_json(self, status, data):
        body = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/tools":
            return self.send_json(200, {"tools": available_tools()})
        if self.path == "/providers":
            return self.send_json(200, {"providers": [{"id": p, "default_model": m} for p, (_, m) in PROVIDERS.items()] + [{"id": "gemini", "default_model": "gemini-2.5-flash"}]})
        if self.path == "/health":
            return self.send_json(200, {"status": "ok", "service": "atlas-zero"})
        self.send_json(404, {"error": "not_found"})

    def do_POST(self):
        if self.path not in ("/chat", "/tools/run"):
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
            if self.headers.get("Origin"):
                return self.send_json(403, {"error": "cross_origin_forbidden"})
            if self.path == "/tools/run":
                return self.send_json(200, run_tool(payload.get("tool"), payload.get("arguments")))
            provider_name = payload.get("provider", "gemini")
            if not isinstance(provider_name, str):
                return self.send_json(400, {"error": "invalid_provider"})
            if provider_name == "gemini":
                if "api_key" in payload:
                    from .core import gemini_reply
                    result = chat(self.store, payload.get("session_id"), payload.get("message"),
                                  provider=lambda messages: gemini_reply(messages, api_key=payload["api_key"], model=payload.get("model")))
                else:
                    result = chat(self.store, payload.get("session_id"), payload.get("message"))
            else:
                result = chat(self.store, payload.get("session_id"), payload.get("message"),
                              provider=lambda messages: generate(messages, provider_name,
                                                               model=payload.get("model"), api_key=payload.get("api_key")))
            self.send_json(200, result)
        except (ValueError, AttributeError, TypeError, json.JSONDecodeError):
            self.send_json(400, {"error": "invalid_request"})
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
