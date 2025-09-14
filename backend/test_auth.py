#!/usr/bin/env python3

import asyncio
import sys
import os
sys.path.append('.')

from api.simple_auth_service import get_auth_service

async def test_authentication():
    db = get_auth_service()

    # Test users
    test_credentials = [
        ("aarav.sharma@gmail.com", "demo123"),
        ("priya.patel@gmail.com", "demo123"),
        ("rajesh.gupta@business.com", "demo123"),
        ("wrong@email.com", "demo123"),
        ("aarav.sharma@gmail.com", "wrongpassword")
    ]

    print("🔐 Testing Authentication:")
    for email, password in test_credentials:
        user = await db.authenticate_user(email, password)
        if user:
            print(f"✅ {email} - Success: {user['name']}")

            # Get user's financial data
            accounts = await db.get_user_accounts(user['id'])
            transactions = await db.get_user_transactions(user['id'], 5)

            print(f"   💰 Accounts: {len(accounts)}")
            for acc in accounts[:2]:  # Show first 2 accounts
                print(f"     - {acc['bank_name']} {acc['account_type']}: ₹{acc['balance']:,.0f}")

            print(f"   💳 Recent Transactions: {len(transactions)}")
            for txn in transactions[:3]:  # Show first 3 transactions
                sign = "+" if txn['amount'] > 0 else ""
                print(f"     - {txn['merchant']}: {sign}₹{txn['amount']:,.0f}")

            print()
        else:
            print(f"❌ {email} - Authentication failed")

if __name__ == "__main__":
    asyncio.run(test_authentication())