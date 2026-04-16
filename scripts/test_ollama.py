import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import config
from services.llm_client import complete

try:
    print(f"Testing connection to {config.LLM_SERVER_URL}...")
    print(f"Model: {config.LLM_MODEL}")
    res = complete("Hello", max_tokens=50)
    print("Response:", res)
except Exception as e:
    print("Error type:", type(e))
    print("Error:", e)
