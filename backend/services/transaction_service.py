"""
Transaction Service - Business logic for transaction operations
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from models import Transaction, Account
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class TransactionService:
    """
    Service class for transaction-related operations
    """

    @staticmethod
    def create_transaction(
        db: Session,
        transaction_data: Dict[str, Any]
    ) -> Transaction:
        """
        Create a new transaction
        """
        # Generate transaction ID
        last_txn = db.query(Transaction).order_by(Transaction.id.desc()).first()
        transaction_id = f"TXN{(last_txn.id + 1):03d}" if last_txn else "TXN001"

        # Set transaction type based on amount
        if "amount" in transaction_data:
            transaction_data["transaction_type"] = (
                "CREDIT" if transaction_data["amount"] > 0 else "DEBIT"
            )

        # Set default transaction date if not provided
        if "transaction_date" not in transaction_data:
            transaction_data["transaction_date"] = datetime.utcnow()

        transaction = Transaction(transaction_id=transaction_id, **transaction_data)
        db.add(transaction)

        # Update account balance
        account = db.query(Account).filter_by(
            account_id=transaction_data["account_id"]
        ).first()

        if account:
            account.balance += transaction_data["amount"]
            account.available_balance = account.balance
            account.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(transaction)

        logger.info(f"Created transaction: {transaction_id}")
        return transaction

    @staticmethod
    def get_user_transactions(
        db: Session,
        user_id: str,
        limit: int = 100,
        offset: int = 0,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Transaction]:
        """
        Get user's transactions with filters
        """
        # Get user's accounts
        accounts = db.query(Account).filter_by(user_id=user_id).all()
        account_ids = [acc.account_id for acc in accounts]

        # Base query
        query = db.query(Transaction).filter(
            Transaction.account_id.in_(account_ids)
        )

        # Apply filters
        if filters:
            if "category" in filters:
                query = query.filter(Transaction.category == filters["category"])

            if "date_from" in filters:
                query = query.filter(
                    Transaction.transaction_date >= filters["date_from"]
                )

            if "date_to" in filters:
                query = query.filter(
                    Transaction.transaction_date <= filters["date_to"]
                )

            if "min_amount" in filters:
                query = query.filter(
                    func.abs(Transaction.amount) >= filters["min_amount"]
                )

            if "max_amount" in filters:
                query = query.filter(
                    func.abs(Transaction.amount) <= filters["max_amount"]
                )

            if "transaction_type" in filters:
                query = query.filter(
                    Transaction.transaction_type == filters["transaction_type"]
                )

        # Order by date (most recent first)
        query = query.order_by(Transaction.transaction_date.desc())

        # Apply pagination
        return query.offset(offset).limit(limit).all()

    @staticmethod
    def analyze_spending_patterns(
        db: Session,
        user_id: str,
        period_days: int = 30
    ) -> Dict[str, Any]:
        """
        Analyze user's spending patterns
        """
        # Get user's accounts
        accounts = db.query(Account).filter_by(user_id=user_id).all()
        account_ids = [acc.account_id for acc in accounts]

        # Get transactions for the period
        start_date = datetime.utcnow() - timedelta(days=period_days)

        transactions = db.query(Transaction).filter(
            and_(
                Transaction.account_id.in_(account_ids),
                Transaction.transaction_date >= start_date
            )
        ).all()

        # Separate income and expenses
        income_transactions = [t for t in transactions if t.amount > 0]
        expense_transactions = [t for t in transactions if t.amount < 0]

        # Calculate totals
        total_income = sum(t.amount for t in income_transactions)
        total_expenses = abs(sum(t.amount for t in expense_transactions))

        # Category breakdown for expenses
        category_breakdown = {}
        for txn in expense_transactions:
            category = txn.category
            if category not in category_breakdown:
                category_breakdown[category] = {
                    "amount": 0,
                    "count": 0,
                    "percentage": 0
                }
            category_breakdown[category]["amount"] += abs(txn.amount)
            category_breakdown[category]["count"] += 1

        # Calculate percentages
        for category in category_breakdown:
            category_breakdown[category]["percentage"] = (
                category_breakdown[category]["amount"] / total_expenses * 100
                if total_expenses > 0 else 0
            )

        # Merchant frequency
        merchant_frequency = {}
        for txn in expense_transactions:
            merchant = txn.merchant
            if merchant not in merchant_frequency:
                merchant_frequency[merchant] = {
                    "count": 0,
                    "total_spent": 0
                }
            merchant_frequency[merchant]["count"] += 1
            merchant_frequency[merchant]["total_spent"] += abs(txn.amount)

        # Top merchants
        top_merchants = sorted(
            merchant_frequency.items(),
            key=lambda x: x[1]["total_spent"],
            reverse=True
        )[:5]

        # Daily average
        daily_average = total_expenses / period_days if period_days > 0 else 0

        # Detect unusual spending
        unusual_transactions = TransactionService.detect_unusual_spending(
            expense_transactions
        )

        return {
            "period_days": period_days,
            "total_income": total_income,
            "total_expenses": total_expenses,
            "net_flow": total_income - total_expenses,
            "daily_average_expense": daily_average,
            "category_breakdown": category_breakdown,
            "top_merchants": [
                {
                    "name": merchant,
                    "count": data["count"],
                    "total_spent": data["total_spent"]
                }
                for merchant, data in top_merchants
            ],
            "unusual_transactions": unusual_transactions,
            "savings_rate": (
                (total_income - total_expenses) / total_income * 100
                if total_income > 0 else 0
            )
        }

    @staticmethod
    def detect_unusual_spending(
        transactions: List[Transaction]
    ) -> List[Dict[str, Any]]:
        """
        Detect unusual spending patterns
        """
        if not transactions:
            return []

        # Calculate statistics
        amounts = [abs(t.amount) for t in transactions]
        avg_amount = sum(amounts) / len(amounts) if amounts else 0
        max_amount = max(amounts) if amounts else 0

        # Standard deviation (simplified)
        if len(amounts) > 1:
            variance = sum((x - avg_amount) ** 2 for x in amounts) / len(amounts)
            std_dev = variance ** 0.5
        else:
            std_dev = 0

        unusual = []

        for txn in transactions:
            amount = abs(txn.amount)
            reasons = []

            # Check if amount is unusual
            if std_dev > 0 and amount > avg_amount + (2 * std_dev):
                reasons.append("Amount significantly above average")

            if amount > max_amount * 0.8:
                reasons.append("Near maximum historical amount")

            # Check time
            hour = txn.transaction_date.hour
            if hour < 6 or hour > 23:
                reasons.append("Unusual transaction time")

            # Check if flagged
            if txn.is_flagged:
                reasons.append("Flagged by fraud detection")

            if reasons:
                unusual.append({
                    "transaction_id": txn.transaction_id,
                    "amount": amount,
                    "merchant": txn.merchant,
                    "date": txn.transaction_date.isoformat(),
                    "reasons": reasons
                })

        return unusual[:10]  # Return top 10 unusual transactions

    @staticmethod
    def categorize_transaction(
        transaction_description: str,
        merchant: str
    ) -> str:
        """
        Auto-categorize transaction based on description and merchant
        """
        # Simple rule-based categorization
        description_lower = transaction_description.lower()
        merchant_lower = merchant.lower()

        # Food & Dining
        food_keywords = ["swiggy", "zomato", "restaurant", "cafe", "food", "pizza", "burger"]
        if any(keyword in merchant_lower for keyword in food_keywords):
            return "FOOD"

        # Transportation
        transport_keywords = ["uber", "ola", "fuel", "petrol", "diesel", "parking"]
        if any(keyword in merchant_lower for keyword in transport_keywords):
            return "TRANSPORT"

        # Shopping
        shopping_keywords = ["amazon", "flipkart", "myntra", "mall", "store", "shop"]
        if any(keyword in merchant_lower for keyword in shopping_keywords):
            return "SHOPPING"

        # Utilities
        utility_keywords = ["electricity", "water", "gas", "internet", "mobile", "phone"]
        if any(keyword in description_lower for keyword in utility_keywords):
            return "UTILITIES"

        # Entertainment
        entertainment_keywords = ["netflix", "prime", "spotify", "movie", "cinema"]
        if any(keyword in merchant_lower for keyword in entertainment_keywords):
            return "ENTERTAINMENT"

        # Healthcare
        health_keywords = ["hospital", "clinic", "pharmacy", "medical", "doctor"]
        if any(keyword in merchant_lower for keyword in health_keywords):
            return "HEALTHCARE"

        # Default
        return "OTHER"

    @staticmethod
    def get_recurring_transactions(
        db: Session,
        user_id: str
    ) -> List[Dict[str, Any]]:
        """
        Identify recurring transactions (subscriptions, EMIs, etc.)
        """
        # Get user's accounts
        accounts = db.query(Account).filter_by(user_id=user_id).all()
        account_ids = [acc.account_id for acc in accounts]

        # Get last 3 months of transactions
        start_date = datetime.utcnow() - timedelta(days=90)

        transactions = db.query(Transaction).filter(
            and_(
                Transaction.account_id.in_(account_ids),
                Transaction.transaction_date >= start_date,
                Transaction.amount < 0  # Only expenses
            )
        ).all()

        # Group by merchant and amount
        merchant_patterns = {}

        for txn in transactions:
            key = f"{txn.merchant}_{abs(txn.amount)}"

            if key not in merchant_patterns:
                merchant_patterns[key] = {
                    "merchant": txn.merchant,
                    "amount": abs(txn.amount),
                    "category": txn.category,
                    "dates": [],
                    "count": 0
                }

            merchant_patterns[key]["dates"].append(txn.transaction_date)
            merchant_patterns[key]["count"] += 1

        # Identify recurring patterns (at least 2 occurrences)
        recurring = []

        for pattern in merchant_patterns.values():
            if pattern["count"] >= 2:
                # Calculate frequency
                dates = sorted(pattern["dates"])
                if len(dates) >= 2:
                    # Average days between transactions
                    days_between = [
                        (dates[i+1] - dates[i]).days
                        for i in range(len(dates)-1)
                    ]
                    avg_frequency = sum(days_between) / len(days_between)

                    # Determine frequency type
                    if 25 <= avg_frequency <= 35:
                        frequency = "MONTHLY"
                    elif 13 <= avg_frequency <= 16:
                        frequency = "BIWEEKLY"
                    elif 6 <= avg_frequency <= 8:
                        frequency = "WEEKLY"
                    elif 85 <= avg_frequency <= 95:
                        frequency = "QUARTERLY"
                    else:
                        frequency = "IRREGULAR"

                    recurring.append({
                        "merchant": pattern["merchant"],
                        "amount": pattern["amount"],
                        "category": pattern["category"],
                        "frequency": frequency,
                        "occurrence_count": pattern["count"],
                        "last_date": dates[-1].isoformat(),
                        "next_expected": (
                            dates[-1] + timedelta(days=int(avg_frequency))
                        ).isoformat()
                    })

        return sorted(recurring, key=lambda x: x["amount"], reverse=True)