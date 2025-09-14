"""
API Dependencies and Authentication
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer()

# JWT Configuration
JWT_SECRET = "hackathon-secret-2025"
JWT_ALGORITHM = "HS256"

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    Validate JWT token and return current user
    """
    token = credentials.credentials

    try:
        # Decode JWT token
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

        # Extract user information
        user = {
            "user_id": payload.get("user_id"),
            "email": payload.get("email"),
            "role": payload.get("role", "user")
        }

        if not user["user_id"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[Dict[str, Any]]:
    """
    Get user if authenticated, otherwise return None
    """
    if not credentials:
        return None

    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None

async def require_admin(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Require admin role
    """
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

class RateLimiter:
    """
    Simple in-memory rate limiter
    """

    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests = {}

    async def check_rate_limit(self, identifier: str) -> bool:
        """
        Check if request is within rate limit
        """
        from datetime import datetime, timedelta

        now = datetime.now()
        minute_ago = now - timedelta(minutes=1)

        # Clean old requests
        if identifier in self.requests:
            self.requests[identifier] = [
                req for req in self.requests[identifier]
                if req > minute_ago
            ]
        else:
            self.requests[identifier] = []

        # Check limit
        if len(self.requests[identifier]) >= self.requests_per_minute:
            return False

        # Add current request
        self.requests[identifier].append(now)
        return True

# Global rate limiter instance
rate_limiter = RateLimiter(requests_per_minute=100)

async def check_rate_limit(
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """
    Check rate limit for current user or IP
    """
    identifier = current_user["user_id"] if current_user else "anonymous"

    if not await rate_limiter.check_rate_limit(identifier):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later."
        )