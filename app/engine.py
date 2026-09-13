import asyncio 
import uuid 
from app.schemas import PromptRequest


class MockLLMEngine:
    async def generate(self, prompt:str , max_tokens: int , temperature:float):
        id = str(uuid.uuid4()) 

        dummy_sentence = "Testing llm engine"

        for word in dummy_sentence.split():

            yield f"data: {word}\n\n"
            await asyncio.sleep(0.08)

        yield "data: [DONE]\n\n"