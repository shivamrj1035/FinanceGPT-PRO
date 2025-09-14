"""
Gemini-powered User Data Generator for FinanceGPT Pro
Creates realistic, diverse user profiles with financial data
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List
import random
import os
from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv()

# Import Gemini
try:
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from ai_models.advanced_gemini import get_gemini_analyzer
    from api.enhanced_database_service import get_enhanced_database_service
    GEMINI_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Gemini not available: {e}")
    GEMINI_AVAILABLE = False

logger = logging.getLogger(__name__)

class GeminiUserGenerator:
    """
    Generate realistic user profiles using Gemini AI
    """

    def __init__(self):
        if GEMINI_AVAILABLE:
            # Check if API key is available
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise Exception("GEMINI_API_KEY not found in environment")

            logger.info(f"✅ API Key found: {api_key[:10]}...")
            self.gemini = get_gemini_analyzer()
            self.db = get_enhanced_database_service()
            logger.info("✅ Gemini analyzer initialized")
        else:
            raise Exception("Gemini API not available for user generation")

    async def generate_user_profile_simple(self, user_type: str) -> Dict[str, Any]:
        """Generate user profile using direct Gemini API call"""
        try:
            import google.genai as genai

            api_key = os.getenv("GEMINI_API_KEY")
            client = genai.Client(api_key=api_key)

            simple_prompt = f"""Generate a realistic Indian financial user profile for a {user_type.replace('_', ' ')}.

Return ONLY this JSON structure with realistic Indian data:
{{
  "name": "Indian Name",
  "email": "email@domain.com",
  "age": 30,
  "profession": "Job Title",
  "location": "Indian City"
}}

