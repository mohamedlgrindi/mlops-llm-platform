import asyncio
import os
from fastapi import FastAPI , Request
from fastapi.responses import StreamingResponse
from app.schemas import PromptRequest, HealthResponse
from contextlib import asynccontextmanager
from app.engine import MockLLMEngine, RemotevLLMEgine
from prometheus_fastapi_instrumentator import Instrumentator



@asynccontextmanager
async def lifespan(app:FastAPI):

    colab_url = os.getenv("COLAB_URL")

    if colab_url :
        print(f"Using Real GPU Remote Engine at: {colab_url}")
        app.state.engine = RemotevLLMEgine(colab_url)
    else:
        print("Using Local Mock Engine")
        app.state.engine = MockLLMEngine()
        
    yield
    app.state.engine = None


app = FastAPI(title="MLOps Autonomous LLM Serving Platform" ,lifespan = lifespan)

Instrumentator().instrument(app).expose(app)


@app.get("/health",response_model =HealthResponse)
async def heatlth_check():
    return {"status":"healthy" , "service":"llm-servicng-api"}



@app.post("/generate")
async def token_generator(payload :PromptRequest, request :Request):


    return StreamingResponse(request.app.state.engine.generate(payload.prompt,payload.max_tokens,payload.temperature)
                             ,media_type="text/event-stream")