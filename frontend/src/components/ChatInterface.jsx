import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader2, Sparkles, Brain, Heart, Target, BookOpen } from 'lucide-react';
import { api } from '../api';
import { emotionColors, emotionLabels, intentLabels, formatTimestamp } from '../utils';

const ChatInput = ({ onSend, isLoading }) => {
  const [input, setInput] = useState('');
  const textareaRef = useRef(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim() && !isLoading) {
      onSend(input.trim());
      setInput('');
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px';
    }
  }, [input]);

  return (
    <form onSubmit={handleSubmit} className="relative">
      <div className="flex items-end gap-2 bg-white border border-gray-200 rounded-2xl p-3 shadow-sm focus-within:ring-2 focus-within:ring-primary-500 focus-within:border-transparent transition-all">
        <textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={'Type your message... (e.g., "I got 50k, rent is due, want to invest but scared")'}
          className="flex-1 resize-none border-none outline-none bg-transparent text-gray-700 placeholder-gray-400 max-h-32 min-h-[44px]"
          rows={1}
          disabled={isLoading}
        />
        <button
          type="submit"
          disabled={!input.trim() || isLoading}
          className="p-2.5 bg-primary-600 text-white rounded-xl hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {isLoading ? (
            <Loader2 className="w-5 h-5 animate-spin" />
          ) : (
            <Send className="w-5 h-5" />
          )}
        </button>
      </div>
    </form>
  );
};

const MessageBubble = ({ message, isUser, metadata }) => {
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4 message-enter`}>
      <div className={`max-w-[80%] ${isUser ? 'order-2' : 'order-1'}`}>
        <div
          className={`px-4 py-3 rounded-2xl ${
            isUser
              ? 'bg-primary-600 text-white rounded-br-md'
              : 'bg-white border border-gray-200 text-gray-800 rounded-bl-md shadow-sm'
          }`}
        >
          <p className="text-sm leading-relaxed whitespace-pre-wrap">{message}</p>
        </div>
        
        {/* Metadata badges for AI messages */}
        {!isUser && metadata && (
          <div className="flex flex-wrap gap-2 mt-2 px-1">
            {metadata.emotion && (
              <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium text-white ${emotionColors[metadata.emotion.emotion] || 'bg-gray-500'}`}>
                <Heart className="w-3 h-3" />
                {emotionLabels[metadata.emotion.emotion]}
              </span>
            )}
            {metadata.intent && (
              <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-700">
                <Target className="w-3 h-3" />
                {intentLabels[metadata.intent.intent]}
              </span>
            )}
          </div>
        )}
        
        <span className={`text-xs text-gray-400 mt-1 block ${isUser ? 'text-right' : 'text-left'}`}>
          {formatTimestamp(new Date())}
        </span>
      </div>
    </div>
  );
};

const TypingIndicator = () => (
  <div className="flex justify-start mb-4">
    <div className="bg-white border border-gray-200 px-4 py-3 rounded-2xl rounded-bl-md shadow-sm">
      <div className="flex gap-1">
        <span className="w-2 h-2 bg-gray-400 rounded-full typing-dot"></span>
        <span className="w-2 h-2 bg-gray-400 rounded-full typing-dot"></span>
        <span className="w-2 h-2 bg-gray-400 rounded-full typing-dot"></span>
      </div>
    </div>
  </div>
);

const EmptyState = ({ onExampleClick }) => {
  const examples = [
    "I got 50k this month, my rent is due, I also want to invest but I'm scared",
    "Should I pay off my student loans or start investing?",
    "I'm overwhelmed by budgeting, where do I even start?",
    "My friends are buying crypto and I feel like I'm missing out",
  ];

  return (
    <div className="flex-1 flex flex-col items-center justify-center p-8 text-center">
      <div className="w-16 h-16 bg-primary-100 rounded-2xl flex items-center justify-center mb-4">
        <Sparkles className="w-8 h-8 text-primary-600" />
      </div>
      <h2 className="text-xl font-semibold text-gray-800 mb-2">
        Welcome to FinSight
      </h2>
      <p className="text-gray-500 max-w-md mb-6">
        Your AI financial friend. Talk naturally about money - I understand emotions, conflicts, and real-life situations.
      </p>
      
      <div className="w-full max-w-md space-y-2">
        <p className="text-xs font-medium text-gray-400 uppercase tracking-wider mb-3">
          Try an example
        </p>
        {examples.map((example, idx) => (
          <button
            key={idx}
            onClick={() => onExampleClick(example)}
            className="w-full text-left p-3 bg-white border border-gray-200 rounded-xl hover:border-primary-300 hover:bg-primary-50 transition-all text-sm text-gray-600"
          >
            {example}
          </button>
        ))}
      </div>
    </div>
  );
};

