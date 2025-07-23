import httpx
import asyncio
from config import OPENAI_API_KEY, PROXY_SERVER


headers = {
    "Authorization": f"Bearer {OPENAI_API_KEY}",
    "Content-Type": "application/json",
}


async def ask_gpt(prompt: str) -> str:
    transport = httpx.AsyncHTTPTransport(proxy=PROXY_SERVER, verify=False)

    async with httpx.AsyncClient(transport=transport, timeout=60.0) as client:
        data_gpt4 = {
            "model": "gpt-4o",
            "messages": [{"role": "user", "content": prompt}],
        }

        try:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data_gpt4,
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                # Переход на GPT-3.5 при лимите
                data_gpt35 = {
                    "model": "gpt-3.5-turbo",
                    "messages": [{"role": "user", "content": prompt}],
                }
                try:
                    response = await client.post(
                        "https://api.openai.com/v1/chat/completions",
                        headers=headers,
                        json=data_gpt35,
                    )
                    response.raise_for_status()
                    result = response.json()
                    return "[GPT-3.5] " + result["choices"][0]["message"]["content"].strip()
                except Exception as e2:
                    return f"[GPT-3.5 Error] {e2}"
            else:
                return f"[HTTP Error] {e.response.status_code}: {e.response.text}"

        except Exception as e:
            return f"OpenAI Error: {e}"
