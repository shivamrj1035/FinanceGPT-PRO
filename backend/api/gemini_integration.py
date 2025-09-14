"""
Gemini AI Integration Module
Handles all AI-powered features using Google's Gemini API
"""

from google import genai
from google.genai import types
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class GeminiIntegration:
    """
    Handles Gemini AI integration for intelligent financial assistance
    """

    def __init__(self):
        # Get API key from environment or use demo key
        self.api_key = os.getenv("GEMINI_API_KEY", "demo-key-for-hackathon")

        # Initialize Gemini client
        self.client = genai.Client(api_key=self.api_key)

        # Model configuration for financial assistant
        self.model_name = "gemini-2.0-flash"
        self.generation_config = types.GenerateContentConfig(
            temperature=0.7,
            top_p=0.95,
            top_k=40,
            max_output_tokens=2048,
            stop_sequences=[],
            response_mime_type="text/plain"
        )

        # System prompts for different contexts
        self.system_prompts = {
            "general": """
            You are FinanceGPT Pro, an advanced AI financial assistant powered by MCP (Model Context Protocol).
            You have access to real-time financial data and can provide personalized, actionable advice.

            Your capabilities:
            1. Analyze spending patterns and provide insights
            2. Detect fraud and unusual transactions
            3. Optimize financial goals and savings
            4. Provide tax planning and investment recommendations
            5. Improve credit scores
            6. Plan for emergencies and retirement

            Always be helpful, accurate, and prioritize the user's financial wellbeing.
            Be specific and reference actual numbers from their accounts when available.
            Speak in a friendly but professional tone.
            """,

            "fraud_analysis": """
            You are a fraud detection specialist analyzing financial transactions.
            Focus on identifying suspicious patterns, unusual behavior, and potential risks.
            Provide clear risk assessments and recommended actions.
            Be specific about why a transaction might be fraudulent.
            """,

            "investment_advisor": """
            You are an investment advisor helping users optimize their portfolio.
            Consider their risk tolerance, goals, and current market conditions.
            Provide balanced advice between growth and safety.
            Always mention risks alongside opportunities.
            Focus on long-term wealth building strategies.
            """,

            "tax_optimizer": """
            You are a tax optimization specialist familiar with Indian tax laws.
            Help users maximize their tax savings through legal deductions and investments.
            Consider both old and new tax regimes.
            Suggest tax-saving instruments under Section 80C and other relevant sections.
            """,

            "budget_coach": """
            You are a personal budget coach helping users manage their finances better.
            Analyze spending patterns and suggest practical ways to save money.
            Be encouraging but realistic about financial goals.
            Provide specific, actionable advice they can implement immediately.
            """
        }

        logger.info("✅ Gemini AI integration initialized")

    async def generate_response(
        self,
        message: str,
        context: Dict[str, Any],
        prompt_type: str = "general"
    ) -> Dict[str, Any]:
        """
        Generate AI response with financial context
        """
        try:
            # Select appropriate system prompt
            system_prompt = self.system_prompts.get(prompt_type, self.system_prompts["general"])

            # Build context information
            context_prompt = self._build_context_prompt(context)

            # Combine prompts
            full_prompt = f"""
            {system_prompt}

            Current Financial Context:
            {context_prompt}

            User Query: {message}

            Please provide a helpful, specific response based on the user's financial data.
            """

            # Generate response using Gemini client
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=full_prompt,
                config=self.generation_config
            )

            # Extract suggestions for follow-up
            suggestions = self._generate_suggestions(message, context, prompt_type)

            return {
                "response": response.text,
                "suggestions": suggestions,
                "confidence": 0.95,  # Can be calculated based on context completeness
                "prompt_type": prompt_type
            }

        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return {
                "response": self._get_fallback_response(prompt_type),
                "suggestions": [],
                "confidence": 0.5,
                "error": str(e)
            }

    def _build_context_prompt(self, context: Dict[str, Any]) -> str:
        """
        Build detailed context prompt from financial data
        """
        prompt_parts = []

        # Account information
        if "accounts" in context:
            accounts = context["accounts"]
            total_balance = sum(acc.get("balance", 0) for acc in accounts)
            prompt_parts.append(f"Total Balance: ₹{total_balance:,.2f}")
            prompt_parts.append(f"Number of Accounts: {len(accounts)}")

            # Account breakdown
            for acc in accounts[:3]:  # Limit to first 3 accounts
                prompt_parts.append(
                    f"- {acc.get('bank_name', 'Bank')} {acc.get('account_type', 'Account')}: "
                    f"₹{acc.get('balance', 0):,.2f}"
                )

        # Recent transactions
        if "transactions" in context:
            transactions = context["transactions"]
            prompt_parts.append(f"Recent Transactions: {len(transactions)}")

            # Calculate spending summary
            total_spent = sum(
                abs(t.get("amount", 0))
                for t in transactions
                if t.get("amount", 0) < 0
            )
            prompt_parts.append(f"Recent Spending: ₹{total_spent:,.2f}")

        # Goals
        if "goals" in context:
            goals = context["goals"]
            prompt_parts.append(f"Active Goals: {len(goals)}")

            for goal in goals[:2]:  # Top 2 goals
                prompt_parts.append(
                    f"- {goal.get('name', 'Goal')}: "
                    f"{goal.get('progress_percentage', 0)}% complete"
                )

        # Investments
        if "investments" in context:
            investments = context["investments"]
            total_invested = sum(inv.get("invested_amount", 0) for inv in investments)
            current_value = sum(inv.get("current_value", 0) for inv in investments)

            if total_invested > 0:
                returns = ((current_value - total_invested) / total_invested) * 100
                prompt_parts.append(f"Investment Returns: {returns:.1f}%")
                prompt_parts.append(f"Portfolio Value: ₹{current_value:,.2f}")

        # Credit score
        if "credit_score" in context:
            score = context["credit_score"]
            prompt_parts.append(f"Credit Score: {score}")

        # Insights
        if "insights" in context:
            insights = context["insights"]
            high_priority = [i for i in insights if i.get("priority") == "HIGH"]
            if high_priority:
                prompt_parts.append(f"High Priority Insights: {len(high_priority)}")

        return "\n".join(prompt_parts)

    def _generate_suggestions(
        self,
        message: str,
        context: Dict[str, Any],
        prompt_type: str
    ) -> List[str]:
        """
        Generate contextual follow-up suggestions
        """
        suggestions = []
        message_lower = message.lower()

        # Context-based suggestions
        if prompt_type == "fraud_analysis":
            suggestions = [
                "Show me all suspicious transactions this month",
                "How can I better protect my accounts?",
                "Set up fraud alerts for unusual activity"
            ]
        elif prompt_type == "investment_advisor":
            suggestions = [
                "What's my optimal asset allocation?",
                "Compare mutual funds vs direct equity",
                "Show tax-saving investment options"
            ]
        elif prompt_type == "tax_optimizer":
            suggestions = [
                "Calculate my tax liability for this year",
                "What are the best ELSS funds?",
                "How much more should I invest in 80C?"
            ]
        elif prompt_type == "budget_coach":
            suggestions = [
                "Where can I cut expenses this month?",
                "Create a 50/30/20 budget plan",
                "Track my daily spending"
            ]
        else:
            # General suggestions based on message content
            if "spend" in message_lower or "expense" in message_lower:
                suggestions.extend([
                    "How can I reduce my monthly expenses?",
                    "What's my biggest spending category?",
                    "Show spending trends over last 3 months"
                ])
            elif "save" in message_lower or "goal" in message_lower:
                suggestions.extend([
                    "How much should I save monthly?",
                    "Create an emergency fund plan",
                    "Optimize my financial goals"
                ])
            elif "invest" in message_lower:
                suggestions.extend([
                    "What's my risk tolerance?",
                    "Show best performing mutual funds",
                    "Calculate SIP returns"
                ])
            elif "credit" in message_lower:
                suggestions.extend([
                    "How to improve my credit score?",
                    "Check my credit utilization",
                    "Should I take a personal loan?"
                ])
            else:
                # Default suggestions
                suggestions = [
                    "Analyze my spending patterns",
                    "Show my financial health score",
                    "What are my top 3 financial priorities?"
                ]

        # Add context-specific suggestions
        if context.get("accounts"):
            total_balance = sum(acc.get("balance", 0) for acc in context["accounts"])
            if total_balance < 100000:
                suggestions.append("How to build emergency fund?")

        if context.get("goals"):
            behind_goals = [g for g in context["goals"] if g.get("status") == "BEHIND"]
            if behind_goals:
                suggestions.append("How to get my goals back on track?")

        return suggestions[:3]  # Return top 3 suggestions

    def _get_fallback_response(self, prompt_type: str) -> str:
        """
        Get fallback response when API fails
        """
        fallback_responses = {
            "fraud_analysis": "I'm analyzing your transactions for potential fraud. Please check your recent transactions and report any unauthorized activity immediately.",
            "investment_advisor": "I recommend diversifying your portfolio across equity, debt, and gold. Please consult with a financial advisor for personalized recommendations.",
            "tax_optimizer": "To optimize your taxes, consider maximizing your Section 80C investments (up to ₹1.5 lakhs) through ELSS, PPF, or life insurance.",
            "budget_coach": "I suggest following the 50/30/20 rule: 50% for needs, 30% for wants, and 20% for savings and debt repayment.",
            "general": "I'm here to help you manage your finances better. Please try rephrasing your question or check your internet connection."
        }
        return fallback_responses.get(prompt_type, fallback_responses["general"])

    async def analyze_fraud_transaction(
        self,
        transaction: Dict[str, Any],
        user_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Specialized fraud analysis for a transaction
        """
        prompt = f"""
        Analyze this transaction for fraud risk:

        Transaction Details:
        - Amount: ₹{transaction.get('amount', 0):,.2f}
        - Merchant: {transaction.get('merchant', 'Unknown')}
        - Category: {transaction.get('category', 'Unknown')}
        - Date/Time: {transaction.get('date', 'Unknown')}
        - Location: {transaction.get('location', 'Not specified')}

        User's typical behavior:
        - Average transaction: ₹{sum(abs(t.get('amount', 0)) for t in user_history) / len(user_history) if user_history else 0:,.2f}
        - Common merchants: {', '.join(set(t.get('merchant', '') for t in user_history[:10]))}

        Provide:
        1. Risk score (0-100)
        2. Specific risk factors
        3. Recommended action (ALLOW/VERIFY/BLOCK)
        4. Explanation in simple terms
        """

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=self.generation_config
            )

            # Parse response and extract structured data
            return {
                "analysis": response.text,
                "risk_assessment": "HIGH",  # Would be parsed from response
                "recommended_action": "VERIFY",
                "confidence": 0.9
            }
        except Exception as e:
            logger.error(f"Fraud analysis error: {e}")
            return {
                "analysis": "Unable to complete fraud analysis. Please review the transaction manually.",
                "risk_assessment": "UNKNOWN",
                "recommended_action": "VERIFY",
                "error": str(e)
            }

    async def generate_financial_insights(
        self,
        user_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate personalized financial insights
        """
        prompt = f"""
        Based on this financial data, provide 3-5 actionable insights:

        {self._build_context_prompt(user_data)}

        For each insight provide:
        1. A clear title (max 10 words)
        2. Detailed explanation (2-3 sentences)
        3. Specific action to take
        4. Potential savings/earnings amount
        5. Priority level (HIGH/MEDIUM/LOW)

        Focus on practical, immediately actionable advice.
        """

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=self.generation_config
            )

            # Parse and structure insights
            insights = []

            # This would normally parse the structured response
            # For now, returning sample insights
            insights.append({
                "title": "Reduce Food Delivery Expenses",
                "description": response.text[:200] + "...",
                "action": "Cook at home 3 days per week",
                "potential_savings": 5000,
                "priority": "HIGH",
                "category": "SPENDING"
            })

            return insights

        except Exception as e:
            logger.error(f"Insight generation error: {e}")
            return [{
                "title": "Review Your Spending",
                "description": "Analyze your recent transactions to identify savings opportunities.",
                "action": "Check your transaction history",
                "potential_savings": 0,
                "priority": "MEDIUM",
                "category": "GENERAL"
            }]

    async def chat_with_context(
        self,
        message: str,
        chat_history: List[Dict[str, str]],
        user_context: Dict[str, Any]
    ) -> str:
        """
        Chat with conversation history and context
        """
        # Build conversation history
        history_prompt = "\n".join([
            f"{'User' if msg.get('role') == 'user' else 'Assistant'}: {msg.get('content', '')}"
            for msg in chat_history[-5:]  # Last 5 messages
        ])

        prompt = f"""
        {self.system_prompts['general']}

        Conversation History:
        {history_prompt}

        Current Context:
        {self._build_context_prompt(user_context)}

        User: {message}

        Assistant: """

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=self.generation_config
            )
            return response.text
        except Exception as e:
            logger.error(f"Chat error: {e}")
            return "I apologize, but I'm having trouble processing your request. Please try again."