const InsightPanel = ({ messages }) => {
  const lastMessage = messages.filter(m => !m.isUser).pop();
  
  if (!lastMessage || !lastMessage.metadata) return null;

  const { emotion, intent, rag_sources } = lastMessage.metadata;

  return (
    <div className="bg-white border-l border-gray-200 p-4 space-y-4 overflow-y-auto">
      <h3 className="font-semibold text-gray-800 flex items-center gap-2">
        <Brain className="w-4 h-4" />
        AI Insights
      </h3>

      {emotion && (
        <div className="space-y-2">
          <label className="text-xs font-medium text-gray-500 uppercase">Detected Emotion</label>
          <div className={`p-3 rounded-xl text-white ${emotionColors[emotion.emotion]}`}>
            <div className="flex items-center justify-between">
              <span className="font-medium">{emotionLabels[emotion.emotion]}</span>
              <span className="text-xs opacity-75">{(emotion.confidence * 100).toFixed(0)}%</span>
            </div>
            <div className="mt-2 h-1.5 bg-white/30 rounded-full overflow-hidden">
              <div 
                className="h-full bg-white rounded-full transition-all"
                style={{ width: `${emotion.intensity * 100}%` }}
              />
            </div>
          </div>
        </div>
      )}

      {intent && (
        <div className="space-y-2">
          <label className="text-xs font-medium text-gray-500 uppercase">Primary Intent</label>
          <div className="p-3 bg-blue-50 border border-blue-100 rounded-xl">
            <div className="flex items-center justify-between">
              <span className="font-medium text-blue-800">{intentLabels[intent.intent]}</span>
              <span className="text-xs text-blue-600">{(intent.confidence * 100).toFixed(0)}%</span>
            </div>
          </div>
          {intent.sub_intents?.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-2">
              {intent.sub_intents.map((sub, idx) => (
                <span key={idx} className="text-xs px-2 py-1 bg-gray-100 text-gray-600 rounded-md">
                  {intentLabels[sub] || sub}
                </span>
              ))}
            </div>
          )}
        </div>
      )}

      {rag_sources && rag_sources.length > 0 && (
        <div className="space-y-2">
          <label className="text-xs font-medium text-gray-500 uppercase flex items-center gap-1">
            <BookOpen className="w-3 h-3" />
            Knowledge Sources
          </label>
          <div className="flex flex-wrap gap-1">
            {rag_sources.map((source, idx) => (
              <span key={idx} className="text-xs px-2 py-1 bg-primary-50 text-primary-700 rounded-md border border-primary-100">
                {source.replace(/_/g, ' ')}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default function ChatInterface() {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState(null);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (text) => {
    setError(null);
    
    // Add user message
    const userMessage = { id: Date.now(), text, isUser: true, timestamp: new Date() };
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await api.chat(text, conversationId);
      
      // Store conversation ID
      if (!conversationId) {
        setConversationId(response.conversation_id);
      }

      // Add AI response with metadata
      const aiMessage = {
        id: Date.now() + 1,
        text: response.message,
        isUser: false,
        timestamp: new Date(),
        metadata: {
          emotion: response.detected_emotion,
          intent: response.detected_intent,
          rag_sources: response.rag_sources,
        },
      };
      
      setMessages(prev => [...prev, aiMessage]);
    } catch (err) {
      setError('Failed to get response. Is the backend running?');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewChat = async () => {
    setMessages([]);
    setConversationId(null);
    setError(null);
    try {
      const response = await api.newConversation();
      setConversationId(response.conversation_id);
    } catch (err) {
      console.error('Failed to create new conversation:', err);
    }
  };

  return (
    <div className="flex h-full">
      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col bg-gray-50">
        {/* Header */}
        <div className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-primary-100 rounded-xl flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-primary-600" />
            </div>
            <div>
              <h1 className="font-semibold text-gray-800">FinSight</h1>
              <p className="text-xs text-gray-500">Your financial friend</p>
            </div>
          </div>
          <button
            onClick={handleNewChat}
            className="px-4 py-2 text-sm font-medium text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
          >
            New Chat
          </button>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6">
          {messages.length === 0 ? (
            <EmptyState onExampleClick={handleSend} />
          ) : (
            <>
              {messages.map((msg) => (
                <MessageBubble
                  key={msg.id}
                  message={msg.text}
                  isUser={msg.isUser}
                  metadata={msg.metadata}
                />
              ))}
              {isLoading && <TypingIndicator />}
              <div ref={messagesEndRef} />
            </>
          )}
          
          {error && (
            <div className="p-4 bg-red-50 border border-red-200 rounded-xl text-red-600 text-sm text-center">
              {error}
            </div>
          )}
        </div>

        {/* Input */}
        <div className="p-4 bg-white border-t border-gray-200">
          <ChatInput onSend={handleSend} isLoading={isLoading} />
        </div>
      </div>

      {/* Insight Panel */}
      <div className="w-80 hidden lg:block">
        <InsightPanel messages={messages} />
      </div>
    </div>
  );
}
