"""
MCP Security Manager
Handles authentication, authorization, and encryption for financial data
"""

import hashlib
import hmac
import json
import jwt
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
import secrets

logger = logging.getLogger(__name__)

class SecurityManager:
    """
    Handles all security aspects of the MCP server
    Critical for financial data protection
    """

    def __init__(self, server):
        self.server = server
        self.jwt_secret = server.config.get("jwt_secret", "hackathon-secret-2025")
        self.jwt_algorithm = server.config.get("jwt_algorithm", "HS256")
        self.encryption_key = server.config.get("encryption_key", self._generate_encryption_key())
        if isinstance(self.encryption_key, str):
            # If it's a string, use it directly as Fernet expects base64 encoded key
            try:
                self.fernet = Fernet(self.encryption_key.encode())
            except:
                # Generate a proper key if the provided one is invalid
                self.encryption_key = Fernet.generate_key()
                self.fernet = Fernet(self.encryption_key)
        else:
            self.fernet = Fernet(self.encryption_key)

        # Session management
        self.active_sessions = {}
        self.api_keys = {}
        self.rate_limits = {}

        # For demo - pre-configured credentials
        self.demo_credentials = {
            "demo@financegpt.com": {
                "password_hash": self._hash_password("Demo@123"),
                "user_id": "USR001",
                "name": "Demo User",
                "role": "user"
            },
            "admin@financegpt.com": {
                "password_hash": self._hash_password("Admin@123"),
                "user_id": "ADMIN001",
                "name": "Admin User",
                "role": "admin"
            }
        }

    def _generate_encryption_key(self) -> bytes:
        """Generate a secure encryption key"""
        return Fernet.generate_key()

    def _hash_password(self, password: str) -> str:
        """Hash password using SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()

    async def initialize(self):
        """Initialize security components"""
        logger.info("🔐 Security Manager initialized")
        logger.info("🔑 Demo credentials ready")
        logger.info("🛡️ Encryption enabled")

    async def authenticate(self, request: Dict[str, Any], connection_id: str) -> bool:
        """
        Authenticate incoming request
        Returns True if authenticated, False otherwise
        """

        # Check if authentication is required
        method = request.get("method", "")

        # Public methods that don't require auth
        public_methods = ["system.ping", "system.info", "auth.login"]
        if method in public_methods:
            return True

        # Check for authentication token
        auth_header = request.get("headers", {}).get("authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
            return await self.verify_token(token)

        # Check for API key
        api_key = request.get("api_key")
        if api_key:
            return await self.verify_api_key(api_key)

        # Check session
        session_id = request.get("session_id")
        if session_id and session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            if datetime.now() < session["expires_at"]:
                return True

        # For demo - allow some requests without auth
        if self.server.config.get("environment") == "development":
            return True

        logger.warning(f"⚠️ Authentication failed for {connection_id[:8]}")
        return False

    async def check_permission(self, request: Dict[str, Any], connection_id: str) -> bool:
        """
        Check if user has permission to access requested resource
        """

        method = request.get("method", "")
        params = request.get("params", {})

        # Extract resource from method
        if method.startswith("resources."):
            resource_type = method.split(".")[1] if len(method.split(".")) > 1 else None
            user_id = params.get("user_id", "USR001")

            # Check permissions in mock data
            permissions = self.server.mock_data.get("permissions", [])
            for perm in permissions:
                if perm["user_id"] == user_id and perm["resource"] == resource_type:
                    if perm["access_level"] == "REVOKED":
                        logger.warning(f"🚫 Permission denied for {resource_type} to {user_id}")
                        return False

        return True

    async def verify_token(self, token: str) -> bool:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])

            # Check expiration
            if "exp" in payload:
                if datetime.fromtimestamp(payload["exp"]) < datetime.now():
                    return False

            return True
        except jwt.InvalidTokenError:
            return False

    async def verify_api_key(self, api_key: str) -> bool:
        """Verify API key"""
        return api_key in self.api_keys

    def generate_token(self, user_id: str, email: str, role: str = "user") -> str:
        """Generate JWT token for authenticated user"""
        payload = {
            "user_id": user_id,
            "email": email,
            "role": role,
            "iat": datetime.now(),
            "exp": datetime.now() + timedelta(hours=24)
        }

        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)

    def create_session(self, user_id: str, connection_id: str) -> str:
        """Create a new session"""
        session_id = secrets.token_urlsafe(32)

        self.active_sessions[session_id] = {
            "user_id": user_id,
            "connection_id": connection_id,
            "created_at": datetime.now(),
            "expires_at": datetime.now() + timedelta(hours=2),
            "last_activity": datetime.now()
        }

        return session_id

    def encrypt_data(self, data: Any) -> str:
        """Encrypt sensitive data"""
        if isinstance(data, dict) or isinstance(data, list):
            data = json.dumps(data)
        elif not isinstance(data, str):
            data = str(data)

        encrypted = self.fernet.encrypt(data.encode())
        return encrypted.decode()

    def decrypt_data(self, encrypted_data: str) -> Any:
        """Decrypt data"""
        try:
            decrypted = self.fernet.decrypt(encrypted_data.encode())
            data = decrypted.decode()

            # Try to parse as JSON
            try:
                return json.loads(data)
            except:
                return data
        except Exception as e:
            logger.error(f"❌ Decryption failed: {e}")
            return None

    async def check_rate_limit(self, connection_id: str) -> bool:
        """Check if connection has exceeded rate limit"""
        now = datetime.now()

        if connection_id not in self.rate_limits:
            self.rate_limits[connection_id] = {
                "requests": [],
                "blocked_until": None
            }

        limits = self.rate_limits[connection_id]

        # Check if currently blocked
        if limits["blocked_until"] and now < limits["blocked_until"]:
            return False

        # Clean old requests (older than 1 minute)
        cutoff = now - timedelta(minutes=1)
        limits["requests"] = [req for req in limits["requests"] if req > cutoff]

        # Check rate limit
        max_requests = self.server.config.get("rate_limit", {}).get("requests_per_minute", 100)
        if len(limits["requests"]) >= max_requests:
            # Block for 1 minute
            limits["blocked_until"] = now + timedelta(minutes=1)
            logger.warning(f"⚠️ Rate limit exceeded for {connection_id[:8]}")
            return False

        # Add current request
        limits["requests"].append(now)
        return True

    def sanitize_output(self, data: Any, user_role: str = "user") -> Any:
        """
        Sanitize output based on user role
        Remove sensitive information if needed
        """

        if isinstance(data, dict):
            # Remove sensitive fields for non-admin users
            if user_role != "admin":
                sensitive_fields = ["password", "secret", "api_key", "encryption_key"]
                for field in sensitive_fields:
                    if field in data:
                        data[field] = "***REDACTED***"

            # Recursively sanitize nested data
            for key, value in data.items():
                data[key] = self.sanitize_output(value, user_role)

        elif isinstance(data, list):
            data = [self.sanitize_output(item, user_role) for item in data]

        return data

    async def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user with email and password"""

        # Check demo credentials
        if email in self.demo_credentials:
            user = self.demo_credentials[email]
            password_hash = self._hash_password(password)

            if password_hash == user["password_hash"]:
                return {
                    "user_id": user["user_id"],
                    "email": email,
                    "name": user["name"],
                    "role": user["role"],
                    "token": self.generate_token(user["user_id"], email, user["role"])
                }

        return None

    def generate_api_key(self, user_id: str) -> str:
        """Generate API key for user"""
        api_key = f"fgpt_{secrets.token_urlsafe(32)}"

        self.api_keys[api_key] = {
            "user_id": user_id,
            "created_at": datetime.now(),
            "last_used": None,
            "usage_count": 0
        }

        return api_key

    def log_security_event(self, event_type: str, details: Dict[str, Any]):
        """Log security events for audit trail"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "details": details
        }

        # In production, this would go to a secure audit log
        logger.info(f"🔐 Security Event: {event_type} - {details}")

    async def validate_financial_transaction(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate financial transaction for security
        This is crucial for preventing fraud
        """

        validation_result = {
            "valid": True,
            "risks": [],
            "score": 0
        }

        # Check amount
        amount = abs(transaction.get("amount", 0))
        if amount > 100000:  # Large transaction
            validation_result["risks"].append("HIGH_AMOUNT")
            validation_result["score"] += 30

        # Check time
        hour = datetime.fromisoformat(transaction.get("date", datetime.now().isoformat())).hour
        if hour < 6 or hour > 23:
            validation_result["risks"].append("UNUSUAL_TIME")
            validation_result["score"] += 20

        # Check merchant
        merchant = transaction.get("merchant", "").upper()
        suspicious_keywords = ["CASINO", "GAMBLING", "CRYPTO", "FOREIGN"]
        for keyword in suspicious_keywords:
            if keyword in merchant:
                validation_result["risks"].append("SUSPICIOUS_MERCHANT")
                validation_result["score"] += 40
                break

        # Determine if transaction should be blocked
        if validation_result["score"] >= 60:
            validation_result["valid"] = False
            validation_result["action"] = "BLOCK"
        elif validation_result["score"] >= 30:
            validation_result["action"] = "REVIEW"
        else:
            validation_result["action"] = "ALLOW"

        return validation_result