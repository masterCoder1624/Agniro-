# app/core/llm_client.py
import os
try:
    import openai
except Exception:
    openai = None
             
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def call_openmining_chat(system_prompt: str, user_prompt: str, max_tokens: int = 256):
    if not OPENAI_API_KEY or openai is None:
        # graceful fallback for dev/demo
        return {"content": f"(LLM disabled) {user_prompt}"}
    openai.api_key = OPENAI_API_KEY
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    resp = openai.ChatCompletion.create(model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"), messages=messages, max_tokens=max_tokens)
    text = resp["choices"][0]["message"]["content"]
    return {"content": text, "raw": resp}
