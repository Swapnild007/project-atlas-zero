import json
import unittest
from unittest.mock import patch

from tests.test_http import HTTPTests


class ToolsHTTPTests(HTTPTests):
    def test_tool_catalog_endpoint(self):
        status, body = self.request("/tools")
        self.assertEqual(status, 200)
        self.assertEqual(body["tools"][0]["id"], "wikipedia_search")

    def test_tool_execution_endpoint(self):
        with patch("atlas_zero.server.run_tool", return_value={
            "tool": "wikipedia_search", "language": "mr",
            "source": "Wikipedia", "results": [{"title": "पुणे", "url": "https://mr.wikipedia.org/wiki/test"}]
        }) as mock_run:
            status, body = self.request("/tools/run", json.dumps({
                "tool": "wikipedia_search", "arguments": {"query": "पुणे", "language": "mr"}
            }).encode())
        self.assertEqual(status, 200)
        self.assertEqual(body["results"][0]["title"], "पुणे")
        mock_run.assert_called_once_with("wikipedia_search", {"query": "पुणे", "language": "mr"})

    def test_tool_rejects_unknown_id(self):
        status, body = self.request("/tools/run", json.dumps({
            "tool": "arbitrary_fetch", "arguments": {"url": "http://localhost"}
        }).encode())
        self.assertEqual(status, 400)
        self.assertEqual(body["error"], "invalid_request")


if __name__ == "__main__":
    unittest.main()
