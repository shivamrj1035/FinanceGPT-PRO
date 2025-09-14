const API_BASE_URL = 'http://localhost:8000';

export interface User {
  user_id: string;
  email: string;
  name: string;
}

export interface Transaction {
  id: number;
  date: string;
  description: string;
  category: string;
  amount: number;
  type: 'income' | 'expense';
}

export interface Account {
  id: number;
  bank_name: string;
  account_type: string;
  balance: number;
}

export interface Investment {
  id: number;
  name: string;
  type: string;
  current_value: number;
}

export interface ApiService {
  getUser: (userId: string) => Promise<User>;
  getAccounts: (userId: string) => Promise<Account[]>;
  getTransactions: (userId: string) => Promise<Transaction[]>;
  getInvestments: (userId: string) => Promise<Investment[]>;
  getCreditScore: (userId: string) => Promise<{ score: number }>;
}

class FinanceApiService implements ApiService {
  async getUser(userId: string): Promise<User> {
    const response = await fetch(`${API_BASE_URL}/api/v1/users/${userId}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch user: ${response.status}`);
    }
    const data = await response.json();
    return data.success ? data.user : null;
  }

  async getAccounts(userId: string): Promise<Account[]> {
    const response = await fetch(`${API_BASE_URL}/api/v1/accounts?user_id=${userId}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch accounts: ${response.status}`);
    }
    const data = await response.json();
    return data.accounts || [];
  }

  async getTransactions(userId: string): Promise<Transaction[]> {
    const response = await fetch(`${API_BASE_URL}/api/v1/transactions?user_id=${userId}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch transactions: ${response.status}`);
    }
    const data = await response.json();
    return data.transactions || [];
  }

  async getInvestments(userId: string): Promise<Investment[]> {
    const response = await fetch(`${API_BASE_URL}/api/v1/investments?user_id=${userId}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch investments: ${response.status}`);
    }
    const data = await response.json();
    return data.investments || [];
  }

  async getCreditScore(userId: string): Promise<{ score: number }> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/users/${userId}/credit-score`);
      if (!response.ok) {
        // Return a default score if API fails
        return { score: 750 };
      }
      const data = await response.json();
      return data.success ? { score: data.credit_score } : { score: 750 };
    } catch (error) {
      // Return a default score if API fails
      return { score: 750 };
    }
  }

  async checkFraud(transaction: any, userId: string): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/api/v1/fraud/check`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        transaction: {
          ...transaction,
          user_id: userId
        }
      })
    });

    if (!response.ok) {
      throw new Error(`Fraud check failed: ${response.status}`);
    }

    const data = await response.json();
    return data;
  }

  async getAiStats(userId: string): Promise<any> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/ai/stats/${userId}`);
      if (!response.ok) {
        return null;
      }
      const data = await response.json();
      return data.success ? data.stats : null;
    } catch (error) {
      return null;
    }
  }
}

export const apiService = new FinanceApiService();