import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface AIAssistantPanelProps {
  currentUser?: { user_id: string; email: string; name?: string } | null;
  onSendMessage: (message: string) => Promise<void>;
  chatHistory: Array<{ type: 'user' | 'ai'; message: string; timestamp?: string }>;
  isThinking?: boolean;
}

const AIAssistantPanel: React.FC<AIAssistantPanelProps> = ({
  currentUser,
  onSendMessage,
  chatHistory,
  isThinking = false
}) => {
  const [inputMessage, setInputMessage] = useState('');
  const [isConnected, setIsConnected] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [chatHistory, isThinking]);

  const quickQuestions = [
    {
      icon: '📈',
      text: "Analyze my portfolio performance",
      color: "text-emerald-400"
    },
    {
      icon: '🥧',
      text: "Show spending breakdown by category",
      color: "text-purple-400"
    },
    {
      icon: '📊',
      text: "Compare this month vs last month",
      color: "text-cyan-400"
    },
    {
      icon: '⚠️',
      text: "Check for unusual transactions",
      color: "text-red-400"
    }
  ];

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isThinking) return;

    try {
      await onSendMessage(inputMessage);
      setInputMessage('');
    } catch (error) {
      console.error('Error sending message:', error);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleQuickQuestion = (question: string) => {
    setInputMessage(question);
  };

  return (
    <div className="bg-slate-800/60 backdrop-blur-xl rounded-2xl border border-slate-700/50 flex flex-col h-full">
      {/* Header */}
      <div className="p-6 border-b border-slate-700/50">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-gradient-to-r from-purple-500/20 to-cyan-500/20 rounded-lg">
              <span className="text-purple-400 text-2xl">🤖</span>
            </div>
            <div>
              <h2 className="text-xl font-bold text-slate-100">AI Financial Assistant</h2>
              <div className="flex items-center space-x-2">
                <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-emerald-400' : 'bg-red-400'}`}></div>
                <span className="text-sm text-slate-400">
                  {isConnected ? 'Connected' : 'Disconnected'}
                </span>
              </div>
            </div>
          </div>

          <div className="flex space-x-2">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="p-2 bg-slate-700/50 hover:bg-slate-700 rounded-lg transition-colors"
              title="Export Conversation"
            >
              <span className="text-slate-400 text-base">⬇️</span>
            </motion.button>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="p-2 bg-slate-700/50 hover:bg-slate-700 rounded-lg transition-colors"
              title="Refresh Insights"
            >
              <span className="text-slate-400 text-base">🔄</span>
            </motion.button>
          </div>
        </div>

        {/* Quick Questions */}
        <div className="space-y-2">
          <p className="text-sm text-slate-400 mb-2">Quick questions:</p>
          <div className="grid grid-cols-1 gap-2">
            {quickQuestions.map((question, index) => (
              <motion.button
                key={index}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => handleQuickQuestion(question.text)}
                className="flex items-center space-x-3 p-3 bg-slate-700/30 hover:bg-slate-700/50 rounded-lg text-left transition-all"
              >
                <span className="text-base">{question.icon}</span>
                <span className="text-sm text-slate-300">{question.text}</span>
              </motion.button>
            ))}
          </div>
        </div>
      </div>

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4 min-h-0">
        <AnimatePresence>
          {chatHistory.map((message, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div className={`max-w-[85%] ${
                message.type === 'user'
                  ? 'bg-gradient-to-r from-cyan-500 to-purple-500 text-white'
                  : 'bg-slate-700/50 text-slate-200'
              } rounded-2xl px-4 py-3`}>
                <div className="flex items-start space-x-2">
                  {message.type === 'ai' && (
                    <div className="p-1 bg-purple-500/20 rounded-lg mt-0.5">
                      <span className="text-purple-400 text-sm">🤖</span>
                    </div>
                  )}
                  <div className="flex-1">
                    <p className="text-sm leading-relaxed">{message.message}</p>
                    {message.timestamp && (
                      <p className="text-xs opacity-70 mt-1">{message.timestamp}</p>
                    )}
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {/* Thinking Animation */}
        {isThinking && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex justify-start"
          >
            <div className="bg-slate-700/50 text-slate-200 rounded-2xl px-4 py-3">
              <div className="flex items-center space-x-2">
                <div className="p-1 bg-purple-500/20 rounded-lg">
                  <span className="text-purple-400 text-sm">🤖</span>
                </div>
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                  <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                </div>
                <span className="text-sm text-slate-400">Analyzing...</span>
              </div>
            </div>
          </motion.div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-6 border-t border-slate-700/50">
        <div className="flex items-end space-x-3">
          <div className="flex-1 relative">
            <textarea
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={currentUser ? "Ask me anything about your finances..." : "Please log in to chat..."}
              disabled={!currentUser || isThinking}
              className="w-full bg-slate-700/50 border border-slate-600/50 rounded-xl px-4 py-3 text-slate-200
                       placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-cyan-400/50 focus:border-cyan-400/50
                       disabled:opacity-50 disabled:cursor-not-allowed resize-none"
              rows={1}
              style={{ minHeight: '44px', maxHeight: '120px' }}
            />
          </div>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={handleSendMessage}
            disabled={!inputMessage.trim() || !currentUser || isThinking}
            className={`p-3 rounded-xl transition-all ${
              inputMessage.trim() && currentUser && !isThinking
                ? 'bg-gradient-to-r from-cyan-500 to-purple-500 hover:shadow-lg hover:shadow-cyan-500/25 text-white'
                : 'bg-slate-700/50 text-slate-400 cursor-not-allowed'
            }`}
          >
            {isThinking ? (
              <span className="text-lg animate-spin">🔄</span>
            ) : (
              <span className="text-lg">➤</span>
            )}
          </motion.button>
        </div>

        {/* Status Bar */}
        <div className="flex items-center justify-between mt-3 text-xs text-slate-500">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-1">
              <span className="text-xs">🟢</span>
              <span>Real-time analysis</span>
            </div>
            <div className="flex items-center space-x-1">
              <span className="text-xs">⭐</span>
              <span>AI-powered insights</span>
            </div>
          </div>
          <div>
            Press Enter to send • Shift+Enter for new line
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIAssistantPanel;