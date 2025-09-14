#!/usr/bin/env python3

import sqlite3
import hashlib
import uuid
from datetime import datetime

# Connect directly to database
db_path = "financebot.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create a test user directly
user_id = f"USR_TEST_{uuid.uuid4().hex[:8].upper()}"
name = "Test User"
email = "test@finara.com"
password_hash = hashlib.sha256("demo123".encode()).hexdigest()

try:
    # Insert test user
    cursor.execute("""
        INSERT INTO users (id, name, email, password_hash, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, name, email, password_hash, datetime.now().isoformat()))

    # Insert test account
    cursor.execute("""
        INSERT INTO accounts (id, user_id, bank_name, account_type, account_number, balance)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (f"ACC_TEST_001", user_id, "Test Bank", "SAVINGS", "****1234", 100000.0))

    conn.commit()
    print(f"✅ Created test user: {name} ({email})")

    # Verify
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    print(f"📊 Total users in database: {user_count}")

    cursor.execute("SELECT name, email FROM users")
    users = cursor.fetchall()
    for user in users:
        print(f"  - {user[0]} ({user[1]})")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

finally:
    conn.close()