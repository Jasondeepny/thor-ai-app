from duck_ai import init_chat, Chat, ModelAlias
import asyncio

async def ai():
   chat = await init_chat('gpt-4o-mini')
   print(f"模型: {chat.model}")
   print(f"旧 VQD: {chat.old_vqd}")
   print(f"新 VQD: {chat.new_vqd}")

   result = await chat.fetch_full(
      "能帮我写一个 go 的异步请求代码吗？"
   )
   print(result)

   # chunks = []
   # async for chunk in chat.fetch_stream('Test message'):
   #    chunks.append(chunk)
   # print(chunks)


if __name__ == '__main__':
    asyncio.run(ai())
