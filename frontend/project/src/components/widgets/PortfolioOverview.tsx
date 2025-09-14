import React from 'react';
import { motion } from 'framer-motion';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

interface PortfolioOverviewProps {
  totalValue: number;
  change: number;
  changePercent: number;
  portfolioData: Array<{ name: string; value: number; color: string }>;
  performanceData: Array<{ month: string; value: number }>;
}

const PortfolioOverview: React.FC<PortfolioOverviewProps> = ({
  totalValue,
  change,
  changePercent,
  portfolioData,
  performanceData
}) => {
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  };

  const isPositive = change >= 0;

  return (
    <div className="bg-gradient-to-br from-white/95 via-blue-50/30 to-indigo-50/40 backdrop-blur-xl rounded-2xl p-6 border border-blue-200/40 shadow-xl shadow-blue-200/10">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-gradient-to-r from-cyan-500/20 to-purple-500/20 rounded-lg">
            <span className="text-cyan-400 text-2xl">📊</span>
          </div>
          <div>
            <h2 className="text-xl font-bold text-slate-800">Portfolio Overview</h2>
            <p className="text-sm text-slate-600">Total investment value</p>
          </div>
        </div>
        <div className="text-right">
          <div className="text-2xl font-bold text-slate-800">{formatCurrency(totalValue)}</div>
          <div className={`flex items-center space-x-1 text-sm font-medium ${
            isPositive ? 'text-emerald-400' : 'text-red-400'
          }`}>
            <span className="text-base">{isPositive ? '📈' : '📉'}</span>
            <span>{isPositive ? '+' : ''}{formatCurrency(change)} ({changePercent.toFixed(1)}%)</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Performance Chart */}
        <div>
          <h3 className="text-sm font-medium text-slate-700 mb-3">6-Month Performance</h3>
          <div className="h-40">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={performanceData}>
                <defs>
                  <linearGradient id="portfolioGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#06b6d4" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="month" axisLine={false} tickLine={false} tick={{ fill: '#64748b', fontSize: 12 }} />
                <YAxis hide />
                <Area
                  type="monotone"
                  dataKey="value"
                  stroke="#06b6d4"
                  strokeWidth={2}
                  fill="url(#portfolioGradient)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Asset Allocation */}
        <div>
          <h3 className="text-sm font-medium text-slate-700 mb-3">Asset Allocation</h3>
          <div className="flex items-center space-x-4">
            <div className="w-32 h-32">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={portfolioData}
                    cx="50%"
                    cy="50%"
                    innerRadius={25}
                    outerRadius={50}
                    paddingAngle={2}
                    dataKey="value"
                  >
                    {portfolioData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="flex-1 space-y-2">
              {portfolioData.map((item) => (
                <div key={item.name} className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <div
                      className="w-3 h-3 rounded-full"
                      style={{ backgroundColor: item.color }}
                    ></div>
                    <span className="text-sm text-slate-700">{item.name}</span>
                  </div>
                  <span className="text-sm font-medium text-slate-700">
                    {formatCurrency(item.value)}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

    </div>
  );
};

export default PortfolioOverview;