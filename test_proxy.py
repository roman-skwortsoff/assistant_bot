import httpx
import asyncio
import json

from config import OPENAI_API_KEY, PROXY_SERVER

headers = {
    "Authorization": f"Bearer {OPENAI_API_KEY}",
    "Content-Type": "application/json",
}

data = {
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "Hello! Who are you?"}],
}

async def ask_gpt_httpx():
    transport = httpx.AsyncHTTPTransport(proxy=PROXY_SERVER, verify=False)

    async with httpx.AsyncClient(transport=transport, timeout=60.0) as client:
        try:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data,
            )
            response.raise_for_status()
            result = response.json()
            print(result["choices"][0]["message"]["content"])
        except httpx.HTTPError as e:
            print("HTTP error:", e)
        except Exception as e:
            print("Other error:", e)

asyncio.run(ask_gpt_httpx())