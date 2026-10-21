import json
import unittest
import urllib.error
import urllib.request

from tests.test_http import HTTPTests


class AccessTokenHTTPTests(HTTPTests):
    def test_token_blocks_untrusted_requests(self):
        previous = self.handler.access_token
        self.handler.access_token = "private-test-token"
        try:
            code, body = self.request("/providers")
            self.assertEqual((code, body["error"]), (401, "unauthorized"))
            code, body = self.request("/chat", json.dumps({
                "session_id": "token-test", "message": "hi"
            }).encode())
            self.assertEqual((code, body["error"]), (401, "unauthorized"))
            req = urllib.request.Request(self.base + "/providers", headers={
                "Authorization": "Bearer private-test-token"
            })
            with urllib.request.urlopen(req, timeout=3) as response:
                self.assertEqual(response.status, 200)
        finally:
            self.handler.access_token = previous


if __name__ == "__main__":
    unittest.main()
