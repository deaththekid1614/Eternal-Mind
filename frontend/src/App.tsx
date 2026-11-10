import { Chat } from "./components/Chat/Chat";

function App() {
  return (
    <div style={{ minHeight: "100vh", backgroundColor: "#121212", color: "#fff", padding: "2rem", fontFamily: "sans-serif" }}>
      <header style={{ textAlign: "center", marginBottom: "2rem" }}>
        <h1>Eternal Mind</h1>
        <p style={{ color: "#888" }}>Local LLM Prototype (Stage 1)</p>
      </header>
      <main>
        <Chat />
      </main>
    </div>
  );
}

export default App;