"""Opt-in live Gemini smoke test. Never prints the API key."""
import os
import sys

from atlas_zero.core import ProviderError, gemini_reply


def main():
    if not os.getenv("GEMINI_API_KEY"):
        print("SKIP: GEMINI_API_KEY is not configured.")
        return 2
    try:
        reply = gemini_reply([{"role": "user", "content": "Reply with exactly: ATLAS_OK"}])
    except ProviderError as exc:
        print(f"FAIL: {exc}")
        return 1
    if "ATLAS_OK" not in reply:
        print("FAIL: Provider replied, but the expected marker was missing.")
        return 1
    print("PASS: Live Gemini provider returned the expected marker.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
