import React from 'react';
import { FiLock, FiDollarSign, FiCreditCard, FiTrendingUp, FiShield, FiStar, FiActivity } from 'react-icons/fi';
import { AreaChart, Area, XAxis, YAxis, ResponsiveContainer, PieChart, Pie, Cell, BarChart, Bar, RadialBarChart, RadialBar } from 'recharts';

interface DataCardProps {
  title: string;
  permission: string;
  isGranted: boolean;
  data: any;
  type: 'assets' | 'liabilities' | 'transactions' | 'investments' | 'epfBalance' | 'creditScore';
}

const DataCard: React.FC<DataCardProps> = ({ title, permission, isGranted, data, type }) => {
  const COLORS = ['#00D1B2', '#8A2BE2', '#FF6B6B', '#4ECDC4'];

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 0
    }).format(amount);
  };

  const getIcon = () => {
    switch (type) {
      case 'assets': return <FiDollarSign className="text-[#00D1B2]" />;
      case 'liabilities': return <FiCreditCard className="text-[#FF6B6B]" />;
      case 'investments': return <FiTrendingUp className="text-[#8A2BE2]" />;
      case 'epfBalance': return <FiShield className="text-[#FFD700]" />;
      case 'creditScore': return <FiStar className="text-[#FFA500]" />;
      case 'transactions': return <FiActivity className="text-[#00D1B2]" />;
      case 'networth': return <FiDollarSign className="text-[#00D1B2]" />;
      case 'cashflow': return <FiActivity className="text-[#8A2BE2]" />;
      case 'investment_performance': return <FiTrendingUp className="text-[#00FF00]" />;
      case 'recent_transactions': return <FiActivity className="text-[#FFA500]" />;
      default: return <FiDollarSign className="text-[#00D1B2]" />;
    }
  };

  const renderContent = () => {
    if (!isGranted) {
      return (
        <div className="flex flex-col items-center justify-center py-8 text-center">
          <FiLock className="text-4xl text-[#A0AEC0] mb-4" />
          <p className="text-[#A0AEC0]">
            Grant '{permission.charAt(0).toUpperCase() + permission.slice(1)}' permission to unlock this insight.
          </p>
        </div>
      );
    }

    switch (type) {
      case 'assets':
        const currentBalance = data.balanceHistory[data.balanceHistory.length - 1]?.balance || 0;
        return (
          <div>
            <div className="flex items-center justify-between mb-4">
              <div>
                <p className="text-2xl font-bold text-white">{formatCurrency(currentBalance)}</p>
                <p className="text-[#A0AEC0] text-sm">Current Balance</p>
              </div>
            </div>
            <div className="h-32">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={data.balanceHistory}>
                  <defs>
                    <linearGradient id="colorBalance" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#00D1B2" stopOpacity={0.8}/>
                      <stop offset="95%" stopColor="#00D1B2" stopOpacity={0.1}/>
                    </linearGradient>
                  </defs>
                  <Area 
                    type="monotone" 
                    dataKey="balance" 
                    stroke="#00D1B2" 
                    strokeWidth={2}
                    fillOpacity={1} 
                    fill="url(#colorBalance)" 
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>
        );

      case 'liabilities':
        const totalDebt = data.breakdown.reduce((sum: number, item: any) => sum + item.value, 0);
        return (
          <div>
            <div className="flex items-center justify-between mb-4">
              <div>
                <p className="text-2xl font-bold text-white">{formatCurrency(totalDebt)}</p>
                <p className="text-[#A0AEC0] text-sm">Total Debt</p>
              </div>
            </div>
            <div className="h-32">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={data.breakdown}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {data.breakdown.map((entry: any, index: number) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="mt-2 space-y-1">
              {data.breakdown.map((item: any, index: number) => (
                <div key={item.name} className="flex items-center text-xs">
                  <div className="flex items-center">
                    <div 
                      className="w-2 h-2 rounded-full mr-2"
                      style={{ backgroundColor: COLORS[index % COLORS.length] }}
                    />
                    <span className="text-[#A0AEC0]">{item.name}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        );

      case 'investments':
        const investmentBreakdown = [
          { name: 'Mutual Funds', value: 180000 },
          { name: 'Stocks', value: 140000 },
          { name: 'Bonds', value: 80000 },
          { name: 'Gold', value: 100000 }
        ];
        return (
          <div>
            <div className="flex items-center justify-between mb-4">
              <div>
                <p className="text-2xl font-bold text-white">{formatCurrency(data.totalValue)}</p>
                <p className="text-[#A0AEC0] text-sm">Portfolio Value</p>
              </div>
            </div>
            <div className="space-y-2">
              {investmentBreakdown.map((item, index) => (
                <div key={item.name} className="flex items-center justify-between">
                  <span className="text-[#A0AEC0] text-sm">{item.name}</span>
                  <span className="text-white font-medium text-sm">{formatCurrency(item.value)}</span>
                </div>
              ))}
            </div>
          </div>
        );

      case 'epfBalance':
        return (
          <div>
            <div className="flex items-center justify-between mb-4">
              <div>
                <p className="text-2xl font-bold text-white">{formatCurrency(data.totalValue)}</p>
                <p className="text-[#A0AEC0] text-sm">Total EPF Balance</p>
              </div>
            </div>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-[#A0AEC0] text-sm">Employee Contribution</span>
                <span className="text-white font-medium text-sm">{formatCurrency(425000)}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-[#A0AEC0] text-sm">Employer Contribution</span>
                <span className="text-white font-medium text-sm">{formatCurrency(425000)}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-[#A0AEC0] text-sm">Interest Earned</span>
                <span className="text-[#00D1B2] font-medium text-sm">8.15% p.a.</span>
              </div>
            </div>
          </div>
        );

      case 'creditScore':
        const scoreData = [{ name: 'Score', value: data.score, fill: '#00D1B2' }];
        return (
          <div>
            <div className="flex items-center justify-between mb-4">
              <div>
                <p className="text-2xl font-bold text-white">{data.score}</p>
                <p className="text-[#A0AEC0] text-sm">Credit Score</p>
              </div>
            </div>
            <div className="h-20">
              <ResponsiveContainer width="100%" height="100%">
                <RadialBarChart cx="50%" cy="50%" innerRadius="60%" outerRadius="90%" data={scoreData}>
                  <RadialBar dataKey="value" cornerRadius={10} fill="#00D1B2" />
                </RadialBarChart>
              </ResponsiveContainer>
            </div>
            <div className="mt-2">
              <div className="flex items-center justify-between">
                <span className="text-[#A0AEC0] text-sm">Rating</span>
                <span className="text-[#00D1B2] font-medium text-sm">Excellent</span>
              </div>
            </div>
          </div>
        );

      case 'transactions':
        return (
          <div>
            <div className="mb-4">
              <p className="text-lg font-bold text-white">Recent Transactions</p>
            </div>
            <div className="space-y-2 max-h-40 overflow-y-auto custom-scrollbar">
              {data.slice(0, 6).map((transaction: any) => (
                <div key={transaction.id} className="flex items-center justify-between py-1">
                  <div className="flex-1">
                    <p className="text-white text-xs font-medium">{transaction.description}</p>
                    <p className="text-[#A0AEC0] text-xs">{transaction.category}</p>
                  </div>
                  <span className={`font-medium text-xs ${
                    transaction.type === 'income' ? 'text-[#00D1B2]' : 'text-[#A0AEC0]'
                  }`}>
                    {transaction.type === 'income' ? '+' : '-'}₹{(transaction.amount/1000).toFixed(0)}k
                  </span>
                </div>
              ))}
            </div>
          </div>
        );

      case 'networth':
        return (
          <div>
            <div className="flex items-center justify-between mb-4">
              <div>
                <p className="text-2xl font-bold text-white">{formatCurrency(data.value)}</p>
                <p className="text-[#A0AEC0] text-sm">Total Net Worth</p>
              </div>
            </div>
            <div className="mt-4">
              <p className="text-[#00D1B2] text-sm font-medium">{data.change}</p>
            </div>
          </div>
        );

      case 'cashflow':
        return (
          <div>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-[#A0AEC0] text-sm">Monthly Income</span>
                <span className="text-[#00D1B2] font-bold">{formatCurrency(data.income)}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-[#A0AEC0] text-sm">Monthly Expenses</span>
                <span className="text-[#FF6B6B] font-bold">-{formatCurrency(data.expenses)}</span>
              </div>
              <div className="border-t border-[#00D1B2]/20 pt-3">
                <div className="flex items-center justify-between">
                  <span className="text-white font-medium">Net Flow</span>
                  <span className={`font-bold ${data.netFlow >= 0 ? 'text-[#00D1B2]' : 'text-[#FF6B6B]'}`}>
                    {data.netFlow >= 0 ? '+' : ''}{formatCurrency(data.netFlow)}
                  </span>
                </div>
              </div>
            </div>
          </div>
        );

      case 'investment_performance':
        return (
          <div>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-[#A0AEC0] text-sm">Total Invested</span>
                <span className="text-white font-medium">{formatCurrency(data.totalInvested)}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-[#A0AEC0] text-sm">Current Value</span>
                <span className="text-white font-bold">{formatCurrency(data.currentValue)}</span>
              </div>
              <div className="border-t border-[#8A2BE2]/20 pt-3">
                <div className="flex items-center justify-between">
                  <span className="text-white font-medium">Returns</span>
                  <div className="text-right">
                    <div className="text-[#00FF00] font-bold">+{formatCurrency(data.returns)}</div>
                    <div className="text-[#00FF00] text-sm">+{data.returnsPct.toFixed(1)}%</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        );

      case 'recent_transactions':
        return (
          <div>
            <div className="mb-4">
              <p className="text-lg font-bold text-white">Latest Activity</p>
            </div>
            <div className="space-y-2 max-h-40 overflow-y-auto custom-scrollbar">
              {data.map((transaction: any) => (
                <div key={transaction.id} className="flex items-center justify-between py-1">
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <p className="text-white text-xs font-medium">{transaction.description}</p>
                      {transaction.isFraud && <span className="text-[#FF6B6B] text-xs">🚨</span>}
                    </div>
                    <p className="text-[#A0AEC0] text-xs">{transaction.category}</p>
                  </div>
                  <span className={`font-medium text-xs ${
                    transaction.amount > 0 ? 'text-[#00D1B2]' : transaction.isFraud ? 'text-[#FF6B6B]' : 'text-[#A0AEC0]'
                  }`}>
                    {transaction.amount > 0 ? '+' : '-'}₹{Math.abs(transaction.amount/1000).toFixed(0)}k
                  </span>
                </div>
              ))}
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="bg-[#10182F] backdrop-blur-sm rounded-2xl p-4 border border-[#00D1B2]/20 h-64">
      <div className="flex items-center mb-4">
        {getIcon()}
        <h2 className="text-lg font-semibold text-white ml-2">{title}</h2>
      </div>
      {renderContent()}
    </div>
  );
};

export default DataCard;