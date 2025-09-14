"""
Mock Data Loader for MCP Server
Loads pre-generated mock financial data for demo
"""

import json
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def load_mock_data():
    """
    Load mock data from extracted database content
    """
    # Try to load from extracted database data first
    data_dir = Path(__file__).parent.parent / "data" / "mock"

    if data_dir.exists():
        try:
            extracted_data = {}
            # Only load 4 core financial data sources for hackathon demo
            data_files = ["users", "accounts", "transactions", "investments"]

            # Load each data type from separate JSON files
            for file_name in data_files:
                file_path = data_dir / f"{file_name}.json"
                if file_path.exists():
                    with open(file_path, 'r') as f:
                        extracted_data[file_name] = json.load(f)
                        logger.info(f"📦 Loaded extracted {file_name} data ({len(extracted_data[file_name])} records)")

            if extracted_data:
                logger.info("✅ Using extracted database content as mock data")
                return extracted_data

        except Exception as e:
            logger.error(f"❌ Failed to load extracted data: {e}")

    # Try to load from generated mock data file as fallback
    mock_data_path = Path(__file__).parent.parent.parent / "data" / "mock_financial_data.json"

    if mock_data_path.exists():
        try:
            with open(mock_data_path, 'r') as f:
                data = json.load(f)
                logger.info(f"📦 Loaded mock data from {mock_data_path}")
                return data
        except Exception as e:
            logger.error(f"❌ Failed to load mock data: {e}")

    # Return default mock data if file not found
    logger.info("🎲 Using default mock data")
    return get_default_mock_data()

def get_default_mock_data():
    """
    Returns default mock financial data for demo
    """
    return {
        "users": [
            {
                "id": "USR001",
                "name": "Demo User",
                "email": "demo@financegpt.com",
                "phone": "+91-9876543210",
                "created_at": "2024-01-01T00:00:00"
            }
        ],
        "accounts": [
            {
                "id": "ACC001",
                "user_id": "USR001",
                "bank_name": "HDFC Bank",
                "account_type": "SAVINGS",
                "account_number": "****1234",
                "balance": 250000.00,
                "currency": "INR",
                "created_at": "2024-01-01T00:00:00"
            },
            {
                "id": "ACC002",
                "user_id": "USR001",
                "bank_name": "ICICI Bank",
                "account_type": "CURRENT",
                "account_number": "****5678",
                "balance": 150000.00,
                "currency": "INR",
                "created_at": "2024-01-01T00:00:00"
            }
        ],
        "transactions": [
            {
                "id": "TXN001",
                "account_id": "ACC001",
                "amount": -5000.00,
                "merchant": "Swiggy",
                "category": "FOOD",
                "date": "2025-01-10T12:30:00",
                "description": "Food delivery",
                "transaction_type": "DEBIT"
            },
            {
                "id": "TXN002",
                "account_id": "ACC001",
                "amount": 150000.00,
                "merchant": "TechCorp Salary",
                "category": "INCOME",
                "date": "2025-01-01T00:00:00",
                "description": "Monthly salary",
                "transaction_type": "CREDIT"
            },
            {
                "id": "TXN003",
                "account_id": "ACC001",
                "amount": -35000.00,
                "merchant": "House Rent",
                "category": "HOUSING",
                "date": "2025-01-05T00:00:00",
                "description": "Monthly rent",
                "transaction_type": "DEBIT"
            },
            {
                "id": "TXN004",
                "account_id": "ACC001",
                "amount": -2500.00,
                "merchant": "Amazon",
                "category": "SHOPPING",
                "date": "2025-01-08T15:45:00",
                "description": "Online shopping",
                "transaction_type": "DEBIT"
            },
            {
                "id": "TXN005",
                "account_id": "ACC002",
                "amount": -15000.00,
                "merchant": "Suspicious Merchant XYZ",
                "category": "OTHER",
                "date": "2025-01-12T03:30:00",
                "description": "International transaction",
                "transaction_type": "DEBIT",
                "flagged": True
            }
        ],
        "goals": [
            {
                "id": "GOAL001",
                "user_id": "USR001",
                "name": "Emergency Fund",
                "target_amount": 500000.00,
                "current_amount": 250000.00,
                "target_date": "2025-12-31",
                "priority": "HIGH",
                "status": "ON_TRACK",
                "progress_percentage": 50
            },
            {
                "id": "GOAL002",
                "user_id": "USR001",
                "name": "Europe Trip",
                "target_amount": 300000.00,
                "current_amount": 75000.00,
                "target_date": "2025-06-30",
                "priority": "MEDIUM",
                "status": "BEHIND",
                "progress_percentage": 25
            }
        ],
        "investments": [
            {
                "id": "INV001",
                "user_id": "USR001",
                "name": "Axis Bluechip Fund",
                "type": "MUTUAL_FUND",
                "invested_amount": 100000.00,
                "current_value": 125000.00,
                "returns_percentage": 25.0,
                "start_date": "2024-01-01"
            },
            {
                "id": "INV002",
                "user_id": "USR001",
                "name": "HDFC Top 100 Fund",
                "type": "MUTUAL_FUND",
                "invested_amount": 50000.00,
                "current_value": 58000.00,
                "returns_percentage": 16.0,
                "start_date": "2024-06-01"
            }
        ],
        "credit_data": [
            {
                "user_id": "USR001",
                "credit_score": 750,
                "credit_age": 5,
                "payment_history": 98,
                "credit_utilization": 25,
                "total_accounts": 3,
                "recent_inquiries": 1,
                "last_updated": "2025-01-01"
            }
        ],
        "alerts": [
            {
                "id": "ALERT001",
                "user_id": "USR001",
                "type": "FRAUD",
                "title": "Suspicious Transaction Detected",
                "message": "Unusual transaction of ₹15,000 detected",
                "severity": "HIGH",
                "created_at": "2025-01-12T03:35:00",
                "read": False
            },
            {
                "id": "ALERT002",
                "user_id": "USR001",
                "type": "GOAL",
                "title": "Goal Behind Schedule",
                "message": "Your Europe Trip goal is 20% behind schedule",
                "severity": "MEDIUM",
                "created_at": "2025-01-10T09:00:00",
                "read": False
            }
        ],
        "insights": [
            {
                "id": "INSIGHT001",
                "user_id": "USR001",
                "type": "SPENDING",
                "title": "Food Expenses Rising",
                "description": "Your food delivery expenses increased by 30% this month",
                "recommendation": "Consider cooking at home 2-3 days per week to save ₹5,000 monthly",
                "priority": "MEDIUM",
                "potential_savings": 5000.00,
                "created_at": "2025-01-11T00:00:00"
            },
            {
                "id": "INSIGHT002",
                "user_id": "USR001",
                "type": "INVESTMENT",
                "title": "Portfolio Performing Well",
                "description": "Your mutual funds have generated 22% average returns",
                "recommendation": "Consider increasing SIP by ₹5,000 to reach goals faster",
                "priority": "LOW",
                "created_at": "2025-01-10T00:00:00"
            }
        ],
        "permissions": [
            {
                "user_id": "USR001",
                "resource": "accounts",
                "access_level": "GRANTED"
            },
            {
                "user_id": "USR001",
                "resource": "transactions",
                "access_level": "GRANTED"
            },
            {
                "user_id": "USR001",
                "resource": "investments",
                "access_level": "GRANTED"
            },
            {
                "user_id": "USR001",
                "resource": "credit_score",
                "access_level": "GRANTED"
            }
        ]
    }