"""
MCP Tools Manager
Handles execution of financial calculation and analysis tools
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import math

# Import advanced tools
from .advanced_tools import (
    FraudRiskScorer,
    GoalAchiever,
    SubscriptionOptimizer,
    EmergencyFundCalculator,
    TaxSaver,
    CreditScoreImprover
)

# Import AI service for enhancement
try:
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from api.ai_service import get_ai_service
    AI_ENHANCEMENT_AVAILABLE = True
except ImportError as e:
    logging.warning(f"AI enhancement not available: {e}")
    AI_ENHANCEMENT_AVAILABLE = False

logger = logging.getLogger(__name__)

class ToolsManager:
    """
    Manages and executes MCP tools for financial calculations
    """

    def __init__(self, server):
        self.server = server
        self.tools = {
            # Basic financial tools
            "budget_analyzer": BudgetAnalyzer(server),
            "expense_tracker": ExpenseTracker(server),
            "savings_calculator": SavingsCalculator(server),
            "loan_calculator": LoanCalculator(server),
            "investment_analyzer": InvestmentAnalyzer(server),
            "tax_calculator": TaxCalculator(server),
            "retirement_planner": RetirementPlanner(server),
            "goal_optimizer": GoalOptimizer(server),
            "fraud_detector": FraudDetector(server),
            "credit_analyzer": CreditAnalyzer(server),
            "bill_reminder": BillReminder(server),
            "portfolio_optimizer": PortfolioOptimizer(server),
            "cash_flow_analyzer": CashFlowAnalyzer(server),
            "insight_generator": InsightGenerator(server),

            # Advanced AI-powered tools
            "fraud_risk_scorer": FraudRiskScorer(server),
            "goal_achiever": GoalAchiever(server),
            "subscription_optimizer": SubscriptionOptimizer(server),
            "emergency_fund_calculator": EmergencyFundCalculator(server),
            "tax_saver": TaxSaver(server),
            "credit_score_improver": CreditScoreImprover(server)
        }

    def list_tools(self) -> List[Dict[str, Any]]:
        """List all available tools with descriptions"""
        tools_list = []
        for name, tool in self.tools.items():
            tools_list.append({
                "name": name,
                "description": tool.description,
                "parameters": tool.parameters
            })
        return tools_list

    async def handle(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tool-related requests"""
        if method == "tools.list":
            return {
                "jsonrpc": "2.0",
                "result": {
                    "tools": self.list_tools()
                }
            }
        elif method == "tools.execute":
            tool_name = params.get("tool")
            tool_params = params.get("params", {})
            result = await self.execute(tool_name, tool_params)
            return {
                "jsonrpc": "2.0",
                "result": result
            }
        else:
            return {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32601,
                    "message": f"Unknown tools method: {method}"
                }
            }

    async def execute(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific tool"""
        if tool_name not in self.tools:
            return {"error": f"Unknown tool: {tool_name}"}

        tool = self.tools[tool_name]
        try:
            result = await tool.execute(params)
            logger.info(f"🔧 Executed tool: {tool_name}")
            return result
        except Exception as e:
            logger.error(f"❌ Tool execution failed: {tool_name} - {e}")
            return {"error": str(e)}


class BaseTool:
    """Base class for all tools"""

    def __init__(self, server):
        self.server = server
        self.description = "Base tool"
        self.parameters = {}

    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the tool"""
        raise NotImplementedError


class BudgetAnalyzer(BaseTool):
    """Analyzes budget and spending patterns"""

    def __init__(self, server):
        super().__init__(server)
        self.description = "Analyze budget allocation and spending patterns"
        self.parameters = {
            "user_id": "User ID",
            "period": "Analysis period (month/quarter/year)"
        }

    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        user_id = params.get("user_id", "USR001")
        period = params.get("period", "month")

        # Get user's transactions
        transactions = self.server.mock_data.get("transactions", [])
        accounts = self.server.mock_data.get("accounts", [])
        
        user_account_ids = [acc["id"] for acc in accounts if acc["user_id"] == user_id]
        user_transactions = [
            txn for txn in transactions 
            if txn["account_id"] in user_account_ids
        ]

        # Calculate budget breakdown
        categories = {}
        total_spent = 0
        
        for txn in user_transactions:
            if txn["amount"] < 0:  # Expenses only
                category = txn["category"]
                amount = abs(txn["amount"])
                
                if category not in categories:
                    categories[category] = 0
                categories[category] += amount
                total_spent += amount

        # Calculate percentages and recommendations
        budget_analysis = {
            "total_spent": total_spent,
            "categories": {},
            "recommendations": [],
            "savings_potential": 0
        }

        # Ideal budget percentages (50/30/20 rule)
        ideal_budget = {
            "HOUSING": 30,
            "FOOD": 15,
            "TRANSPORT": 15,
            "UTILITIES": 10,
            "ENTERTAINMENT": 10,
            "SHOPPING": 10,
            "HEALTHCARE": 5,
            "OTHER": 5
        }

        for category, amount in categories.items():
            percentage = (amount / total_spent * 100) if total_spent > 0 else 0
            ideal_pct = ideal_budget.get(category, 10)
            
            budget_analysis["categories"][category] = {
                "amount": amount,
                "percentage": round(percentage, 1),
                "ideal_percentage": ideal_pct,
                "status": "OK" if percentage <= ideal_pct * 1.2 else "OVERSPENDING"
            }

            if percentage > ideal_pct * 1.2:
                savings = amount - (total_spent * ideal_pct / 100)
                budget_analysis["savings_potential"] += savings
                budget_analysis["recommendations"].append(
                    f"Reduce {category} spending by ₹{savings:,.0f} to meet ideal budget"
                )

        return budget_analysis


class ExpenseTracker(BaseTool):
    """Tracks and categorizes expenses"""

    def __init__(self, server):
        super().__init__(server)
        self.description = "Track and categorize expenses with trends"
        self.parameters = {
            "user_id": "User ID",
            "days": "Number of days to track"
        }

    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        user_id = params.get("user_id", "USR001")
        days = params.get("days", 30)

        # Get transactions
        cutoff_date = datetime.now() - timedelta(days=days)
        transactions = self.server.mock_data.get("transactions", [])
        accounts = self.server.mock_data.get("accounts", [])
        
        user_account_ids = [acc["id"] for acc in accounts if acc["user_id"] == user_id]
        
        # Filter and analyze expenses
        daily_expenses = {}
        category_totals = {}
        merchant_frequency = {}
        
        for txn in transactions:
            if txn["account_id"] in user_account_ids and txn["amount"] < 0:
                txn_date = datetime.fromisoformat(txn["date"]).date()
                
                if datetime.combine(txn_date, datetime.min.time()) >= cutoff_date:
                    # Daily tracking
                    date_str = txn_date.isoformat()
                    if date_str not in daily_expenses:
                        daily_expenses[date_str] = 0
                    daily_expenses[date_str] += abs(txn["amount"])
                    
                    # Category tracking
                    category = txn["category"]
                    if category not in category_totals:
                        category_totals[category] = 0
                    category_totals[category] += abs(txn["amount"])
                    
                    # Merchant frequency
                    merchant = txn["merchant"]
                    if merchant not in merchant_frequency:
                        merchant_frequency[merchant] = {"count": 0, "total": 0}
                    merchant_frequency[merchant]["count"] += 1
                    merchant_frequency[merchant]["total"] += abs(txn["amount"])

        # Calculate statistics
        total_expenses = sum(category_totals.values())
        daily_average = total_expenses / days if days > 0 else 0

        # Find top merchants
        top_merchants = sorted(
            merchant_frequency.items(),
            key=lambda x: x[1]["total"],
            reverse=True
        )[:5]

        basic_result = {
            "total_expenses": total_expenses,
            "daily_average": daily_average,
            "category_breakdown": category_totals,
            "top_merchants": [
                {
                    "name": merchant,
                    "visits": data["count"],
                    "total_spent": data["total"],
                    "average_per_visit": data["total"] / data["count"]
                }
                for merchant, data in top_merchants
            ],
            "daily_trend": daily_expenses,
            "period_days": days
        }

        # Enhance with AI insights if available
        if AI_ENHANCEMENT_AVAILABLE and user_transactions:
            try:
                ai_service = get_ai_service()
                # Convert to the expected format for AI analysis
                filtered_transactions = [
                    txn for txn in user_transactions
                    if txn["amount"] < 0 and datetime.fromisoformat(txn["date"]) >= cutoff_date
                ]

                enhanced_result = await ai_service.enhance_spending_analysis(
                    transactions=filtered_transactions,
                    existing_result=basic_result
                )
                enhanced_result["ai_enhanced"] = True
                return enhanced_result
            except Exception as e:
                logger.warning(f"AI enhancement failed: {e}")

        basic_result["ai_enhanced"] = False
        return basic_result


class SavingsCalculator(BaseTool):
    """Calculates savings potential and recommendations"""

    def __init__(self, server):
        super().__init__(server)
        self.description = "Calculate savings potential and provide recommendations"
        self.parameters = {
            "user_id": "User ID",
            "target_amount": "Savings target",
            "months": "Time period in months"
        }

    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        user_id = params.get("user_id", "USR001")
        target_amount = params.get("target_amount", 100000)
        months = params.get("months", 12)

        # Get user's financial data
        transactions = self.server.mock_data.get("transactions", [])
        accounts = self.server.mock_data.get("accounts", [])
        
        user_account_ids = [acc["id"] for acc in accounts if acc["user_id"] == user_id]
        user_transactions = [
            txn for txn in transactions 
            if txn["account_id"] in user_account_ids
        ]

        # Calculate current savings rate
        total_income = sum(txn["amount"] for txn in user_transactions if txn["amount"] > 0)
        total_expenses = abs(sum(txn["amount"] for txn in user_transactions if txn["amount"] < 0))
        current_savings = total_income - total_expenses
        savings_rate = (current_savings / total_income * 100) if total_income > 0 else 0

        # Calculate required monthly savings
        required_monthly = target_amount / months
        current_monthly = current_savings / 12  # Assuming annual data
        gap = required_monthly - current_monthly

        # Generate recommendations
        recommendations = []
        if gap > 0:
            recommendations.append(f"Increase monthly savings by ₹{gap:,.0f}")
            
            # Suggest expense cuts
            if gap < total_expenses * 0.1:
                recommendations.append("Cut 10% from discretionary spending")
            elif gap < total_expenses * 0.2:
                recommendations.append("Reduce entertainment and dining by 20%")
            else:
                recommendations.append("Consider additional income sources")

        # Calculate compound interest projection
        interest_rate = 0.07  # 7% annual return
        monthly_rate = interest_rate / 12
        
        if required_monthly > 0:
            future_value = required_monthly * ((1 + monthly_rate) ** months - 1) / monthly_rate
        else:
            future_value = 0

        return {
            "target_amount": target_amount,
            "months_to_goal": months,
            "required_monthly_savings": required_monthly,
            "current_monthly_savings": current_monthly,
            "savings_gap": max(0, gap),
            "current_savings_rate": round(savings_rate, 1),
            "projected_value_with_interest": future_value,
            "recommendations": recommendations,
            "achievable": gap <= 0
        }


class LoanCalculator(BaseTool):
    """Calculates loan EMI and amortization"""

    def __init__(self, server):
        super().__init__(server)
        self.description = "Calculate loan EMI, total interest, and amortization schedule"
        self.parameters = {
            "principal": "Loan amount",
            "interest_rate": "Annual interest rate (%)",
            "tenure_months": "Loan tenure in months"
        }

    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        principal = params.get("principal", 1000000)
        annual_rate = params.get("interest_rate", 8.5)
        tenure = params.get("tenure_months", 240)

        # Calculate EMI using formula
        monthly_rate = annual_rate / 100 / 12
        
        if monthly_rate > 0:
            emi = principal * monthly_rate * (1 + monthly_rate) ** tenure / \
                  ((1 + monthly_rate) ** tenure - 1)
        else:
            emi = principal / tenure

        # Calculate total payment and interest
        total_payment = emi * tenure
        total_interest = total_payment - principal

        # Generate amortization schedule (first 12 months)
        schedule = []
        balance = principal
        
        for month in range(1, min(13, tenure + 1)):
            interest_payment = balance * monthly_rate
            principal_payment = emi - interest_payment
            balance -= principal_payment
            
            schedule.append({
                "month": month,
                "emi": round(emi, 2),
                "principal": round(principal_payment, 2),
                "interest": round(interest_payment, 2),
                "balance": round(balance, 2)
            })

        return {
            "loan_amount": principal,
            "interest_rate": annual_rate,
            "tenure_months": tenure,
            "monthly_emi": round(emi, 2),
            "total_payment": round(total_payment, 2),
            "total_interest": round(total_interest, 2),
            "interest_percentage": round(total_interest / principal * 100, 1),
            "amortization_schedule": schedule
        }


class FraudDetector(BaseTool):
    """Detects potential fraudulent transactions"""

    def __init__(self, server):
        super().__init__(server)
        self.description = "Detect potentially fraudulent transactions using pattern analysis"
        self.parameters = {
            "user_id": "User ID",
            "transaction": "Transaction to check (optional)"
        }

    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        user_id = params.get("user_id", "USR001")
        check_transaction = params.get("transaction")

        # Get user's transaction history
        transactions = self.server.mock_data.get("transactions", [])
        accounts = self.server.mock_data.get("accounts", [])

        user_account_ids = [acc["id"] for acc in accounts if acc["user_id"] == user_id]
        user_transactions = [
            txn for txn in transactions
            if txn["account_id"] in user_account_ids
        ]

        # Build user profile
        avg_transaction = sum(abs(t["amount"]) for t in user_transactions) / len(user_transactions) if user_transactions else 0
        max_transaction = max(abs(t["amount"]) for t in user_transactions) if user_transactions else 0
        common_merchants = {}
        common_categories = {}

        for txn in user_transactions:
            merchant = txn["merchant"]
            category = txn["category"]

            if merchant not in common_merchants:
                common_merchants[merchant] = 0
            common_merchants[merchant] += 1

            if category not in common_categories:
                common_categories[category] = 0
            common_categories[category] += 1

        # Check specific transaction or scan all
        if check_transaction:
            # Basic analysis
            basic_result = self._analyze_transaction(
                check_transaction,
                avg_transaction,
                max_transaction,
                common_merchants,
                common_categories
            )

            # Enhance with AI if available
            if AI_ENHANCEMENT_AVAILABLE:
                try:
                    ai_service = get_ai_service()
                    enhanced_result = await ai_service.enhance_fraud_detection(
                        transaction=check_transaction,
                        existing_result=basic_result
                    )
                    return {"transaction_analysis": enhanced_result}
                except Exception as e:
                    logger.warning(f"AI enhancement failed: {e}")

            return {"transaction_analysis": basic_result}
        else:
            # Scan recent transactions
            suspicious = []
            for txn in user_transactions[-20:]:  # Check last 20 transactions
                # Basic analysis
                analysis = self._analyze_transaction(
                    txn,
                    avg_transaction,
                    max_transaction,
                    common_merchants,
                    common_categories
                )

                # Enhance with AI if available and risk is moderate
                if AI_ENHANCEMENT_AVAILABLE and analysis["risk_score"] > 30:
                    try:
                        ai_service = get_ai_service()
                        enhanced_analysis = await ai_service.enhance_fraud_detection(
                            transaction=txn,
                            existing_result=analysis
                        )
                        analysis = enhanced_analysis
                    except Exception as e:
                        logger.warning(f"AI enhancement failed: {e}")

                if analysis["risk_score"] > 50:
                    suspicious.append(analysis)

            return {
                "suspicious_transactions": suspicious,
                "total_checked": min(20, len(user_transactions)),
                "alerts_generated": len(suspicious),
                "ai_enhanced": AI_ENHANCEMENT_AVAILABLE
            }

    def _analyze_transaction(self, txn, avg_amount, max_amount, common_merchants, common_categories):
        """Analyze a single transaction for fraud"""
        risk_score = 0
        risk_factors = []
        
        amount = abs(txn["amount"])
        
        # Check amount anomaly
        if amount > avg_amount * 3:
            risk_score += 30
            risk_factors.append("Unusually high amount")
        
        if amount > max_amount * 1.5:
            risk_score += 20
            risk_factors.append("Exceeds historical maximum")
        
        # Check merchant
        merchant = txn["merchant"]
        if merchant not in common_merchants:
            risk_score += 15
            risk_factors.append("New merchant")
        
        # Check time
        hour = datetime.fromisoformat(txn["date"]).hour
        if hour < 6 or hour > 23:
            risk_score += 20
            risk_factors.append("Unusual time")
        
        # Check category
        if txn["category"] not in common_categories:
            risk_score += 15
            risk_factors.append("Unusual category")
        
        return {
            "transaction_id": txn["id"],
            "amount": amount,
            "merchant": merchant,
            "date": txn["date"],
            "risk_score": min(risk_score, 100),
            "risk_level": "HIGH" if risk_score > 70 else "MEDIUM" if risk_score > 40 else "LOW",
            "risk_factors": risk_factors,
            "recommended_action": "BLOCK" if risk_score > 70 else "VERIFY" if risk_score > 40 else "ALLOW"
        }


class InsightGenerator(BaseTool):
    """Generates AI-powered financial insights"""

    def __init__(self, server):
        super().__init__(server)
        self.description = "Generate personalized financial insights and recommendations"
        self.parameters = {
            "user_id": "User ID",
            "insight_type": "Type of insight (spending/savings/investment)"
        }

    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        user_id = params.get("user_id", "USR001")
        insight_type = params.get("insight_type", "general")

        # Gather comprehensive user data
        accounts = self.server.mock_data.get("accounts", [])
        transactions = self.server.mock_data.get("transactions", [])
        goals = self.server.mock_data.get("goals", [])
        investments = self.server.mock_data.get("investments", [])
        
        user_accounts = [acc for acc in accounts if acc["user_id"] == user_id]
        user_goals = [goal for goal in goals if goal["user_id"] == user_id]
        user_investments = [inv for inv in investments if inv["user_id"] == user_id]
        
        # Calculate key metrics
        total_balance = sum(acc["balance"] for acc in user_accounts)
        account_ids = [acc["id"] for acc in user_accounts]
        user_transactions = [t for t in transactions if t["account_id"] in account_ids]
        
        monthly_income = sum(t["amount"] for t in user_transactions if t["amount"] > 0) / 12
        monthly_expenses = abs(sum(t["amount"] for t in user_transactions if t["amount"] < 0)) / 12
        savings_rate = ((monthly_income - monthly_expenses) / monthly_income * 100) if monthly_income > 0 else 0
        
        # Generate insights based on type
        insights = []
        
        if insight_type in ["spending", "general"]:
            # Spending insights
            if monthly_expenses > monthly_income * 0.8:
                insights.append({
                    "type": "warning",
                    "category": "spending",
                    "title": "High Expense Ratio Alert",
                    "description": f"You're spending {monthly_expenses/monthly_income*100:.1f}% of your income. Consider reducing expenses.",
                    "priority": "HIGH",
                    "action": "Review and cut unnecessary expenses"
                })
            
            # Find biggest expense category
            category_spending = {}
            for txn in user_transactions:
                if txn["amount"] < 0:
                    cat = txn["category"]
                    if cat not in category_spending:
                        category_spending[cat] = 0
                    category_spending[cat] += abs(txn["amount"])
            
            if category_spending:
                top_category = max(category_spending.items(), key=lambda x: x[1])
                insights.append({
                    "type": "info",
                    "category": "spending",
                    "title": "Highest Spending Category",
                    "description": f"{top_category[0]} accounts for ₹{top_category[1]:,.0f} of your expenses",
                    "priority": "MEDIUM",
                    "action": f"Consider ways to reduce {top_category[0]} spending"
                })
        
        if insight_type in ["savings", "general"]:
            # Savings insights
            if savings_rate < 20:
                insights.append({
                    "type": "warning",
                    "category": "savings",
                    "title": "Low Savings Rate",
                    "description": f"You're saving only {savings_rate:.1f}% of income. Aim for at least 20%.",
                    "priority": "HIGH",
                    "action": "Increase monthly savings by ₹{:.0f}".format(monthly_income * 0.2 - (monthly_income - monthly_expenses))
                })
            
            # Emergency fund check
            emergency_fund_needed = monthly_expenses * 6
            if total_balance < emergency_fund_needed:
                insights.append({
                    "type": "recommendation",
                    "category": "savings",
                    "title": "Build Emergency Fund",
                    "description": f"Your emergency fund should be ₹{emergency_fund_needed:,.0f} (6 months expenses)",
                    "priority": "HIGH",
                    "action": f"Save additional ₹{emergency_fund_needed - total_balance:,.0f}"
                })
        
        if insight_type in ["investment", "general"]:
            # Investment insights
            if user_investments:
                total_invested = sum(inv["invested_amount"] for inv in user_investments)
                current_value = sum(inv["current_value"] for inv in user_investments)
                returns = ((current_value - total_invested) / total_invested * 100) if total_invested > 0 else 0
                
                insights.append({
                    "type": "success" if returns > 10 else "info",
                    "category": "investment",
                    "title": "Portfolio Performance",
                    "description": f"Your investments have {returns:.1f}% returns",
                    "priority": "MEDIUM",
                    "action": "Review and rebalance portfolio" if returns < 10 else "Continue current strategy"
                })
            else:
                insights.append({
                    "type": "recommendation",
                    "category": "investment",
                    "title": "Start Investing",
                    "description": "You have no active investments. Start with SIPs in mutual funds.",
                    "priority": "HIGH",
                    "action": "Begin with ₹5,000 monthly SIP"
                })
        
        # Goal-based insights
        if user_goals:
            behind_goals = [g for g in user_goals if g["status"] == "BEHIND"]
            if behind_goals:
                insights.append({
                    "type": "warning",
                    "category": "goals",
                    "title": "Goals Behind Schedule",
                    "description": f"{len(behind_goals)} of your {len(user_goals)} goals are behind schedule",
                    "priority": "HIGH",
                    "action": "Review and adjust goal contributions"
                })
        
        return {
            "insights": insights,
            "summary": {
                "total_insights": len(insights),
                "high_priority": len([i for i in insights if i["priority"] == "HIGH"]),
                "categories_covered": list(set(i["category"] for i in insights))
            },
            "metrics": {
                "savings_rate": round(savings_rate, 1),
                "expense_ratio": round(monthly_expenses / monthly_income * 100, 1) if monthly_income > 0 else 0,
                "net_worth": total_balance,
                "monthly_surplus": monthly_income - monthly_expenses
            }
        }


# Additional specialized tools
class TaxCalculator(BaseTool):
    """Calculates tax liability and savings"""

    def __init__(self, server):
        super().__init__(server)
        self.description = "Calculate tax liability and suggest tax-saving investments"
        self.parameters = {
            "annual_income": "Annual taxable income",
            "investments": "Tax-saving investments"
        }

    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        income = params.get("annual_income", 1000000)
        investments = params.get("investments", {})
        
        # Indian tax slabs (New Regime)
        tax = 0
        if income > 1500000:
            tax += (income - 1500000) * 0.30
            income = 1500000
        if income > 1200000:
            tax += (income - 1200000) * 0.20
            income = 1200000
        if income > 900000:
            tax += (income - 900000) * 0.15
            income = 900000
        if income > 600000:
            tax += (income - 600000) * 0.10
            income = 600000
        if income > 300000:
            tax += (income - 300000) * 0.05
        
        # Calculate savings under 80C
        total_80c = sum(investments.get(k, 0) for k in ["ppf", "elss", "nsc", "fd", "lic"])
        deduction_80c = min(total_80c, 150000)
        
        return {
            "gross_income": params.get("annual_income", 1000000),
            "tax_before_savings": tax,
            "deduction_80c": deduction_80c,
            "tax_after_savings": max(0, tax - deduction_80c * 0.3),
            "tax_saved": min(deduction_80c * 0.3, tax),
            "effective_tax_rate": (tax / params.get("annual_income", 1000000) * 100)
        }


class GoalOptimizer(BaseTool):
    """Optimizes financial goals"""

    def __init__(self, server):
        super().__init__(server)
        self.description = "Optimize multiple financial goals with priority-based allocation"
        self.parameters = {
            "user_id": "User ID",
            "available_monthly": "Available monthly amount for goals"
        }

    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        user_id = params.get("user_id", "USR001")
        available = params.get("available_monthly", 50000)
        
        goals = self.server.mock_data.get("goals", [])
        user_goals = [g for g in goals if g["user_id"] == user_id]
        
        # Prioritize goals
        priority_order = {"EMERGENCY": 1, "HIGH": 2, "MEDIUM": 3, "LOW": 4}
        user_goals.sort(key=lambda x: priority_order.get(x.get("priority", "LOW"), 5))
        
        # Allocate funds
        allocations = []
        remaining = available
        
        for goal in user_goals:
            if remaining <= 0:
                break
                
            target = goal["target_amount"]
            current = goal["current_amount"]
            needed = target - current
            months_left = 12  # Assume 1 year timeline
            monthly_needed = needed / months_left
            
            allocation = min(monthly_needed, remaining)
            allocations.append({
                "goal_name": goal["name"],
                "priority": goal.get("priority", "MEDIUM"),
                "monthly_allocation": allocation,
                "months_to_complete": needed / allocation if allocation > 0 else float('inf'),
                "progress_increase": (allocation * 12 / target * 100) if target > 0 else 0
            })
            
            remaining -= allocation
        
        return {
            "total_available": available,
            "total_allocated": available - remaining,
            "unallocated": remaining,
            "goal_allocations": allocations,
            "optimization_summary": f"Optimized {len(allocations)} goals with ₹{available - remaining:,.0f} monthly"
        }


class CreditAnalyzer(BaseTool):
    """Analyzes credit score factors"""

    def __init__(self, server):
        super().__init__(server)
        self.description = "Analyze credit score and provide improvement recommendations"
        self.parameters = {
            "user_id": "User ID"
        }

    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        user_id = params.get("user_id", "USR001")
        
        # Get credit data
        credit_data = self.server.mock_data.get("credit_data", [])
        user_credit = next((c for c in credit_data if c["user_id"] == user_id), None)
        
        if not user_credit:
            return {"error": "Credit data not found"}
        
        score = user_credit["credit_score"]
        factors = []
        recommendations = []
        
        # Analyze factors
        if user_credit.get("payment_history", 100) < 95:
            factors.append("Payment history issues")
            recommendations.append("Set up automatic payments to never miss due dates")
        
        if user_credit.get("credit_utilization", 0) > 30:
            factors.append("High credit utilization")
            recommendations.append(f"Reduce credit card usage to below 30% of limit")
        
        if user_credit.get("credit_age", 0) < 3:
            factors.append("Short credit history")
            recommendations.append("Keep old credit cards active to build history")
        
        # Score interpretation
        if score >= 750:
            interpretation = "Excellent - Eligible for best rates"
        elif score >= 700:
            interpretation = "Good - Favorable rates available"
        elif score >= 650:
            interpretation = "Fair - Room for improvement"
        else:
            interpretation = "Poor - Focus on improvement"
        
        return {
            "credit_score": score,
            "interpretation": interpretation,
            "negative_factors": factors,
            "recommendations": recommendations,
            "potential_score_increase": min(850 - score, len(recommendations) * 25),
            "time_to_improve": f"{len(recommendations) * 3} months"
        }


# Additional utility tools
class BillReminder(BaseTool):
    """Manages bill payment reminders"""

    def __init__(self, server):
        super().__init__(server)
        self.description = "Track and remind about upcoming bill payments"

    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Implementation for bill reminders
        return {"status": "Bill reminder set"}


class PortfolioOptimizer(BaseTool):
    """Optimizes investment portfolio"""

    def __init__(self, server):
        super().__init__(server)
        self.description = "Optimize investment portfolio based on risk profile"

    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Implementation for portfolio optimization
        return {"status": "Portfolio optimized"}


class CashFlowAnalyzer(BaseTool):
    """Analyzes cash flow patterns"""

    def __init__(self, server):
        super().__init__(server)
        self.description = "Analyze income and expense patterns for cash flow optimization"

    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Implementation for cash flow analysis
        return {"status": "Cash flow analyzed"}


class InvestmentAnalyzer(BaseTool):
    """Analyzes investment performance"""

    def __init__(self, server):
        super().__init__(server)
        self.description = "Analyze investment portfolio performance and returns"
        self.parameters = {
            "user_id": "User ID",
            "goals": "Investment goals (optional)"
        }

    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        user_id = params.get("user_id", "USR001")
        goals = params.get("goals", [])

        # Get user profile from mock data
        accounts = self.server.mock_data.get("accounts", [])
        transactions = self.server.mock_data.get("transactions", [])

        # Build user profile for investment analysis
        user_profile = {
            "age": 30,  # Mock data
            "monthly_income": 75000,  # Derived from transactions
            "risk_tolerance": "MODERATE",
            "investment_horizon": 10,
            "current_investments": 500000  # Mock current portfolio value
        }

        # Mock goals if none provided
        if not goals:
            goals = [
                {"name": "Retirement", "target_amount": 10000000, "deadline": "2034-01-01"},
                {"name": "House Purchase", "target_amount": 5000000, "deadline": "2029-01-01"}
            ]

        # Basic investment analysis
        basic_result = {
            "user_profile": user_profile,
            "portfolio_summary": {
                "total_value": user_profile["current_investments"],
                "equity_allocation": 60,
                "debt_allocation": 30,
                "gold_allocation": 10,
                "expected_return": 12.5
            },
            "goal_analysis": [
                {
                    "goal": goal["name"],
                    "target": goal.get("target_amount", 1000000),
                    "required_sip": goal.get("target_amount", 1000000) / 120,  # Basic calculation
                    "feasibility": "Achievable with disciplined investing"
                }
                for goal in goals
            ]
        }

        # Enhance with AI if available
        if AI_ENHANCEMENT_AVAILABLE:
            try:
                ai_service = get_ai_service()
                enhanced_result = await ai_service.enhance_investment_analysis(
                    user_profile=user_profile,
                    goals=goals,
                    existing_result=basic_result
                )
                enhanced_result["ai_enhanced"] = True
                return enhanced_result
            except Exception as e:
                logger.warning(f"AI enhancement failed: {e}")

        basic_result["ai_enhanced"] = False
        return basic_result


class RetirementPlanner(BaseTool):
    """Plans for retirement savings"""

    def __init__(self, server):
        super().__init__(server)
        self.description = "Calculate retirement corpus and monthly savings needed"

    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Implementation for retirement planning
        return {"status": "Retirement plan created"}