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

def complete(prompt: str, max_tokens: int = 128000, timeout: float = 120.0) -> str:
    client = get_client()
    response = client.chat.completions.create(
        model=config.LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        timeout=timeout,
        extra_body={
        "thinking": False
    }
    )
    finish_reason = response.choices[0].finish_reason
    msg = response.choices[0].message
    return response #msg.content if finish_reason == "stop" else "exploded response, {reason: " + finish_reason + "}"
