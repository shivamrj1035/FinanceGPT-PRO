import React from 'react';
import { motion } from 'framer-motion';
import { ComposedChart, Bar, Line, XAxis, YAxis, CartesianGrid, ResponsiveContainer, Tooltip } from 'recharts';

interface CashFlowData {
  month: string;
  income: number;
  expenses: number;
  netFlow: number;
}

interface CashFlowChartProps {
  data: CashFlowData[];
  monthlyIncome: number;
  monthlyExpenses: number;
  netFlow: number;
}

const CashFlowChart: React.FC<CashFlowChartProps> = ({
  data,
  monthlyIncome,
  monthlyExpenses,
  netFlow
}) => {
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  };

  const customTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-3 shadow-xl">
          <p className="text-slate-200 font-medium">{`Month: ${label}`}</p>
          {payload.map((entry: any, index: number) => (
            <p key={index} className={`text-sm ${entry.dataKey === 'income' ? 'text-emerald-400' :
              entry.dataKey === 'expenses' ? 'text-red-400' : 'text-cyan-400'}`}>
              {`${entry.dataKey}: ${formatCurrency(entry.value)}`}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="bg-gradient-to-br from-white/95 via-emerald-50/20 to-green-50/30 backdrop-blur-xl rounded-2xl p-6 border border-emerald-200/40 shadow-xl shadow-emerald-100/10">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-gradient-to-r from-emerald-500/20 to-cyan-500/20 rounded-lg">
            <span className="text-emerald-400 text-2xl">💹</span>
          </div>
          <div>
            <h2 className="text-xl font-bold text-slate-800">Cash Flow Analysis</h2>
            <p className="text-sm text-slate-600">Monthly income vs expenses</p>
          </div>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <motion.div
          whileHover={{ scale: 1.02 }}
          className="bg-gradient-to-r from-emerald-500/10 to-emerald-500/5 border border-emerald-500/20 rounded-xl p-4"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-slate-600">Monthly Income</p>
              <p className="text-xl font-bold text-emerald-400">{formatCurrency(monthlyIncome)}</p>
            </div>
            <span className="text-emerald-400 text-3xl">⬆️</span>
          </div>
        </motion.div>

        <motion.div
          whileHover={{ scale: 1.02 }}
          className="bg-gradient-to-r from-red-500/10 to-red-500/5 border border-red-500/20 rounded-xl p-4"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-slate-600">Monthly Expenses</p>
              <p className="text-xl font-bold text-red-400">{formatCurrency(monthlyExpenses)}</p>
            </div>
            <span className="text-red-400 text-3xl">⬇️</span>
          </div>
        </motion.div>

        <motion.div
          whileHover={{ scale: 1.02 }}
          className={`bg-gradient-to-r ${netFlow >= 0 ? 'from-cyan-500/10 to-cyan-500/5 border-cyan-500/20' : 'from-red-500/10 to-red-500/5 border-red-500/20'} border rounded-xl p-4`}
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-slate-600">Net Flow</p>
              <p className={`text-xl font-bold ${netFlow >= 0 ? 'text-cyan-400' : 'text-red-400'}`}>
                {netFlow >= 0 ? '+' : ''}{formatCurrency(netFlow)}
              </p>
            </div>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
              netFlow >= 0 ? 'bg-cyan-400/20' : 'bg-red-400/20'
            }`}>
              <span className={`text-lg ${netFlow >= 0 ? 'text-cyan-400' : 'text-red-400'}`}>
                {netFlow >= 0 ? '⬆️' : '⬇️'}
              </span>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Chart */}
      <div className="mb-4">
        <h3 className="text-sm font-medium text-slate-300 mb-3">6-Month Trend</h3>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis
                dataKey="month"
                axisLine={false}
                tickLine={false}
                tick={{ fill: '#64748b', fontSize: 12 }}
              />
              <YAxis
                axisLine={false}
                tickLine={false}
                tick={{ fill: '#64748b', fontSize: 12 }}
                tickFormatter={(value) => `₹${(value/1000).toFixed(0)}k`}
              />
              <Tooltip content={customTooltip} />
              <Bar dataKey="income" fill="#10b981" radius={[4, 4, 0, 0]} />
              <Bar dataKey="expenses" fill="#ef4444" radius={[4, 4, 0, 0]} />
              <Line
                type="monotone"
                dataKey="netFlow"
                stroke="#06b6d4"
                strokeWidth={3}
                dot={{ fill: '#06b6d4', strokeWidth: 2, r: 4 }}
              />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Insights */}
      <div className="bg-slate-700/30 rounded-xl p-4 border border-slate-600/50">
        <div className="flex items-start space-x-3">
          <div className="p-1 bg-cyan-500/20 rounded-lg mt-0.5">
            <span className="text-cyan-400 text-base">💡</span>
          </div>
          <div>
            <h4 className="text-sm font-medium text-slate-200 mb-1">AI Insights</h4>
            <p className="text-sm text-slate-600">
              Your cash flow has been positive for the last 3 months. Consider increasing your SIP investments
              by ₹5,000 to optimize your portfolio growth.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CashFlowChart;