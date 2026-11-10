import httpx
from app.config import settings

async def generate_response(prompt: str) -> str:
    """
    Sends a prompt to the local Ollama instance and returns the generated text.
    """
    url = f"{settings.LLM_BASE_URL}/api/generate"
    
    payload = {
        "model": settings.LLM_MODEL,
        "prompt": prompt,
        "stream": False,
        "keep_alive": "10m", # Keeps model in RAM for 10 mins so it doesn't reload
        "options": {
            "temperature": settings.LLM_TEMPERATURE,
            "num_ctx": settings.LLM_CONTEXT_LENGTH
        }
    }
    
    # Increased timeout to 5 minutes (300s) for cold starts on HDD
    async with httpx.AsyncClient(timeout=300.0) as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        
        data = response.json()
        return data.get("response", "").strip()