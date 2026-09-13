import asyncio
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from app.schemas import PromptRequest , HealthResponse



app = FastAPI(title= "MLOps Autonomous LLM Serving Platform")


@app.get("/health",response_model =HealthResponse)
async def heatlth_check():
    return {"status":"healthy" , "service":"llm-servicng-api"}



@app.post("/generate")
async def token_generator(payload :PromptRequest):

  
    async def token_stream():
        generated_text = f"Simulated LLM response generated for prompt: '{payload.prompt}'"
        tokens = generated_text.split(" ")
        
        for token in tokens:
            yield f"data: {token}\n\n"
            await asyncio.sleep(0.08)
        
        yield "data: [DONE]\n\n"

    return StreamingResponse(token_stream(),media_type="text/event-stream")