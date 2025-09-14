"""
Simple Authentication Service for FinanceGPT Pro
Works with existing database without reinitializing schema
"""

import sqlite3
import hashlib
import logging
from typing import Dict, Any, List, Optional
import os

logger = logging.getLogger(__name__)

class SimpleAuthService:
    """
    Simple authentication service that works with existing database
    """

    def __init__(self, db_path: str = "financebot.db"):
        if not os.path.isabs(db_path):
            self.db_path = os.path.join(os.getcwd(), db_path)
        else:
            self.db_path = db_path

        logger.info(f"🔐 Auth service using database: {self.db_path}")

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
                    import json
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

    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT id, name, email, profile_data FROM users WHERE id = ?
                """, (user_id,))

                user = cursor.fetchone()
                if user:
                    import json
                    return {
                        "id": user['id'],
                        "name": user['name'],
                        "email": user['email'],
                        "profile": json.loads(user['profile_data']) if user['profile_data'] else {}
                    }
                return None

        except Exception as e:
            logger.error(f"Failed to get user: {e}")
            return None

    async def get_user_investments(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's investments"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT * FROM investments WHERE user_id = ?
                """, (user_id,))

                return [dict(row) for row in cursor.fetchall()]

        except Exception as e:
            logger.error(f"Failed to get investments: {e}")
            return []

# Singleton instance
_auth_service = None

def get_auth_service() -> SimpleAuthService:
    """Get singleton instance of auth service"""
    global _auth_service
    if _auth_service is None:
        _auth_service = SimpleAuthService()
    return _auth_service