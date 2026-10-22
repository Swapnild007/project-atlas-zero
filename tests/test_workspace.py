import unittest
import urllib.request
from tests.test_http import HTTPTests


class WorkspaceHTTPTests(HTTPTests):
    def test_workspace_served_at_root(self):
        with urllib.request.urlopen(self.base + "/", timeout=3) as response:
            html = response.read().decode("utf-8")
            self.assertEqual(response.status, 200)
            self.assertIn("text/html", response.headers["Content-Type"])
            self.assertIn("Atlas Zero", html)
            self.assertIn('id="form"', html)
            self.assertIn("Content-Security-Policy", response.headers)

    def test_workspace_does_not_require_api_token(self):
        self.handler.access_token = "temporary-test-token"
        try:
            with urllib.request.urlopen(self.base + "/", timeout=3) as response:
                self.assertEqual(response.status, 200)
        finally:
            self.handler.access_token = None


if __name__ == "__main__":
    unittest.main()
