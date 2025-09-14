#!/usr/bin/env python3
"""
Export user profiles to JSON files for documentation
"""

import sqlite3
import json
import os

def export_user_profiles():
    """Export all user data to individual JSON files"""

    conn = sqlite3.connect("financebot.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get all users
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()

    users_data = []

    for user in users:
        user_data = {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "profile": json.loads(user["profile_data"]) if user["profile_data"] else {},
            "created_at": user["created_at"]
        }

        # Get accounts
        cursor.execute("SELECT * FROM accounts WHERE user_id = ?", (user["id"],))
        accounts = [dict(row) for row in cursor.fetchall()]
        user_data["accounts"] = accounts

        # Get transactions (last 30)
        cursor.execute("""
            SELECT * FROM transactions WHERE user_id = ?
            ORDER BY date DESC LIMIT 30
        """, (user["id"],))
        transactions = [dict(row) for row in cursor.fetchall()]
        user_data["transactions"] = transactions

        # Get investments
        cursor.execute("SELECT * FROM investments WHERE user_id = ?", (user["id"],))
        investments = [dict(row) for row in cursor.fetchall()]
        user_data["investments"] = investments

        # Get goals
        cursor.execute("SELECT * FROM goals WHERE user_id = ?", (user["id"],))
        goals = [dict(row) for row in cursor.fetchall()]
        user_data["goals"] = goals

        # Calculate summary stats
        total_balance = sum(acc["balance"] for acc in accounts)
        total_investments = sum(inv["current_value"] for inv in investments)
        monthly_income = sum(txn["amount"] for txn in transactions if txn["amount"] > 0) / 3  # Rough estimate
        monthly_expenses = abs(sum(txn["amount"] for txn in transactions if txn["amount"] < 0)) / 3

        user_data["summary"] = {
            "total_balance": total_balance,
            "total_investments": total_investments,
            "estimated_monthly_income": monthly_income,
            "estimated_monthly_expenses": monthly_expenses,
            "net_worth": total_balance + total_investments
        }

        users_data.append(user_data)

        # Save individual user file
        user_type = user_data["profile"].get("user_type", "unknown")
        filename = f"../users/{user_type}_{user_data['name'].lower().replace(' ', '_')}.json"

        os.makedirs(os.path.dirname(filename), exist_ok=True)

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(user_data, f, indent=2, ensure_ascii=False)

        print(f"✅ Exported {user_data['name']} to {filename}")

    # Save all users summary
    summary_file = "../users/all_users_summary.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(users_data, f, indent=2, ensure_ascii=False)

    print(f"📊 Exported summary to {summary_file}")

    # Create demo credentials file
    credentials = {
        "demo_users": [
            {
                "name": user["name"],
                "email": user["email"],
                "password": "demo123",
                "user_type": user["profile"].get("user_type", "unknown"),
                "description": user["profile"].get("profession", "Professional")
            }
            for user in users_data
        ]
    }

    cred_file = "../users/demo_credentials.json"
    with open(cred_file, 'w', encoding='utf-8') as f:
        json.dump(credentials, f, indent=2, ensure_ascii=False)

    print(f"🔐 Exported credentials to {cred_file}")

    conn.close()
    print("\n🎉 All user profiles exported successfully!")

if __name__ == "__main__":
    export_user_profiles()