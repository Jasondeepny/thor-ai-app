from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import asyncio
import requests
import json
import os
from models.ask_request import AskRequest   
from typing import AsyncGenerator
from init_db import init_db,select_models,select_roles,select_model, select_role
from models.config import Config

load_dotenv()

init_db()

app = FastAPI(title="Thor AI API", description="This is Thor AI API", version="1.0.0")

app.mount("/static", StaticFiles(directory="static"), name="static")

# API_KEY = "sk-Z1KpscdYPoXUaEttvLqjUguJAIW8CRFCCNoL7tiuKfC3fFng"
API_KEY = os.getenv("OPENAI_API_KEY")

@app.get("/")
async def read_root():
    return FileResponse("static/home.html")

@app.get("/api/models")
async def get_models():
   return select_models()

@app.get("/api/roles")
async def get_roles():
     return select_roles()

@app.post("/api/ask")
async def ask(request: AskRequest):
    role = select_role(request.role.strip())
    model = select_model(request.model.strip())
    
    if role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    if model is None:
        raise HTTPException(status_code=404, detail="Model not found")

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model[0].lower(),
        "messages": [
            {"role": "system", "content": f"You are an expert in {role[0]} for development."},
            {"role": "user", "content": request.question},
        ],
        "stream": Config.STREAM,
    }
    
    response = requests.post(Config.BASE_URL, headers=headers, json=data)
    if response.status_code != 200:
        print(f'Error: response status code {response.status_code}')
        print(f'Response content: {response.text}')
        raise HTTPException(status_code=response.status_code, detail=f"Error from upstream server: {response.text}")

    return StreamingResponse(process_response(response), media_type="text/event-stream")

async def process_response(response) -> AsyncGenerator[str, None]:
    async for line in response.iter_lines():
        if line:
            decoded_line = line.decode("utf-8")
            if decoded_line.startswith("data: "):
                json_data = decoded_line[6:]
                if json_data == "[DONE]":
                    yield "data: [DONE]\n\n"
                    break
                try:
                    data = json.loads(json_data)
                    yield f"data: {json.dumps(data)}\n\n"
                except json.JSONDecodeError:
                    print(f"Error decoding JSON: {json_data}")
        await asyncio.sleep(0.01)

# @app.get("/chat.html")
# async def chat():
#     return FileResponse("static/chat.html")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
