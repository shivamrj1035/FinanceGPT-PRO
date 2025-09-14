"""
Complete Mock Data Generator for FinanceGPT Pro
Generates all required JSON files for the backend
"""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path

class MockDataGenerator:
    def __init__(self):
        self.backend_mock_dir = Path("backend/data/mock")
        self.backend_mock_dir.mkdir(parents=True, exist_ok=True)

    def generate_users(self):
        """Generate user data"""
        users = [
            {
                "id": "USR001",
                "email": "demo@financegpt.com",
                "name": "Rajesh Kumar",
                "phone": "+91-9876543210",
                "pan": "ABCDE1234F",
                "aadhar": "1234-5678-9012",
                "created_at": "2024-01-01T00:00:00",
                "kyc_verified": True,
                "risk_profile": "MODERATE"
            },
            {
                "id": "USR002",
                "email": "priya@example.com",
                "name": "Priya Sharma",
                "phone": "+91-9876543211",
                "pan": "XYZAB5678G",
                "aadhar": "9876-5432-1098",
                "created_at": "2024-01-15T00:00:00",
                "kyc_verified": True,
                "risk_profile": "CONSERVATIVE"
            }
        ]
        return users

    def generate_accounts(self):
        """Generate bank account data"""
        accounts = [
            {
                "id": "ACC001",
                "user_id": "USR001",
                "account_number": "HDFC1234567890",
                "bank_name": "HDFC Bank",
                "account_type": "SAVINGS",
                "balance": 125000.50,
                "currency": "INR",
                "ifsc": "HDFC0001234",
                "created_at": "2024-01-01T00:00:00"
            },
            {
                "id": "ACC002",
                "user_id": "USR001",
                "account_number": "ICICI9876543210",
                "bank_name": "ICICI Bank",
                "account_type": "CURRENT",
                "balance": 450000.00,
                "currency": "INR",
                "ifsc": "ICIC0001234",
                "created_at": "2024-01-01T00:00:00"
            }
        ]
        return accounts

    def generate_transactions(self):
        """Generate transaction data with patterns"""
        transactions = []
        base_date = datetime.now() - timedelta(days=90)

        # Sample transactions with various patterns
        patterns = [
            # Regular expenses
            {"amount": -1500, "merchant": "Swiggy", "category": "FOOD", "type": "DEBIT"},
            {"amount": -2500, "merchant": "Uber", "category": "TRANSPORT", "type": "DEBIT"},
            {"amount": -35000, "merchant": "House Rent", "category": "HOUSING", "type": "DEBIT"},
            {"amount": -5000, "merchant": "Amazon", "category": "SHOPPING", "type": "DEBIT"},
            {"amount": -1200, "merchant": "Netflix", "category": "ENTERTAINMENT", "type": "DEBIT"},
            # Income
            {"amount": 75000, "merchant": "Salary Credit", "category": "SALARY", "type": "CREDIT"},
            {"amount": 15000, "merchant": "Freelance Payment", "category": "INCOME", "type": "CREDIT"},
            # Suspicious for demo
            {"amount": -45000, "merchant": "SUSPICIOUS-INTL-MERCHANT", "category": "SUSPICIOUS", "type": "DEBIT"},
        ]

        for i in range(50):
            pattern = random.choice(patterns)
            transaction_date = base_date + timedelta(days=random.randint(0, 90))

            transactions.append({
                "id": f"TXN{i+1:06d}",
                "account_id": random.choice(["ACC001", "ACC002"]),
                "amount": pattern["amount"] + random.randint(-500, 500),
                "merchant": pattern["merchant"],
                "category": pattern["category"],
                "description": f"Payment to {pattern['merchant']}",
                "date": transaction_date.isoformat(),
                "type": pattern["type"],
                "status": "COMPLETED",
                "upi_id": f"pay@{pattern['merchant'].lower().replace(' ', '')}" if pattern["type"] == "DEBIT" else None
            })

        return sorted(transactions, key=lambda x: x["date"], reverse=True)[:20]

    def generate_goals(self):
        """Generate financial goals"""
        goals = [
            {
                "id": "GOAL001",
                "user_id": "USR001",
                "name": "Emergency Fund",
                "target_amount": 500000,
                "current_amount": 125000,
                "deadline": "2025-12-31",
                "category": "SAVINGS",
                "priority": "HIGH",
                "status": "IN_PROGRESS",
                "created_at": "2024-01-01T00:00:00"
            },
            {
                "id": "GOAL002",
                "user_id": "USR001",
                "name": "Dream Vacation - Europe",
                "target_amount": 300000,
                "current_amount": 75000,
                "deadline": "2025-06-30",
                "category": "TRAVEL",
                "priority": "MEDIUM",
                "status": "IN_PROGRESS",
                "created_at": "2024-02-01T00:00:00"
            }
        ]
        return goals

    def generate_investments(self):
        """Generate investment data"""
        investments = [
            {
                "id": "INV001",
                "user_id": "USR001",
                "type": "MUTUAL_FUND",
                "name": "HDFC Mid-Cap Opportunities",
                "invested_amount": 150000,
                "current_value": 175000,
                "returns_percentage": 16.67,
                "start_date": "2023-01-01",
                "asset_class": "EQUITY"
            },
            {
                "id": "INV002",
                "user_id": "USR001",
                "type": "STOCKS",
                "name": "Reliance Industries",
                "invested_amount": 50000,
                "current_value": 62000,
                "returns_percentage": 24.0,
                "start_date": "2023-06-01",
                "asset_class": "EQUITY"
            }
        ]
        return investments

    def generate_alerts(self):
        """Generate alerts"""
        alerts = [
            {
                "id": "ALERT001",
                "user_id": "USR001",
                "type": "SPENDING",
                "severity": "MEDIUM",
                "title": "High Food Spending",
                "message": "Your food expenses are 20% higher than last month",
                "date": datetime.now().isoformat(),
                "read": False
            },
            {
                "id": "ALERT002",
                "user_id": "USR001",
                "type": "GOAL",
                "severity": "LOW",
                "title": "Goal Progress Update",
                "message": "You've reached 25% of your Emergency Fund goal!",
                "date": datetime.now().isoformat(),
                "read": False
            }
        ]
        return alerts

    def generate_insights(self):
        """Generate AI insights"""
        insights = [
            {
                "id": "INS001",
                "user_id": "USR001",
                "type": "SPENDING_PATTERN",
                "title": "Weekend Spending Spike",
                "description": "You spend 40% more on weekends compared to weekdays",
                "recommendation": "Consider meal prepping to reduce weekend food delivery costs",
                "potential_savings": 5000,
                "priority": "MEDIUM",
                "created_at": datetime.now().isoformat()
            },
            {
                "id": "INS002",
                "user_id": "USR001",
                "type": "INVESTMENT",
                "title": "Portfolio Rebalancing Needed",
                "description": "Your portfolio is 85% equity, above your moderate risk profile",
                "recommendation": "Consider adding 20% debt funds for better risk management",
                "potential_savings": 0,
                "priority": "HIGH",
                "created_at": datetime.now().isoformat()
            }
        ]
        return insights

    def generate_chat_history(self):
        """Generate chat history"""
        chat_history = [
            {
                "id": "CHAT001",
                "user_id": "USR001",
                "message": "How can I reduce my monthly expenses?",
                "response": "Based on your spending analysis, here are top 3 ways to reduce expenses:\n1. Food delivery (₹15,000/month) - Cook more at home\n2. Subscriptions (₹5,000/month) - Cancel unused services\n3. Transport (₹8,000/month) - Use public transport when possible",
                "timestamp": datetime.now().isoformat(),
                "context": "expense_reduction"
            }
        ]
        return chat_history

    def generate_credit_data(self):
        """Generate credit score data"""
        credit_data = [
            {
                "user_id": "USR001",
                "credit_score": 750,
                "credit_age": 5,
                "payment_history": 98,
                "credit_utilization": 25,
                "total_accounts": 3,
                "hard_inquiries": 1,
                "last_updated": datetime.now().isoformat()
            }
        ]
        return credit_data

    def generate_epf_data(self):
        """Generate EPF data"""
        epf_data = [
            {
                "user_id": "USR001",
                "uan": "100123456789",
                "balance": 850000,
                "employer_contribution": 4500,
                "employee_contribution": 4500,
                "interest_rate": 8.15,
                "last_updated": datetime.now().isoformat()
            }
        ]
        return epf_data

    def generate_permissions(self):
        """Generate permissions data"""
        permissions = [
            {
                "user_id": "USR001",
                "resource": "accounts",
                "access_level": "FULL",
                "granted_at": "2024-01-01T00:00:00"
            },
            {
                "user_id": "USR001",
                "resource": "transactions",
                "access_level": "FULL",
                "granted_at": "2024-01-01T00:00:00"
            }
        ]
        return permissions

    def save_json(self, data, filename):
        """Save data to JSON file"""
        filepath = self.backend_mock_dir / f"{filename}.json"
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        print(f"✅ Created {filepath}")

    def generate_all(self):
        """Generate all mock data files"""
        print("🚀 Generating mock data files...")

        # Generate all data
        data_map = {
            "users": self.generate_users(),
            "accounts": self.generate_accounts(),
            "transactions": self.generate_transactions(),
            "goals": self.generate_goals(),
            "investments": self.generate_investments(),
            "alerts": self.generate_alerts(),
            "insights": self.generate_insights(),
            "chat_history": self.generate_chat_history(),
            "credit_data": self.generate_credit_data(),
            "epf_data": self.generate_epf_data(),
            "permissions": self.generate_permissions()
        }

        # Save all files
        for name, data in data_map.items():
            self.save_json(data, name)

        print(f"\n✨ Generated {len(data_map)} mock data files!")
        print(f"📁 Location: {self.backend_mock_dir}")
        return len(data_map)

if __name__ == "__main__":
    generator = MockDataGenerator()
    generator.generate_all()