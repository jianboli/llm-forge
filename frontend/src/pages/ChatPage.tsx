// frontend/src/pages/ChatPage.tsx
import React, { useState, useEffect, useRef, useCallback } from 'react';
import axios from 'axios';
import './ChatPage.css'; // We'll create this CSS file

const API_BASE_URL = '/api'; // Using relative path for proxy

interface Model {
  id: string;
  name: string;
}

interface Message {
  sender: 'user' | 'bot';
  text: string;
  modelId?: string; // Track which model generated the bot message
}

function ChatPage() {
  const [models, setModels] = useState<Model[]>([]);
  const [selectedModel, setSelectedModel] = useState<string>('');
  const [message, setMessage] = useState<string>('');
  const [chatHistory, setChatHistory] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const chatContainerRef = useRef<HTMLDivElement>(null);

  // Fetch models on component mount
  useEffect(() => {
    axios.get<{ id: string; name: string }[]>(`${API_BASE_URL}/models`)
      .then(response => {
        setModels(response.data);
        // Select the first model by default if available
        if (response.data.length > 0) {
          setSelectedModel(response.data[0].id);
        }
      })
      .catch(err => {
        console.error("Error fetching models:", err);
        setError('Failed to load models. Is the backend running?');
      });
  }, []);

  // Scroll to bottom of chat history
  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [chatHistory]);

  const handleSendMessage = useCallback(async (event?: React.FormEvent) => {
    if (event) event.preventDefault(); // Prevent form submission reload if used in a form
    if (!message.trim() || !selectedModel || isLoading) return;

    const userMessage: Message = { sender: 'user', text: message };
    setChatHistory(prev => [...prev, userMessage]);
    setMessage(''); // Clear input field immediately
    setIsLoading(true);
    setError(null);

    try {
      const response = await axios.post<{ response: string; model_id: string }>(
        `${API_BASE_URL}/chat`,
        {
          model_id: selectedModel,
          message: userMessage.text // Send the message text
          // Could send history here later: history: chatHistory
        }
      );

      const botMessage: Message = {
          sender: 'bot',
          text: response.data.response,
          modelId: response.data.model_id
      };
      setChatHistory(prev => [...prev, botMessage]);

    } catch (err: any) {
      console.error("Error sending message:", err);
      const errorMsg = err.response?.data?.detail || err.message || 'Failed to get response from the bot.';
      setError(errorMsg);
      // Optionally add an error message to chat history
      setChatHistory(prev => [...prev, { sender: 'bot', text: `Error: ${errorMsg}`, modelId: selectedModel }]);
    } finally {
      setIsLoading(false);
    }
  }, [message, selectedModel, isLoading]); // Include dependencies

  const handleKeyDown = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'Enter' && !event.shiftKey) { // Send on Enter, allow Shift+Enter for newline
      handleSendMessage();
    }
  };


  return (
    <div className="chat-page-container">
      <h2>Chat Interface</h2>

      {error && <p className="error-message">Error: {error}</p>}

      <div className="model-selector">
        <label htmlFor="model-select">Select Model: </label>
        <select
          id="model-select"
          value={selectedModel}
          onChange={(e) => setSelectedModel(e.target.value)}
          disabled={models.length === 0 || isLoading}
        >
          {models.length === 0 && <option>Loading models...</option>}
          {models.map(model => (
            <option key={model.id} value={model.id}>
              {model.name}
            </option>
          ))}
        </select>
      </div>

      <div className="chat-history" ref={chatContainerRef}>
        {chatHistory.map((msg, index) => (
          <div key={index} className={`chat-message ${msg.sender}`}>
            <span className="sender-label">{msg.sender === 'user' ? 'You' : `Bot (${msg.modelId || selectedModel})`}: </span>
            <p>{msg.text}</p>
          </div>
        ))}
        {isLoading && <div className="chat-message bot loading"><span>Bot is thinking...</span></div>}
      </div>

      <div className="chat-input">
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown} // Add Enter key listener
          placeholder="Type your message..."
          disabled={isLoading || !selectedModel}
        />
        <button onClick={() => handleSendMessage()} disabled={isLoading || !selectedModel || !message.trim()}>
          Send
        </button>
      </div>
    </div>
  );
}

export default ChatPage;