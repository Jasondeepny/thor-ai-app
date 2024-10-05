import requests
import json  # 添加导入

url = "https://api.deepbricks.ai/v1/chat/completions"
body = {
    "model": "claude-3.5-sonnet",
    "messages": [
        {"role": "system", "content": f"You are an expert in golang for development."},
        {"role": "user", "content": """go routine demo"""},
    ],
    "stream": True,
}
# response = requests.post(
#     url,
#     headers={
#         "Authorization": "Bearer sk-dK4ZipmJeBRcTHBh7d1fE1BaEc0b4427B5A1Eb01F621C2Eb"
#     },
#     json=body,
#     stream=True,
# )

# full_response = ""
# for chunk in response.iter_lines():
#     if chunk:
#         decoded_chunk = chunk.decode('utf-8').strip()  # 解码并去除空白
#         if decoded_chunk.startswith("data: "):  # 检查是否以 "data: " 开头
#             json_data = decoded_chunk[6:]  # 去掉 "data: " 前缀
#             try:
#                 data = json.loads(json_data)  # 解析 JSON 数据
#                 # 检查 'choices' 和 'content' 是否存在
#                 if 'choices' in data and len(data['choices']) > 0:
#                     delta = data['choices'][0].get('delta', {})
#                     if 'content' in delta and delta['content'] is not None:
#                         full_response += delta['content']  # 提取 content
#             except json.JSONDecodeError:
#                 print("JSON 解码错误:", json_data)  # 打印错误信息
# print(full_response)


API_KEY = "sk-dK4ZipmJeBRcTHBh7d1fE1BaEc0b4427B5A1Eb01F621C2Eb"
BASE_URL = "https://api.deepbricks.ai/v1/chat/completions"

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

completion = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are a helpful python code assistant."},
        {"role": "user", "content": """Python 操作mysql """},
    ],
    stream=True,
)

full_response = ""
for chunk in completion:
    if chunk.choices[0].delta.content is not None:
        full_response += chunk.choices[0].delta.content

print(full_response)
