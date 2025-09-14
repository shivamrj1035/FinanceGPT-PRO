"""
User Service - Business logic for user operations
"""

from sqlalchemy.orm import Session
from models import User, Account, Goal, Investment
from typing import Optional, Dict, Any, List
import hashlib
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class UserService:
    """
    Service class for user-related operations
    """

    @staticmethod
    def create_user(db: Session, user_data: Dict[str, Any]) -> User:
        """
        Create a new user
        """
        # Hash password
        if "password" in user_data:
            user_data["password_hash"] = hashlib.sha256(
                user_data.pop("password").encode()
            ).hexdigest()

        # Generate user ID
        last_user = db.query(User).order_by(User.id.desc()).first()
        user_id = f"USR{(last_user.id + 1):03d}" if last_user else "USR001"

        user = User(user_id=user_id, **user_data)
        db.add(user)
        db.commit()
        db.refresh(user)

        logger.info(f"Created new user: {user.email}")
        return user

    @staticmethod
    def authenticate_user(
        db: Session,
        email: str,
        password: str
    ) -> Optional[User]:
        """
        Authenticate user with email and password
        """
        user = db.query(User).filter_by(email=email).first()

        if not user:
            return None

        password_hash = hashlib.sha256(password.encode()).hexdigest()

        if user.password_hash != password_hash:
            return None

        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()

        return user

    @staticmethod
    def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
        """
        Get user by user_id
        """
        return db.query(User).filter_by(user_id=user_id).first()

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """
        Get user by email
        """
        return db.query(User).filter_by(email=email).first()

    @staticmethod
    def update_user(
        db: Session,
        user_id: str,
        update_data: Dict[str, Any]
    ) -> Optional[User]:
        """
        Update user information
        """
        user = db.query(User).filter_by(user_id=user_id).first()

        if not user:
            return None

        # Update fields
        for key, value in update_data.items():
            if hasattr(user, key) and key != "password":
                setattr(user, key, value)

        # Handle password update
        if "password" in update_data:
            user.password_hash = hashlib.sha256(
                update_data["password"].encode()
            ).hexdigest()

        user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    def get_user_financial_summary(
        db: Session,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Get user's complete financial summary
        """
        user = db.query(User).filter_by(user_id=user_id).first()

        if not user:
            return {}

        # Get accounts summary
        accounts = db.query(Account).filter_by(user_id=user_id).all()
        total_balance = sum(acc.balance for acc in accounts)
        total_debt = sum(
            acc.balance for acc in accounts
            if acc.balance < 0
        )

        # Get goals summary
        goals = db.query(Goal).filter_by(user_id=user_id).all()
        active_goals = [g for g in goals if g.is_active]
        goals_on_track = len([g for g in active_goals if g.status == "ON_TRACK"])

        # Get investments summary
        investments = db.query(Investment).filter_by(user_id=user_id).all()
        total_invested = sum(inv.invested_amount for inv in investments)
        current_value = sum(inv.current_value for inv in investments)
        total_returns = current_value - total_invested

        return {
            "user": {
                "name": user.name,
                "email": user.email,
                "credit_score": user.credit_score,
                "risk_tolerance": user.risk_tolerance,
                "monthly_income": user.monthly_income
            },
            "accounts": {
                "total_accounts": len(accounts),
                "total_balance": total_balance,
                "total_debt": abs(total_debt),
                "net_worth": total_balance + current_value
            },
            "goals": {
                "total_goals": len(goals),
                "active_goals": len(active_goals),
                "goals_on_track": goals_on_track,
                "goals_behind": len(active_goals) - goals_on_track
            },
            "investments": {
                "total_invested": total_invested,
                "current_value": current_value,
                "total_returns": total_returns,
                "returns_percentage": (
                    (total_returns / total_invested * 100)
                    if total_invested > 0 else 0
                )
            }
        }

    @staticmethod
    def calculate_financial_health_score(
        db: Session,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Calculate user's financial health score
        """
        summary = UserService.get_user_financial_summary(db, user_id)

        if not summary:
            return {"score": 0, "grade": "N/A"}

        score = 0
        factors = []

        # Credit score factor (30 points)
        credit_score = summary["user"]["credit_score"]
        if credit_score >= 750:
            score += 30
            factors.append({"factor": "credit_score", "points": 30, "status": "excellent"})
        elif credit_score >= 700:
            score += 20
            factors.append({"factor": "credit_score", "points": 20, "status": "good"})
        elif credit_score >= 650:
            score += 10
            factors.append({"factor": "credit_score", "points": 10, "status": "fair"})
        else:
            factors.append({"factor": "credit_score", "points": 0, "status": "poor"})

        # Savings rate factor (25 points)
        monthly_income = summary["user"]["monthly_income"]
        if monthly_income > 0:
            # Simplified calculation
            savings_rate = 0.2  # Assume 20% for demo
            if savings_rate >= 0.2:
                score += 25
                factors.append({"factor": "savings_rate", "points": 25, "status": "excellent"})
            elif savings_rate >= 0.1:
                score += 15
                factors.append({"factor": "savings_rate", "points": 15, "status": "good"})
            else:
                score += 5
                factors.append({"factor": "savings_rate", "points": 5, "status": "poor"})

        # Investment returns (20 points)
        returns_pct = summary["investments"]["returns_percentage"]
        if returns_pct >= 15:
            score += 20
            factors.append({"factor": "investment_returns", "points": 20, "status": "excellent"})
        elif returns_pct >= 8:
            score += 15
            factors.append({"factor": "investment_returns", "points": 15, "status": "good"})
        elif returns_pct >= 0:
            score += 10
            factors.append({"factor": "investment_returns", "points": 10, "status": "fair"})
        else:
            factors.append({"factor": "investment_returns", "points": 0, "status": "poor"})

        # Debt-to-income ratio (15 points)
        debt_ratio = abs(summary["accounts"]["total_debt"]) / monthly_income if monthly_income > 0 else 0
        if debt_ratio <= 0.3:
            score += 15
            factors.append({"factor": "debt_ratio", "points": 15, "status": "excellent"})
        elif debt_ratio <= 0.5:
            score += 10
            factors.append({"factor": "debt_ratio", "points": 10, "status": "good"})
        else:
            score += 5
            factors.append({"factor": "debt_ratio", "points": 5, "status": "high"})

        # Goals progress (10 points)
        if summary["goals"]["active_goals"] > 0:
            goals_success_rate = (
                summary["goals"]["goals_on_track"] /
                summary["goals"]["active_goals"]
            )
            if goals_success_rate >= 0.8:
                score += 10
                factors.append({"factor": "goals_progress", "points": 10, "status": "excellent"})
            elif goals_success_rate >= 0.5:
                score += 7
                factors.append({"factor": "goals_progress", "points": 7, "status": "good"})
            else:
                score += 3
                factors.append({"factor": "goals_progress", "points": 3, "status": "poor"})

        # Determine grade
        if score >= 90:
            grade = "A+"
            interpretation = "Excellent financial health"
        elif score >= 80:
            grade = "A"
            interpretation = "Very good financial health"
        elif score >= 70:
            grade = "B"
            interpretation = "Good financial health"
        elif score >= 60:
            grade = "C"
            interpretation = "Fair financial health"
        elif score >= 50:
            grade = "D"
            interpretation = "Poor financial health"
        else:
            grade = "F"
            interpretation = "Critical - immediate attention needed"

        return {
            "score": score,
            "grade": grade,
            "interpretation": interpretation,
            "factors": factors,
            "recommendations": UserService._get_health_recommendations(score, factors)
        }

    @staticmethod
    def _get_health_recommendations(score: int, factors: List[Dict]) -> List[str]:
        """
        Get recommendations based on health score
        """
        recommendations = []

        # Check each factor and provide recommendations
        for factor in factors:
            if factor["factor"] == "credit_score" and factor["status"] != "excellent":
                recommendations.append("Improve credit score by paying bills on time")

            if factor["factor"] == "savings_rate" and factor["status"] == "poor":
                recommendations.append("Increase monthly savings to at least 20% of income")

            if factor["factor"] == "investment_returns" and factor["status"] != "excellent":
                recommendations.append("Review and optimize your investment portfolio")

            if factor["factor"] == "debt_ratio" and factor["status"] == "high":
                recommendations.append("Focus on reducing high-interest debt")

            if factor["factor"] == "goals_progress" and factor["status"] == "poor":
                recommendations.append("Review and adjust your financial goals")

        return recommendations[:3]  # Return top 3 recommendations