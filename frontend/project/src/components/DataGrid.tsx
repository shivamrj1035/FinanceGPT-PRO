import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import DataCard from './DataCard';
import { apiService, User, Account, Transaction, Investment } from '../services/apiService';

interface DataGridProps {
  permissions: Record<string, boolean>;
  currentUser?: { user_id: string; email: string } | null;
}

const DataGrid: React.FC<DataGridProps> = ({ permissions, currentUser }) => {
  const [userData, setUserData] = useState<User | null>(null);
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [investments, setInvestments] = useState<Investment[]>([]);
  const [creditScore, setCreditScore] = useState<{ score: number }>({ score: 750 });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      if (!currentUser) {
        setLoading(false);
        return;
      }

      try {
        setLoading(true);

        // Fetch all data in parallel
        const [userRes, accountsRes, transactionsRes, investmentsRes, creditRes] = await Promise.allSettled([
          apiService.getUser(currentUser.user_id),
          apiService.getAccounts(currentUser.user_id),
          apiService.getTransactions(currentUser.user_id),
          apiService.getInvestments(currentUser.user_id),
          apiService.getCreditScore(currentUser.user_id)
        ]);

        if (userRes.status === 'fulfilled') setUserData(userRes.value);
        if (accountsRes.status === 'fulfilled') setAccounts(accountsRes.value);
        if (transactionsRes.status === 'fulfilled') setTransactions(transactionsRes.value);
        if (investmentsRes.status === 'fulfilled') setInvestments(investmentsRes.value);
        if (creditRes.status === 'fulfilled') setCreditScore(creditRes.value);

      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [currentUser]);

  // Transform data to match DataCard expectations
  // Calculate meaningful financial metrics
  const calculateNetWorth = () => {
    const totalAssets = accounts.reduce((sum, account) => sum + account.balance, 0);
    const totalLiabilities = 525000; // Mock debt data
    return totalAssets - totalLiabilities;
  };

  const calculateMonthlyFlow = () => {
    const recentTransactions = transactions.slice(0, 30); // Last 30 transactions
    const income = recentTransactions
      .filter(t => t.amount > 0)
      .reduce((sum, t) => sum + t.amount, 0);
    const expenses = recentTransactions
      .filter(t => t.amount < 0)
      .reduce((sum, t) => sum + Math.abs(t.amount), 0);
    return { income, expenses, netFlow: income - expenses };
  };

  const calculateInvestmentPerformance = () => {
    const totalInvested = investments.reduce((sum, inv) => sum + (inv.invested_amount || inv.current_value * 0.8), 0);
    const currentValue = investments.reduce((sum, inv) => sum + inv.current_value, 0);
    const returns = currentValue - totalInvested;
    const returnsPct = totalInvested > 0 ? (returns / totalInvested) * 100 : 0;
    return { totalInvested, currentValue, returns, returnsPct };
  };

  const formatRecentTransactions = () => {
    return transactions.slice(0, 5).map(t => ({
      ...t,
      isFraud: t.amount < -10000 || t.description?.includes('Suspicious')
    }));
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="text-center">
          <h2 className="text-2xl font-semibold text-white mb-2">
            Loading your financial data...
          </h2>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-semibold text-white mb-2">
          Hi {userData?.name || currentUser?.email?.split('@')[0] || 'there'}, let's get a clear view of your finances.
        </h2>
      </div>

      {/* Financial Overview - 4 Key Metrics in 2x2 Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <AnimatePresence mode="wait">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            transition={{ duration: 0.3 }}
          >
            <DataCard
              title="Net Worth"
              permission="networth"
              isGranted={true} // Always show for demo
              data={{ value: calculateNetWorth(), change: '+₹45,000 this month' }}
              type="networth"
            />
          </motion.div>

          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            transition={{ duration: 0.3, delay: 0.1 }}
          >
            <DataCard
              title="Monthly Cash Flow"
              permission="cashflow"
              isGranted={true}
              data={calculateMonthlyFlow()}
              type="cashflow"
            />
          </motion.div>

          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            transition={{ duration: 0.3, delay: 0.2 }}
          >
            <DataCard
              title="Investment Performance"
              permission="investments"
              isGranted={true}
              data={calculateInvestmentPerformance()}
              type="investment_performance"
            />
          </motion.div>

          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            transition={{ duration: 0.3, delay: 0.3 }}
          >
            <DataCard
              title="Recent Transactions"
              permission="transactions"
              isGranted={permissions.transactions}
              data={formatRecentTransactions()}
              type="recent_transactions"
            />
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  );
};

export default DataGrid;