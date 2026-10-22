import json
import unittest
import urllib.error
import urllib.request
from unittest.mock import patch

from tests.test_http import HTTPTests


class BrowserSecurityTests(HTTPTests):
    def test_same_origin_browser_post_allowed(self):
        with patch("atlas_zero.server.chat", return_value={"session_id": "browser", "reply": "ok"}):
            req = urllib.request.Request(
                self.base + "/chat",
                data=json.dumps({"session_id": "browser", "message": "hello"}).encode(),
                headers={"Content-Type": "application/json", "Origin": self.base},
            )
            with urllib.request.urlopen(req, timeout=3) as response:
                self.assertEqual(response.status, 200)

    def test_dns_rebinding_host_rejected(self):
        req = urllib.request.Request(
            self.base + "/providers",
            headers={"Host": "attacker.example"},
        )
        with self.assertRaises(urllib.error.HTTPError) as err:
            urllib.request.urlopen(req, timeout=3)
        self.assertEqual(err.exception.code, 403)

    def test_foreign_origin_tools_rejected(self):
        req = urllib.request.Request(
            self.base + "/tools/run",
            data=json.dumps({"tool": "wikipedia_search", "arguments": {"query": "India"}}).encode(),
            headers={"Content-Type": "application/json", "Origin": "https://attacker.example"},
        )
        with self.assertRaises(urllib.error.HTTPError) as err:
            urllib.request.urlopen(req, timeout=3)
        self.assertEqual(err.exception.code, 403)


if __name__ == "__main__":
    unittest.main()
