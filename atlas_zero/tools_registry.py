"""Curated public-data tools. No arbitrary URL fetching or secret forwarding."""
import json
import urllib.error
import urllib.parse
import urllib.request

from .core import ProviderError

LANGUAGES = frozenset({"en", "hi", "mr"})
MAX_RESPONSE_BYTES = 128 * 1024
USER_AGENT = "AtlasZero/0.1 (public-data research client; https://github.com/Swapnild007/project-atlas-zero)"


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def available_tools():
    return [{"id": "wikipedia_search", "description": "Search Wikipedia articles",
             "languages": sorted(LANGUAGES), "requires_key": False}]


def wikipedia_search(query, language="en", limit=5, transport=None):
    if not isinstance(query, str) or not 1 <= len(query.strip()) <= 200:
        raise ValueError("invalid_query")
    if language not in LANGUAGES:
        raise ValueError("unsupported_language")
    if type(limit) is not int or not 1 <= limit <= 10:
        raise ValueError("invalid_limit")

    params = urllib.parse.urlencode({"q": query.strip(), "limit": limit})
    url = f"https://{language}.wikipedia.org/w/rest.php/v1/search/page?{params}"
    req = urllib.request.Request(
        url, headers={"Accept": "application/json", "User-Agent": USER_AGENT},
        method="GET"
    )
    try:
        if transport is None:
            with urllib.request.build_opener(NoRedirect).open(req, timeout=10) as response:
                raw = response.read(MAX_RESPONSE_BYTES + 1)
                if len(raw) > MAX_RESPONSE_BYTES:
                    raise ProviderError("tool_response_too_large")
                payload = json.loads(raw)
        else:
            payload = transport(req)
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
        raise ProviderError("tool_unavailable") from None
    except (ValueError, UnicodeDecodeError, TypeError):
        raise ProviderError("tool_invalid_response") from None

    if not isinstance(payload, dict) or not isinstance(payload.get("pages"), list):
        raise ProviderError("tool_invalid_response")
    results = []
    for page in payload["pages"][:limit]:
        if not isinstance(page, dict):
            continue
        title = page.get("title")
        if not isinstance(title, str) or not title:
            continue
        results.append({
            "title": title[:250],
            "description": (page.get("description") or "")[:500]
                if isinstance(page.get("description"), (str, type(None))) else "",
            "url": f"https://{language}.wikipedia.org/wiki/{urllib.parse.quote(title.replace(' ', '_'), safe='')}",
        })
    return {"tool": "wikipedia_search", "language": language,
            "source": "Wikipedia", "results": results}


def run_tool(tool_id, arguments, transport=None):
    if tool_id != "wikipedia_search":
        raise ValueError("unsupported_tool")
    if not isinstance(arguments, dict):
        raise ValueError("invalid_arguments")
    if set(arguments) - {"query", "language", "limit"}:
        raise ValueError("invalid_arguments")
    return wikipedia_search(arguments.get("query"), arguments.get("language", "en"),
                            arguments.get("limit", 5), transport=transport)
