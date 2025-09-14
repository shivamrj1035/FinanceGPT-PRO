"""
Enhanced Database Service for FinanceGPT Pro
Handles complete user data management with Gemini-generated content
"""

import sqlite3
import json
import logging
import hashlib
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import os

logger = logging.getLogger(__name__)

class EnhancedDatabaseService:
    """
    Complete database service for user management and financial data
    """

    def __init__(self, db_path: str = "financebot.db"):
        # Use absolute path
        if not os.path.isabs(db_path):
            self.db_path = os.path.join(os.getcwd(), db_path)
        else:
            self.db_path = db_path

        logger.info(f"💾 Using database: {self.db_path}")
        self.init_complete_schema()

    def init_complete_schema(self):
        """Initialize complete database schema"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Drop existing tables for fresh start
                tables_to_drop = [
                    'ai_predictions', 'ai_insights', 'fraud_detections', 'user_ai_preferences',
                    'users', 'accounts', 'transactions', 'investments', 'goals', 'alerts'
                ]

                for table in tables_to_drop:
                    cursor.execute(f"DROP TABLE IF EXISTS {table}")

                # Users table with authentication
                cursor.execute("""
                    CREATE TABLE users (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        password_hash TEXT NOT NULL,
                        profile_data TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Accounts table
                cursor.execute("""
                    CREATE TABLE accounts (
                        id TEXT PRIMARY KEY,
                        user_id TEXT NOT NULL,
                        bank_name TEXT NOT NULL,
                        account_type TEXT NOT NULL,
                        account_number TEXT NOT NULL,
                        balance REAL NOT NULL,
                        currency TEXT DEFAULT 'INR',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                """)

                # Transactions table
                cursor.execute("""
                    CREATE TABLE transactions (
                        id TEXT PRIMARY KEY,
                        account_id TEXT NOT NULL,
                        user_id TEXT NOT NULL,
                        amount REAL NOT NULL,
                        merchant TEXT,
                        category TEXT,
                        description TEXT,
                        date TIMESTAMP NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (account_id) REFERENCES accounts (id),
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                """)

                # Investments table
                cursor.execute("""
                    CREATE TABLE investments (
                        id TEXT PRIMARY KEY,
                        user_id TEXT NOT NULL,
                        investment_type TEXT NOT NULL,
                        name TEXT NOT NULL,
                        amount REAL NOT NULL,
                        current_value REAL NOT NULL,
                        purchase_date TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                """)

                # Goals table
                cursor.execute("""
                    CREATE TABLE goals (
                        id TEXT PRIMARY KEY,
                        user_id TEXT NOT NULL,
                        name TEXT NOT NULL,
                        target_amount REAL NOT NULL,
                        current_amount REAL DEFAULT 0,
                        target_date TIMESTAMP,
                        status TEXT DEFAULT 'ACTIVE',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                """)

                # AI-related tables
                cursor.execute("""
                    CREATE TABLE ai_predictions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL,
                        prediction_type TEXT NOT NULL,
                        input_data TEXT,
                        prediction_result TEXT,
                        confidence_score REAL,
                        model_version TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                """)

                cursor.execute("""
                    CREATE TABLE ai_insights (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL,
                        insight_type TEXT NOT NULL,
                        context_data TEXT,
                        insights TEXT,
                        recommendations TEXT,
                        confidence_score REAL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                """)

                cursor.execute("""
                    CREATE TABLE fraud_detections (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL,
                        transaction_id TEXT,
                        transaction_data TEXT,
                        risk_score REAL,
                        risk_level TEXT,
                        risk_factors TEXT,
                        recommended_action TEXT,
                        ai_analysis TEXT,
                        model_version TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                """)

                # Create indexes for better performance
                cursor.execute("CREATE INDEX idx_users_email ON users (email)")
                cursor.execute("CREATE INDEX idx_accounts_user_id ON accounts (user_id)")
                cursor.execute("CREATE INDEX idx_transactions_user_id ON transactions (user_id)")
                cursor.execute("CREATE INDEX idx_transactions_date ON transactions (date)")
                cursor.execute("CREATE INDEX idx_ai_predictions_user_id ON ai_predictions (user_id)")

                conn.commit()
                logger.info("✅ Complete database schema initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize database schema: {e}")
            raise

    def hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()

    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        return hashlib.sha256(password.encode()).hexdigest() == password_hash

    async def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user against database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT id, name, email, password_hash, profile_data
                    FROM users WHERE email = ?
                """, (email,))

                user = cursor.fetchone()
                if user and self.verify_password(password, user['password_hash']):
                    return {
                        "id": user['id'],
                        "name": user['name'],
                        "email": user['email'],
                        "profile": json.loads(user['profile_data']) if user['profile_data'] else {}
                    }
                return None

        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return None

    async def create_user(self, user_data: Dict[str, Any]) -> bool:
        """Create a new user with complete financial profile"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Insert user
                cursor.execute("""
                    INSERT INTO users (id, name, email, password_hash, profile_data)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    user_data['id'],
                    user_data['name'],
                    user_data['email'],
                    self.hash_password(user_data['password']),
                    json.dumps(user_data.get('profile', {}))
                ))

                # Insert accounts
                for account in user_data.get('accounts', []):
                    cursor.execute("""
                        INSERT INTO accounts (id, user_id, bank_name, account_type, account_number, balance)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        account['id'],
                        user_data['id'],
                        account['bank_name'],
                        account['account_type'],
                        account['account_number'],
                        account['balance']
                    ))

                # Insert transactions
                for transaction in user_data.get('transactions', []):
                    cursor.execute("""
                        INSERT INTO transactions (id, account_id, user_id, amount, merchant, category, description, date)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        transaction['id'],
                        transaction['account_id'],
                        user_data['id'],
                        transaction['amount'],
                        transaction['merchant'],
                        transaction['category'],
                        transaction.get('description', ''),
                        transaction['date']
                    ))

                # Insert investments
                for investment in user_data.get('investments', []):
                    cursor.execute("""
                        INSERT INTO investments (id, user_id, investment_type, name, amount, current_value, purchase_date)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        investment['id'],
                        user_data['id'],
                        investment['type'],
                        investment['name'],
                        investment['amount'],
                        investment['current_value'],
                        investment.get('purchase_date')
                    ))

                # Insert goals
                for goal in user_data.get('goals', []):
                    cursor.execute("""
                        INSERT INTO goals (id, user_id, name, target_amount, current_amount, target_date)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        goal['id'],
                        user_data['id'],
                        goal['name'],
                        goal['target_amount'],
                        goal.get('current_amount', 0),
                        goal.get('target_date')
                    ))

                conn.commit()
                logger.info(f"✅ Created user {user_data['name']} with complete profile")

                # Verify creation
                cursor.execute("SELECT COUNT(*) FROM users WHERE id = ?", (user_data['id'],))
                count = cursor.fetchone()[0]
                logger.info(f"📊 User verification: {count} records found for {user_data['id']}")

                return True

        except Exception as e:
            logger.error(f"Failed to create user {user_data.get('name', 'Unknown')}: {e}")
            import traceback
            traceback.print_exc()
            return False

    async def get_user_accounts(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's accounts"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT * FROM accounts WHERE user_id = ?
                """, (user_id,))

                return [dict(row) for row in cursor.fetchall()]

        except Exception as e:
            logger.error(f"Failed to get accounts: {e}")
            return []

    async def get_user_transactions(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get user's transactions"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT * FROM transactions WHERE user_id = ?
                    ORDER BY date DESC LIMIT ?
                """, (user_id, limit))

                return [dict(row) for row in cursor.fetchall()]

        except Exception as e:
            logger.error(f"Failed to get transactions: {e}")
            return []

    async def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all users for admin purposes"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT id, name, email, created_at FROM users
                """)

                return [dict(row) for row in cursor.fetchall()]

        except Exception as e:
            logger.error(f"Failed to get users: {e}")
            return []


# Singleton instance
_enhanced_db_service = None

def get_enhanced_database_service() -> EnhancedDatabaseService:
    """Get singleton instance of enhanced database service"""
    global _enhanced_db_service
    if _enhanced_db_service is None:
        _enhanced_db_service = EnhancedDatabaseService()
    return _enhanced_db_service