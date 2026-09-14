from pydantic import BaseModel , Field


class HealthResponse(BaseModel):
    """Schema for API health status check response."""
    status: str =Field(..., description = "Operational status of the API service")
    service: str =Field(..., description = "Unique name of the microservice")



class PromptRequest(BaseModel):
    """Schema for incoming LLM text generation requests."""
    
    prompt: str = Field(...,description="User prompt")
    max_token: int = Field(default=128 , ge= 1 , le = 1024)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)