import io
import json
import unittest
import urllib.error
from atlas_zero.core import ProviderError, gemini_reply


class ProviderTests(unittest.TestCase):
    def test_gemini_request_contract_and_unicode(self):
        def transport(req):
            self.assertEqual(req.get_method(), "POST")
            self.assertEqual(req.get_header("X-goog-api-key"), "test-key")
            body = json.loads(req.data)
            self.assertEqual(body["contents"][0]["parts"][0]["text"], "नमस्कार")
            self.assertEqual(body["contents"][1]["role"], "model")
            self.assertEqual(body["contents"][1]["parts"][0]["text"], "Hello")
            return {"candidates": [{"content": {"parts": [{"text": "नमस्कार!"}]}}]}
        reply = gemini_reply([
            {"role": "user", "content": "नमस्कार"},
            {"role": "assistant", "content": "Hello"},
        ], api_key="test-key", transport=transport)
        self.assertEqual(reply, "नमस्कार!")

    def test_gemini_empty_candidates(self):
        with self.assertRaisesRegex(ProviderError, "empty_provider_response"):
            gemini_reply([{"role": "user", "content": "Hi"}], api_key="test-key", transport=lambda req: {"candidates": []})

    def test_gemini_rate_limit(self):
        def transport(req):
            raise urllib.error.HTTPError(req.full_url, 429, "rate limit", {}, io.BytesIO(b"{}"))
        with self.assertRaisesRegex(ProviderError, "provider_rate_limited"):
            gemini_reply([{"role": "user", "content": "Hi"}], api_key="test-key", transport=transport)

    def test_invalid_model(self):
        with self.assertRaisesRegex(ProviderError, "invalid_model"):
            gemini_reply([{"role": "user", "content": "Hi"}], api_key="test-key", model="../bad")


if __name__ == "__main__":
    unittest.main()
