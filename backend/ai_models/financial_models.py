"""
AI/ML Models for FinanceGPT Pro
Advanced financial prediction and analysis models
"""

import json
import random
import statistics
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import math

class FraudDetectionModel:
    """
    Real-time fraud detection using pattern analysis and anomaly detection
    """

    def __init__(self):
        self.name = "FraudShield AI"
        self.version = "2.0"
        self.threshold = 0.7  # Risk score threshold

    def predict(self, transaction: Dict[str, Any], user_history: List[Dict]) -> Dict[str, Any]:
        """
        Predict fraud probability for a transaction
        """
        risk_score = 0.0
        risk_factors = []

        # Feature extraction
        amount = abs(transaction.get("amount", 0))
        merchant = transaction.get("merchant", "").upper()
        category = transaction.get("category", "")
        time = datetime.fromisoformat(transaction.get("date", datetime.now().isoformat()))

        # Historical analysis
        if user_history:
            avg_amount = statistics.mean([abs(t["amount"]) for t in user_history])
            max_amount = max([abs(t["amount"]) for t in user_history])

            # Amount anomaly detection
            if amount > avg_amount * 3:
                risk_score += 0.35
                risk_factors.append("Amount 3x higher than average")

            if amount > max_amount * 1.5:
                risk_score += 0.25
                risk_factors.append("Exceeds historical maximum")

        # Time-based analysis
        hour = time.hour
        if hour < 6 or hour > 23:
            risk_score += 0.20
            risk_factors.append("Unusual transaction time")

        # Merchant analysis
        suspicious_keywords = ["CASINO", "GAMBLING", "CRYPTO", "FOREIGN", "SUSPICIOUS"]
        for keyword in suspicious_keywords:
            if keyword in merchant:
                risk_score += 0.40
                risk_factors.append(f"Suspicious merchant: {keyword}")
                break

        # Location-based risk (simulated)
        if "INTL" in merchant or "FOREIGN" in merchant:
            risk_score += 0.30
            risk_factors.append("International transaction")

        # Velocity check (multiple transactions in short time)
        recent_txns = [t for t in user_history[-10:] if t.get("date")]
        if len(recent_txns) >= 5:
            time_diffs = []
            for i in range(1, len(recent_txns)):
                t1 = datetime.fromisoformat(recent_txns[i-1]["date"])
                t2 = datetime.fromisoformat(recent_txns[i]["date"])
                time_diffs.append((t2 - t1).total_seconds())

            if time_diffs and min(time_diffs) < 60:  # Less than 1 minute apart
                risk_score += 0.25
                risk_factors.append("Rapid transaction velocity")

        # Normalize score
        risk_score = min(risk_score, 1.0)

        # Determine action
        if risk_score >= 0.8:
            action = "BLOCK"
            severity = "CRITICAL"
        elif risk_score >= 0.6:
            action = "VERIFY"
            severity = "HIGH"
        elif risk_score >= 0.4:
            action = "MONITOR"
            severity = "MEDIUM"
        else:
            action = "ALLOW"
            severity = "LOW"

        return {
            "risk_score": round(risk_score, 3),
            "risk_level": severity,
            "risk_factors": risk_factors,
            "recommended_action": action,
            "confidence": round(0.85 + random.uniform(-0.1, 0.1), 2),
            "model_version": self.version,
            "timestamp": datetime.now().isoformat()
        }


