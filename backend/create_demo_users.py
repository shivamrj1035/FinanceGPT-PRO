#!/usr/bin/env python3
"""
Create demo users directly in database
"""

import sqlite3
import hashlib
import uuid
import json
from datetime import datetime, timedelta
import random

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def create_demo_users():
    """Create 3 demo users with realistic data"""

    users_data = [
        {
            "name": "Aarav Sharma",
            "email": "aarav.sharma@gmail.com",
            "age": 28,
            "profession": "Software Engineer",
            "location": "Bangalore",
            "user_type": "young_professional"
        },
        {
            "name": "Priya Patel",
            "email": "priya.patel@gmail.com",
            "age": 35,
            "profession": "Marketing Manager",
            "location": "Delhi",
            "user_type": "family_person"
        },
        {
            "name": "Rajesh Gupta",
            "email": "rajesh.gupta@business.com",
            "age": 45,
            "profession": "Business Owner",
            "location": "Mumbai",
            "user_type": "senior_saver"
        }
    ]

    conn = sqlite3.connect("financebot.db")
    cursor = conn.cursor()

    for user_data in users_data:
        user_id = f"USR_{uuid.uuid4().hex[:8].upper()}"

        try:
            # Insert user
            cursor.execute("""
                INSERT INTO users (id, name, email, password_hash, profile_data, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                user_data["name"],
                user_data["email"],
                hash_password("demo123"),
                json.dumps({
                    "age": user_data["age"],
                    "profession": user_data["profession"],
                    "location": user_data["location"],
                    "user_type": user_data["user_type"]
                }),
                datetime.now().isoformat()
            ))

            # Create accounts based on user type
            accounts = []
            if user_data["user_type"] == "young_professional":
                accounts = [
                    {"bank": "HDFC Bank", "type": "SAVINGS", "balance": 150000},
                    {"bank": "ICICI Bank", "type": "SALARY", "balance": 85000}
                ]
            elif user_data["user_type"] == "family_person":
                accounts = [
                    {"bank": "SBI", "type": "SAVINGS", "balance": 250000},
                    {"bank": "HDFC Bank", "type": "JOINT", "balance": 120000}
                ]
            else:  # senior_saver
                accounts = [
                    {"bank": "ICICI Bank", "type": "CURRENT", "balance": 500000},
                    {"bank": "AXIS Bank", "type": "SAVINGS", "balance": 300000},
                    {"bank": "SBI", "type": "BUSINESS", "balance": 750000}
                ]

            account_ids = []
            for i, acc in enumerate(accounts):
                account_id = f"ACC_{user_id}_{i+1:03d}"
                account_ids.append(account_id)

                cursor.execute("""
                    INSERT INTO accounts (id, user_id, bank_name, account_type, account_number, balance, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    account_id,
                    user_id,
                    acc["bank"],
                    acc["type"],
                    f"****{random.randint(1000, 9999)}",
                    float(acc["balance"]),
                    datetime.now().isoformat()
                ))

            # Create transactions based on user type
            merchants = {
                "young_professional": ["SWIGGY", "UBER", "AMAZON", "NETFLIX", "STARBUCKS", "PVR", "FLIPKART"],
                "family_person": ["BIG BAZAAR", "APOLLO PHARMACY", "SCHOOL FEE", "D-MART", "RELIANCE FRESH"],
                "senior_saver": ["BUSINESS SUPPLIER", "FINE DINING", "PREMIUM CLUB", "TRAVEL AGENCY", "CONSULTANCY"]
            }

            categories = ["FOOD", "TRANSPORT", "SHOPPING", "ENTERTAINMENT", "BILLS", "MEDICAL", "EDUCATION"]

            for i in range(25):  # 25 transactions per user
                txn_merchants = merchants[user_data["user_type"]]
                amount = random.choice([
                    -random.randint(500, 5000),    # Small expenses
                    -random.randint(5000, 25000),  # Medium expenses
                    -random.randint(25000, 100000), # Large expenses
                    random.randint(50000, 200000)   # Income
                ])

                if user_data["user_type"] == "senior_saver":
                    amount *= random.choice([1, 2, 3])  # Higher amounts

                cursor.execute("""
                    INSERT INTO transactions (id, account_id, user_id, amount, merchant, category, description, date, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    f"TXN_{user_id}_{i+1:04d}",
                    random.choice(account_ids),
                    user_id,
                    float(amount),
                    random.choice(txn_merchants),
                    random.choice(categories),
                    f"Transaction {i+1}",
                    (datetime.now() - timedelta(days=random.randint(1, 90))).isoformat(),
                    datetime.now().isoformat()
                ))

            # Create investments
            investments = {
                "young_professional": ["SIP - HDFC Top 100", "PPF Account", "Stocks - TCS"],
                "family_person": ["Child Education Plan", "Life Insurance", "SIP - Balanced Fund"],
                "senior_saver": ["Real Estate Fund", "Corporate Bonds", "Equity Portfolio", "Gold ETF"]
            }

            for i, inv_name in enumerate(investments[user_data["user_type"]]):
                amount = random.randint(50000, 500000)
                if user_data["user_type"] == "senior_saver":
                    amount *= 3

                cursor.execute("""
                    INSERT INTO investments (id, user_id, investment_type, name, amount, current_value, purchase_date, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    f"INV_{user_id}_{i+1:03d}",
                    user_id,
                    inv_name.split()[0],
                    inv_name,
                    float(amount),
                    float(amount * random.uniform(0.9, 1.4)),
                    (datetime.now() - timedelta(days=random.randint(30, 730))).isoformat(),
                    datetime.now().isoformat()
                ))

            # Create goals
            goals = {
                "young_professional": ["House Purchase", "Emergency Fund", "Vacation Fund"],
                "family_person": ["Children Education", "Family Vacation", "Home Renovation"],
                "senior_saver": ["Retirement Corpus", "Business Expansion", "Luxury Purchase"]
            }

            for i, goal_name in enumerate(goals[user_data["user_type"]]):
                target = random.randint(500000, 2000000)
                if user_data["user_type"] == "senior_saver":
                    target *= 5

                cursor.execute("""
                    INSERT INTO goals (id, user_id, name, target_amount, current_amount, target_date, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    f"GOAL_{user_id}_{i+1:03d}",
                    user_id,
                    goal_name,
                    float(target),
                    float(random.randint(0, target // 5)),
                    (datetime.now() + timedelta(days=random.randint(365, 1825))).isoformat(),
                    datetime.now().isoformat()
                ))

            print(f"✅ Created {user_data['name']} ({user_data['email']}) with complete profile")

        except Exception as e:
            print(f"❌ Failed to create {user_data['name']}: {e}")
            import traceback
            traceback.print_exc()

    conn.commit()

    # Verify creation
    cursor.execute("SELECT COUNT(*) FROM users")
    users_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM accounts")
    accounts_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM transactions")
    transactions_count = cursor.fetchone()[0]

    print(f"\n📊 Database Summary:")
    print(f"  👥 Users: {users_count}")
    print(f"  🏦 Accounts: {accounts_count}")
    print(f"  💳 Transactions: {transactions_count}")

    cursor.execute("SELECT name, email FROM users")
    users = cursor.fetchall()
    print(f"\n👥 Created Users:")
    for user in users:
        print(f"  - {user[0]} ({user[1]})")

    conn.close()
    print("\n🎉 Demo users created successfully!")

if __name__ == "__main__":
    create_demo_users()