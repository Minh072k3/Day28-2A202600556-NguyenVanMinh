# scripts/mock_kaggle_gpu.py
import hashlib
import threading
import time
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn

# --- 1. Helper function for 384-dimensional deterministic embedding ---
def get_deterministic_embedding(text: str) -> list[float]:
    embedding = []
    for i in range(12):
        chunk = hashlib.sha256(f"{text}:{i}".encode('utf-8')).digest()
        for byte in chunk:
            # Normalize to [-1.0, 1.0]
            val = (byte / 255.0) * 2.0 - 1.0
            embedding.append(val)
    # L2 normalization
    norm = sum(x * x for x in embedding) ** 0.5
    if norm > 0:
        embedding = [x / norm for x in embedding]
    return embedding

# --- 2. vLLM Mock Server (Port 8001) ---
vllm_app = FastAPI(title="vLLM Mock Server")

@vllm_app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    body = await request.json()
    messages = body.get("messages", [])
    model = body.get("model", "Qwen/Qwen2.5-7B-Instruct-GPTQ-Int4")
    
    user_query = ""
    if messages:
        user_query = messages[-1].get("content", "")
    
    print(f"[vLLM Mock] Received query: {user_query}")
    
    # Return mock completions response
    return {
        "id": "chatcmpl-mock-12345",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model,
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": f"Platform engineering is a discipline focused on designing and building toolchains and workflows that enable self-service capabilities for software engineering organizations. Here context is simulated. Your query was: '{user_query}'."
                },
                "finish_reason": "stop"
            }
        ]
    }

@vllm_app.get("/health")
def health():
    return {"status": "ok"}

# --- 3. Embedding Mock Server (Port 8002) ---
embed_app = FastAPI(title="Embedding Mock Server")

@embed_app.post("/embed")
async def embed(request: Request):
    body = await request.json()
    texts = body.get("texts", [])
    print(f"[Embedding Mock] Embedding {len(texts)} texts...")
    embeddings = [get_deterministic_embedding(t) for t in texts]
    return {"embeddings": embeddings}

# --- 4. Main runner ---
def run_vllm():
    uvicorn.run(vllm_app, host="0.0.0.0", port=8001, log_level="warning")

def run_embed():
    uvicorn.run(embed_app, host="0.0.0.0", port=8002, log_level="warning")

if __name__ == "__main__":
    t1 = threading.Thread(target=run_vllm, daemon=True)
    t2 = threading.Thread(target=run_embed, daemon=True)
    
    t1.start()
    t2.start()
    
    print("vLLM Mock Server started on port 8001")
    print("Embedding Mock Server started on port 8002")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping mock servers...")
