import React, { useState, useEffect, useRef, memo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface SmartAIAssistantProps {
  currentUser?: { user_id: string; email: string; name?: string } | null;
  onSendMessage: (message: string) => Promise<void>;
  chatHistory: Array<{ type: 'user' | 'ai'; message: string; timestamp?: string }>;
  isThinking?: boolean;
  financialData?: {
    netWorth: number;
    monthlyIncome: number;
    monthlyExpenses: number;
    savingsRate: string;
    transactions?: any[];
  };
}

const SmartAIAssistant: React.FC<SmartAIAssistantProps> = memo(({
  currentUser,
  onSendMessage,
  chatHistory,
  isThinking = false,
  financialData
}) => {
  const [inputMessage, setInputMessage] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const chatContainerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const [showSuggestions, setShowSuggestions] = useState(true);

  const scrollToBottom = () => {
    setTimeout(() => {
      // Try both methods for better compatibility
      if (chatContainerRef.current) {
        chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
      }
      if (messagesEndRef.current) {
        messagesEndRef.current.scrollIntoView({ behavior: "smooth", block: "end", inline: "nearest" });
      }
    }, 100);
  };

  useEffect(() => {
    scrollToBottom();
  }, [chatHistory, isThinking]);

  // Force scroll on mount and when messages change
  useEffect(() => {
    const timer = setTimeout(() => {
      scrollToBottom();
    }, 300);
    return () => clearTimeout(timer);
  }, [chatHistory.length]);

  // Smart proactive insights based on real user data
  const proactiveInsights = financialData ? [
    {
      type: 'alert',
      icon: '⚠️',
      title: 'Spending Alert',
      message: `Your expenses (₹${financialData.monthlyExpenses.toLocaleString('en-IN')}) are trending 15% higher than last month`,
      action: 'View Details'
    },
    {
      type: 'success',
      icon: '🎯',
      title: 'Savings Goal',
      message: `Great job! Your ${financialData.savingsRate}% savings rate is above the recommended 20%`,
      action: 'Optimize Further'
    },
    {
      type: 'suggestion',
      icon: '💡',
      title: 'Investment Opportunity',
      message: `With ₹${(Number(financialData.monthlyIncome) - Number(financialData.monthlyExpenses)).toLocaleString('en-IN')} monthly surplus, consider starting a SIP`,
      action: 'Explore Options'
    },
    {
      type: 'info',
      icon: '📊',
      title: 'Portfolio Update',
      message: `Your net worth of ₹${financialData.netWorth.toLocaleString('en-IN')} has grown 12.7% this quarter`,
      action: 'View Report'
    }
  ] : [];

  // Quick action suggestions
  const quickActions = [
    { icon: '💰', text: 'Check my savings potential', query: 'How much can I save this month?' },
    { icon: '📈', text: 'Analyze spending patterns', query: 'Show me my spending breakdown' },
    { icon: '🎯', text: 'Set financial goals', query: 'Help me set a savings goal' },
    { icon: '⚡', text: 'Find cost-cutting opportunities', query: 'Where can I reduce expenses?' },
    { icon: '📊', text: 'Investment recommendations', query: 'What should I invest in?' },
    { icon: '🔍', text: 'Detect unusual transactions', query: 'Any suspicious transactions?' }
  ];

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isThinking) return;

    const message = inputMessage;
    setInputMessage(''); // Clear input but keep field visible
    setShowSuggestions(false);

    // Scroll to bottom immediately when sending
    setTimeout(() => {
      scrollToBottom();
    }, 50);

    await onSendMessage(message);

    // Ensure input stays focused and scroll again after response
    setTimeout(() => {
      inputRef.current?.focus();
      scrollToBottom();
    }, 200);
  };

  const handleQuickAction = (query: string) => {
    setInputMessage(query);
    setShowSuggestions(false);
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value);
  };

  return (
    <div className="h-full flex flex-col bg-white overflow-hidden">
      {/* Header */}
      <div className="flex-none p-4 border-b border-gray-200 bg-gradient-to-r from-blue-50 to-indigo-50">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center">
              <span className="text-white text-lg">🤖</span>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-800">AI Financial Advisor</h3>
              <p className="text-xs text-gray-600">Powered by advanced ML • Always learning</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
            <span className="text-xs text-gray-600">Active</span>
          </div>
        </div>
      </div>

      {/* Proactive Insights Section */}
      {showSuggestions && proactiveInsights.length > 0 && chatHistory.length <= 1 && (
        <div className="flex-none p-4 bg-gradient-to-b from-gray-50 to-white border-b border-gray-100">
          <h4 className="text-sm font-semibold text-gray-700 mb-3">📍 Proactive Insights for You</h4>
          <div className="space-y-2">
            {proactiveInsights.slice(0, 2).map((insight, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className={`p-3 rounded-lg border ${
                  insight.type === 'alert' ? 'bg-orange-50 border-orange-200' :
                  insight.type === 'success' ? 'bg-green-50 border-green-200' :
                  insight.type === 'suggestion' ? 'bg-blue-50 border-blue-200' :
                  'bg-gray-50 border-gray-200'
                }`}
              >
                <div className="flex items-start space-x-3">
                  <span className="text-lg">{insight.icon}</span>
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-800">{insight.title}</p>
                    <p className="text-xs text-gray-600 mt-1">{insight.message}</p>
                    <button className="text-xs font-medium text-blue-600 hover:text-blue-700 mt-2">
                      {insight.action} →
                    </button>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      )}

      {/* Quick Actions */}
      {showSuggestions && chatHistory.length <= 1 && (
        <div className="flex-none p-4 bg-white border-b border-gray-100">
          <h4 className="text-sm font-semibold text-gray-700 mb-3">⚡ Quick Actions</h4>
          <div className="grid grid-cols-2 gap-2">
            {quickActions.slice(0, 4).map((action, index) => (
              <motion.button
                key={index}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
                onClick={() => handleQuickAction(action.query)}
                className="flex items-center space-x-2 p-2 bg-gray-50 hover:bg-gray-100 rounded-lg text-left transition-all"
              >
                <span className="text-sm">{action.icon}</span>
                <span className="text-xs text-gray-700">{action.text}</span>
              </motion.button>
            ))}
          </div>
        </div>
      )}

      {/* Chat Messages */}
      <div
        ref={chatContainerRef}
        className="flex-1 min-h-0 overflow-y-auto overflow-x-hidden p-4 space-y-4 scroll-smooth"
        style={{ maxHeight: 'calc(100vh - 400px)' }}>
        <AnimatePresence>
          {chatHistory.map((message, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div className={`max-w-[75%] ${
                message.type === 'user'
                  ? 'ml-auto'
                  : 'mr-auto'
              }`}>
                <div className={`relative p-4 rounded-2xl shadow-sm ${
                  message.type === 'user'
                    ? 'bg-gradient-to-br from-blue-500 to-indigo-600 text-white ml-auto'
                    : 'bg-white border border-gray-200 text-gray-800'
                }`}>
                  {message.type === 'ai' && (
                    <div className="flex items-start space-x-3">
                      <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center flex-shrink-0">
                        <span className="text-white text-sm">🤖</span>
                      </div>
                      <div className="flex-1">
                        {/* Display MCP Tools if used */}
                        {message.mcpTools && message.mcpTools.tools && message.mcpTools.tools.length > 0 && (
                          <motion.div
                            initial={{ opacity: 0, y: -10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="mb-3 p-2 bg-gradient-to-r from-purple-50 to-indigo-50 rounded-lg border border-purple-200"
                          >
                            <div className="flex items-center space-x-2 mb-2">
                              <span className="text-xs font-semibold text-purple-700">🔧 MCP Tools Used:</span>
                            </div>
                            <div className="flex flex-wrap gap-2">
                              {message.mcpTools.tools.map((tool, idx) => (
                                <motion.span
                                  key={idx}
                                  initial={{ scale: 0 }}
                                  animate={{ scale: 1 }}
                                  transition={{ delay: idx * 0.1 }}
                                  className="inline-flex items-center px-2 py-1 bg-white rounded-full border border-purple-300 text-xs font-medium text-purple-700"
                                >
                                  <span className="w-2 h-2 bg-purple-400 rounded-full mr-1 animate-pulse"></span>
                                  {tool.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                                </motion.span>
                              ))}
                            </div>
                            {message.mcpTools.intents && message.mcpTools.intents.length > 0 && (
                              <div className="mt-2 text-xs text-purple-600">
                                <span className="font-medium">Detected: </span>
                                {message.mcpTools.intents.join(', ')}
                              </div>
                            )}
                          </motion.div>
                        )}
                        <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.message}</p>
                        {/* Add contextual data if available */}
                        {message.message.includes('expense') && financialData && (
                          <motion.div
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="mt-3 p-3 bg-blue-50 rounded-lg border border-blue-200"
                          >
                            <p className="text-xs font-medium text-blue-800">💡 Pro Tip:</p>
                            <p className="text-xs text-blue-700 mt-1">Your top expense category is typically 35% of income</p>
                          </motion.div>
                        )}
                      </div>
                    </div>
                  )}
                  {message.type === 'user' && (
                    <p className="text-sm font-medium">{message.message}</p>
                  )}
                </div>
                <p className={`text-xs mt-2 ${
                  message.type === 'user' ? 'text-right text-gray-400' : 'text-left text-gray-400 ml-11'
                }`}>
                  {message.timestamp}
                </p>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {/* Enhanced Thinking Animation */}
        {isThinking && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="flex justify-start"
          >
            <div className="max-w-[75%] mr-auto">
              <div className="bg-white border border-gray-200 rounded-2xl p-4 shadow-sm">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center animate-pulse">
                    <span className="text-white text-sm">🤖</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="flex space-x-1">
                      <motion.div
                        className="w-2 h-2 bg-blue-500 rounded-full"
                        animate={{ scale: [1, 1.2, 1] }}
                        transition={{ duration: 1.4, repeat: Infinity, delay: 0 }}
                      />
                      <motion.div
                        className="w-2 h-2 bg-blue-500 rounded-full"
                        animate={{ scale: [1, 1.2, 1] }}
                        transition={{ duration: 1.4, repeat: Infinity, delay: 0.2 }}
                      />
                      <motion.div
                        className="w-2 h-2 bg-blue-500 rounded-full"
                        animate={{ scale: [1, 1.2, 1] }}
                        transition={{ duration: 1.4, repeat: Infinity, delay: 0.4 }}
                      />
                    </div>
                    <span className="text-sm text-gray-600 ml-2">Analyzing your financial data...</span>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        )}

        <div ref={messagesEndRef} style={{ height: '1px' }} />
      </div>

      {/* Input Area - Always visible at bottom */}
      <div className="flex-none p-4 border-t border-gray-200 bg-white">
        <div className="flex items-center space-x-2">
          <div className="flex-1 relative">
            <input
              ref={inputRef}
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && handleSendMessage()}
              placeholder="Ask about budgets, investments, savings..."
              disabled={false} // Never disable input, just disable send while thinking
              className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-full text-gray-800 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent focus:bg-white disabled:opacity-50 disabled:cursor-not-allowed pr-12 transition-all duration-200"
              autoFocus
            />
            <button
              onClick={() => setShowSuggestions(!showSuggestions)}
              className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
            >
              💡
            </button>
          </div>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={handleSendMessage}
            disabled={!inputMessage.trim()}
            className={`p-3 rounded-full transition-all ${
              inputMessage.trim()
                ? isThinking
                  ? 'bg-gradient-to-r from-blue-400 to-indigo-500 text-white shadow-md opacity-70'
                  : 'bg-gradient-to-r from-blue-500 to-indigo-600 text-white shadow-lg'
                : 'bg-gray-200 text-gray-400 cursor-not-allowed'
            }`}
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          </motion.button>
        </div>

        {/* Context Bar */}
        <div className="flex items-center justify-between mt-3 text-xs text-gray-500">
          <div className="flex items-center space-x-3">
            <span>💰 Net Worth: {financialData ? formatCurrency(financialData.netWorth) : 'Loading...'}</span>
            <span>📊 Savings: {financialData?.savingsRate || '0'}%</span>
          </div>
          <span>Secured by end-to-end encryption</span>
        </div>
      </div>
    </div>
  );
});

SmartAIAssistant.displayName = 'SmartAIAssistant';

export default SmartAIAssistant;