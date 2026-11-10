from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.intelligence.llm_service import generate_response

router = APIRouter()

# Define the shape of the data the frontend will send
class ChatRequest(BaseModel):
    message: str

# Define the shape of the data we will return
class ChatResponse(BaseModel):
    response: str

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Receives a message, sends it to the LLM, and returns the response.
    """
    try:
        reply = await generate_response(request.message)
        return ChatResponse(response=reply)
    except Exception as e:
        # If Ollama is offline or crashes, we return a clean error
        raise HTTPException(status_code=500, detail=f"LLM Error: {str(e)}")