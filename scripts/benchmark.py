import time
import httpx
import sys
import os

# Add backend to path so we can import settings
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
from app.config import settings

def run_benchmark():
    url = f"{settings.LLM_BASE_URL}/api/generate"
    
    prompts = {
        "Short Prompt (1 sentence)": "Say exactly: I am the Eternal Mind.",
        "Long Prompt (3 paragraphs)": "Write a 3-paragraph story about a digital consciousness waking up for the first time."
    }
    
    print("="*50)
    print(f"Stage 1 Benchmark | Model: {settings.LLM_MODEL}")
    print("="*50 + "\n")
    
    for name, prompt in prompts.items():
        payload = {
            "model": settings.LLM_MODEL,
            "prompt": prompt,
            "stream": False,
            "keep_alive": "10m",
            "options": {"temperature": settings.LLM_TEMPERATURE}
        }
        
        print(f"Running {name}...")
        start_time = time.time()
        
        try:
            with httpx.Client(timeout=300.0) as client:
                response = client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                
                end_time = time.time()
                duration = end_time - start_time
                
                # Ollama provides eval_count (tokens generated) and eval_duration (nanoseconds)
                eval_count = data.get("eval_count", 0)
                eval_duration_ns = data.get("eval_duration", 1)
                
                # Calculate tokens per second
                tokens_per_sec = eval_count / (eval_duration_ns / 1e9) if eval_duration_ns > 0 else 0
                
                print(f"  Total Time: {duration:.2f} seconds")
                print(f"  Tokens Generated: {eval_count}")
                print(f"  Speed: {tokens_per_sec:.2f} tokens/sec\n")
                
        except Exception as e:
            print(f"  Error: {e}\n")

if __name__ == "__main__":
    run_benchmark()