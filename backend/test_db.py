#!/usr/bin/env python3

import asyncio
import sys
import os
sys.path.append('.')

from api.enhanced_database_service import get_enhanced_database_service

async def test_database():
    import os
    db_path = os.path.join(os.getcwd(), "financebot.db")
    print(f"🔍 Looking for database at: {db_path}")

    db = get_enhanced_database_service()
    users = await db.get_all_users()

    print(f"📊 Found {len(users)} users in database:")
    for user in users:
        print(f"  - {user['name']} ({user['email']}) - Created: {user['created_at']}")

        # Get user accounts
        accounts = await db.get_user_accounts(user['id'])
        print(f"    📱 Accounts: {len(accounts)}")

        # Get user transactions
        transactions = await db.get_user_transactions(user['id'], 5)
        print(f"    💳 Transactions: {len(transactions)} (showing 5)")

        print()

if __name__ == "__main__":
    asyncio.run(test_database())