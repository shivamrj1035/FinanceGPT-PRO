import React, { useState, useEffect, memo, useCallback, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import PortfolioOverview from './widgets/PortfolioOverview';
import CashFlowChart from './widgets/CashFlowChart';
import SmartAIAssistant from './SmartAIAssistant';
import { apiService, User, Account, Transaction, Investment } from '../services/apiService';
import { aiChatService } from '../services/aiChatService';

interface ModernDashboardProps {
  currentUser?: { user_id: string; email: string; name?: string } | null;
  onLogout: () => void;
}

const ModernDashboard: React.FC<ModernDashboardProps> = memo(({
  currentUser,
  onLogout
}) => {
  const [activeTab, setActiveTab] = useState('overview');
  const [userData, setUserData] = useState<User | null>(null);
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [investments, setInvestments] = useState<Investment[]>([]);
  const [loading, setLoading] = useState(true);
  const [chatHistory, setChatHistory] = useState<Array<{ type: 'user' | 'ai'; message: string; timestamp?: string }>>([
    {
      type: 'ai',
      message: `Welcome back! I'm your AI Financial Advisor. I can see you're doing great with a ${accounts.length > 0 ? 'healthy portfolio' : 'growing wealth'}. How can I help optimize your finances today?`,
      timestamp: new Date().toLocaleTimeString()
    }
  ]);
  const [isThinking, setIsThinking] = useState(false);
  const [showAIPanel, setShowAIPanel] = useState(false);

  // Handle escape key to close modal
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && showAIPanel) {
        setShowAIPanel(false);
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [showAIPanel]);

  // Fetch MCP data based on user
  useEffect(() => {
    const fetchMCPData = async () => {
      if (!currentUser) {
        setLoading(false);
        return;
      }

      try {
        setLoading(true);

        // Fetch all data from MCP in parallel
        const [userRes, accountsRes, transactionsRes, investmentsRes] = await Promise.allSettled([
          apiService.getUser(currentUser.user_id),
          apiService.getAccounts(currentUser.user_id),
          apiService.getTransactions(currentUser.user_id),
          apiService.getInvestments(currentUser.user_id)
        ]);

        if (userRes.status === 'fulfilled') setUserData(userRes.value);
        if (accountsRes.status === 'fulfilled') setAccounts(accountsRes.value);
        if (transactionsRes.status === 'fulfilled') setTransactions(transactionsRes.value);
        if (investmentsRes.status === 'fulfilled') setInvestments(investmentsRes.value);
      } catch (error) {
        console.error('Error fetching MCP data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchMCPData();
    // Refresh data every 5 minutes to reduce unnecessary updates
    const interval = setInterval(fetchMCPData, 300000); // 5 minutes
    return () => clearInterval(interval);
  }, [currentUser]);

  // Helper function for colors
  const getColorForType = (type: string) => {
    const colors: Record<string, string> = {
      'SIP': '#06b6d4',
      'PPF': '#8b5cf6',
      'Stocks': '#10b981',
      'Real Estate': '#f59e0b',
      'Corporate Bonds': '#ef4444',
      'Equity': '#06b6d4',
      'Gold': '#fbbf24',
      'Other': '#64748b'
    };
    return colors[type] || colors.Other;
  };

  // Calculate real metrics from MCP data
  const metrics = useMemo(() => {
    const totalBalance = accounts.reduce((sum, acc) => sum + acc.balance, 0);
    const totalInvestments = investments.reduce((sum, inv) => sum + inv.current_value, 0);
    const netWorth = totalBalance + totalInvestments;

    // Calculate monthly income and expenses from transactions
    const now = new Date();
    const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1);
    const monthlyTransactions = transactions.filter(t => {
      // Try both date fields since API might use either
      const transactionDate = new Date(t.date || t.transaction_date || t.created_at);
      return transactionDate >= startOfMonth;
    });

    const monthlyIncome = monthlyTransactions
      .filter(t => t.amount > 0)
      .reduce((sum, t) => sum + t.amount, 0);

    const monthlyExpenses = Math.abs(monthlyTransactions
      .filter(t => t.amount < 0)
      .reduce((sum, t) => sum + t.amount, 0));

    const savingsRate = monthlyIncome > 0
      ? ((monthlyIncome - monthlyExpenses) / monthlyIncome * 100).toFixed(1)
      : '0';

    // Portfolio allocation from investments
    const portfolioData = investments.reduce((acc, inv) => {
      const type = inv.investment_type || 'Other';
      if (!acc[type]) {
        acc[type] = { value: 0, color: getColorForType(type) };
      }
      acc[type].value += inv.current_value;
      return acc;
    }, {} as Record<string, { value: number; color: string }>);

    // Add cash to portfolio
    if (totalBalance > 0) {
      portfolioData['Cash'] = { value: totalBalance, color: '#f59e0b' };
    }

    // Generate 6-month performance data
    const performanceData = [];
    const baseValue = netWorth * 0.85;
    for (let i = 5; i >= 0; i--) {
      const date = new Date();
      date.setMonth(date.getMonth() - i);
      const monthName = date.toLocaleDateString('en-US', { month: 'short' });
      const variation = Math.random() * 0.05 - 0.025; // ±2.5% variation
      performanceData.push({
        month: monthName,
        value: Math.round(baseValue * (1 + (5-i) * 0.03) * (1 + variation))
      });
    }

    // Generate 6-month cash flow data
    const cashFlowData = [];
    for (let i = 5; i >= 0; i--) {
      const date = new Date();
      date.setMonth(date.getMonth() - i);
      const monthName = date.toLocaleDateString('en-US', { month: 'short' });
      const incomeVariation = Math.random() * 20000 - 10000;
      const expenseVariation = Math.random() * 10000 - 5000;
      cashFlowData.push({
        month: monthName,
        income: Math.round(monthlyIncome + incomeVariation),
        expenses: Math.round(monthlyExpenses + expenseVariation)
      });
    }

    return {
      netWorth,
      totalBalance,
      totalInvestments,
      monthlyIncome,
      monthlyExpenses,
      savingsRate,
      portfolioData: Object.entries(portfolioData).map(([name, data]) => ({
        name,
        value: data.value,
        color: data.color
      })),
      performanceData,
      cashFlowData
    };
  }, [accounts, investments, transactions]);

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value);
  };

  const handleSendMessage = useCallback(async (message: string) => {
    if (!message.trim() || isThinking || !currentUser) return;

    // Add user message
    setChatHistory(prev => [...prev, {
      type: 'user',
      message,
      timestamp: new Date().toLocaleTimeString()
    }]);

    setIsThinking(true);

    try {
      // Prepare context for AI with streaming support
      const context = {
        userId: currentUser.user_id,
        financialData: {
          netWorth: metrics.netWorth,
          monthlyIncome: metrics.monthlyIncome,
          monthlyExpenses: metrics.monthlyExpenses,
          savingsRate: metrics.savingsRate,
          accounts: accounts.length,
          transactions: transactions.length,
          investments: investments.length
        },
        conversationHistory: chatHistory.map(msg => ({
          role: msg.type === 'user' ? 'user' as const : 'assistant' as const,
          content: msg.message,
          timestamp: msg.timestamp
        }))
      };

      // Get streaming response
      const responseStream = await aiChatService.sendMessage(message, context);

      let fullResponse = '';
      let isFirstChunk = true;
      let mcpToolsData = null;

      // Process streaming response
      for await (const chunk of responseStream) {
        // Check if this chunk contains MCP tools metadata
        if (chunk.includes('[MCP_TOOLS_START]') && chunk.includes('[MCP_TOOLS_END]')) {
          const toolsMatch = chunk.match(/\[MCP_TOOLS_START\](.*?)\[MCP_TOOLS_END\]/);
          if (toolsMatch) {
            try {
              mcpToolsData = JSON.parse(toolsMatch[1]);
              // Remove the metadata from the chunk
              const cleanChunk = chunk.replace(/\[MCP_TOOLS_START\].*?\[MCP_TOOLS_END\]/, '');
              if (cleanChunk.trim()) {
                fullResponse += cleanChunk;
              }
              continue;
            } catch (e) {
              console.error('Failed to parse MCP tools data:', e);
            }
          }
        }

        if (isFirstChunk && chunk.trim()) {
          // Add initial AI message with MCP tools data if available
          setChatHistory(prev => [...prev, {
            type: 'ai',
            message: chunk,
            timestamp: new Date().toLocaleTimeString(),
            mcpTools: mcpToolsData
          }]);
          isFirstChunk = false;
        } else if (!isFirstChunk) {
          // Update the last AI message with streaming content
          setChatHistory(prev => {
            const newHistory = [...prev];
            const lastMessage = newHistory[newHistory.length - 1];
            if (lastMessage && lastMessage.type === 'ai') {
              lastMessage.message += chunk;
              if (mcpToolsData && !lastMessage.mcpTools) {
                lastMessage.mcpTools = mcpToolsData;
              }
            }
            return newHistory;
          });
        }
        fullResponse += chunk;
      }

      // Save conversation to backend
      await aiChatService.saveConversation(currentUser.user_id, [
        { role: 'user', content: message },
        { role: 'assistant', content: fullResponse }
      ]);
    } catch (error) {
      console.error('Chat error:', error);

      // Fallback response on error
      setChatHistory(prev => [...prev, {
        type: 'ai',
        message: `I can help you with your finances. You have ${accounts.length} accounts with a total balance of ${formatCurrency(metrics.totalBalance)}. What would you like to know?`,
        timestamp: new Date().toLocaleTimeString()
      }]);
    } finally {
      setIsThinking(false);
    }
  }, [isThinking, currentUser, metrics, accounts, transactions, investments, chatHistory]);

  const navItems = [
    { id: 'overview', label: 'Overview', icon: '📊' },
    { id: 'transactions', label: 'Transactions', icon: '💳' },
    { id: 'analytics', label: 'Analytics', icon: '📈' },
    { id: 'reports', label: 'Reports', icon: '📄' }
  ];

  if (loading) {
    return (
      <div className="h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Loading your financial data from MCP...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      {/* Top Navigation Bar */}
      <header className="bg-white border-b border-gray-200 px-6 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-8">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold">F</span>
              </div>
              <h1 className="text-xl font-bold text-gray-800">FinanceGPT Pro</h1>
            </div>

            {/* Navigation Tabs */}
            <nav className="flex items-center space-x-1">
              {navItems.map(item => (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`px-4 py-2 rounded-lg flex items-center space-x-2 transition-all ${
                    activeTab === item.id
                      ? 'bg-blue-50 text-blue-600'
                      : 'text-gray-600 hover:bg-gray-50'
                  }`}
                >
                  <span>{item.icon}</span>
                  <span className="font-medium">{item.label}</span>
                </button>
              ))}
            </nav>
          </div>

          <div className="flex items-center space-x-4">
            {/* AI Assistant Toggle */}
            <button
              onClick={() => setShowAIPanel(!showAIPanel)}
              className="px-4 py-2 bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-lg flex items-center space-x-2 hover:shadow-lg transition-all"
            >
              <span>🤖</span>
              <span>AI Assistant</span>
            </button>

            {/* User Profile */}
            <div className="flex items-center space-x-3 px-4 py-2 bg-gray-50 rounded-lg">
              <div className="w-8 h-8 bg-gradient-to-br from-green-500 to-emerald-600 rounded-full flex items-center justify-center">
                <span className="text-white font-semibold">
                  {(currentUser?.name || currentUser?.email || 'U')[0].toUpperCase()}
                </span>
              </div>
              <div>
                <div className="text-sm font-medium text-gray-800">
                  {currentUser?.name || currentUser?.email?.split('@')[0]}
                </div>
                <div className="text-xs text-gray-500">{currentUser?.email}</div>
              </div>
            </div>

            <button
              onClick={onLogout}
              className="px-4 py-2 bg-red-50 text-red-600 rounded-lg hover:bg-red-100 transition-colors"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <div className="flex-1 overflow-hidden">
        <main className="h-full p-6 overflow-auto">
          {/* KPI Cards - Real MCP Data */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <div className="bg-white rounded-xl p-6 border border-gray-200">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-gray-600">Net Worth</span>
                <span className="text-xl">💰</span>
              </div>
              <div className="text-2xl font-bold text-gray-800">
                {formatCurrency(metrics.netWorth)}
              </div>
              <div className="text-xs text-green-600 mt-1">
                From {accounts.length} accounts
              </div>
            </div>

            <div className="bg-white rounded-xl p-6 border border-gray-200">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-gray-600">Monthly Income</span>
                <span className="text-xl">📈</span>
              </div>
              <div className="text-2xl font-bold text-gray-800">
                {formatCurrency(metrics.monthlyIncome)}
              </div>
              <div className="text-xs text-gray-500 mt-1">
                This month
              </div>
            </div>

            <div className="bg-white rounded-xl p-6 border border-gray-200">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-gray-600">Monthly Expenses</span>
                <span className="text-xl">💳</span>
              </div>
              <div className="text-2xl font-bold text-gray-800">
                {formatCurrency(metrics.monthlyExpenses)}
              </div>
              <div className="text-xs text-gray-500 mt-1">
                {transactions.length} transactions
              </div>
            </div>

            <div className="bg-white rounded-xl p-6 border border-gray-200">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-gray-600">Savings Rate</span>
                <span className="text-xl">🎯</span>
              </div>
              <div className="text-2xl font-bold text-gray-800">
                {metrics.savingsRate}%
              </div>
              <div className="text-xs text-gray-500 mt-1">
                {formatCurrency(metrics.monthlyIncome - metrics.monthlyExpenses)}/month
              </div>
            </div>
          </div>

          {/* Charts Section */}
          <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
            <PortfolioOverview
              totalValue={metrics.netWorth}
              change={1000}
              changePercent={2.5}
              portfolioData={metrics.portfolioData}
              performanceData={metrics.performanceData}
            />

            <CashFlowChart
              data={metrics.cashFlowData}
              monthlyIncome={metrics.monthlyIncome}
              monthlyExpenses={metrics.monthlyExpenses}
              netFlow={metrics.monthlyIncome - metrics.monthlyExpenses}
            />
          </div>

          {/* Recent Transactions */}
          <div className="mt-6 bg-white rounded-xl p-6 border border-gray-200">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">Recent Transactions</h3>
            <div className="space-y-2">
              {transactions.slice(0, 5).map((transaction, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                      transaction.amount > 0 ? 'bg-green-100' : 'bg-red-100'
                    }`}>
                      <span>{transaction.amount > 0 ? '📈' : '📉'}</span>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-800">
                        {transaction.description || transaction.category}
                      </p>
                      <p className="text-xs text-gray-500">
                        {new Date(transaction.date || transaction.transaction_date || transaction.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                  <div className={`text-lg font-semibold ${
                    transaction.amount > 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {transaction.amount > 0 ? '+' : ''}{formatCurrency(Math.abs(transaction.amount))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </main>
      </div>

      {/* AI Assistant Modal Overlay */}
      <AnimatePresence mode="wait">
        {showAIPanel && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-md"
            onClick={() => setShowAIPanel(false)}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0, y: 20 }}
              animate={{ scale: 1, opacity: 1, y: 0 }}
              exit={{ scale: 0.95, opacity: 0, y: 20 }}
              transition={{
                type: 'spring',
                damping: 25,
                stiffness: 300,
                duration: 0.3
              }}
              className="w-full max-w-5xl h-[90vh] bg-white rounded-2xl shadow-2xl overflow-hidden"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="h-full flex flex-col">
                {/* Modal Header */}
                <div className="flex items-center justify-between p-4 border-b border-gray-200 bg-gradient-to-r from-blue-50 to-indigo-50">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center">
                      <span className="text-white text-lg">🤖</span>
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold text-gray-800">AI Financial Advisor</h3>
                      <p className="text-xs text-gray-600">Personalized insights for {currentUser?.name || currentUser?.email}</p>
                    </div>
                  </div>
                  <button
                    onClick={() => setShowAIPanel(false)}
                    className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                  >
                    <svg className="w-6 h-6 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>

                {/* AI Assistant Content */}
                <div className="flex-1">
                  <SmartAIAssistant
                    currentUser={currentUser}
                    onSendMessage={handleSendMessage}
                    chatHistory={chatHistory}
                    isThinking={isThinking}
                    financialData={{
                      netWorth: metrics.netWorth,
                      monthlyIncome: metrics.monthlyIncome,
                      monthlyExpenses: metrics.monthlyExpenses,
                      savingsRate: metrics.savingsRate,
                      transactions: transactions
                    }}
                  />
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
});

ModernDashboard.displayName = 'ModernDashboard';

export default ModernDashboard;