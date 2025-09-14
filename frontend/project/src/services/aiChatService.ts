interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp?: string;
}

interface ChatContext {
  userId: string;
  financialData?: {
    netWorth: number;
    monthlyIncome: number;
    monthlyExpenses: number;
    savingsRate: string;
    accounts?: number;
    transactions?: number;
    investments?: number;
  };
  conversationHistory?: ChatMessage[];
}

class AIChatService {
  private apiUrl = 'http://localhost:8000/api/v1';
  private abortController: AbortController | null = null;

  async sendMessage(message: string, context: ChatContext): Promise<AsyncGenerator<string>> {
    // Cancel any ongoing request
    if (this.abortController) {
      this.abortController.abort();
    }

    this.abortController = new AbortController();

    const requestBody = {
      message,
      user_id: context.userId,
      context: {
        financial_summary: context.financialData,
        conversation_history: context.conversationHistory?.slice(-5) // Last 5 messages for context
      }
    };

    try {
      const response = await fetch(`${this.apiUrl}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
        signal: this.abortController.signal,
      });

      if (!response.ok) {
        throw new Error(`Chat API error: ${response.status}`);
      }

      // If streaming is supported
      if (response.body && response.headers.get('content-type')?.includes('text/event-stream')) {
        return this.handleStreamingResponse(response);
      } else {
        // Fallback to non-streaming response
        return this.handleNonStreamingResponse(response);
      }
    } catch (error: any) {
      if (error.name === 'AbortError') {
        throw new Error('Request cancelled');
      }
      console.error('Chat API error:', error);
      // Return a fallback generator with error message
      return this.generateFallbackResponse(message, context);
    }
  }

  private async *handleStreamingResponse(response: Response): AsyncGenerator<string> {
    const reader = response.body!.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            if (data === '[DONE]') {
              return;
            }
            try {
              const parsed = JSON.parse(data);
              if (parsed.content) {
                yield parsed.content;
              }
            } catch (e) {
              console.error('Error parsing SSE data:', e);
            }
          }
        }
      }
    } finally {
      reader.releaseLock();
    }
  }

  private async *handleNonStreamingResponse(response: Response): AsyncGenerator<string> {
    const data = await response.json();
    const message = data.response || data.message || 'I understand your question. Let me analyze your financial data...';

    // Extract MCP tools information if available
    const mcpTools = data.mcp_tools_used || [];
    const toolInsights = data.tool_insights || null;
    const detectedIntents = data.detected_intents || [];

    // Yield special metadata first if MCP tools were used
    if (mcpTools.length > 0) {
      yield `[MCP_TOOLS_START]${JSON.stringify({
        tools: mcpTools,
        insights: toolInsights,
        intents: detectedIntents
      })}[MCP_TOOLS_END]`;
    }

    // Simulate streaming for non-streaming responses
    const words = message.split(' ');
    for (let i = 0; i < words.length; i++) {
      yield words[i] + (i < words.length - 1 ? ' ' : '');
      await new Promise(resolve => setTimeout(resolve, 30)); // Small delay for effect
    }
  }

  private async *generateFallbackResponse(message: string, context: ChatContext): AsyncGenerator<string> {
    const lowerMessage = message.toLowerCase();
    let response = '';

    if (!context.financialData) {
      response = "I'm having trouble accessing your financial data at the moment. Please try again in a few seconds.";
    } else {
      const { netWorth, monthlyIncome, monthlyExpenses, savingsRate } = context.financialData;

      if (lowerMessage.includes('saving') || lowerMessage.includes('save')) {
        response = `Based on your current financial profile, you're saving ₹${(monthlyIncome - monthlyExpenses).toLocaleString('en-IN')} per month, which is ${savingsRate}% of your income. This is excellent! To optimize further, consider automating transfers to a high-yield savings account or starting a SIP for long-term wealth building.`;
      } else if (lowerMessage.includes('expense') || lowerMessage.includes('spending')) {
        response = `Your monthly expenses are ₹${monthlyExpenses.toLocaleString('en-IN')}. With your income of ₹${monthlyIncome.toLocaleString('en-IN')}, you're maintaining a healthy ${savingsRate}% savings rate. I can help you identify areas to optimize your spending if you'd like.`;
      } else if (lowerMessage.includes('invest')) {
        response = `With your current savings of ₹${(monthlyIncome - monthlyExpenses).toLocaleString('en-IN')} per month, here's what I recommend:\n\n1. Emergency Fund: Ensure 6 months of expenses (₹${(monthlyExpenses * 6).toLocaleString('en-IN')})\n2. SIP in Index Funds: Start with ₹30,000/month\n3. PPF for Tax Benefits: ₹12,500/month\n4. Consider a 60:40 equity-debt ratio based on your profile`;
      } else if (lowerMessage.includes('net worth') || lowerMessage.includes('wealth')) {
        response = `Your current net worth is ₹${netWorth.toLocaleString('en-IN')}. You're doing great! With your ${savingsRate}% savings rate, you're on track to grow your wealth significantly. Would you like me to project your net worth growth over the next 5 years?`;
      } else if (lowerMessage.includes('goal') || lowerMessage.includes('target')) {
        response = `Let's set some financial goals! Based on your profile:\n\n• Short-term (1 year): Build emergency fund to ₹${(monthlyExpenses * 6).toLocaleString('en-IN')}\n• Medium-term (3 years): Grow net worth to ₹${(netWorth * 1.5).toLocaleString('en-IN')}\n• Long-term (5 years): Achieve financial independence with ₹${(netWorth * 2.5).toLocaleString('en-IN')}\n\nWhich goal would you like to focus on first?`;
      } else if (lowerMessage.includes('budget')) {
        response = `Here's a recommended budget based on your ₹${monthlyIncome.toLocaleString('en-IN')} monthly income:\n\n• Essentials (50%): ₹${(monthlyIncome * 0.5).toLocaleString('en-IN')}\n• Savings & Investments (30%): ₹${(monthlyIncome * 0.3).toLocaleString('en-IN')}\n• Lifestyle (20%): ₹${(monthlyIncome * 0.2).toLocaleString('en-IN')}\n\nYou're currently saving ${savingsRate}%, which is fantastic!`;
      } else {
        response = `I'm here to help with your finances! You have a net worth of ₹${netWorth.toLocaleString('en-IN')} and save ${savingsRate}% of your income. What specific aspect of your finances would you like to explore - budgeting, investments, savings goals, or expense optimization?`;
      }
    }

    // Simulate streaming
    const words = response.split(' ');
    for (let i = 0; i < words.length; i++) {
      yield words[i] + (i < words.length - 1 ? ' ' : '');
      await new Promise(resolve => setTimeout(resolve, 20));
    }
  }

  cancelRequest(): void {
    if (this.abortController) {
      this.abortController.abort();
      this.abortController = null;
    }
  }

  async saveConversation(userId: string, messages: ChatMessage[]): Promise<void> {
    try {
      await fetch(`${this.apiUrl}/chat/history`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: userId,
          messages,
          timestamp: new Date().toISOString()
        })
      });
    } catch (error) {
      console.error('Failed to save conversation:', error);
    }
  }

  async loadConversationHistory(userId: string): Promise<ChatMessage[]> {
    try {
      const response = await fetch(`${this.apiUrl}/chat/history/${userId}`);
      if (response.ok) {
        const data = await response.json();
        return data.messages || [];
      }
    } catch (error) {
      console.error('Failed to load conversation history:', error);
    }
    return [];
  }
}

export const aiChatService = new AIChatService();
export type { ChatMessage, ChatContext };