import json
import certifi
import ssl
from typing import List, Dict, AsyncGenerator, Literal
import asyncio
from aiohttp import ClientSession,ClientError, ClientTimeout

STATUS_URL = "https://pp.block.pp.ua/duckchat/v1/status";
CHAT_URL = "https://pp.block.pp.ua/duckchat/v1/chat";
# STATUS_URL = "https://duckduckgo.com/duckchat/v1/status"
# CHAT_URL = "https://duckduckgo.com/duckchat/v1/chat"
STATUS_HEADERS = {"x-vqd-accept": "1"}

ModelAlias = Literal["gpt-4o-mini", "claude-3-haiku", "llama", "mixtral"]
Role = Literal["user", "assistant"]
SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())


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

    async def fetch(self, content: str, max_retries=3) -> bytes:
        self.messages.append({"content": content, "role": "user"})
        payload = {
            "model": self.model,
            "messages": self.messages,
        }
        for attempt in range(max_retries):
            try:
                async with ClientSession(
                    timeout=ClientTimeout(total=60)
                ) as session:
                    async with session.post(
                        CHAT_URL,
                        json=payload,
                        headers={
                            "x-vqd-4": self.new_vqd,
                            "Content-Type": "application/json",
                        },
                        ssl=SSL_CONTEXT,
                    ) as response:
                        response.raise_for_status()
                        self.new_vqd = response.headers.get("x-vqd-4", "")
                        return await response.read()
            except (ClientError, asyncio.TimeoutError) as e:
                print(f"Attempt request {attempt + 1} failed: {str(e)}")
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(2**attempt)

    async def fetch_full(self, content: str) -> str:
        response_content = await self.fetch(content)
        text = ""
        for line in response_content.split(b"\n"):
            if line.startswith(b"data: ") and line != b"data: [DONE]":
                try:
                    data = json.loads(tuple(line.decode("utf-8").split("data: "))[1])
                    if "message" in data:
                        text += data["message"]
                except (IndexError, json.JSONDecodeError):
                    print(f"Error processing line: {line}")

        if not text:
            raise Exception("No response from server")
        self.old_vqd = self.new_vqd
        self.messages.append({"content": text, "role": "assistant"})
        return text

    async def fetch_stream(self, content: str) -> AsyncGenerator[str, None]:
        response_content = await self.fetch(content)
        text = ""
        for line in response_content.split(b"\n"):
            if line.startswith(b"data: ") and line != b"data: [DONE]":
                try:
                    data = json.loads(tuple(line.decode("utf-8").split("data: "))[1])
                    if "message" in data:
                        chunk=data["message"]
                        text += chunk
                        yield chunk
                except (IndexError, json.JSONDecodeError):
                    print(f"Error processing line: {line}")

        self.old_vqd = self.new_vqd
        self.messages.append({"content": text, "role": "assistant"})

    def redo(self):
        self.new_vqd = self.old_vqd
        self.messages = self.messages[:-2]


# 解析响应体，更精简的写法
# def safe_parse(line):
#     try:
#         return json.loads(line[6:].decode("utf-8"))
#     except (UnicodeDecodeError, json.JSONDecodeError):
#         return None
# data_list = list(
#     filter(
#         None,
#         (
#             safe_parse(line)
#             for line in response_content.split(b"\n")
#             if line.startswith(b"data: ") and line != b"data: [DONE]"
#         ),
#     )
# )

async def init_chat(model: ModelAlias) -> Chat:
    async with ClientSession() as session:
        async with await session.get(
            STATUS_URL, headers=STATUS_HEADERS, ssl=SSL_CONTEXT
        ) as response:
            vqd = response.headers.get("x-vqd-4")
            if not vqd:
                raise Exception(
                    f"{response.status}: Failed to initialize chat. {response.reason}"
                )
    return Chat(vqd, MODEL_MAP[model])
