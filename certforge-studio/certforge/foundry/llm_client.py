"""Optional Azure OpenAI (Foundry Models) chat client. Behind USE_FOUNDRY_LLM.

``complete`` returns model text, or ``None`` on any failure / when disabled, so
every caller degrades gracefully to deterministic output. The ``openai`` and
``azure-identity`` packages are imported lazily.
"""
from __future__ import annotations

from certforge import config


def llm_available() -> bool:
    """True only when the LLM flag is on and an endpoint is configured."""
    return bool(config.use_foundry_llm() and config.openai_endpoint())


def complete(system: str, user: str, max_tokens: int = 400, temperature: float = 0.3) -> str | None:
    """Return a chat completion string, or ``None`` on any failure / when disabled."""
    if not llm_available():
        return None
    try:
        from openai import AzureOpenAI

        api_key = config.openai_api_key()
        if api_key:
            client = AzureOpenAI(
                azure_endpoint=config.openai_endpoint(),
                api_key=api_key,
                api_version=config.openai_api_version(),
            )
        else:
            # Keyless: Microsoft Entra / managed identity via a bearer token provider.
            from azure.identity import DefaultAzureCredential, get_bearer_token_provider

            token_provider = get_bearer_token_provider(
                DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
            )
            client = AzureOpenAI(
                azure_endpoint=config.openai_endpoint(),
                azure_ad_token_provider=token_provider,
                api_version=config.openai_api_version(),
            )

        resp = client.chat.completions.create(
            model=config.openai_deployment(),
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        text = resp.choices[0].message.content
        return text.strip() if text else None
    except Exception:
        # Fail safe: any API/network/auth error degrades to deterministic output.
        return None
