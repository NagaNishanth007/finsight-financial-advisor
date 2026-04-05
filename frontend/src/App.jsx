import React, { useState, useEffect } from 'react';
import { AlertCircle, CheckCircle, XCircle } from 'lucide-react';
import { api } from './api';
import ChatInterface from './components/ChatInterface';

function App() {
  const [backendStatus, setBackendStatus] = useState('checking'); // checking, online, offline
  const [statusMessage, setStatusMessage] = useState('Checking backend connection...');

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const response = await api.health();
        if (response.status === 'healthy') {
          setBackendStatus('online');
          setStatusMessage('Backend connected');
        } else {
          setBackendStatus('offline');
          setStatusMessage('Backend unavailable');
        }
      } catch (err) {
        setBackendStatus('offline');
        setStatusMessage('Cannot connect to backend at localhost:8000');
      }
    };

    checkHealth();
    const interval = setInterval(checkHealth, 30000); // Check every 30s
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="h-screen w-screen bg-gray-100 flex flex-col overflow-hidden">
      {/* Status Bar */}
      <div className={`px-4 py-2 flex items-center justify-center gap-2 text-sm transition-colors ${
        backendStatus === 'online' 
          ? 'bg-green-50 text-green-700' 
          : backendStatus === 'offline'
          ? 'bg-red-50 text-red-700'
          : 'bg-yellow-50 text-yellow-700'
      }`}>
        {backendStatus === 'online' && <CheckCircle className="w-4 h-4" />}
        {backendStatus === 'offline' && <XCircle className="w-4 h-4" />}
        {backendStatus === 'checking' && <AlertCircle className="w-4 h-4" />}
        <span>{statusMessage}</span>
        {backendStatus === 'offline' && (
          <span className="text-xs opacity-75 ml-2">
            Run: uvicorn app.main:app --reload
          </span>
        )}
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-hidden">
        <ChatInterface />
      </div>
    </div>
  );
}

export default App;
