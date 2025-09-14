"""
AI Service Layer for FinanceGPT Pro
Provides AI-enhanced analysis while maintaining backward compatibility
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import os
from dotenv import load_dotenv

# Import database service
try:
    from .database_service import get_database_service
    DATABASE_INTEGRATION_AVAILABLE = True
except ImportError:
    DATABASE_INTEGRATION_AVAILABLE = False

# Load environment variables
load_dotenv()

# Import AI models
try:
    from ai_models import (
        fraud_detector,
        spending_analyzer,
        investment_engine,
        credit_predictor,
        get_gemini_analyzer,
        get_consistency_checker
    )
    AI_MODELS_AVAILABLE = True
except ImportError as e:
    logging.warning(f"AI models not available: {e}")
    AI_MODELS_AVAILABLE = False

logger = logging.getLogger(__name__)


class AIService:
    """
    Central AI service that enhances existing functionality
    Falls back gracefully if AI is unavailable
    """

    def __init__(self):
        self.ai_enabled = AI_MODELS_AVAILABLE and os.getenv("GEMINI_API_KEY")
        self.database_enabled = DATABASE_INTEGRATION_AVAILABLE

        if self.ai_enabled:
            self.gemini = get_gemini_analyzer()
            self.consistency_checker = get_consistency_checker()
            logger.info("✅ AI Service initialized with Gemini")
        else:
            logger.warning("⚠️ AI Service running without Gemini (using basic models)")

        if self.database_enabled:
            self.db = get_database_service()
            logger.info("✅ Database integration enabled")
        else:
            logger.warning("⚠️ Database integration not available")

    async def enhance_fraud_detection(
        self,
        transaction: Dict[str, Any],
        existing_result: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Enhance fraud detection with AI analysis
        Preserves existing result structure
        """
        try:
            # Start with existing result or create new
            result = existing_result or {
                "risk_score": 0.5,
                "risk_level": "MEDIUM",
                "recommended_action": "MONITOR"
            }

            # Add basic model analysis
            if AI_MODELS_AVAILABLE:
                # Get user history (mock for now)
                history = self._get_mock_history()

                # Basic fraud detection
                basic_result = fraud_detector.predict(transaction, history)
                result.update({
                    "risk_score": basic_result["risk_score"],
                    "risk_level": basic_result["risk_level"],
                    "recommended_action": basic_result["recommended_action"],
                    "risk_factors": basic_result.get("risk_factors", [])
                })

            # Enhance with Gemini if available
            if self.ai_enabled:
                try:
                    gemini_result = await self.gemini.analyze_fraud_with_cot(
                        transaction=transaction,
                        user_history=self._get_mock_history()
                    )

                    # Add AI insights without overwriting basic data
                    result["ai_analysis"] = {
                        "reasoning_steps": gemini_result.get("reasoning_steps", []),
                        "confidence": gemini_result.get("confidence", 0),
                        "explanation": gemini_result.get("explanation", ""),
                        "indian_context": gemini_result.get("indian_context_notes", "")
                    }

                    # Use AI score if confidence is high
                    if gemini_result.get("confidence", 0) > 0.7:
                        result["risk_score"] = gemini_result.get("risk_score", result["risk_score"])
                        result["risk_level"] = gemini_result.get("risk_level", result["risk_level"])

                except Exception as e:
                    logger.warning(f"Gemini analysis failed, using basic model: {e}")

            # Store prediction in database if enabled
            if self.database_enabled:
                try:
                    user_id = transaction.get("user_id", "unknown")
                    await self.db.store_fraud_prediction(user_id, transaction, result)
                except Exception as e:
                    logger.warning(f"Database storage failed: {e}")

            return result

        except Exception as e:
            logger.error(f"AI fraud enhancement failed: {e}")
            return existing_result or {"error": "Analysis failed"}

    async def enhance_investment_analysis(
        self,
        user_profile: Dict[str, Any],
        goals: List[Dict],
        existing_result: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Enhance investment recommendations with AI
        """
        try:
            result = existing_result or {}

            # Basic investment analysis
            if AI_MODELS_AVAILABLE:
                basic_result = investment_engine.recommend(user_profile, goals)
                result.update(basic_result)

            # Enhance with Gemini
            if self.ai_enabled:
                try:
                    gemini_result = await self.gemini.analyze_investment_with_few_shot(
                        user_profile=user_profile,
                        goals=goals
                    )

                    # Merge AI insights
                    result["ai_recommendations"] = {
                        "asset_allocation": gemini_result.get("asset_allocation", {}),
                        "specific_funds": gemini_result.get("specific_recommendations", []),
                        "tax_saving": gemini_result.get("tax_saving_instruments", []),
                        "sip_plan": gemini_result.get("sip_plan", {}),
                        "key_advice": gemini_result.get("key_advice", [])
                    }

                except Exception as e:
                    logger.warning(f"Gemini investment analysis failed: {e}")

            return result

        except Exception as e:
            logger.error(f"AI investment enhancement failed: {e}")
            return existing_result or {}

    async def enhance_spending_analysis(
        self,
        transactions: List[Dict],
        existing_result: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Enhance spending analysis with AI insights
        """
        try:
            result = existing_result or {}

            # Basic spending analysis
            if AI_MODELS_AVAILABLE:
                basic_result = spending_analyzer.analyze(transactions)
                result.update(basic_result)

            # Add AI-powered insights
            if self.ai_enabled and transactions:
                try:
                    # Get spending insights from Gemini
                    query = f"Analyze spending patterns for {len(transactions)} transactions"
                    context = {
                        "total_spent": sum(abs(t.get("amount", 0)) for t in transactions if t.get("amount", 0) < 0),
                        "transaction_count": len(transactions),
                        "categories": list(set(t.get("category", "OTHER") for t in transactions))
                    }

                    gemini_result = await self.gemini.analyze_with_self_consistency(
                        query=query,
                        context=context,
                        passes=2
                    )

                    result["ai_insights"] = {
                        "recommendations": gemini_result.get("recommendation", ""),
                        "key_points": gemini_result.get("key_points", []),
                        "action_items": gemini_result.get("action_items", []),
                        "confidence": gemini_result.get("confidence_score", 0)
                    }

                except Exception as e:
                    logger.warning(f"Gemini spending analysis failed: {e}")

            return result

        except Exception as e:
            logger.error(f"AI spending enhancement failed: {e}")
            return existing_result or {}

    async def enhance_credit_analysis(
        self,
        user_data: Dict[str, Any],
        existing_result: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Enhance credit score analysis with AI
        """
        try:
            result = existing_result or {}

            # Basic credit analysis
            if AI_MODELS_AVAILABLE:
                basic_result = credit_predictor.predict(user_data)
                result.update(basic_result)

            # Add AI recommendations
            if self.ai_enabled:
                try:
                    query = "How to improve credit score from {} to 800+".format(
                        result.get("predicted_score", 700)
                    )

                    gemini_result = await self.gemini.explain_financial_concept(
                        concept=f"Credit Score Improvement from {result.get('predicted_score', 700)}",
                        user_level="intermediate"
                    )

                    result["ai_guidance"] = {
                        "improvement_steps": gemini_result.get("action_steps", []),
                        "benefits": gemini_result.get("benefits", []),
                        "timeline": "3-6 months with consistent effort"
                    }

                except Exception as e:
                    logger.warning(f"Gemini credit analysis failed: {e}")

            return result

        except Exception as e:
            logger.error(f"AI credit enhancement failed: {e}")
            return existing_result or {}

    async def generate_ai_insights(
        self,
        data_type: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate AI-powered insights for any data type
        """
        if not self.ai_enabled:
            return {
                "insights": ["AI insights require Gemini API key"],
                "source": "basic_analysis"
            }

        try:
            # Map data types to prompts
            prompts = {
                "transactions": "Analyze these financial transactions and provide actionable insights",
                "portfolio": "Evaluate this investment portfolio and suggest optimizations",
                "goals": "Review these financial goals and provide achievement strategies",
                "fraud": "Assess fraud risk patterns and recommend preventive measures"
            }

            query = prompts.get(data_type, f"Analyze this {data_type} data")

            result = await self.gemini.analyze_with_self_consistency(
                query=query,
                context=context,
                passes=2
            )

            insight_result = {
                "insights": result.get("key_points", []),
                "recommendations": result.get("action_items", []),
                "confidence": result.get("confidence_score", 0),
                "source": "gemini_ai"
            }

            # Store insight in database if enabled
            if self.database_enabled:
                try:
                    user_id = context.get("user_id", "unknown")
                    await self.db.store_ai_insight(user_id, data_type, context, insight_result)
                except Exception as e:
                    logger.warning(f"Database storage failed: {e}")

            return insight_result

        except Exception as e:
            logger.error(f"AI insight generation failed: {e}")
            return {
                "insights": ["Analysis failed"],
                "source": "error"
            }

    def _get_mock_history(self) -> List[Dict]:
        """
        Get mock transaction history for analysis
        """
        return [
            {"amount": -5000, "merchant": "AMAZON", "category": "SHOPPING", "date": datetime.now().isoformat()},
            {"amount": -2000, "merchant": "SWIGGY", "category": "FOOD", "date": datetime.now().isoformat()},
            {"amount": -1500, "merchant": "UBER", "category": "TRANSPORT", "date": datetime.now().isoformat()},
            {"amount": -3000, "merchant": "FLIPKART", "category": "SHOPPING", "date": datetime.now().isoformat()},
            {"amount": -500, "merchant": "NETFLIX", "category": "ENTERTAINMENT", "date": datetime.now().isoformat()}
        ]

    async def check_consistency(
        self,
        results: List[Dict[str, Any]],
        check_type: str = "risk_score"
    ) -> Dict[str, Any]:
        """
        Check consistency across multiple AI results
        """
        if not self.ai_enabled or not self.consistency_checker:
            return {"consistent": True, "confidence": 1.0}

        try:
            if check_type == "risk_score":
                return self.consistency_checker.check_risk_score_consistency(results)
            elif check_type == "numerical":
                values = [r.get("value", 0) for r in results]
                return self.consistency_checker.check_numerical_consistency(values)
            else:
                return {"consistent": True, "confidence": 1.0}

        except Exception as e:
            logger.error(f"Consistency check failed: {e}")
            return {"consistent": False, "error": str(e)}


# Singleton instance
_ai_service = None

def get_ai_service() -> AIService:
    """
    Get singleton instance of AI service
    """
    global _ai_service
    if _ai_service is None:
        _ai_service = AIService()
    return _ai_service