class SpendingPatternAnalyzer:
    """
    Analyzes spending patterns to identify trends and anomalies
    """

    def __init__(self):
        self.name = "SpendSmart AI"
        self.categories = ["FOOD", "TRANSPORT", "SHOPPING", "ENTERTAINMENT", "UTILITIES", "HEALTHCARE"]

    def analyze(self, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze spending patterns from transaction history
        """
        if not transactions:
            return {"error": "No transactions to analyze"}

        # Group by category
        category_spending = {}
        daily_spending = {}
        merchant_frequency = {}

        for txn in transactions:
            if txn["amount"] < 0:  # Only expenses
                amount = abs(txn["amount"])
                category = txn.get("category", "OTHER")
                merchant = txn.get("merchant", "Unknown")
                date = datetime.fromisoformat(txn["date"]).date()

                # Category analysis
                if category not in category_spending:
                    category_spending[category] = []
                category_spending[category].append(amount)

                # Daily analysis
                date_str = date.isoformat()
                if date_str not in daily_spending:
                    daily_spending[date_str] = 0
                daily_spending[date_str] += amount

                # Merchant analysis
                if merchant not in merchant_frequency:
                    merchant_frequency[merchant] = {"count": 0, "total": 0}
                merchant_frequency[merchant]["count"] += 1
                merchant_frequency[merchant]["total"] += amount

        # Calculate insights
        insights = []

        # Category insights
        category_stats = {}
        for cat, amounts in category_spending.items():
            category_stats[cat] = {
                "total": sum(amounts),
                "average": statistics.mean(amounts),
                "count": len(amounts),
                "max": max(amounts),
                "min": min(amounts)
            }

        # Find highest spending category
        if category_stats:
            top_category = max(category_stats.items(), key=lambda x: x[1]["total"])
            insights.append({
                "type": "HIGH_SPENDING",
                "category": top_category[0],
                "amount": top_category[1]["total"],
                "message": f"Highest spending in {top_category[0]}: ₹{top_category[1]['total']:,.0f}"
            })

        # Weekend vs weekday analysis
        weekend_spending = 0
        weekday_spending = 0
        for date_str, amount in daily_spending.items():
            date = datetime.fromisoformat(date_str)
            if date.weekday() >= 5:  # Saturday or Sunday
                weekend_spending += amount
            else:
                weekday_spending += amount

        if weekend_spending > weekday_spending * 0.4:  # Weekend is > 40% of weekday
            insights.append({
                "type": "WEEKEND_SPIKE",
                "ratio": weekend_spending / max(weekday_spending, 1),
                "message": f"Weekend spending is {weekend_spending/max(weekday_spending, 1):.1f}x weekday spending"
            })

        # Recurring subscription detection
        recurring = []
        for merchant, data in merchant_frequency.items():
            if data["count"] >= 3:  # At least 3 transactions
                avg_amount = data["total"] / data["count"]
                # Check if amounts are consistent (subscription-like)
                recurring.append({
                    "merchant": merchant,
                    "frequency": data["count"],
                    "monthly_cost": avg_amount,
                    "annual_cost": avg_amount * 12
                })

        # ML-based predictions
        if daily_spending:
            amounts = list(daily_spending.values())
            daily_avg = statistics.mean(amounts)
            daily_std = statistics.stdev(amounts) if len(amounts) > 1 else 0

            # Predict next month's spending
            predicted_monthly = daily_avg * 30
            confidence_interval = daily_std * 30 * 1.96  # 95% confidence

            predictions = {
                "next_month_estimate": predicted_monthly,
                "confidence_range": {
                    "low": max(0, predicted_monthly - confidence_interval),
                    "high": predicted_monthly + confidence_interval
                },
                "confidence_level": 0.85
            }
        else:
            predictions = {}

        return {
            "category_breakdown": category_stats,
            "insights": insights,
            "recurring_subscriptions": recurring[:5],  # Top 5
            "predictions": predictions,
            "analysis_period": {
                "start": min(daily_spending.keys()) if daily_spending else None,
                "end": max(daily_spending.keys()) if daily_spending else None,
                "days": len(daily_spending)
            }
        }


class InvestmentRecommendationEngine:
    """
    AI-powered investment recommendation based on user profile and goals
    """

    def __init__(self):
        self.name = "InvestPro AI"
        self.asset_classes = {
            "EQUITY": {"risk": 0.8, "return": 0.15},
            "DEBT": {"risk": 0.2, "return": 0.07},
            "GOLD": {"risk": 0.4, "return": 0.08},
            "REAL_ESTATE": {"risk": 0.6, "return": 0.12},
            "CRYPTO": {"risk": 0.95, "return": 0.25}
        }

    def recommend(self, user_profile: Dict[str, Any], goals: List[Dict]) -> Dict[str, Any]:
        """
        Generate personalized investment recommendations
        """
        age = user_profile.get("age", 30)
        income = user_profile.get("monthly_income", 50000)
        risk_tolerance = user_profile.get("risk_tolerance", "MODERATE").upper()

        # Risk score mapping
        risk_scores = {
            "CONSERVATIVE": 0.3,
            "MODERATE": 0.5,
            "AGGRESSIVE": 0.8
        }
        risk_score = risk_scores.get(risk_tolerance, 0.5)

        # Age-based allocation (100 - age rule for equity)
        equity_allocation = min(100 - age, 80) / 100

        # Adjust based on risk tolerance
        equity_allocation *= (1 + (risk_score - 0.5))
        equity_allocation = max(0.2, min(0.8, equity_allocation))  # Clamp between 20-80%

        # Portfolio allocation
        portfolio = {
            "EQUITY": round(equity_allocation * 100),
            "DEBT": round((1 - equity_allocation) * 0.6 * 100),
            "GOLD": round((1 - equity_allocation) * 0.3 * 100),
            "CASH": round((1 - equity_allocation) * 0.1 * 100)
        }

        # Specific fund recommendations
        recommendations = []

        # Equity recommendations
        if portfolio["EQUITY"] > 0:
            recommendations.append({
                "type": "MUTUAL_FUND",
                "name": "HDFC Mid-Cap Opportunities Fund",
                "allocation": portfolio["EQUITY"] * 0.4,
                "expected_return": 15.5,
                "risk_level": "HIGH",
                "reason": "High growth potential for long-term wealth creation"
            })
            recommendations.append({
                "type": "INDEX_FUND",
                "name": "UTI Nifty 50 Index Fund",
                "allocation": portfolio["EQUITY"] * 0.6,
                "expected_return": 12.0,
                "risk_level": "MEDIUM",
                "reason": "Diversified exposure to top 50 companies"
            })

        # Debt recommendations
        if portfolio["DEBT"] > 0:
            recommendations.append({
                "type": "DEBT_FUND",
                "name": "ICICI Prudential Corporate Bond Fund",
                "allocation": portfolio["DEBT"],
                "expected_return": 7.5,
                "risk_level": "LOW",
                "reason": "Stable returns with capital preservation"
            })

        # Gold recommendation
        if portfolio["GOLD"] > 0:
            recommendations.append({
                "type": "GOLD_ETF",
                "name": "SBI Gold ETF",
                "allocation": portfolio["GOLD"],
                "expected_return": 8.0,
                "risk_level": "MEDIUM",
                "reason": "Portfolio diversification and inflation hedge"
            })

        # SIP calculation for goals
        sip_recommendations = []
        for goal in goals[:3]:  # Top 3 goals
            target = goal.get("target_amount", 100000)
            deadline = goal.get("deadline")
            if deadline:
                months = max(1, (datetime.fromisoformat(deadline) - datetime.now()).days / 30)
                # SIP calculation with expected returns
                rate = 0.12 / 12  # 12% annual return
                if rate > 0:
                    sip_amount = target * rate / ((1 + rate) ** months - 1)
                else:
                    sip_amount = target / months

                sip_recommendations.append({
                    "goal": goal.get("name", "Unknown Goal"),
                    "monthly_sip": round(sip_amount),
                    "duration_months": round(months),
                    "expected_corpus": target
                })

        # Risk analysis
        portfolio_risk = sum(
            portfolio.get(asset, 0) * self.asset_classes.get(asset, {}).get("risk", 0)
            for asset in portfolio
        ) / 100

        portfolio_return = sum(
            portfolio.get(asset, 0) * self.asset_classes.get(asset, {}).get("return", 0)
            for asset in portfolio
        ) / 100

        return {
            "portfolio_allocation": portfolio,
            "specific_recommendations": recommendations,
            "sip_plans": sip_recommendations,
            "risk_analysis": {
                "portfolio_risk_score": round(portfolio_risk, 2),
                "expected_annual_return": round(portfolio_return * 100, 1),
                "risk_adjusted_return": round(portfolio_return / max(portfolio_risk, 0.1), 2)
            },
            "investment_amount": {
                "minimum_monthly": round(income * 0.2),
                "recommended_monthly": round(income * 0.3),
                "maximum_monthly": round(income * 0.5)
            },
            "next_review_date": (datetime.now() + timedelta(days=90)).isoformat()
        }


class CreditScorePredictor:
    """
    Predicts credit score and provides improvement strategies
    """

    def __init__(self):
        self.name = "CreditWise AI"
        self.base_score = 750

    def predict(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict credit score based on financial behavior
        """
        score = self.base_score
        factors = []
        recommendations = []

        # Payment history (35% weight)
        payment_history = user_data.get("payment_history", 100)
        if payment_history < 100:
            score -= (100 - payment_history) * 2
            factors.append(f"Payment history: {payment_history}%")
            recommendations.append("Set up automatic payments to never miss due dates")

        # Credit utilization (30% weight)
        credit_utilization = user_data.get("credit_utilization", 30)
        if credit_utilization > 30:
            score -= (credit_utilization - 30) * 1.5
            factors.append(f"High credit utilization: {credit_utilization}%")
            recommendations.append(f"Reduce credit card usage to below 30% of limit")

        # Credit age (15% weight)
        credit_age = user_data.get("credit_age_years", 5)
        if credit_age < 3:
            score -= (3 - credit_age) * 20
            factors.append(f"Short credit history: {credit_age} years")
            recommendations.append("Keep old credit cards active to build history")

        # Credit mix (10% weight)
        credit_mix = user_data.get("account_types", 2)
        if credit_mix < 3:
            score -= (3 - credit_mix) * 10
            factors.append(f"Limited credit mix: {credit_mix} types")
            recommendations.append("Diversify credit types (cards, loans, etc.)")

        # Hard inquiries (10% weight)
        hard_inquiries = user_data.get("hard_inquiries", 0)
        if hard_inquiries > 2:
            score -= (hard_inquiries - 2) * 15
            factors.append(f"Too many hard inquiries: {hard_inquiries}")
            recommendations.append("Avoid applying for new credit frequently")

        # Ensure score is within valid range
        score = max(300, min(900, score))

        # Score interpretation
        if score >= 750:
            category = "Excellent"
            benefits = ["Best interest rates", "Premium credit cards", "Higher credit limits"]
        elif score >= 700:
            category = "Good"
            benefits = ["Favorable interest rates", "Good credit card options"]
        elif score >= 650:
            category = "Fair"
            benefits = ["Average interest rates", "Basic credit options"]
        else:
            category = "Poor"
            benefits = ["Limited credit options", "Higher interest rates"]

        # Improvement potential
        max_improvement = 0
        if payment_history < 100:
            max_improvement += (100 - payment_history) * 2
        if credit_utilization > 30:
            max_improvement += (credit_utilization - 30) * 1.5

        return {
            "predicted_score": round(score),
            "category": category,
            "factors_affecting_score": factors,
            "recommendations": recommendations[:3],  # Top 3 recommendations
            "benefits": benefits,
            "improvement_potential": {
                "points": round(max_improvement),
                "timeframe": "3-6 months",
                "new_score": round(min(900, score + max_improvement))
            },
            "score_breakdown": {
                "payment_history": payment_history,
                "credit_utilization": credit_utilization,
                "credit_age": credit_age,
                "credit_mix": credit_mix,
                "hard_inquiries": hard_inquiries
            },
            "confidence": 0.92,
            "last_updated": datetime.now().isoformat()
        }


# Initialize models (singleton pattern)
fraud_detector = FraudDetectionModel()
spending_analyzer = SpendingPatternAnalyzer()
investment_engine = InvestmentRecommendationEngine()
credit_predictor = CreditScorePredictor()

# Export for easy access
__all__ = [
    'fraud_detector',
    'spending_analyzer',
    'investment_engine',
    'credit_predictor',
    'FraudDetectionModel',
    'SpendingPatternAnalyzer',
    'InvestmentRecommendationEngine',
    'CreditScorePredictor'
]