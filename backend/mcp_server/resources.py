"""
MCP Resource Manager
Handles all financial data resources (accounts, transactions, etc.)
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class ResourceManager:
    """
    Manages all financial resources accessible via MCP
    This is where we serve our mock financial data to AI clients
    """

    def __init__(self, server):
        self.server = server
        # Streamlined to 3 core financial resources for hackathon demo
        self.resources = {
            "accounts": AccountsResource(server),
            "transactions": TransactionsResource(server),
            "investments": InvestmentsResource(server)
        }

    def list_resources(self) -> List[str]:
        """List all available resources"""
        return list(self.resources.keys())

    async def handle(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Route resource requests to appropriate handler"""

        # Extract resource type and action
        parts = method.split(".")
        if len(parts) < 3:
            return self.server.protocol.error_response("Invalid resource method", -32602)

        resource_type = parts[1]
        action = parts[2]

        if resource_type not in self.resources:
            return self.server.protocol.error_response(f"Unknown resource: {resource_type}", -32003)

        resource = self.resources[resource_type]

        # Handle different actions
        if action == "list":
            result = await resource.list(params)
        elif action == "get":
            result = await resource.get(params)
        elif action == "search":
            result = await resource.search(params)
        elif action == "aggregate":
            result = await resource.aggregate(params)
        else:
            return self.server.protocol.error_response(f"Unknown action: {action}", -32602)

        return self.server.protocol.create_response(result)


class BaseResource:
    """Base class for all resources"""

    def __init__(self, server):
        self.server = server

    async def check_permission(self, user_id: str, resource: str) -> bool:
        """Check if user has permission to access this resource"""
        permissions = self.server.mock_data.get("permissions", [])
        for perm in permissions:
            if perm["user_id"] == user_id and perm["resource"] == resource:
                return perm["access_level"] == "GRANTED"
        return True  # Default to granted for demo

    async def list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List all items in this resource"""
        raise NotImplementedError

    async def get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get specific item"""
        raise NotImplementedError

    async def search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search items"""
        raise NotImplementedError

    async def aggregate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Aggregate data"""
        raise NotImplementedError


class AccountsResource(BaseResource):
    """Handles bank account data"""

    async def list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        user_id = params.get("user_id", "USR001")

        # Check permission
        if not await self.check_permission(user_id, "accounts"):
            return {"error": "Permission denied for accounts"}

        accounts = self.server.mock_data.get("accounts", [])
        user_accounts = [acc for acc in accounts if acc["user_id"] == user_id]

        # Calculate total balance
        total_balance = sum(acc["balance"] for acc in user_accounts)

        return {
            "accounts": user_accounts,
            "total_balance": total_balance,
            "count": len(user_accounts),
            "currency": "INR"
        }

    async def get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        account_id = params.get("account_id")
        if not account_id:
            return {"error": "account_id required"}

        accounts = self.server.mock_data.get("accounts", [])
        for account in accounts:
            if account["id"] == account_id:
                return {"account": account}

        return {"error": "Account not found"}

    async def search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        query = params.get("query", "").lower()
        accounts = self.server.mock_data.get("accounts", [])

        results = [
            acc for acc in accounts
            if query in acc["bank_name"].lower() or query in acc["account_type"].lower()
        ]

        return {"results": results, "count": len(results)}

    async def aggregate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        user_id = params.get("user_id", "USR001")
        accounts = self.server.mock_data.get("accounts", [])
        user_accounts = [acc for acc in accounts if acc["user_id"] == user_id]

        aggregation = {
            "total_balance": sum(acc["balance"] for acc in user_accounts),
            "by_type": {},
            "by_bank": {}
        }

        for acc in user_accounts:
            # By type
            acc_type = acc["account_type"]
            if acc_type not in aggregation["by_type"]:
                aggregation["by_type"][acc_type] = 0
            aggregation["by_type"][acc_type] += acc["balance"]

            # By bank
            bank = acc["bank_name"]
            if bank not in aggregation["by_bank"]:
                aggregation["by_bank"][bank] = 0
            aggregation["by_bank"][bank] += acc["balance"]

        return aggregation


