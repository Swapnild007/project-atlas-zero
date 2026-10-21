import tempfile
import unittest
from pathlib import Path
from atlas_zero.core import ConversationStore, ProviderError, chat, gemini_reply

class CoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.store = ConversationStore(Path(self.tmp.name) / "test.sqlite")

    def tearDown(self):
        self.tmp.cleanup()

    def test_roundtrip(self):
        result = chat(self.store, "demo", "नमस्कार", lambda messages: "नमस्कार!")
        self.assertEqual(result["reply"], "नमस्कार!")
        self.assertEqual(len(self.store.history("demo")), 2)

    def test_context(self):
        chat(self.store, "demo", "first", lambda messages: "one")
        chat(self.store, "demo", "second", lambda messages: str(len(messages)))
        self.assertEqual(self.store.history("demo")[-1]["content"], "3")

    def test_provider_failure_does_not_save_user_message(self):
        def failing(_):
            raise ProviderError("offline")
        with self.assertRaises(ProviderError):
            chat(self.store, "demo", "hello", failing)
        self.assertEqual(self.store.history("demo"), [])

    def test_missing_key(self):
        with self.assertRaisesRegex(ProviderError, "provider_not_configured"):
            gemini_reply([{"role": "user", "content": "hello"}], api_key="")

    def test_invalid_message(self):
        with self.assertRaises(ValueError):
            chat(self.store, "demo", " ", lambda _: "reply")

    def test_invalid_session(self):
        with self.assertRaises(ValueError):
            chat(self.store, "../bad", "hello", lambda _: "reply")

if __name__ == "__main__":
    unittest.main()