Use realistic Indian names and details. Return only the JSON, nothing else."""

            response = client.models.generate_content(
                model='gemini-2.0-flash',
                contents=simple_prompt
            )
            json_str = response.text.strip()

            # Remove markdown if present
            if json_str.startswith("```"):
                lines = json_str.split('\n')
                json_str = '\n'.join([line for line in lines if not line.startswith("```")])

            # Find JSON in the response
            import re
            json_match = re.search(r'\{.*\}', json_str, re.DOTALL)
            if json_match:
                profile = json.loads(json_match.group())
                logger.info(f"✅ Generated profile for {profile.get('name', 'Unknown')}")
                return await self._create_enhanced_fallback_profile(user_type, profile)

            logger.warning("No JSON found in Gemini response")
            return await self._create_fallback_profile(user_type)

        except Exception as e:
            logger.error(f"Direct Gemini call failed: {e}")
            return await self._create_fallback_profile(user_type)

    async def generate_user_profile(self, user_type: str) -> Dict[str, Any]:
        """Generate a complete user profile based on type"""

        prompts = {
            "young_professional": """
            Create a realistic financial profile for a 28-year-old software engineer in Bangalore, India.

            Include:
            - Personal details (name, email, demographics)
            - 2-3 bank accounts (savings, salary account)
            - 50+ realistic transactions from last 3 months (UPI, card payments, salary credits)
            - Investment portfolio (mutual funds, stocks, PPF)
            - Financial goals (house purchase, vacation, emergency fund)
            - Spending patterns typical of tech professionals

            Make transactions realistic with Indian merchants like:
            - Swiggy, Zomato, Uber, Ola
            - Amazon, Flipkart, BigBasket
            - PVR, BookMyShow
            - Local grocery stores, petrol pumps
            - Utility payments, rent

            Return as JSON with Indian context.
            """,

            "family_person": """
            Create a realistic financial profile for a 35-year-old married person with 2 kids in Delhi, India.

            Include:
            - Personal details (name, email, demographics)
            - Joint and individual accounts
            - Family-oriented transactions (school fees, groceries, medical)
            - Home loan, car loan, insurance premiums
            - Child education planning, retirement savings
            - Conservative investment approach
            - Higher expenses for family needs

            Make transactions show family spending patterns:
            - School fee payments
            - Medical expenses
            - Family shopping at malls
            - Vacation bookings
            - Children's activities

            Return as JSON with Indian family context.
            """,

            "senior_saver": """
            Create a realistic financial profile for a 45-year-old business owner in Mumbai, India.

            Include:
            - Personal details (name, email, demographics)
            - Multiple business and personal accounts
            - High-value transactions and investments
            - Diverse investment portfolio (real estate, equity, bonds)
            - Tax-saving investments
            - Business expenses mixed with personal
            - Regular large transactions

            Make transactions show business owner patterns:
            - Business supplier payments
            - Client payments received
            - High-end restaurant bills
            - Premium shopping
            - Travel expenses
            - Professional services

            Return as JSON with Indian business context.
            """
        }

        try:
            # Modify prompt to ensure JSON output
            json_prompt = f"""
            {prompts[user_type]}

            IMPORTANT: Return ONLY a valid JSON object with this exact structure:
            {{
                "name": "Full Name",
                "email": "email@example.com",
                "age": 30,
                "profession": "Job Title",
                "location": "City, India",
                "accounts": [
                    {{"bank": "Bank Name", "type": "SAVINGS", "balance": 150000}}
                ],
                "transactions": [
                    {{"amount": -5000, "merchant": "Merchant Name", "category": "FOOD", "description": "Transaction desc"}}
                ],
                "investments": [
                    {{"type": "MUTUAL_FUND", "name": "Investment Name", "amount": 100000, "current_value": 110000}}
                ],
                "goals": [
                    {{"name": "Goal Name", "target_amount": 500000, "current_amount": 50000}}
                ]
            }}

            Return ONLY the JSON, no other text.
            """

            result = await self.gemini.analyze_with_self_consistency(
                query=json_prompt,
                context={"task": "user_generation", "format": "json_only"},
                passes=1
            )

            logger.info(f"📋 Raw Gemini result type: {type(result)}")

            # Parse the generated profile
            if isinstance(result, dict) and "recommendation" in result:
                recommendation = result["recommendation"]
                logger.info(f"📋 Recommendation type: {type(recommendation)}")
                logger.info(f"📋 First 200 chars: {str(recommendation)[:200]}...")

                if isinstance(recommendation, str):
                    # Clean the response and extract JSON
                    cleaned = recommendation.strip()

                    # Remove markdown code blocks if present
                    if cleaned.startswith("```"):
                        lines = cleaned.split('\n')
                        cleaned = '\n'.join(lines[1:-1])

                    # Try multiple JSON extraction methods
                    import re

                    # Method 1: Look for complete JSON object
                    json_matches = re.findall(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', cleaned, re.DOTALL)

                    for json_str in json_matches:
                        try:
                            profile_data = json.loads(json_str)
                            logger.info(f"✅ Successfully parsed JSON with {len(profile_data)} keys")
                            return await self._structure_user_data(profile_data, user_type)
                        except json.JSONDecodeError as e:
                            logger.warning(f"JSON parse attempt failed: {e}")
                            continue

                    # Method 2: Try the entire cleaned string
                    try:
                        profile_data = json.loads(cleaned)
                        logger.info(f"✅ Successfully parsed full response as JSON")
                        return await self._structure_user_data(profile_data, user_type)
                    except json.JSONDecodeError:
                        logger.warning("Failed to parse full response as JSON")

            logger.warning("Failed to parse JSON from Gemini response, using fallback")
            return await self._create_fallback_profile(user_type)

        except Exception as e:
            logger.warning(f"Gemini generation failed for {user_type}: {e}")
            return await self._create_fallback_profile(user_type)

    async def _structure_user_data(self, raw_data: Dict[str, Any], user_type: str) -> Dict[str, Any]:
        """Structure the Gemini-generated data into our database format"""
        user_id = f"USR_{uuid.uuid4().hex[:8].upper()}"

        # Extract basic info
        name = raw_data.get("name", f"Demo {user_type.replace('_', ' ').title()}")
        email = raw_data.get("email", f"{name.lower().replace(' ', '.')}@example.com")

        structured_data = {
            "id": user_id,
            "name": name,
            "email": email,
            "password": "demo123",  # Demo password
            "profile": {
                "age": raw_data.get("age", 30),
                "profession": raw_data.get("profession", "Professional"),
                "location": raw_data.get("location", "India"),
                "user_type": user_type
            },
            "accounts": [],
            "transactions": [],
            "investments": [],
            "goals": []
        }

        # Generate accounts
        accounts = raw_data.get("accounts", [])
        for i, account_data in enumerate(accounts[:3]):  # Max 3 accounts
            account = {
                "id": f"ACC_{user_id}_{i+1:03d}",
                "bank_name": account_data.get("bank", ["HDFC Bank", "ICICI Bank", "SBI"][i % 3]),
                "account_type": account_data.get("type", "SAVINGS"),
                "account_number": f"****{random.randint(1000, 9999)}",
                "balance": float(account_data.get("balance", random.randint(50000, 500000)))
            }
            structured_data["accounts"].append(account)

        # Generate transactions
        transactions = raw_data.get("transactions", [])
        account_ids = [acc["id"] for acc in structured_data["accounts"]]

        for i, txn_data in enumerate(transactions[:50]):  # Max 50 transactions
            transaction = {
                "id": f"TXN_{user_id}_{i+1:04d}",
                "account_id": random.choice(account_ids),
                "amount": float(txn_data.get("amount", random.randint(-50000, 100000))),
                "merchant": txn_data.get("merchant", "Generic Merchant"),
                "category": txn_data.get("category", "GENERAL"),
                "description": txn_data.get("description", "Transaction"),
                "date": (datetime.now() - timedelta(days=random.randint(1, 90))).isoformat()
            }
            structured_data["transactions"].append(transaction)

        # Generate investments
        investments = raw_data.get("investments", [])
        for i, inv_data in enumerate(investments[:5]):  # Max 5 investments
            investment = {
                "id": f"INV_{user_id}_{i+1:03d}",
                "type": inv_data.get("type", "MUTUAL_FUND"),
                "name": inv_data.get("name", f"Investment {i+1}"),
                "amount": float(inv_data.get("amount", random.randint(10000, 100000))),
                "current_value": float(inv_data.get("current_value", inv_data.get("amount", 0) * 1.1)),
                "purchase_date": (datetime.now() - timedelta(days=random.randint(30, 365))).isoformat()
            }
            structured_data["investments"].append(investment)

        # Generate goals
        goals = raw_data.get("goals", [])
        for i, goal_data in enumerate(goals[:3]):  # Max 3 goals
            goal = {
                "id": f"GOAL_{user_id}_{i+1:03d}",
                "name": goal_data.get("name", f"Financial Goal {i+1}"),
                "target_amount": float(goal_data.get("target_amount", random.randint(100000, 1000000))),
                "current_amount": float(goal_data.get("current_amount", 0)),
                "target_date": (datetime.now() + timedelta(days=random.randint(365, 1825))).isoformat()
            }
            structured_data["goals"].append(goal)

        return structured_data

    async def _create_enhanced_fallback_profile(self, user_type: str, gemini_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Create enhanced fallback using Gemini-generated basic info"""
        user_id = f"USR_{uuid.uuid4().hex[:8].upper()}"

        return {
            "id": user_id,
            "name": gemini_profile.get("name", f"Demo User {user_type}"),
            "email": gemini_profile.get("email", f"demo{user_id.lower()}@finara.com"),
            "password": "demo123",
            "profile": {
                "age": gemini_profile.get("age", 30),
                "profession": gemini_profile.get("profession", "Professional"),
                "location": gemini_profile.get("location", "India"),
                "user_type": user_type
            },
            "accounts": self._generate_sample_accounts(user_id, user_type),
            "transactions": self._generate_sample_transactions(user_id, user_type),
            "investments": self._generate_sample_investments(user_id, user_type),
            "goals": self._generate_sample_goals(user_id, user_type)
        }

    async def _create_fallback_profile(self, user_type: str) -> Dict[str, Any]:
        """Create a fallback profile if Gemini generation fails"""
        user_id = f"USR_{uuid.uuid4().hex[:8].upper()}"

        profiles = {
            "young_professional": {
                "name": "Arjun Sharma",
                "email": "arjun.sharma@techcorp.com",
                "profession": "Software Engineer",
                "age": 28,
                "location": "Bangalore"
            },
            "family_person": {
                "name": "Priya Patel",
                "email": "priya.patel@gmail.com",
                "profession": "Marketing Manager",
                "age": 35,
                "location": "Delhi"
            },
            "senior_saver": {
                "name": "Rajesh Gupta",
                "email": "rajesh.gupta@business.com",
                "profession": "Business Owner",
                "age": 45,
                "location": "Mumbai"
            }
        }

        profile = profiles[user_type]

        return {
            "id": user_id,
            "name": profile["name"],
            "email": profile["email"],
            "password": "demo123",
            "profile": profile,
            "accounts": self._generate_sample_accounts(user_id, user_type),
            "transactions": self._generate_sample_transactions(user_id, user_type),
            "investments": self._generate_sample_investments(user_id, user_type),
            "goals": self._generate_sample_goals(user_id, user_type)
        }

    def _generate_sample_accounts(self, user_id: str, user_type: str) -> List[Dict[str, Any]]:
        """Generate sample accounts based on user type"""
        accounts = []

        base_accounts = [
            {"bank": "HDFC Bank", "type": "SAVINGS", "balance": 150000},
            {"bank": "ICICI Bank", "type": "CURRENT", "balance": 75000}
        ]

        if user_type == "senior_saver":
            base_accounts.append({"bank": "SBI", "type": "BUSINESS", "balance": 500000})

        for i, acc in enumerate(base_accounts):
            accounts.append({
                "id": f"ACC_{user_id}_{i+1:03d}",
                "bank_name": acc["bank"],
                "account_type": acc["type"],
                "account_number": f"****{random.randint(1000, 9999)}",
                "balance": float(acc["balance"])
            })

        return accounts

    def _generate_sample_transactions(self, user_id: str, user_type: str) -> List[Dict[str, Any]]:
        """Generate sample transactions based on user type"""
        transactions = []

        merchants = {
            "young_professional": ["SWIGGY", "UBER", "AMAZON", "NETFLIX", "STARBUCKS", "PVR"],
            "family_person": ["BIG BAZAAR", "APOLLO PHARMACY", "SCHOOL FEE", "GROCERY STORE", "MEDICAL"],
            "senior_saver": ["BUSINESS SUPPLIER", "RESTAURANT", "TRAVEL AGENCY", "PREMIUM BRAND", "TAX PAYMENT"]
        }

        for i in range(30):  # Generate 30 sample transactions
            amount = random.randint(-50000, 20000) if random.random() < 0.7 else random.randint(50000, 200000)

            transactions.append({
                "id": f"TXN_{user_id}_{i+1:04d}",
                "account_id": f"ACC_{user_id}_001",
                "amount": float(amount),
                "merchant": random.choice(merchants[user_type]),
                "category": random.choice(["FOOD", "TRANSPORT", "SHOPPING", "BILLS", "ENTERTAINMENT"]),
                "description": f"Transaction {i+1}",
                "date": (datetime.now() - timedelta(days=random.randint(1, 90))).isoformat()
            })

        return transactions

    def _generate_sample_investments(self, user_id: str, user_type: str) -> List[Dict[str, Any]]:
        """Generate sample investments"""
        investments = []

        inv_types = {
            "young_professional": ["MUTUAL_FUND", "PPF", "STOCKS"],
            "family_person": ["CHILD_PLAN", "LIFE_INSURANCE", "MUTUAL_FUND"],
            "senior_saver": ["REAL_ESTATE", "BONDS", "EQUITY", "GOLD"]
        }

        for i, inv_type in enumerate(inv_types[user_type]):
            amount = random.randint(50000, 500000)
            investments.append({
                "id": f"INV_{user_id}_{i+1:03d}",
                "type": inv_type,
                "name": f"{inv_type.replace('_', ' ').title()} Investment",
                "amount": float(amount),
                "current_value": float(amount * random.uniform(0.9, 1.3)),
                "purchase_date": (datetime.now() - timedelta(days=random.randint(30, 365))).isoformat()
            })

        return investments

    def _generate_sample_goals(self, user_id: str, user_type: str) -> List[Dict[str, Any]]:
        """Generate sample goals"""
        goals = []

        goal_types = {
            "young_professional": ["House Purchase", "Vacation Fund", "Emergency Fund"],
            "family_person": ["Children Education", "Family Vacation", "Home Renovation"],
            "senior_saver": ["Retirement Fund", "Business Expansion", "Luxury Purchase"]
        }

        for i, goal_name in enumerate(goal_types[user_type]):
            goals.append({
                "id": f"GOAL_{user_id}_{i+1:03d}",
                "name": goal_name,
                "target_amount": float(random.randint(500000, 5000000)),
                "current_amount": float(random.randint(0, 200000)),
                "target_date": (datetime.now() + timedelta(days=random.randint(365, 1825))).isoformat()
            })

        return goals

    async def generate_all_users(self) -> List[Dict[str, Any]]:
        """Generate all three user types"""
        user_types = ["young_professional", "family_person", "senior_saver"]
        users = []

        for user_type in user_types:
            logger.info(f"🤖 Generating {user_type} profile with Gemini...")
            user_data = await self.generate_user_profile_simple(user_type)
            users.append(user_data)
            logger.info(f"✅ Generated {user_data['name']} ({user_data['email']})")

        return users

    async def populate_database(self) -> bool:
        """Generate users and populate the database"""
        try:
            logger.info("🚀 Starting Gemini-powered user generation...")

            # Generate all users
            users = await self.generate_all_users()

            # Store in database
            logger.info("💾 Storing users in database...")
            for user_data in users:
                success = await self.db.create_user(user_data)
                if success:
                    logger.info(f"✅ Stored {user_data['name']} in database")
                else:
                    logger.error(f"❌ Failed to store {user_data['name']}")

            logger.info("🎉 Database population complete!")
            return True

        except Exception as e:
            logger.error(f"Database population failed: {e}")
            return False


async def main():
    """Main function to generate and populate users"""
    logging.basicConfig(level=logging.INFO)

    if not GEMINI_AVAILABLE:
        logger.error("❌ Gemini API not available. Please check your setup.")
        return

    try:
        generator = GeminiUserGenerator()
        success = await generator.populate_database()
        if success:
            print("✅ Database populated successfully!")
        else:
            print("❌ Database population failed!")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())