"""
Enhanced Mock Data Generator for FinanceGPT Pro
Includes realistic patterns, anomalies, and demo scenarios
"""

import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from faker import Faker

fake = Faker('en_IN')

# ... [Previous category definitions remain the same] ...

class EnhancedMockGenerator:
    def __init__(self, output_dir: str = "data/mock"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_realistic_transactions(self, accounts: List[Dict], days: int = 90) -> List[Dict[str, Any]]:
        """Generate transactions with realistic patterns"""
        transactions = []
        transaction_id = 1
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        for account in accounts:
            user_salary = random.randint(30000, 150000)

            # 1. SALARY - Fixed date each month
            salary_day = random.randint(1, 5)  # Usually early in month
            current_date = start_date
            while current_date <= end_date:
                if current_date.day == salary_day:
                    transactions.append({
                        "id": f"TXN{transaction_id:06d}",
                        "account_id": account["id"],
                        "amount": user_salary,
                        "merchant": "Monthly Salary Credit",
                        "category": "Salary",
                        "description": f"Salary for {current_date.strftime('%B %Y')}",
                        "date": current_date.isoformat(),
                        "type": "CREDIT",
                        "status": "COMPLETED",
                        "mode": "BANK_TRANSFER",
                        "is_recurring": True,
                        "tags": ["salary", "income", "recurring"]
                    })
                    transaction_id += 1
                current_date += timedelta(days=1)

            # 2. RECURRING SUBSCRIPTIONS
            subscriptions = [
                {"name": "Netflix", "amount": 649, "day": 5},
                {"name": "Spotify", "amount": 119, "day": 10},
                {"name": "Amazon Prime", "amount": 179, "day": 15},
                {"name": "Gym Membership", "amount": 2000, "day": 1},
            ]

            for sub in random.sample(subscriptions, k=random.randint(1, 3)):
                current_date = start_date
                while current_date <= end_date:
                    if current_date.day == sub["day"]:
                        transactions.append({
                            "id": f"TXN{transaction_id:06d}",
                            "account_id": account["id"],
                            "amount": -sub["amount"],
                            "merchant": sub["name"],
                            "category": "Entertainment" if "Netflix" in sub["name"] or "Spotify" in sub["name"] else "Healthcare",
                            "description": f"{sub['name']} Monthly Subscription",
                            "date": current_date.isoformat(),
                            "type": "DEBIT",
                            "status": "COMPLETED",
                            "mode": "AUTO_DEBIT",
                            "is_recurring": True,
                            "tags": ["subscription", "recurring", "essential"]
                        })
                        transaction_id += 1
                    current_date += timedelta(days=1)

            # 3. WEEKEND SPENDING PATTERNS
            for i in range(days):
                current_date = start_date + timedelta(days=i)
                is_weekend = current_date.weekday() in [5, 6]

                # More food and entertainment on weekends
                if is_weekend:
                    # Food delivery
                    if random.random() < 0.7:  # 70% chance
                        transactions.append({
                            "id": f"TXN{transaction_id:06d}",
                            "account_id": account["id"],
                            "amount": -random.randint(300, 1500),
                            "merchant": random.choice(["Swiggy", "Zomato", "Restaurant"]),
                            "category": "Food & Dining",
                            "description": "Weekend dining",
                            "date": current_date.isoformat(),
                            "type": "DEBIT",
                            "status": "COMPLETED",
                            "mode": "UPI",
                            "is_weekend_expense": True,
                            "tags": ["weekend", "leisure", "food"]
                        })
                        transaction_id += 1

            # 4. SEASONAL PATTERNS
            # Diwali shopping spike (October-November)
            if start_date.month in [10, 11]:
                for _ in range(random.randint(5, 10)):
                    transactions.append({
                        "id": f"TXN{transaction_id:06d}",
                        "account_id": account["id"],
                        "amount": -random.randint(1000, 10000),
                        "merchant": random.choice(["Amazon", "Flipkart", "Myntra", "Local Store"]),
                        "category": "Shopping",
                        "description": "Diwali Shopping",
                        "date": fake.date_time_between(start_date=start_date, end_date=end_date).isoformat(),
                        "type": "DEBIT",
                        "status": "COMPLETED",
                        "mode": random.choice(["CARD", "UPI", "NET_BANKING"]),
                        "is_seasonal": True,
                        "tags": ["diwali", "festival", "shopping"]
                    })
                    transaction_id += 1

            # 5. SUSPICIOUS/FRAUD TRANSACTIONS (for demo)
            if random.random() < 0.1:  # 10% accounts have suspicious activity
                fraud_date = fake.date_time_between(start_date=end_date - timedelta(days=7), end_date=end_date)
                transactions.append({
                    "id": f"TXN{transaction_id:06d}",
                    "account_id": account["id"],
                    "amount": -random.randint(10000, 50000),
                    "merchant": "Unknown International Merchant",
                    "category": "Suspicious",
                    "description": "INTL TRANSACTION - UNUSUAL PATTERN",
                    "date": fraud_date.isoformat(),
                    "type": "DEBIT",
                    "status": "PENDING_REVIEW",
                    "mode": "INTERNATIONAL_CARD",
                    "is_suspicious": True,
                    "fraud_score": random.uniform(0.7, 0.95),
                    "tags": ["suspicious", "fraud_alert", "international"]
                })
                transaction_id += 1

        return sorted(transactions, key=lambda x: x["date"], reverse=True)

    def generate_chat_history(self, users: List[Dict]) -> List[Dict[str, Any]]:
        """Generate realistic chat conversations"""
        chat_history = []
        chat_id = 1

        conversations = [
            {
                "query": "Can I afford a ₹50,000 vacation next month?",
                "response": "Based on your current spending pattern and savings rate, you can afford a ₹50,000 vacation. You have ₹1,85,000 in savings and your monthly surplus is ₹25,000. However, I recommend keeping at least ₹1,50,000 as emergency fund.",
                "intent": "affordability_check",
                "confidence": 0.92
            },
            {
                "query": "Why did my expenses increase last month?",
                "response": "Your expenses increased by 23% last month primarily due to:\n1. Diwali shopping: ₹15,000 (+₹12,000 from usual)\n2. Extra dining out: ₹8,500 (+₹4,000)\n3. One-time insurance premium: ₹10,000\nYour regular expenses remained stable.",
                "intent": "expense_analysis",
                "confidence": 0.88
            },
            {
                "query": "Show me my top spending categories",
                "response": "Here are your top 5 spending categories this month:\n1. Food & Dining: ₹12,500 (28%)\n2. Shopping: ₹8,000 (18%)\n3. Transportation: ₹6,500 (14%)\n4. Utilities: ₹5,000 (11%)\n5. Entertainment: ₹3,500 (8%)",
                "intent": "category_analysis",
                "confidence": 0.95
            },
            {
                "query": "Am I saving enough for retirement?",
                "response": "Based on your current age (32) and savings rate (₹15,000/month in EPF + ₹10,000 in investments), you're on track to accumulate ₹2.5 crores by age 60. However, considering inflation, I recommend increasing your SIP by ₹5,000 to maintain your lifestyle post-retirement.",
                "intent": "retirement_planning",
                "confidence": 0.85
            },
            {
                "query": "Is this ₹25,000 transaction suspicious?",
                "response": "⚠️ This transaction appears suspicious. It was made at 2:30 AM from an international merchant you've never used before. The amount is 5x your average transaction size. I've temporarily blocked this transaction. Please confirm if this was you.",
                "intent": "fraud_detection",
                "confidence": 0.94
            }
        ]

        for user in users:
            # Each user has 5-15 chat interactions
            num_chats = random.randint(5, 15)
            user_conversations = random.sample(conversations, min(num_chats, len(conversations)))

            for conv in user_conversations:
                chat_date = fake.date_time_between(start_date='-30d', end_date='now')
                chat = {
                    "id": f"CHAT{chat_id:05d}",
                    "user_id": user["id"],
                    "message": conv["query"],
                    "response": conv["response"],
                    "intent": conv["intent"],
                    "confidence_score": conv["confidence"],
                    "timestamp": chat_date.isoformat(),
                    "response_time_ms": random.randint(100, 500),
                    "helpful": random.choice([True, True, True, False]),  # 75% helpful
                    "follow_up_action": random.choice([None, "set_budget", "create_goal", "review_transactions"])
                }
                chat_history.append(chat)
                chat_id += 1

        return sorted(chat_history, key=lambda x: x["timestamp"], reverse=True)

    def generate_financial_goals(self, users: List[Dict]) -> List[Dict[str, Any]]:
        """Generate savings goals with progress"""
        goals = []
        goal_id = 1

        goal_templates = [
            {"name": "Emergency Fund", "target_multiplier": 6, "category": "SAFETY"},
            {"name": "Dream Vacation - Europe", "target": 200000, "category": "LIFESTYLE"},
            {"name": "New Car - EV", "target": 1500000, "category": "PURCHASE"},
            {"name": "Home Down Payment", "target": 2500000, "category": "PROPERTY"},
            {"name": "Child Education", "target": 1000000, "category": "EDUCATION"},
            {"name": "Wedding Fund", "target": 500000, "category": "LIFESTYLE"},
            {"name": "Startup Capital", "target": 1000000, "category": "BUSINESS"}
        ]

        for user in users:
            # Each user has 2-4 active goals
            num_goals = random.randint(2, 4)
            user_goals = random.sample(goal_templates, num_goals)

            for goal_template in user_goals:
                if goal_template["name"] == "Emergency Fund":
                    target = user["profile"]["annual_income"] / 2  # 6 months salary
                else:
                    target = goal_template.get("target", random.randint(100000, 1000000))

                progress = random.uniform(0.1, 0.95)
                current = target * progress

                goal = {
                    "id": f"GOAL{goal_id:03d}",
                    "user_id": user["id"],
                    "name": goal_template["name"],
                    "category": goal_template["category"],
                    "target_amount": round(target, 2),
                    "current_amount": round(current, 2),
                    "progress_percentage": round(progress * 100, 1),
                    "monthly_contribution": round(target / 24, 2),  # 2-year goal
                    "start_date": fake.date_time_between(start_date='-1y', end_date='-1m').isoformat(),
                    "target_date": fake.date_time_between(start_date='+6m', end_date='+2y').isoformat(),
                    "status": "ON_TRACK" if progress > 0.4 else "BEHIND",
                    "auto_deduct": random.choice([True, False]),
                    "priority": random.randint(1, 5)
                }
                goals.append(goal)
                goal_id += 1

        return goals

    def generate_alerts(self, users: List[Dict]) -> List[Dict[str, Any]]:
        """Generate various alerts for demo"""
        alerts = []
        alert_id = 1

        alert_templates = [
            {
                "type": "FRAUD_ALERT",
                "severity": "HIGH",
                "title": "Suspicious Transaction Detected",
                "message": "A transaction of ₹25,000 from an unknown international merchant was blocked",
                "action_required": True
            },
            {
                "type": "BUDGET_WARNING",
                "severity": "MEDIUM",
                "title": "Budget Limit Approaching",
                "message": "You've used 85% of your Food & Dining budget for this month",
                "action_required": False
            },
            {
                "type": "BILL_REMINDER",
                "severity": "LOW",
                "title": "Upcoming Bill Payment",
                "message": "Your electricity bill of ₹3,500 is due in 3 days",
                "action_required": True
            },
            {
                "type": "GOAL_ACHIEVED",
                "severity": "INFO",
                "title": "Goal Milestone Reached!",
                "message": "Congratulations! You've reached 50% of your Emergency Fund goal",
                "action_required": False
            },
            {
                "type": "MARKET_UPDATE",
                "severity": "INFO",
                "title": "Portfolio Performance",
                "message": "Your investment portfolio is up 12% this month, outperforming the market",
                "action_required": False
            },
            {
                "type": "UNUSUAL_SPENDING",
                "severity": "MEDIUM",
                "title": "Unusual Spending Pattern",
                "message": "Your shopping expenses are 200% higher than your 3-month average",
                "action_required": False
            },
            {
                "type": "SAVINGS_TIP",
                "severity": "INFO",
                "title": "Savings Opportunity",
                "message": "You could save ₹2,000/month by switching to annual subscriptions",
                "action_required": False
            }
        ]

        for user in users:
            # Each user has 3-8 recent alerts
            num_alerts = random.randint(3, 8)
            user_alerts = random.sample(alert_templates, num_alerts)

            for alert_template in user_alerts:
                alert = {
                    "id": f"ALRT{alert_id:04d}",
                    "user_id": user["id"],
                    "type": alert_template["type"],
                    "severity": alert_template["severity"],
                    "title": alert_template["title"],
                    "message": alert_template["message"],
                    "created_at": fake.date_time_between(start_date='-7d', end_date='now').isoformat(),
                    "read": random.choice([True, False, False]),  # 33% read
                    "action_required": alert_template["action_required"],
                    "action_taken": None,
                    "expires_at": fake.date_time_between(start_date='+1d', end_date='+7d').isoformat()
                }
                alerts.append(alert)
                alert_id += 1

        return sorted(alerts, key=lambda x: x["created_at"], reverse=True)

    def generate_insights(self, users: List[Dict]) -> List[Dict[str, Any]]:
        """Generate AI-powered insights"""
        insights = []
        insight_id = 1

        insight_templates = [
            {
                "type": "SPENDING_PATTERN",
                "title": "Weekend Spending Spike",
                "description": "You spend 40% more on weekends compared to weekdays",
                "recommendation": "Set a weekend budget of ₹3,000 to control impulse spending"
            },
            {
                "type": "SAVINGS_OPPORTUNITY",
                "title": "Subscription Optimization",
                "description": "You have 3 streaming services but only use 1 regularly",
                "recommendation": "Cancel unused subscriptions to save ₹828/month"
            },
            {
                "type": "INVESTMENT_ADVICE",
                "title": "Portfolio Rebalancing Needed",
                "description": "Your portfolio is 80% equity, above your moderate risk profile",
                "recommendation": "Consider adding 20% debt funds for better risk management"
            },
            {
                "type": "CASHFLOW_PREDICTION",
                "title": "Positive Cash Flow Trend",
                "description": "Your savings rate has increased by 15% over last quarter",
                "recommendation": "Consider increasing SIP amount by ₹5,000"
            }
        ]

        for user in users:
            user_insights = random.sample(insight_templates, random.randint(2, 4))

            for insight_template in user_insights:
                insight = {
                    "id": f"INST{insight_id:04d}",
                    "user_id": user["id"],
                    "type": insight_template["type"],
                    "title": insight_template["title"],
                    "description": insight_template["description"],
                    "recommendation": insight_template["recommendation"],
                    "potential_savings": random.randint(500, 5000) if "SAVINGS" in insight_template["type"] else None,
                    "confidence_score": round(random.uniform(0.75, 0.95), 2),
                    "created_at": fake.date_time_between(start_date='-30d', end_date='now').isoformat(),
                    "is_actionable": True,
                    "priority": random.choice(["HIGH", "MEDIUM", "LOW"])
                }
                insights.append(insight)
                insight_id += 1

        return insights

    def generate_demo_scenarios(self) -> Dict[str, Any]:
        """Generate specific demo scenarios for presentation"""
        scenarios = {
            "fraud_detection_demo": {
                "transaction_id": "TXN999999",
                "amount": -35000,
                "merchant": "SUSPICIOUS-MERCHANT-INTL",
                "timestamp": datetime.now().isoformat(),
                "fraud_score": 0.92,
                "detection_time_ms": 87,
                "auto_blocked": True
            },
            "real_time_alert": {
                "type": "INSTANT_NOTIFICATION",
                "message": "Large transaction detected: ₹50,000 at Apple Store",
                "requires_approval": True,
                "timeout_seconds": 30
            },
            "mcp_permission_demo": {
                "revoke_resource": "credit_score",
                "grant_resource": "transactions",
                "demo_timestamp": datetime.now().isoformat()
            },
            "ai_conversation_demo": {
                "complex_query": "Based on my spending trends and upcoming expenses, can I afford to invest ₹30,000 in mutual funds this month without affecting my emergency fund?",
                "expected_response_points": [
                    "Current emergency fund status",
                    "Monthly expense analysis",
                    "Upcoming committed expenses",
                    "Surplus calculation",
                    "Investment recommendation"
                ]
            }
        }
        return scenarios

    def generate_all_enhanced(self):
        """Generate all enhanced mock data"""
        print("🚀 Starting enhanced mock data generation...")

        # Basic data (from original generator)
        users = self.generate_users(5)
        accounts = self.generate_accounts(users, 3)

        # Enhanced data
        transactions = self.generate_realistic_transactions(accounts, 90)
        chat_history = self.generate_chat_history(users)
        goals = self.generate_financial_goals(users)
        alerts = self.generate_alerts(users)
        insights = self.generate_insights(users)
        demo_scenarios = self.generate_demo_scenarios()

        # Save all data
        self.save_data(users, "users")
        self.save_data(accounts, "accounts")
        self.save_data(transactions, "transactions")
        self.save_data(chat_history, "chat_history")
        self.save_data(goals, "goals")
        self.save_data(alerts, "alerts")
        self.save_data(insights, "insights")
        self.save_data(demo_scenarios, "demo_scenarios")

        print("\n✨ Enhanced mock data generation complete!")
        print("📊 Generated realistic patterns including:")
        print("   - Monthly salary credits")
        print("   - Recurring subscriptions")
        print("   - Weekend spending patterns")
        print("   - Seasonal shopping spikes")
        print("   - Suspicious transactions for fraud demo")
        print("   - Chat history with AI responses")
        print("   - Financial goals with progress tracking")
        print("   - Various alert types")
        print("   - AI-powered insights")
        print("   - Demo scenarios for presentation")

        return {
            "status": "success",
            "generated_files": 8,
            "total_records": len(transactions) + len(chat_history) + len(goals) + len(alerts)
        }

# Additional helper methods would go here...

if __name__ == "__main__":
    generator = EnhancedMockGenerator()
    result = generator.generate_all_enhanced()
    print(f"\n✅ Mock data generation complete: {result}")