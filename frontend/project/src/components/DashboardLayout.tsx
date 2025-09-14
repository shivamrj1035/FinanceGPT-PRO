import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface DashboardLayoutProps {
  children: React.ReactNode;
  currentUser?: { user_id: string; email: string; name?: string } | null;
  onLogout: () => void;
}

interface LiveStats {
  portfolioValue: string;
  netWorth: string;
  creditScore: string;
  portfolioChange: string;
  netWorthChange: string;
  creditChange: string;
  lastUpdated: string;
}

const DashboardLayout: React.FC<DashboardLayoutProps> = ({
  children,
  currentUser,
  onLogout
}) => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [activeSection, setActiveSection] = useState('overview');
  const [liveStats, setLiveStats] = useState<LiveStats>({
    portfolioValue: '₹11,36,351',
    netWorth: '₹8,46,351',
    creditScore: '742',
    portfolioChange: '+11.7%',
    netWorthChange: '+5.2%',
    creditChange: '+12',
    lastUpdated: new Date().toLocaleTimeString()
  });
  const [isOnline, setIsOnline] = useState(true);

  // Update live stats every 30 seconds to simulate real-time updates
  useEffect(() => {
    const interval = setInterval(() => {
      setLiveStats(prev => ({
        ...prev,
        lastUpdated: new Date().toLocaleTimeString()
      }));
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  const navigation = [
    { id: 'overview', label: 'Overview', icon: '📊', active: true },
    { id: 'portfolio', label: 'Portfolio', icon: '💼' },
    { id: 'analytics', label: 'Analytics', icon: '📈' },
    { id: 'ai-assistant', label: 'AI Assistant', icon: '🤖' },
    { id: 'transactions', label: 'Transactions', icon: '💳' },
    { id: 'reports', label: 'Reports', icon: '📄' },
  ];

  const quickStats = [
    {
      label: 'Portfolio Value',
      value: liveStats.portfolioValue,
      change: liveStats.portfolioChange,
      icon: '📈',
      trend: 'up',
      color: 'text-emerald-600'
    },
    {
      label: 'Net Worth',
      value: liveStats.netWorth,
      change: liveStats.netWorthChange,
      icon: '💰',
      trend: 'up',
      color: 'text-blue-600'
    },
    {
      label: 'Credit Score',
      value: liveStats.creditScore,
      change: liveStats.creditChange,
      icon: '🛡️',
      trend: 'up',
      color: 'text-purple-600'
    },
  ];

  return (
    <div className="h-screen flex flex-col overflow-hidden bg-gradient-to-br from-slate-50 via-blue-50/30 to-indigo-50/50">
      {/* Fixed Header - 64px */}
      <header
        className="flex-none h-16 bg-white/95 backdrop-blur-xl border-b border-slate-200/50 shadow-lg shadow-slate-200/10"
        style={{ height: 'var(--header-height)' }}
      >
        <div className="flex items-center justify-between h-full px-6">
          {/* Left Section - Logo & Controls */}
          <div className="flex items-center space-x-4">
            <button
              onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
              className="p-2 rounded-lg bg-gradient-to-r from-blue-50 to-indigo-50 hover:from-blue-100 hover:to-indigo-100 border border-blue-200/50 transition-all duration-200"
            >
              <span className="text-gray-600 text-lg">
                {sidebarCollapsed ? '☰' : '←'}
              </span>
            </button>
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">F</span>
              </div>
              <h1 className="text-xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 bg-clip-text text-transparent">
                FinanceGPT Pro
              </h1>
            </div>
          </div>

          {/* Center Section - Live Stats Ticker */}
          <div className="hidden xl:flex items-center space-x-8 px-6 py-2 bg-white/50 rounded-full border border-slate-200/50">
            {quickStats.map((stat, index) => (
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="flex items-center space-x-2"
              >
                <span className="text-lg">{stat.icon}</span>
                <div className="text-center">
                  <div className="flex items-center space-x-1">
                    <span className="text-sm font-semibold text-gray-800">{stat.value}</span>
                    <span className={`text-xs font-medium ${stat.color}`}>
                      {stat.change}
                    </span>
                  </div>
                  <div className="text-xs text-gray-500">{stat.label}</div>
                </div>
              </motion.div>
            ))}
          </div>

          {/* Right Section - Status & User Menu */}
          <div className="flex items-center space-x-4">
            {/* Live Status Indicator */}
            <div className="flex items-center space-x-2 px-3 py-1 bg-emerald-50 rounded-full border border-emerald-200/50">
              <div className={`w-2 h-2 rounded-full ${isOnline ? 'bg-emerald-400' : 'bg-gray-400'} animate-pulse`}></div>
              <span className="text-xs font-medium text-emerald-700">
                {isOnline ? 'Live' : 'Offline'}
              </span>
              <span className="text-xs text-emerald-600">{liveStats.lastUpdated}</span>
            </div>

            {/* Notifications */}
            <button className="relative p-2 rounded-lg bg-white border border-slate-200/50 hover:bg-slate-50 transition-colors">
              <span className="text-gray-600 text-lg">🔔</span>
              <span className="absolute -top-1 -right-1 w-3 h-3 bg-red-400 rounded-full animate-pulse"></span>
            </button>

            {/* User Profile */}
            <div className="flex items-center space-x-3 px-4 py-2 bg-white rounded-lg border border-slate-200/50">
              <div className="w-8 h-8 rounded-full bg-gradient-to-r from-blue-600 to-indigo-600 flex items-center justify-center">
                <span className="text-white text-sm font-medium">
                  {(currentUser?.name || currentUser?.email || 'U').charAt(0).toUpperCase()}
                </span>
              </div>
              <div className="hidden md:block">
                <div className="text-sm font-medium text-gray-800">
                  {currentUser?.name || currentUser?.email?.split('@')[0] || 'User'}
                </div>
                <div className="text-xs text-gray-500">Premium Account</div>
              </div>
            </div>

            {/* Logout */}
            <button
              onClick={onLogout}
              className="p-2 rounded-lg bg-red-50 hover:bg-red-100 border border-red-200/50 transition-colors group"
              title="Logout"
            >
              <span className="text-red-600 text-lg group-hover:scale-110 transition-transform">🚪</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main Content Area - Remaining viewport height */}
      <div className="flex-1 flex overflow-hidden">
        {/* Fixed Sidebar */}
        <AnimatePresence>
          <motion.aside
            initial={false}
            animate={{
              width: sidebarCollapsed ? 'var(--sidebar-collapsed-width)' : 'var(--sidebar-width)',
            }}
            transition={{ duration: 0.3, ease: 'easeInOut' }}
            className="flex-none bg-white/80 backdrop-blur-xl border-r border-slate-200/30 shadow-xl shadow-slate-200/10 overflow-hidden"
          >
            <nav className="h-full flex flex-col p-4">
              {/* Navigation Items */}
              <div className="space-y-2">
                {navigation.map((item, index) => (
                  <motion.button
                    key={item.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.05 }}
                    onClick={() => setActiveSection(item.id)}
                    className={`w-full flex items-center space-x-3 px-4 py-3 rounded-xl transition-all duration-200 group ${
                      activeSection === item.id
                        ? 'bg-gradient-to-r from-blue-500/15 to-purple-500/15 border border-blue-400/40 text-blue-700 shadow-lg shadow-blue-200/20'
                        : 'hover:bg-gradient-to-r hover:from-blue-50/80 hover:to-indigo-50/80 text-slate-600 hover:text-slate-800 hover:shadow-md hover:shadow-blue-100/20'
                    }`}
                  >
                    <span className={`text-lg transition-transform group-hover:scale-110 ${sidebarCollapsed ? 'mx-auto' : ''}`}>
                      {item.icon}
                    </span>
                    {!sidebarCollapsed && (
                      <span className="font-medium">{item.label}</span>
                    )}
                    {!sidebarCollapsed && activeSection === item.id && (
                      <motion.div
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        className="ml-auto w-2 h-2 bg-blue-500 rounded-full"
                      />
                    )}
                  </motion.button>
                ))}
              </div>

              {/* AI Insights Panel */}
              {!sidebarCollapsed && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.4 }}
                  className="mt-auto p-4 bg-gradient-to-br from-blue-500/10 via-purple-500/8 to-indigo-500/10 rounded-xl border border-blue-400/20 shadow-lg shadow-blue-200/10"
                >
                  <div className="flex items-center space-x-2 mb-2">
                    <span className="text-lg">🤖</span>
                    <div className="text-sm font-semibold text-blue-700">AI Insights</div>
                  </div>
                  <div className="text-xs text-gray-600 mb-3">
                    Your spending pattern shows a 15% increase this month. I recommend reviewing your subscriptions.
                  </div>
                  <button className="w-full text-xs bg-blue-500/20 hover:bg-blue-500/30 px-3 py-2 rounded-lg text-blue-700 transition-colors">
                    View Analysis
                  </button>
                </motion.div>
              )}
            </nav>
          </motion.aside>
        </AnimatePresence>

        {/* Main Dashboard Content - Scrollable */}
        <main className="flex-1 overflow-auto custom-scrollbar bg-transparent">
          <div className="h-full p-6">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
};

export default DashboardLayout;