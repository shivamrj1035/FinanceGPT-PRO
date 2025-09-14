import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FiSend, FiUser, FiCpu } from 'react-icons/fi';

interface AIAssistantProps {
  permissions: Record<string, boolean>;
  chatHistory: Array<{ sender: string; content: string }>;
  addChatMessage: (sender: string, content: string) => void;
  currentUser?: { user_id: string; email: string } | null;
}

const AIAssistant: React.FC<AIAssistantProps> = ({ permissions, chatHistory, addChatMessage, currentUser }) => {
  const [inputMessage, setInputMessage] = useState('');
  const [isThinking, setIsThinking] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const wsRef = useRef<WebSocket | null>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [chatHistory, isThinking]);

  // WebSocket connection management
  useEffect(() => {
    if (!currentUser) return;

    let reconnectAttempts = 0;
    const maxReconnectAttempts = 3;
    let reconnectTimeoutId: NodeJS.Timeout | null = null;

    const connectWebSocket = () => {
      if (reconnectAttempts >= maxReconnectAttempts) {
        console.log('Max reconnection attempts reached');
        return;
      }

      try {
        const ws = new WebSocket(`ws://localhost:8000/ws/${currentUser.user_id}`);

        ws.onopen = () => {
          setIsConnected(true);
          reconnectAttempts = 0; // Reset on successful connection
          console.log('WebSocket connected successfully');
          // Only show connection message once per user session
          const hasShownConnectionMessage = sessionStorage.getItem('ws_connected');
          if (!hasShownConnectionMessage) {
            addChatMessage('ai', '🔗 Real-time connection established. I can now provide instant fraud alerts and analysis.');
            sessionStorage.setItem('ws_connected', 'true');
          }
        };

        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            if (data.type === 'fraud_alert') {
              addChatMessage('ai', `🚨 FRAUD ALERT: ${data.message}`);
            } else if (data.type === 'ai_response') {
              addChatMessage('ai', data.message);
            } else if (data.type === 'notification') {
              addChatMessage('ai', `📢 ${data.message}`);
            }
          } catch (error) {
            console.error('Error parsing WebSocket message:', error);
          }
        };

        ws.onclose = (event) => {
          console.log('WebSocket closed with code:', event.code, 'reason:', event.reason);
          setIsConnected(false);
          wsRef.current = null;

          // Only reconnect if not a manual close (code 1000) and we haven't hit max attempts
          if (event.code !== 1000 && reconnectAttempts < maxReconnectAttempts) {
            reconnectAttempts++;
            console.log(`Reconnection attempt ${reconnectAttempts}/${maxReconnectAttempts}`);
            reconnectTimeoutId = setTimeout(() => {
              connectWebSocket();
            }, 10000); // Longer delay to prevent storm
          }
        };

        ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          setIsConnected(false);
        };

        wsRef.current = ws;
      } catch (error) {
        console.error('Failed to connect WebSocket:', error);
      }
    };

    connectWebSocket();

    return () => {
      if (reconnectTimeoutId) {
        clearTimeout(reconnectTimeoutId);
      }
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.close(1000, 'Component unmounting'); // Clean close
        wsRef.current = null;
      }
    };
  }, [currentUser, addChatMessage]);

  const handleAIResponse = async (userMessage: string) => {
    if (!currentUser) {
      addChatMessage('ai', "Please log in to get personalized financial advice.");
      return;
    }

    if (!permissions.transactions) {
      addChatMessage('ai', "I need access to your transaction data to provide personalized advice. Please grant the 'Transactions' permission in the control panel.");
      return;
    }

    setIsThinking(true);

    try {
      const response = await fetch('http://localhost:8000/api/v1/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage,
          user_id: currentUser.user_id
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      if (data.success) {
        addChatMessage('ai', data.response);
      } else {
        addChatMessage('ai', data.error || "Sorry, I encountered an error processing your request. Please try again.");
      }
    } catch (error) {
      console.error('Error calling AI chat API:', error);
      addChatMessage('ai', "I'm having trouble connecting to my brain right now. Please check if the backend server is running and try again.");
    } finally {
      setIsThinking(false);
    }
  };

  const handleSendMessage = () => {
    if (!inputMessage.trim()) return;

    addChatMessage('user', inputMessage);
    const userMessage = inputMessage;
    setInputMessage('');

    // Handle real AI responses
    handleAIResponse(userMessage);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const isInputDisabled = !permissions.transactions;

  return (
    <div className="bg-[#10182F] backdrop-blur-sm rounded-2xl p-6 border border-[#00D1B2]/20 h-[calc(100vh-140px)] flex flex-col">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold text-white">AI Assistant</h2>
        <div className="flex items-center space-x-2">
          <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-400' : 'bg-red-400'}`}></div>
          <span className={`text-xs ${isConnected ? 'text-green-400' : 'text-red-400'}`}>
            {isConnected ? 'Live' : 'Offline'}
          </span>
        </div>
      </div>
      
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto space-y-4 mb-4 custom-scrollbar">
        <AnimatePresence>
          {chatHistory.map((message, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
              className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div className={`max-w-[85%] rounded-2xl px-4 py-3 ${
                message.sender === 'user' 
                  ? 'bg-[#8A2BE2] text-white' 
                  : 'bg-[#0A0F1F] text-[#A0AEC0] border border-[#00D1B2]/30 shadow-[0_0_15px_rgba(0,209,178,0.1)]'
              }`}>
                <div className="flex items-start space-x-2">
                  {message.sender === 'ai' && <FiCpu className="mt-1 text-[#00D1B2] flex-shrink-0" />}
                  {message.sender === 'user' && <FiUser className="mt-1 text-white flex-shrink-0" />}
                  <p className="text-sm leading-relaxed">{message.content}</p>
                </div>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {isThinking && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex justify-start"
          >
            <div className="bg-[#0A0F1F] border border-[#00D1B2]/30 rounded-2xl px-4 py-3 shadow-[0_0_15px_rgba(0,209,178,0.1)]">
              <div className="flex items-center space-x-2">
                <FiCpu className="text-[#00D1B2]" />
                <div className="flex space-x-1">
                  <motion.div
                    animate={{ opacity: [0.4, 1, 0.4] }}
                    transition={{ duration: 1.5, repeat: Infinity, delay: 0 }}
                    className="w-2 h-2 bg-[#00D1B2] rounded-full"
                  />
                  <motion.div
                    animate={{ opacity: [0.4, 1, 0.4] }}
                    transition={{ duration: 1.5, repeat: Infinity, delay: 0.5 }}
                    className="w-2 h-2 bg-[#00D1B2] rounded-full"
                  />
                  <motion.div
                    animate={{ opacity: [0.4, 1, 0.4] }}
                    transition={{ duration: 1.5, repeat: Infinity, delay: 1 }}
                    className="w-2 h-2 bg-[#00D1B2] rounded-full"
                  />
                </div>
              </div>
            </div>
          </motion.div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="flex space-x-2">
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          disabled={isInputDisabled}
          className={`flex-1 px-4 py-3 bg-[#0A0F1F] border rounded-lg text-white focus:outline-none transition-all ${
            isInputDisabled 
              ? 'border-gray-600 cursor-not-allowed opacity-50' 
              : 'border-[#00D1B2]/20 focus:border-[#00D1B2] focus:shadow-[0_0_15px_rgba(0,209,178,0.3)]'
          }`}
          placeholder={
            isInputDisabled 
              ? "Grant 'Transactions' permission to chat" 
              : "Ask me about your finances..."
          }
        />
        <motion.button
          whileHover={!isInputDisabled ? { scale: 1.05 } : {}}
          whileTap={!isInputDisabled ? { scale: 0.95 } : {}}
          onClick={handleSendMessage}
          disabled={isInputDisabled || !inputMessage.trim()}
          className={`px-4 py-3 rounded-lg font-medium transition-all ${
            isInputDisabled || !inputMessage.trim()
              ? 'bg-gray-600 cursor-not-allowed opacity-50' 
              : 'bg-gradient-to-r from-[#00D1B2] to-[#8A2BE2] hover:shadow-[0_0_20px_rgba(0,209,178,0.4)]'
          } text-white`}
        >
          <FiSend />
        </motion.button>
      </div>
    </div>
  );
};

export default AIAssistant;