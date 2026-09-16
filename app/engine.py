import asyncio 
import uuid 
import httpx


class RemotevLLMEgine:
    def __init__(self, colab_url :str):
        self.colab_url = colab_url


    async def generate(self, prompt: str , max_tokens: int , temperatur: float):

        payload = {"prompt":prompt,
                   "max_tokens":max_tokens,
                    "temperature":temperatur
                   }

        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream("POST",self.colab_url, json=payload) as response:
                async for line in response.aiter_lines():
                    if line:
                        yield f"{line}\n\n"


class MockLLMEngine:
    async def generate(self, prompt:str , max_tokens: int , temperature:float):
        id = str(uuid.uuid4()) 

        dummy_sentence = "Testing llm engine"

        for word in dummy_sentence.split():

            yield f"data: {word}\n\n"
            await asyncio.sleep(0.08)

        yield "data: [DONE]\n\n"