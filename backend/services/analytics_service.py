"""
Analytics Service - Advanced financial analytics
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from models import Transaction, Account, Goal, Investment
from typing import Dict, Any, List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class AnalyticsService:
    """
    Service class for financial analytics
    """

    @staticmethod
    def calculate_cash_flow(
        db: Session,
        user_id: str,
        months: int = 6
    ) -> Dict[str, Any]:
        """
        Calculate cash flow analysis
        """
        # Get user's accounts
        accounts = db.query(Account).filter_by(user_id=user_id).all()
        account_ids = [acc.account_id for acc in accounts]

        # Get transactions for the period
        start_date = datetime.utcnow() - timedelta(days=months * 30)

        transactions = db.query(Transaction).filter(
            Transaction.account_id.in_(account_ids),
            Transaction.transaction_date >= start_date
        ).all()

        # Group by month
        monthly_cash_flow = {}

        for txn in transactions:
            month_key = txn.transaction_date.strftime("%Y-%m")

            if month_key not in monthly_cash_flow:
                monthly_cash_flow[month_key] = {
                    "income": 0,
                    "expenses": 0,
                    "net_flow": 0
                }

            if txn.amount > 0:
                monthly_cash_flow[month_key]["income"] += txn.amount
            else:
                monthly_cash_flow[month_key]["expenses"] += abs(txn.amount)

        # Calculate net flow
        for month in monthly_cash_flow:
            monthly_cash_flow[month]["net_flow"] = (
                monthly_cash_flow[month]["income"] -
                monthly_cash_flow[month]["expenses"]
            )

        # Calculate averages
        if monthly_cash_flow:
            avg_income = sum(
                m["income"] for m in monthly_cash_flow.values()
            ) / len(monthly_cash_flow)
            avg_expenses = sum(
                m["expenses"] for m in monthly_cash_flow.values()
            ) / len(monthly_cash_flow)
            avg_net_flow = avg_income - avg_expenses
        else:
            avg_income = avg_expenses = avg_net_flow = 0

        # Trend analysis
        months_list = sorted(monthly_cash_flow.keys())
        if len(months_list) >= 2:
            recent_month = monthly_cash_flow[months_list[-1]]
            previous_month = monthly_cash_flow[months_list[-2]]

            income_trend = (
                (recent_month["income"] - previous_month["income"]) /
                previous_month["income"] * 100
                if previous_month["income"] > 0 else 0
            )
            expense_trend = (
                (recent_month["expenses"] - previous_month["expenses"]) /
                previous_month["expenses"] * 100
                if previous_month["expenses"] > 0 else 0
            )
        else:
            income_trend = expense_trend = 0

        return {
            "monthly_data": monthly_cash_flow,
            "averages": {
                "income": avg_income,
                "expenses": avg_expenses,
                "net_flow": avg_net_flow
            },
            "trends": {
                "income_trend": income_trend,
                "expense_trend": expense_trend,
                "trend_direction": "improving" if income_trend > expense_trend else "declining"
            },
            "months_analyzed": months
        }

    @staticmethod
    def investment_performance_analysis(
        db: Session,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Analyze investment portfolio performance
        """
        investments = db.query(Investment).filter_by(
            user_id=user_id,
            is_active=True
        ).all()

        if not investments:
            return {
                "total_invested": 0,
                "current_value": 0,
                "total_returns": 0,
                "portfolio_analysis": {}
            }

        # Calculate totals
        total_invested = sum(inv.invested_amount for inv in investments)
        current_value = sum(inv.current_value for inv in investments)
        total_returns = current_value - total_invested

        # Category breakdown
        category_breakdown = {}
        for inv in investments:
            category = inv.category
            if category not in category_breakdown:
                category_breakdown[category] = {
                    "invested": 0,
                    "current_value": 0,
                    "returns": 0,
                    "allocation_percentage": 0,
                    "count": 0
                }

            category_breakdown[category]["invested"] += inv.invested_amount
            category_breakdown[category]["current_value"] += inv.current_value
            category_breakdown[category]["returns"] += (
                inv.current_value - inv.invested_amount
            )
            category_breakdown[category]["count"] += 1

        # Calculate allocation percentages
        for category in category_breakdown:
            category_breakdown[category]["allocation_percentage"] = (
                category_breakdown[category]["current_value"] / current_value * 100
                if current_value > 0 else 0
            )
            category_breakdown[category]["returns_percentage"] = (
                (category_breakdown[category]["returns"] /
                 category_breakdown[category]["invested"] * 100)
                if category_breakdown[category]["invested"] > 0 else 0
            )

        # Best and worst performers
        sorted_investments = sorted(
            investments,
            key=lambda x: x.returns_percentage,
            reverse=True
        )

        best_performers = [
            {
                "name": inv.name,
                "returns_percentage": inv.returns_percentage,
                "returns_amount": inv.returns_amount
            }
            for inv in sorted_investments[:3]
        ]

        worst_performers = [
            {
                "name": inv.name,
                "returns_percentage": inv.returns_percentage,
                "returns_amount": inv.returns_amount
            }
            for inv in sorted_investments[-3:] if inv.returns_percentage < 0
        ]

        # Risk analysis
        risk_distribution = {
            "LOW": 0,
            "MODERATE": 0,
            "HIGH": 0,
            "VERY_HIGH": 0
        }

        for inv in investments:
            risk_level = inv.risk_level
            if risk_level in risk_distribution:
                risk_distribution[risk_level] += inv.current_value

        # Calculate risk percentages
        for risk in risk_distribution:
            risk_distribution[risk] = (
                risk_distribution[risk] / current_value * 100
                if current_value > 0 else 0
            )

        return {
            "total_invested": total_invested,
            "current_value": current_value,
            "total_returns": total_returns,
            "returns_percentage": (
                total_returns / total_invested * 100
                if total_invested > 0 else 0
            ),
            "category_breakdown": category_breakdown,
            "best_performers": best_performers,
            "worst_performers": worst_performers,
            "risk_distribution": risk_distribution,
            "portfolio_health": AnalyticsService._assess_portfolio_health(
                category_breakdown,
                risk_distribution
            )
        }

    @staticmethod
    def _assess_portfolio_health(
        category_breakdown: Dict,
        risk_distribution: Dict
    ) -> Dict[str, Any]:
        """
        Assess portfolio health
        """
        health_score = 100
        issues = []
        recommendations = []

        # Check diversification
        if len(category_breakdown) < 3:
            health_score -= 20
            issues.append("Low diversification")
            recommendations.append("Diversify across more asset categories")

        # Check risk balance
        high_risk = risk_distribution.get("HIGH", 0) + risk_distribution.get("VERY_HIGH", 0)
        if high_risk > 50:
            health_score -= 15
            issues.append("High risk concentration")
            recommendations.append("Balance portfolio with low-risk investments")

        # Check equity allocation (age-based)
        # Simplified: assume user is 30 years old
        ideal_equity = 70  # 100 - age
        actual_equity = category_breakdown.get("EQUITY", {}).get("allocation_percentage", 0)

        if abs(actual_equity - ideal_equity) > 20:
            health_score -= 10
            issues.append("Equity allocation not optimal for age")
            recommendations.append(f"Adjust equity allocation to around {ideal_equity}%")

        return {
            "score": health_score,
            "status": "healthy" if health_score >= 70 else "needs_attention",
            "issues": issues,
            "recommendations": recommendations
        }

    @staticmethod
    def goal_progress_analysis(
        db: Session,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Analyze progress towards financial goals
        """
        goals = db.query(Goal).filter_by(
            user_id=user_id,
            is_active=True
        ).all()

        if not goals:
            return {
                "total_goals": 0,
                "goals_analysis": []
            }

        goals_analysis = []

        for goal in goals:
            # Calculate time progress
            total_days = (goal.target_date - goal.start_date).days
            elapsed_days = (datetime.utcnow() - goal.start_date).days
            time_progress = (elapsed_days / total_days * 100) if total_days > 0 else 0

            # Calculate required monthly savings
            months_remaining = (goal.target_date - datetime.utcnow()).days / 30
            remaining_amount = goal.target_amount - goal.current_amount

            if months_remaining > 0:
                required_monthly = remaining_amount / months_remaining
            else:
                required_monthly = 0

            # Determine if on track
            if goal.progress_percentage >= time_progress - 5:
                status = "ON_TRACK"
                health = "good"
            elif goal.progress_percentage >= time_progress - 15:
                status = "SLIGHTLY_BEHIND"
                health = "fair"
            else:
                status = "BEHIND"
                health = "poor"

            goals_analysis.append({
                "goal_name": goal.name,
                "category": goal.category,
                "priority": goal.priority,
                "target_amount": goal.target_amount,
                "current_amount": goal.current_amount,
                "remaining_amount": remaining_amount,
                "progress_percentage": goal.progress_percentage,
                "time_progress_percentage": time_progress,
                "status": status,
                "health": health,
                "required_monthly_savings": required_monthly,
                "current_monthly_contribution": goal.monthly_contribution,
                "days_remaining": (goal.target_date - datetime.utcnow()).days,
                "achievability": "achievable" if required_monthly <= goal.monthly_contribution * 1.5 else "challenging"
            })

        # Summary statistics
        on_track_count = len([g for g in goals_analysis if g["status"] == "ON_TRACK"])
        behind_count = len([g for g in goals_analysis if g["status"] == "BEHIND"])
        total_target = sum(g["target_amount"] for g in goals_analysis)
        total_saved = sum(g["current_amount"] for g in goals_analysis)

        return {
            "total_goals": len(goals),
            "on_track": on_track_count,
            "behind": behind_count,
            "total_target_amount": total_target,
            "total_saved_amount": total_saved,
            "overall_progress": (total_saved / total_target * 100) if total_target > 0 else 0,
            "goals_analysis": goals_analysis,
            "recommendations": AnalyticsService._get_goal_recommendations(goals_analysis)
        }

    @staticmethod
    def _get_goal_recommendations(goals_analysis: List[Dict]) -> List[str]:
        """
        Generate goal-based recommendations
        """
        recommendations = []

        # Check for behind goals
        behind_goals = [g for g in goals_analysis if g["status"] == "BEHIND"]
        if behind_goals:
            for goal in behind_goals[:2]:  # Top 2 behind goals
                increase_needed = goal["required_monthly_savings"] - goal["current_monthly_contribution"]
                if increase_needed > 0:
                    recommendations.append(
                        f"Increase monthly contribution for '{goal['goal_name']}' by ₹{increase_needed:,.0f}"
                    )

        # Check for unrealistic goals
        challenging_goals = [g for g in goals_analysis if g["achievability"] == "challenging"]
        if challenging_goals:
            recommendations.append(
                f"Consider extending timeline for {len(challenging_goals)} challenging goal(s)"
            )

        # Suggest prioritization
        high_priority_behind = [
            g for g in goals_analysis
            if g["priority"] == "HIGH" and g["status"] != "ON_TRACK"
        ]
        if high_priority_behind:
            recommendations.append(
                "Focus on high-priority goals that are falling behind"
            )

        return recommendations[:3]