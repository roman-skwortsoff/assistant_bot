import httpx
import asyncio
from config import OPENAI_API_KEY, PROXY_SERVER
import base64
from pathlib import Path


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

async def ask_gpt_with_image(image_path: str, prompt: str = "") -> str:
    transport = httpx.AsyncHTTPTransport(proxy=PROXY_SERVER, verify=False)

    async with httpx.AsyncClient(transport=transport, timeout=60.0) as client:
        # Считываем изображение и кодируем в base64
        image_data = Path(image_path).read_bytes()
        b64_image = base64.b64encode(image_data).decode("utf-8")

        # Создаём JSON-поддерживаемую мультимодальную структуру
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"}},
                    {"type": "text", "text": prompt or "Нужен ответ:"}
                ],
            }
        ]

        data = {
            "model": "gpt-4o",
            "messages": messages,
            "max_tokens": 1000,
        }

        try:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data,
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()

        except httpx.HTTPStatusError as e:
            return f"[HTTP Error] {e.response.status_code}: {e.response.text}"

        except Exception as e:
            return f"OpenAI Error: {e}"