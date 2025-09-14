#!/usr/bin/env python3
"""
Extract Database Content to MCP Data Sources
Converts rich database content to MCP-compatible JSON format
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, List, Any

def extract_database_content(db_path: str = "financebot.db") -> Dict[str, Any]:
    """Extract all data from database and convert to MCP format"""

    if not os.path.isabs(db_path):
        db_path = os.path.join(os.getcwd(), db_path)

    print(f"📊 Extracting data from: {db_path}")

    extracted_data = {
        "accounts": [],
        "transactions": [],
        "investments": [],
        "users": []
    }

    try:
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Extract Users
            print("👤 Extracting users...")
            cursor.execute("SELECT * FROM users")
            users = cursor.fetchall()
            for user in users:
                profile_data = {}
                if user["profile_data"]:
                    try:
                        profile_data = json.loads(user["profile_data"])
                    except:
                        profile_data = {}

                extracted_data["users"].append({
                    "id": user["id"],
                    "name": user["name"],
                    "email": user["email"],
                    "user_type": "premium",
                    "profile_data": profile_data,
                    "created_at": user["created_at"] if "created_at" in user.keys() else datetime.now().isoformat()
                })

            # Extract Accounts
            print("🏦 Extracting accounts...")
            cursor.execute("SELECT * FROM accounts")
            accounts = cursor.fetchall()
            for account in accounts:
                extracted_data["accounts"].append({
                    "id": account["id"],
                    "user_id": account["user_id"],
                    "bank_name": account["bank_name"],
                    "account_type": account["account_type"],
                    "account_number": account["account_number"],
                    "balance": float(account["balance"]),
                    "currency": account["currency"] if "currency" in account.keys() else "INR",
                    "created_at": account["created_at"] if "created_at" in account.keys() else datetime.now().isoformat(),
                    "status": "active",
                    "branch": "Main Branch"
                })

            # Extract Transactions
            print("💳 Extracting transactions...")
            cursor.execute("SELECT * FROM transactions ORDER BY date DESC")
            transactions = cursor.fetchall()
            for txn in transactions:
                extracted_data["transactions"].append({
                    "id": txn["id"],
                    "account_id": txn["account_id"],
                    "user_id": txn["user_id"],
                    "amount": float(txn["amount"]),
                    "merchant": txn["merchant"] if "merchant" in txn.keys() and txn["merchant"] else "Unknown",
                    "category": txn["category"] if "category" in txn.keys() and txn["category"] else "Other",
                    "description": txn["description"] if "description" in txn.keys() and txn["description"] else "Transaction",
                    "date": txn["date"],
                    "created_at": txn["created_at"] if "created_at" in txn.keys() else datetime.now().isoformat(),
                    "type": "expense" if float(txn["amount"]) < 0 else "income",
                    "status": "completed",
                    "payment_method": "card"
                })

            # Extract Investments
            print("📈 Extracting investments...")
            cursor.execute("SELECT * FROM investments")
            investments = cursor.fetchall()
            for inv in investments:
                invested_amount = float(inv["amount"])
                current_value = float(inv["current_value"])
                returns = current_value - invested_amount
                returns_percentage = (returns / invested_amount) * 100 if invested_amount > 0 else 0

                extracted_data["investments"].append({
                    "id": inv["id"],
                    "user_id": inv["user_id"],
                    "type": inv["investment_type"],
                    "name": inv["name"],
                    "invested_amount": invested_amount,
                    "current_value": current_value,
                    "purchase_date": inv["purchase_date"] if "purchase_date" in inv.keys() and inv["purchase_date"] else datetime.now().isoformat(),
                    "created_at": inv["created_at"] if "created_at" in inv.keys() else datetime.now().isoformat(),
                    "returns": returns,
                    "returns_percentage": returns_percentage,
                    "status": "active"
                })

    except Exception as e:
        print(f"❌ Error extracting data: {e}")
        return {}

    print(f"✅ Extracted: {len(extracted_data['users'])} users, {len(extracted_data['accounts'])} accounts, {len(extracted_data['transactions'])} transactions, {len(extracted_data['investments'])} investments")
    return extracted_data

def save_mcp_data_files(extracted_data: Dict[str, Any], output_dir: str = "data/mock"):
    """Save extracted data as JSON files for MCP resources"""

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Save each data type as separate JSON file
    for data_type, data in extracted_data.items():
        file_path = os.path.join(output_dir, f"{data_type}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        print(f"💾 Saved {data_type} data to {file_path}")

def group_data_by_user(extracted_data: Dict[str, Any]) -> Dict[str, Dict[str, List]]:
    """Group all data by user_id for easy access in MCP resources"""

    user_data = {}

    # Initialize user data structure
    for user in extracted_data["users"]:
        user_id = user["id"]
        user_data[user_id] = {
            "user_info": user,
            "accounts": [],
            "transactions": [],
            "investments": []
        }

    # Group accounts by user
    for account in extracted_data["accounts"]:
        user_id = account["user_id"]
        if user_id in user_data:
            user_data[user_id]["accounts"].append(account)

    # Group transactions by user
    for txn in extracted_data["transactions"]:
        user_id = txn["user_id"]
        if user_id in user_data:
            user_data[user_id]["transactions"].append(txn)

    # Group investments by user
    for inv in extracted_data["investments"]:
        user_id = inv["user_id"]
        if user_id in user_data:
            user_data[user_id]["investments"].append(inv)

    return user_data

if __name__ == "__main__":
    # Extract database content
    print("🚀 Starting database extraction...")
    extracted_data = extract_database_content()

    if extracted_data:
        # Save as JSON files for MCP
        save_mcp_data_files(extracted_data)

        # Group by user and save
        user_grouped_data = group_data_by_user(extracted_data)

        with open("data/mock/user_grouped_data.json", 'w', encoding='utf-8') as f:
            json.dump(user_grouped_data, f, indent=2, ensure_ascii=False, default=str)
        print("💾 Saved user-grouped data to data/mock/user_grouped_data.json")

        print("✅ Database extraction completed successfully!")
        print("\n📊 Summary:")
        for data_type, data in extracted_data.items():
            print(f"  - {data_type}: {len(data)} records")
    else:
        print("❌ Database extraction failed!")