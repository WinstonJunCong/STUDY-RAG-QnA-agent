from openai import OpenAI
import config

_client = None

def get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(
            api_key=config.LLM_API_KEY or "dummy",
            base_url=config.LLM_SERVER_URL,
        )
    return _client

def complete(prompt: str, max_tokens: int = 2000, timeout: float = 120.0) -> str:
    client = get_client()
    response = client.chat.completions.create(
        model=config.LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        timeout=timeout,
    )
    msg = response.choices[0].message
    return msg.content or msg.reasoning_content or ""
