import io
import json
import unittest
import urllib.error
from atlas_zero.core import ProviderError
from atlas_zero.providers import PROVIDERS, generate


class ProviderAdapterTests(unittest.TestCase):
    def test_all_provider_endpoints_are_https_and_allowlisted(self):
        self.assertEqual(set(PROVIDERS), {"openai", "groq", "openrouter", "mistral"})
        self.assertTrue(all(url.startswith("https://") for url, _ in PROVIDERS.values()))

    def test_each_adapter_sends_unicode_and_key_only_in_header(self):
        for provider in PROVIDERS:
            with self.subTest(provider=provider):
                def fake(req):
                    self.assertEqual(req.full_url, PROVIDERS[provider][0])
                    self.assertEqual(req.get_header("Authorization"), "Bearer private-test-key")
                    self.assertNotIn(b"private-test-key", req.data)
                    body = json.loads(req.data)
                    self.assertEqual(body["messages"][-1]["content"], "नमस्कार")
                    return {"choices": [{"message": {"content": "नमस्कार!"}}]}
                answer = generate([{"role": "user", "content": "नमस्कार"}], provider,
                                  api_key="private-test-key", transport=fake)
                self.assertEqual(answer, "नमस्कार!")

    def test_unknown_provider_rejected(self):
        with self.assertRaisesRegex(ProviderError, "unsupported_provider"):
            generate([{"role": "user", "content": "hi"}], "custom", api_key="test")

    def test_missing_key_rejected(self):
        with self.assertRaisesRegex(ProviderError, "provider_not_configured"):
            generate([{"role": "user", "content": "hi"}], "openai")

    def test_empty_response_rejected(self):
        with self.assertRaisesRegex(ProviderError, "invalid_response"):
            generate([{"role": "user", "content": "hi"}], "openai",
                     api_key="test", transport=lambda _: {"choices": []})

    def test_authentication_failure_redacted(self):
        def fake(req):
            raise urllib.error.HTTPError(req.full_url, 401, "secret leaked", {}, io.BytesIO())
        with self.assertRaisesRegex(ProviderError, "^authentication_failed$"):
            generate([{"role": "user", "content": "hi"}], "openai",
                     api_key="test", transport=fake)

    def test_rate_limit(self):
        def fake(req):
            raise urllib.error.HTTPError(req.full_url, 429, "slow", {}, io.BytesIO())
        with self.assertRaisesRegex(ProviderError, "rate_limited"):
            generate([{"role": "user", "content": "hi"}], "groq",
                     api_key="test", transport=fake)

    def test_invalid_model_rejected(self):
        with self.assertRaisesRegex(ProviderError, "invalid_model"):
            generate([{"role": "user", "content": "hi"}], "openai",
                     model="../?bad", api_key="test")


if __name__ == "__main__":
    unittest.main()
