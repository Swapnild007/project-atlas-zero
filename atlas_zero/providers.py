"""Provider-neutral adapters. Credentials are supplied per call and never stored."""
import json
import urllib.error
import urllib.request

from .core import ProviderError, SYSTEM_INSTRUCTION

PROVIDERS = {
    "openai": ("https://api.openai.com/v1/chat/completions", "gpt-4.1-mini"),
    "groq": ("https://api.groq.com/openai/v1/chat/completions", "llama-3.3-70b-versatile"),
    "openrouter": ("https://openrouter.ai/api/v1/chat/completions", "openai/gpt-4.1-mini"),
    "mistral": ("https://api.mistral.ai/v1/chat/completions", "mistral-small-latest"),
}


def generate(messages, provider, model=None, api_key=None, transport=None):
    """Send one turn through a fixed allowlisted provider endpoint."""
    if provider not in PROVIDERS:
        raise ProviderError("unsupported_provider")
    if not isinstance(api_key, str) or not api_key.strip():
        raise ProviderError("provider_not_configured")
    url, default_model = PROVIDERS[provider]
    model = model or default_model
    if not isinstance(model, str) or not 1 <= len(model) <= 120 or not all(
        c.isalnum() or c in "-._/:" for c in model
    ):
        raise ProviderError("invalid_model")
    if not isinstance(messages, list) or not messages or any(
        not isinstance(m, dict)
        or m.get("role") not in ("user", "assistant")
        or not isinstance(m.get("content"), str)
        for m in messages
    ):
        raise ProviderError("invalid_messages")
    payload = {
        "model": model,
        "messages": [{"role": "system", "content": SYSTEM_INSTRUCTION}] + messages,
    }
    request = urllib.request.Request(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": "Bearer " + api_key},
        method="POST",
    )
    try:
        if transport is None:
            with urllib.request.urlopen(request, timeout=35) as response:
                result = json.load(response)
        else:
            result = transport(request)
        choices = result.get("choices", []) if isinstance(result, dict) else []
        answer = choices[0].get("message", {}).get("content") if choices else None
        if not isinstance(answer, str) or not answer.strip():
            raise ProviderError("invalid_response")
        return answer
    except urllib.error.HTTPError as exc:
        if exc.code in (401, 403):
            raise ProviderError("authentication_failed") from None
        if exc.code == 429:
            raise ProviderError("rate_limited") from None
        raise ProviderError("provider_unavailable") from None
    except (urllib.error.URLError, TimeoutError):
        raise ProviderError("provider_unavailable") from None
    except (ValueError, TypeError, KeyError, IndexError, AttributeError):
        raise ProviderError("invalid_response") from None
