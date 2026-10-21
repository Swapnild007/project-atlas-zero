import unittest
from atlas_zero.core import ProviderError
from atlas_zero.tools_registry import available_tools, run_tool, wikipedia_search


class PublicToolsTests(unittest.TestCase):
    def test_catalog(self):
        self.assertEqual(available_tools()[0]["id"], "wikipedia_search")

    def test_multilingual_search_and_source(self):
        for lang in ("en", "hi", "mr"):
            with self.subTest(lang=lang):
                def fake(req):
                    self.assertEqual(req.full_url.split("/")[2], lang + ".wikipedia.org")
                    self.assertEqual(req.get_method(), "GET")
                    self.assertNotIn("Authorization", dict(req.header_items()))
                    return {"pages": [{"title": "छत्रपती शिवाजी महाराज", "description": "इतिहास"}]}
                data = wikipedia_search("शिवाजी", language=lang, transport=fake)
                self.assertEqual(data["source"], "Wikipedia")
                self.assertEqual(data["results"][0]["description"], "इतिहास")
                self.assertTrue(data["results"][0]["url"].startswith("https://" + lang + ".wikipedia.org/wiki/"))

    def test_query_validation(self):
        for bad in ("", " ", 42, "x" * 201):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    wikipedia_search(bad, transport=lambda req: {})

    def test_language_allowlist(self):
        with self.assertRaisesRegex(ValueError, "unsupported_language"):
            wikipedia_search("Earth", language="evil.example", transport=lambda req: {})

    def test_reject_unregistered_tool(self):
        with self.assertRaisesRegex(ValueError, "unsupported_tool"):
            run_tool("fetch_url", {"url": "http://localhost/"})

    def test_reject_extra_parameters(self):
        with self.assertRaisesRegex(ValueError, "invalid_arguments"):
            run_tool("wikipedia_search", {"query": "Earth", "api_key": "private"})

    def test_invalid_upstream_response(self):
        with self.assertRaisesRegex(ProviderError, "tool_invalid_response"):
            wikipedia_search("Earth", transport=lambda req: {"not_pages": []})

    def test_empty_results(self):
        result = run_tool("wikipedia_search", {"query": "Earth"}, transport=lambda req: {"pages": []})
        self.assertEqual(result["results"], [])


if __name__ == "__main__":
    unittest.main()
