import json
import aiohttp
import asyncio
from typing import List, Dict, AsyncGenerator, Literal

STATUS_URL = "https://duckduckgo.com/duckchat/v1/status"
CHAT_URL = "https://duckduckgo.com/duckchat/v1/chat"
STATUS_HEADERS = {"x-vqd-accept": "1"}

ModelAlias = Literal["gpt-4o-mini", "claude-3-haiku", "llama", "mixtral"]
Role = Literal["user", "assistant"]

MODEL_MAP = {
    "gpt-4o-mini": "gpt-4o-mini",
    "claude-3-haiku": "claude-3-haiku-20240307",
    "llama": "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
    "mixtral": "mistralai/Mixtral-8x7B-Instruct-v0.1",
}


class Chat:
    def __init__(self, vqd: str, model: str):
        self.old_vqd = vqd
        self.new_vqd = vqd
        self.model = model
        self.messages: List[Dict[str, str]] = []

    async def fetch(self, content: str) -> aiohttp.ClientResponse:
        self.messages.append({"content": content, "role": "user"})
        payload = {
            "model": self.model,
            "messages": self.messages,
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(
                CHAT_URL,
                headers={"x-vqd-4": self.new_vqd, "Content-Type": "application/json"},
                json=payload,
            ) as response:
                if not response.ok:
                    raise Exception(
                        f"{response.status}: Failed to send message. {response.reason}"
                    )
                return response

    async def fetch_full(self, content: str) -> str:
        response = await self.fetch(content)
        text = ""
        async for line in response.content:
            data = json.loads(line.decode("utf-8").split("data: ")[1])
            if "message" not in data:
                break
            text += data["message"]

        self.old_vqd = self.new_vqd
        self.new_vqd = response.headers.get("x-vqd-4", "")
        self.messages.append({"content": text, "role": "assistant"})
        return text

    async def fetch_stream(self, content: str) -> AsyncGenerator[str, None]:
        response = await self.fetch(content)
        text = ""
        async for line in response.content:
            data = json.loads(line.decode("utf-8").split("data: ")[1])
            if "message" not in data:
                break
            chunk = data["message"]
            text += chunk
            yield chunk

        self.old_vqd = self.new_vqd
        self.new_vqd = response.headers.get("x-vqd-4", "")
        self.messages.append({"content": text, "role": "assistant"})

    def redo(self):
        self.new_vqd = self.old_vqd
        self.messages = self.messages[:-2]


async def init_chat(model: ModelAlias) -> Chat:
    async with aiohttp.ClientSession() as session:
        async with session.get(STATUS_URL, headers=STATUS_HEADERS) as response:
            vqd = response.headers.get("x-vqd-4")
            if not vqd:
                raise Exception(
                    f"{response.status}: Failed to initialize chat. {response.reason}"
                )
    return Chat(vqd, MODEL_MAP[model])
