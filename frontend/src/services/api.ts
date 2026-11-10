const API_BASE_URL = "http://127.0.0.1:8000/api";

export interface ChatResponse {
  response: string;
}

export async function sendMessage(message: string): Promise<string> {
  try {
    const res = await fetch(`${API_BASE_URL}/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ message }),
    });

    if (!res.ok) {
      throw new Error(`Backend error: ${res.status}`);
    }

    const data: ChatResponse = await res.json();
    return data.response;
  } catch (error) {
    console.error("Failed to send message:", error);
    return "Error: Could not connect to the Eternal Mind backend.";
  }
}