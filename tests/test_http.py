import json
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch

from atlas_zero.core import ConversationStore
from atlas_zero.server import Handler


class HTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tempdir = tempfile.TemporaryDirectory()
        cls.handler = type("TestHandler", (Handler,), {})
        cls.handler.store = ConversationStore(Path(cls.tempdir.name) / "http.sqlite")
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), cls.handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=3)
        cls.tempdir.cleanup()

    def request(self, path, data=None):
        headers = {"Content-Type": "application/json"}
        req = urllib.request.Request(self.base + path, data=data, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=3) as res:
                return res.status, json.load(res)
        except urllib.error.HTTPError as err:
            return err.code, json.load(err)

    def test_health(self):
        code, payload = self.request("/health")
        self.assertEqual(code, 200)
        self.assertEqual(payload["status"], "ok")

    def test_missing_endpoint(self):
        code, payload = self.request("/missing")
        self.assertEqual((code, payload["error"]), (404, "not_found"))

    def test_invalid_json(self):
        code, payload = self.request("/chat", b"{")
        self.assertEqual((code, payload["error"]), (400, "invalid_request"))

    def test_missing_api_key_returns_visible_error(self):
        with patch.dict("os.environ", {"GEMINI_API_KEY": ""}):
            code, payload = self.request("/chat", json.dumps({"session_id": "http-test", "message": "hello"}).encode())
        self.assertEqual((code, payload["error"]), (503, "provider_not_configured"))

    def test_rejects_oversized_body(self):
        code, payload = self.request("/chat", b"x" * 16001)
        self.assertEqual((code, payload["error"]), (413, "invalid_body_size"))


if __name__ == "__main__":
    unittest.main()