class TransactionsResource(BaseResource):
    """Handles transaction data"""

    async def list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        user_id = params.get("user_id", "USR001")
        limit = params.get("limit", 100)
        offset = params.get("offset", 0)

        # Check permission
        if not await self.check_permission(user_id, "transactions"):
            return {"error": "Permission denied for transactions"}

        # Get user's accounts
        accounts = self.server.mock_data.get("accounts", [])
        user_account_ids = [acc["id"] for acc in accounts if acc["user_id"] == user_id]

        # Get transactions for user's accounts
        transactions = self.server.mock_data.get("transactions", [])
        user_transactions = [
            txn for txn in transactions
            if txn["account_id"] in user_account_ids
        ]

        # Apply pagination
        paginated = user_transactions[offset:offset + limit]

        return {
            "transactions": paginated,
            "total": len(user_transactions),
            "limit": limit,
            "offset": offset
        }

    async def search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        user_id = params.get("user_id", "USR001")
        filters = params.get("filters", {})

        # Get user's transactions
        accounts = self.server.mock_data.get("accounts", [])
        user_account_ids = [acc["id"] for acc in accounts if acc["user_id"] == user_id]

        transactions = self.server.mock_data.get("transactions", [])
        results = [
            txn for txn in transactions
            if txn["account_id"] in user_account_ids
        ]

        # Apply filters
        if "category" in filters:
            results = [txn for txn in results if txn["category"] == filters["category"]]

        if "min_amount" in filters:
            results = [txn for txn in results if abs(txn["amount"]) >= filters["min_amount"]]

        if "max_amount" in filters:
            results = [txn for txn in results if abs(txn["amount"]) <= filters["max_amount"]]

        if "date_from" in filters:
            date_from = datetime.fromisoformat(filters["date_from"])
            results = [
                txn for txn in results
                if datetime.fromisoformat(txn["date"]) >= date_from
            ]

        if "date_to" in filters:
            date_to = datetime.fromisoformat(filters["date_to"])
            results = [
                txn for txn in results
                if datetime.fromisoformat(txn["date"]) <= date_to
            ]

        return {"results": results, "count": len(results)}

    async def aggregate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        user_id = params.get("user_id", "USR001")
        period = params.get("period", "month")  # month, week, day

        # Get user's transactions
        accounts = self.server.mock_data.get("accounts", [])
        user_account_ids = [acc["id"] for acc in accounts if acc["user_id"] == user_id]

        transactions = self.server.mock_data.get("transactions", [])
        user_transactions = [
            txn for txn in transactions
            if txn["account_id"] in user_account_ids
        ]

        # Calculate date range
        now = datetime.now()
        if period == "month":
            start_date = now - timedelta(days=30)
        elif period == "week":
            start_date = now - timedelta(days=7)
        else:
            start_date = now - timedelta(days=1)

        # Filter by date
        recent_transactions = [
            txn for txn in user_transactions
            if datetime.fromisoformat(txn["date"]) >= start_date
        ]

        # Aggregate by category
        by_category = {}
        total_income = 0
        total_expense = 0

        for txn in recent_transactions:
            category = txn["category"]
            amount = txn["amount"]

            if category not in by_category:
                by_category[category] = {"count": 0, "total": 0}

            by_category[category]["count"] += 1
            by_category[category]["total"] += abs(amount)

            if amount > 0:
                total_income += amount
            else:
                total_expense += abs(amount)

        return {
            "period": period,
            "total_income": total_income,
            "total_expense": total_expense,
            "net_flow": total_income - total_expense,
            "by_category": by_category,
            "transaction_count": len(recent_transactions),
            "daily_average": total_expense / 30 if period == "month" else total_expense / 7
        }


class InvestmentsResource(BaseResource):
    """Handles investment portfolio data"""

    async def list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        user_id = params.get("user_id", "USR001")

        if not await self.check_permission(user_id, "investments"):
            return {"error": "Permission denied for investments"}

        investments = self.server.mock_data.get("investments", [])
        user_investments = [inv for inv in investments if inv["user_id"] == user_id]

        total_invested = sum(inv["invested_amount"] for inv in user_investments)
        total_current = sum(inv["current_value"] for inv in user_investments)
        total_returns = total_current - total_invested
        returns_percentage = (total_returns / total_invested * 100) if total_invested > 0 else 0

        return {
            "investments": user_investments,
            "summary": {
                "total_invested": total_invested,
                "current_value": total_current,
                "total_returns": total_returns,
                "returns_percentage": round(returns_percentage, 2)
            }
        }


class GoalsResource(BaseResource):
    """Handles financial goals"""

    async def list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        user_id = params.get("user_id", "USR001")

        goals = self.server.mock_data.get("goals", [])
        user_goals = [goal for goal in goals if goal["user_id"] == user_id]

        # Calculate overall progress
        if user_goals:
            avg_progress = sum(goal["progress_percentage"] for goal in user_goals) / len(user_goals)
        else:
            avg_progress = 0

        return {
            "goals": user_goals,
            "summary": {
                "total_goals": len(user_goals),
                "average_progress": round(avg_progress, 1),
                "on_track": len([g for g in user_goals if g["status"] == "ON_TRACK"]),
                "behind": len([g for g in user_goals if g["status"] == "BEHIND"])
            }
        }


class AlertsResource(BaseResource):
    """Handles alerts and notifications"""

    async def list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        user_id = params.get("user_id", "USR001")
        unread_only = params.get("unread_only", False)

        alerts = self.server.mock_data.get("alerts", [])
        user_alerts = [alert for alert in alerts if alert["user_id"] == user_id]

        if unread_only:
            user_alerts = [alert for alert in user_alerts if not alert["read"]]

        # Sort by date (most recent first)
        user_alerts.sort(key=lambda x: x["created_at"], reverse=True)

        return {
            "alerts": user_alerts,
            "unread_count": len([a for a in user_alerts if not a["read"]]),
            "total": len(user_alerts)
        }


class InsightsResource(BaseResource):
    """Handles AI-generated insights"""

    async def list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        user_id = params.get("user_id", "USR001")

        insights = self.server.mock_data.get("insights", [])
        user_insights = [insight for insight in insights if insight["user_id"] == user_id]

        # Sort by priority
        priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
        user_insights.sort(key=lambda x: priority_order.get(x["priority"], 3))

        return {
            "insights": user_insights,
            "count": len(user_insights),
            "high_priority": len([i for i in user_insights if i["priority"] == "HIGH"])
        }


class CreditResource(BaseResource):
    """Handles credit score and loan data"""

    async def get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        user_id = params.get("user_id", "USR001")

        if not await self.check_permission(user_id, "credit_score"):
            return {"error": "Permission denied for credit score"}

        credit_data = self.server.mock_data.get("credit_data", [])
        for credit in credit_data:
            if credit["user_id"] == user_id:
                return {"credit": credit}

        return {"error": "Credit data not found"}


class EPFResource(BaseResource):
    """Handles EPF/retirement data"""

    async def get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        user_id = params.get("user_id", "USR001")

        if not await self.check_permission(user_id, "epf_data"):
            return {"error": "Permission denied for EPF data"}

        epf_data = self.server.mock_data.get("epf_data", [])
        for epf in epf_data:
            if epf["user_id"] == user_id:
                return {"epf": epf}

        return {"error": "EPF data not found"}