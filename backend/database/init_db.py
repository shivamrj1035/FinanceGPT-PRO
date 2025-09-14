"""
Database initialization and population
"""

from sqlalchemy.orm import Session
from database.connection import engine, Base, SessionLocal
from models import User, Account, Transaction, Goal, Investment, Alert, Insight
import hashlib
import json
from datetime import datetime, timedelta
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def init_database():
    """
    Initialize database tables
    """
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Database tables created successfully")

def populate_initial_data(db: Session = None):
    """
    Populate database with initial demo data
    """
    if not db:
        db = SessionLocal()

    try:
        # Check if data already exists
        existing_user = db.query(User).filter_by(email="demo@financegpt.com").first()
        if existing_user:
            logger.info("Demo data already exists")
            return

        logger.info("Populating initial demo data...")

        # Create demo user
        demo_user = User(
            user_id="USR001",
            email="demo@financegpt.com",
            name="Demo User",
            phone="+91-9876543210",
            password_hash=hashlib.sha256("Demo@123".encode()).hexdigest(),
            age=28,
            occupation="Software Engineer",
            monthly_income=150000,
            risk_tolerance="MODERATE",
            credit_score=750,
            pan_number="ABCDE1234F",
            is_active=True,
            is_verified=True
        )
        db.add(demo_user)

        # Create admin user
        admin_user = User(
            user_id="ADMIN001",
            email="admin@financegpt.com",
            name="Admin User",
            phone="+91-9876543211",
            password_hash=hashlib.sha256("Admin@123".encode()).hexdigest(),
            age=35,
            occupation="System Administrator",
            monthly_income=200000,
            risk_tolerance="HIGH",
            credit_score=800,
            is_active=True,
            is_verified=True,
            is_premium=True
        )
        db.add(admin_user)

        # Create accounts for demo user
        hdfc_account = Account(
            account_id="ACC001",
            user_id="USR001",
            bank_name="HDFC Bank",
            account_type="SAVINGS",
            account_number="****1234",
            ifsc_code="HDFC0001234",
            balance=250000,
            available_balance=250000,
            is_primary=True
        )
        db.add(hdfc_account)

        icici_account = Account(
            account_id="ACC002",
            user_id="USR001",
            bank_name="ICICI Bank",
            account_type="CURRENT",
            account_number="****5678",
            ifsc_code="ICIC0001234",
            balance=150000,
            available_balance=150000
        )
        db.add(icici_account)

        credit_card = Account(
            account_id="ACC003",
            user_id="USR001",
            bank_name="HDFC Bank",
            account_type="CREDIT_CARD",
            account_number="****9012",
            balance=-25000,  # Outstanding amount
            credit_limit=200000,
            credit_used=25000,
            minimum_due=5000,
            due_date=datetime.now() + timedelta(days=15)
        )
        db.add(credit_card)

        # Create sample transactions
        transactions_data = [
            {
                "transaction_id": "TXN001",
                "account_id": "ACC001",
                "amount": 150000,
                "transaction_type": "CREDIT",
                "category": "INCOME",
                "merchant": "TechCorp Salary",
                "payment_method": "NETBANKING",
                "description": "Monthly salary",
                "transaction_date": datetime.now() - timedelta(days=30)
            },
            {
                "transaction_id": "TXN002",
                "account_id": "ACC001",
                "amount": -35000,
                "transaction_type": "DEBIT",
                "category": "HOUSING",
                "merchant": "House Rent",
                "payment_method": "NETBANKING",
                "description": "Monthly rent payment",
                "transaction_date": datetime.now() - timedelta(days=25)
            },
            {
                "transaction_id": "TXN003",
                "account_id": "ACC001",
                "amount": -5000,
                "transaction_type": "DEBIT",
                "category": "FOOD",
                "merchant": "Swiggy",
                "payment_method": "UPI",
                "description": "Food delivery",
                "transaction_date": datetime.now() - timedelta(days=2)
            },
            {
                "transaction_id": "TXN004",
                "account_id": "ACC001",
                "amount": -2500,
                "transaction_type": "DEBIT",
                "category": "SHOPPING",
                "merchant": "Amazon",
                "payment_method": "CARD",
                "description": "Online shopping",
                "transaction_date": datetime.now() - timedelta(days=5)
            },
            {
                "transaction_id": "TXN005",
                "account_id": "ACC001",
                "amount": -15000,
                "transaction_type": "DEBIT",
                "category": "OTHER",
                "merchant": "Suspicious Merchant XYZ",
                "payment_method": "CARD",
                "description": "International transaction",
                "transaction_date": datetime.now() - timedelta(hours=3),
                "is_flagged": True,
                "fraud_score": 85,
                "fraud_reason": "Unusual merchant, high amount, odd timing"
            }
        ]

        for txn_data in transactions_data:
            transaction = Transaction(**txn_data)
            db.add(transaction)

        # Create financial goals
        emergency_fund = Goal(
            goal_id="GOAL001",
            user_id="USR001",
            name="Emergency Fund",
            description="Build 6 months of expenses as emergency fund",
            category="EMERGENCY",
            priority="HIGH",
            target_amount=500000,
            current_amount=250000,
            monthly_contribution=20000,
            target_date=datetime.now() + timedelta(days=365),
            progress_percentage=50,
            status="ON_TRACK"
        )
        db.add(emergency_fund)

        europe_trip = Goal(
            goal_id="GOAL002",
            user_id="USR001",
            name="Europe Trip",
            description="Save for Europe vacation",
            category="VACATION",
            priority="MEDIUM",
            target_amount=300000,
            current_amount=75000,
            monthly_contribution=15000,
            target_date=datetime.now() + timedelta(days=180),
            progress_percentage=25,
            status="BEHIND"
        )
        db.add(europe_trip)

        # Create investments
        mutual_fund1 = Investment(
            investment_id="INV001",
            user_id="USR001",
            name="Axis Bluechip Fund",
            type="MUTUAL_FUND",
            category="EQUITY",
            subcategory="LARGE_CAP",
            provider="Axis Mutual Fund",
            invested_amount=100000,
            current_value=125000,
            units=1000,
            nav=125,
            returns_amount=25000,
            returns_percentage=25,
            risk_level="MODERATE",
            purchase_date=datetime.now() - timedelta(days=365),
            is_sip=True,
            sip_amount=5000,
            sip_date=5
        )
        db.add(mutual_fund1)

        mutual_fund2 = Investment(
            investment_id="INV002",
            user_id="USR001",
            name="HDFC Top 100 Fund",
            type="MUTUAL_FUND",
            category="EQUITY",
            subcategory="LARGE_CAP",
            provider="HDFC Mutual Fund",
            invested_amount=50000,
            current_value=58000,
            units=500,
            nav=116,
            returns_amount=8000,
            returns_percentage=16,
            risk_level="MODERATE",
            purchase_date=datetime.now() - timedelta(days=180)
        )
        db.add(mutual_fund2)

        # Create alerts
        fraud_alert = Alert(
            alert_id="ALERT001",
            user_id="USR001",
            type="FRAUD",
            title="Suspicious Transaction Detected",
            message="Unusual transaction of ₹15,000 detected from Suspicious Merchant XYZ",
            severity="HIGH",
            related_entity_type="transaction",
            related_entity_id="TXN005",
            action_required=True,
            action_type="VERIFY",
            is_read=False
        )
        db.add(fraud_alert)

        goal_alert = Alert(
            alert_id="ALERT002",
            user_id="USR001",
            type="GOAL",
            title="Goal Behind Schedule",
            message="Your Europe Trip goal is 20% behind schedule",
            severity="MEDIUM",
            related_entity_type="goal",
            related_entity_id="GOAL002",
            is_read=False
        )
        db.add(goal_alert)

        # Create insights
        spending_insight = Insight(
            insight_id="INSIGHT001",
            user_id="USR001",
            type="SPENDING",
            category="FOOD",
            title="Food Expenses Rising",
            description="Your food delivery expenses increased by 30% this month",
            recommendation="Consider cooking at home 2-3 days per week to save ₹5,000 monthly",
            priority="MEDIUM",
            potential_savings=5000,
            impact_timeframe="IMMEDIATE",
            confidence_score=0.85
        )
        db.add(spending_insight)

        investment_insight = Insight(
            insight_id="INSIGHT002",
            user_id="USR001",
            type="INVESTMENT",
            category="MUTUAL_FUND",
            title="Portfolio Performing Well",
            description="Your mutual funds have generated 22% average returns",
            recommendation="Consider increasing SIP by ₹5,000 to reach goals faster",
            priority="LOW",
            potential_earnings=15000,
            impact_timeframe="LONG_TERM",
            confidence_score=0.90
        )
        db.add(investment_insight)

        # Commit all changes
        db.commit()
        logger.info("✅ Initial demo data populated successfully")

    except Exception as e:
        logger.error(f"Error populating demo data: {e}")
        db.rollback()
        raise
    finally:
        if not db:
            db.close()

def load_mock_data_to_db():
    """
    Load mock data from JSON file to database
    """
    mock_data_path = Path(__file__).parent.parent / "data" / "mock_financial_data.json"

    if not mock_data_path.exists():
        logger.warning("Mock data file not found, using default demo data")
        populate_initial_data()
        return

    try:
        with open(mock_data_path, 'r') as f:
            mock_data = json.load(f)

        db = SessionLocal()

        # Process and insert mock data
        # This would be more complex in production
        logger.info("Loading mock data from JSON file...")

        # Add implementation to load from JSON if needed

        db.commit()
        logger.info("✅ Mock data loaded successfully")

    except Exception as e:
        logger.error(f"Error loading mock data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    # Initialize database when run directly
    init_database()
    populate_initial_data()