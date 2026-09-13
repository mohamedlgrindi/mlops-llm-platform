import asyncio
from fastapi import FastAPI , Request
from fastapi.responses import StreamingResponse
from app.schemas import PromptRequest, HealthResponse
from contextlib import asynccontextmanager
from app.engine import MockLLMEngine


@asynccontextmanager
async def lifespan(app:FastAPI):

    app.state.engine = MockLLMEngine()

    yield
    print("Shutting down engine...")

    app.state.engine = None

app = FastAPI(title="MLOps Autonomous LLM Serving Platform" ,lifespan = lifespan)


@app.get("/health",response_model =HealthResponse)
async def heatlth_check():
    return {"status":"healthy" , "service":"llm-servicng-api"}



@app.post("/generate")
async def token_generator(payload :PromptRequest, request :Request):


    return StreamingResponse(request.app.state.engine.generate(payload.prompt,payload.max_tokens,payload.temperature)
                             ,media_type="text/event-stream")