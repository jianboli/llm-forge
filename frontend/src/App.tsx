// src/App.tsx
import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import axios from 'axios';
import './App.css'; // Basic styling
import ChatPage from './pages/ChatPage';
import ModelEvalPage from './pages/ModelPage'; // Assuming this is a separate page for model evaluation

// Define API base URL (adjust if needed, esp. for production)
// When running via docker-compose, frontend requests to /api/ should be proxied by Nginx to the backend service
const API_BASE_URL = '/api'; // Use relative path for proxying

function HomePage() {
  const [status, setStatus] = useState<string>('Checking backend status...');

  useEffect(() => {
    axios.get(`${API_BASE_URL}/status`)
      .then(response => {
        setStatus(response.data.status || 'Backend responded, but no status message.');
      })
      .catch(error => {
        console.error("Error fetching backend status:", error);
        setStatus('Failed to connect to backend.');
      });
  }, []);

  return (
    <div>
      <h2>Welcome to LLM-Forge</h2>
      <p>This is the main dashboard area (Under Construction).</p>
      <p><strong>Backend Connection Status:</strong> {status}</p>
    </div>
  );
}

function FineTunePage() { return <h2>Fine-Tuning (Under Construction)</h2>; }
function RagPage() { return <h2>RAG Workflows (Under Construction)</h2>; }
function AgentsPage() { return <h2>Agentic Workflows (Under Construction)</h2>; }

function App() {
  return (
    <Router>
      <div className="app-container">
        <nav className="sidebar">
          <h1>LLM-Forge</h1>
          <ul>
            <li><Link to="/">Dashboard</Link></li>
            <li><Link to="/chat">Chat</Link></li>
            <li><Link to="/models">Models</Link></li>
            <li><Link to="/finetune">Fine-Tune</Link></li>
            <li><Link to="/rag">RAG</Link></li>
            <li><Link to="/agents">Agents</Link></li>
          </ul>
        </nav>
        <main className="content">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/chat" element={<ChatPage />} />
            <Route path="/models" element={<ModelEvalPage />} />
            <Route path="/finetune" element={<FineTunePage />} />
            <Route path="/rag" element={<RagPage />} />
            <Route path="/agents" element={<AgentsPage />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
