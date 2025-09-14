import React, { useState, useEffect, useCallback, memo } from 'react';
import { KPICard, MetricCard } from './ui';

interface LiveKPIDashboardProps {
  currentUser?: { user_id: string; email: string; name?: string } | null;
  className?: string;
}

const LiveKPIDashboard: React.FC<LiveKPIDashboardProps> = memo(({
  currentUser,
  className = ''
}) => {
  // Essential KPIs only
  const [portfolioValue, setPortfolioValue] = useState(1136351);
  const [monthlyIncome, setMonthlyIncome] = useState(125000);
  const [monthlyExpenses, setMonthlyExpenses] = useState(89500);
  const [netWorth, setNetWorth] = useState(1136351);

  // Format currency with memoization
  const formatCurrency = useCallback((value: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value);
  }, []);

  // Calculate derived values
  const netFlow = monthlyIncome - monthlyExpenses;
  const savingsRate = ((netFlow / monthlyIncome) * 100).toFixed(1);

  return (
    <div className={`${className}`}>
      {/* Simplified header without animations */}
      <div className="mb-6">
        <h2 className="text-xl font-bold text-slate-800">
          Financial Overview
        </h2>
      </div>

      {/* Essential KPIs only - 4 cards in a single row */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl p-4 border border-gray-200 shadow-sm">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-600">Net Worth</span>
            <span className="text-lg">💰</span>
          </div>
          <div className="text-2xl font-bold text-gray-800">
            {formatCurrency(netWorth)}
          </div>
          <div className="text-xs text-green-600 mt-1">
            +12.7% this month
          </div>
        </div>

        <div className="bg-white rounded-xl p-4 border border-gray-200 shadow-sm">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-600">Monthly Income</span>
            <span className="text-lg">📊</span>
          </div>
          <div className="text-2xl font-bold text-gray-800">
            {formatCurrency(monthlyIncome)}
          </div>
          <div className="text-xs text-gray-500 mt-1">
            Regular income
          </div>
        </div>

        <div className="bg-white rounded-xl p-4 border border-gray-200 shadow-sm">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-600">Monthly Expenses</span>
            <span className="text-lg">💳</span>
          </div>
          <div className="text-2xl font-bold text-gray-800">
            {formatCurrency(monthlyExpenses)}
          </div>
          <div className="text-xs text-green-600 mt-1">
            -3.2% vs last month
          </div>
        </div>

        <div className="bg-white rounded-xl p-4 border border-gray-200 shadow-sm">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-600">Savings Rate</span>
            <span className="text-lg">🎯</span>
          </div>
          <div className="text-2xl font-bold text-gray-800">
            {savingsRate}%
          </div>
          <div className="text-xs text-gray-500 mt-1">
            {formatCurrency(netFlow)}/month
          </div>
        </div>
      </div>
    </div>
  );
});

LiveKPIDashboard.displayName = 'LiveKPIDashboard';

export default LiveKPIDashboard;