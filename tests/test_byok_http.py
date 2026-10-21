import json
import unittest
from unittest.mock import patch

from tests.test_http import HTTPTests


class BYOKHTTPTests(HTTPTests):
    def test_provider_catalog(self):
        code, body = self.request("/providers")
        self.assertEqual(code, 200)
        self.assertEqual({p["id"] for p in body["providers"]},
                         {"gemini", "openai", "groq", "openrouter", "mistral"})

    def test_byok_request_routes_without_persisting_key(self):
        with patch("atlas_zero.server.generate", return_value="Hello from model") as provider:
            code, body = self.request("/chat", json.dumps({
                "session_id": "byok-http",
                "message": "Hello",
                "provider": "openai",
                "model": "gpt-4.1-mini",
                "api_key": "fake-key-only",
            }).encode())
        self.assertEqual(code, 200)
        self.assertEqual(body["reply"], "Hello from model")
        self.assertEqual(provider.call_args.kwargs["api_key"], "fake-key-only")
        history = self.handler.store.history("byok-http")
        self.assertEqual([m["content"] for m in history], ["Hello", "Hello from model"])
        self.assertNotIn("fake-key-only", json.dumps(history))


if __name__ == "__main__":
    unittest.main()
