import { useState } from "react";
import { sendMessage } from "../../services/api";

interface Message {
  role: "user" | "assistant";
  text: string;
}

export function Chat() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMsg = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", text: userMsg }]);
    setIsLoading(true);

    const reply = await sendMessage(userMsg);
    
    setMessages((prev) => [...prev, { role: "assistant", text: reply }]);
    setIsLoading(false);
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", width: "100%", maxWidth: "600px", margin: "0 auto" }}>
      
      {/* Chat History */}
      <div style={{ height: "400px", overflowY: "auto", border: "1px solid #333", padding: "1rem", marginBottom: "1rem", borderRadius: "8px", backgroundColor: "#1e1e1e" }}>
        {messages.length === 0 && (
          <p style={{ color: "#888", textAlign: "center", marginTop: "2rem" }}>Eternal Mind is ready. Say hello.</p>
        )}
        {messages.map((msg, i) => (
          <div key={i} style={{ marginBottom: "1rem", textAlign: msg.role === "user" ? "right" : "left" }}>
            <span style={{ 
              display: "inline-block", 
              padding: "0.5rem 1rem", 
              borderRadius: "12px",
              backgroundColor: msg.role === "user" ? "#007acc" : "#333",
              color: "#fff" 
            }}>
              {msg.text}
            </span>
          </div>
        ))}
        {isLoading && <p style={{ color: "#888" }}>Thinking...</p>}
      </div>

      {/* Input Area */}
      <div style={{ display: "flex", gap: "0.5rem" }}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          placeholder="Type a message..."
          style={{ flex: 1, padding: "0.75rem", borderRadius: "8px", border: "1px solid #333", backgroundColor: "#1e1e1e", color: "#fff" }}
        />
        <button 
          onClick={handleSend} 
          disabled={isLoading}
          style={{ padding: "0.75rem 1.5rem", borderRadius: "8px", backgroundColor: "#007acc", color: "#fff", border: "none", cursor: isLoading ? "not-allowed" : "pointer" }}
        >
          Send
        </button>
      </div>
    </div>
  );
}