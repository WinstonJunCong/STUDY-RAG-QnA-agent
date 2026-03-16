import config
from llama_index.llms.ollama import Ollama

try:
    llm = Ollama(
        model="phi3:mini",
        base_url=config.OLLAMA_BASE_URL,
        request_timeout=120.0,
        context_window=2048,
        num_output=256,
    )
    print("Testing connection to Ollama...")
    res = llm.complete("Hello")
    print("Response:", res)
except Exception as e:
    print("Error type:", type(e))
    print("Error:", e)
