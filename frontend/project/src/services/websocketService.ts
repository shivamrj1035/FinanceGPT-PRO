export interface KPIUpdate {
  type: 'portfolio' | 'accounts' | 'transactions' | 'credit' | 'market';
  data: any;
  timestamp: string;
  user_id: string;
}

export interface PortfolioKPI {
  totalValue: number;
  change: number;
  changePercent: number;
  cashBalance: number;
  investmentValue: number;
  riskScore: number;
}

export interface AccountKPI {
  totalBalance: number;
  monthlyIncome: number;
  monthlyExpenses: number;
  netFlow: number;
  accountCount: number;
  highValueTransactionAlert: boolean;
}

export interface MarketKPI {
  marketStatus: 'open' | 'closed' | 'pre-market' | 'after-hours';
  nifty50: number;
  sensex: number;
  usdInr: number;
  goldPrice: number;
  lastUpdated: string;
}

class WebSocketService {
  private ws: WebSocket | null = null;
  private url: string;
  private userId: string | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private listeners: Map<string, Set<(data: any) => void>> = new Map();
  private isConnecting = false;

  constructor() {
    this.url = 'ws://localhost:9001';
  }

  connect(userId: string): Promise<void> {
    if (this.isConnecting || (this.ws && this.ws.readyState === WebSocket.CONNECTING)) {
      return Promise.resolve();
    }

    if (this.ws && this.ws.readyState === WebSocket.OPEN && this.userId === userId) {
      return Promise.resolve();
    }

    this.userId = userId;
    this.isConnecting = true;

    return new Promise((resolve, reject) => {
      try {
        // Close existing connection if any
        if (this.ws) {
          this.ws.close();
        }

        this.ws = new WebSocket(`${this.url}/ws/${userId}`);

        this.ws.onopen = () => {
          console.log('✅ WebSocket connected for user:', userId);
          this.isConnecting = false;
          this.reconnectAttempts = 0;
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const update: KPIUpdate = JSON.parse(event.data);
            this.notifyListeners(update.type, update);
          } catch (error) {
            console.error('Error parsing WebSocket message:', error);
          }
        };

        this.ws.onclose = (event) => {
          console.log('📡 WebSocket disconnected:', event.code, event.reason);
          this.isConnecting = false;

          if (event.code !== 1000 && this.reconnectAttempts < this.maxReconnectAttempts) {
            setTimeout(() => {
              this.reconnectAttempts++;
              console.log(`🔄 Reconnecting... Attempt ${this.reconnectAttempts}`);
              this.connect(userId);
            }, this.reconnectDelay * this.reconnectAttempts);
          }
        };

        this.ws.onerror = (error) => {
          console.error('❌ WebSocket error:', error);
          this.isConnecting = false;
          reject(error);
        };

        // Connection timeout
        setTimeout(() => {
          if (this.isConnecting) {
            this.isConnecting = false;
            reject(new Error('WebSocket connection timeout'));
          }
        }, 5000);

      } catch (error) {
        this.isConnecting = false;
        reject(error);
      }
    });
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close(1000, 'Client disconnect');
      this.ws = null;
    }
    this.userId = null;
    this.listeners.clear();
  }

  subscribe(eventType: string, callback: (data: any) => void): () => void {
    if (!this.listeners.has(eventType)) {
      this.listeners.set(eventType, new Set());
    }
    this.listeners.get(eventType)!.add(callback);

    // Return unsubscribe function
    return () => {
      const listeners = this.listeners.get(eventType);
      if (listeners) {
        listeners.delete(callback);
        if (listeners.size === 0) {
          this.listeners.delete(eventType);
        }
      }
    };
  }

  private notifyListeners(eventType: string, data: any): void {
    const listeners = this.listeners.get(eventType);
    if (listeners) {
      listeners.forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error('Error in WebSocket listener:', error);
        }
      });
    }
  }

  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  getConnectionState(): 'connecting' | 'open' | 'closing' | 'closed' {
    if (!this.ws) return 'closed';

    switch (this.ws.readyState) {
      case WebSocket.CONNECTING: return 'connecting';
      case WebSocket.OPEN: return 'open';
      case WebSocket.CLOSING: return 'closing';
      case WebSocket.CLOSED: return 'closed';
      default: return 'closed';
    }
  }

  // Send a heartbeat to keep connection alive
  sendHeartbeat(): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type: 'heartbeat', timestamp: new Date().toISOString() }));
    }
  }

  // Request specific data updates
  requestUpdate(type: 'portfolio' | 'accounts' | 'transactions' | 'market'): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'request_update',
        target: type,
        timestamp: new Date().toISOString()
      }));
    }
  }
}

// Export singleton instance
export const websocketService = new WebSocketService();

// Export types
export type { KPIUpdate, PortfolioKPI, AccountKPI, MarketKPI };
export default websocketService;