"""
Advanced Gemini AI Integration with Chain-of-Thought Reasoning
Implements sophisticated prompting techniques for financial analysis
"""

from google import genai
from google.genai import types
import json
import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import statistics
import os

logger = logging.getLogger(__name__)


class GeminiAdvancedAnalyzer:
    """
    Advanced Gemini integration with Chain-of-Thought, Few-Shot, and Self-Consistency
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "demo-key-for-hackathon")
        self.client = genai.Client(api_key=self.api_key)
        self.model = "gemini-2.0-flash"

        # Configuration for different analysis types
        self.configs = {
            "fraud": types.GenerateContentConfig(
                temperature=0.7,
                top_p=0.95,
                max_output_tokens=2048,
                response_mime_type="text/plain"
            ),
            "investment": types.GenerateContentConfig(
                temperature=0.8,
                top_p=0.9,
                max_output_tokens=3072,
                response_mime_type="text/plain"
            ),
            "general": types.GenerateContentConfig(
                temperature=0.9,
                top_p=0.95,
                max_output_tokens=2048,
                response_mime_type="text/plain"
            )
        }

        # Few-shot examples for Indian financial context
        self.few_shot_examples = {
            "fraud": [
                {
                    "transaction": {"amount": 50000, "merchant": "FLIPKART", "category": "SHOPPING"},
                    "analysis": "Normal e-commerce transaction during sale season",
                    "risk": "LOW"
                },
                {
                    "transaction": {"amount": 100000, "merchant": "CRYPTO_EXCHANGE_XYZ", "category": "INVESTMENT"},
                    "analysis": "High-risk crypto transaction, unusual for user profile",
                    "risk": "HIGH"
                }
            ],
            "tax": [
                {
                    "query": "How to save tax on 15 LPA salary?",
                    "response": "Utilize 80C (₹1.5L), 80D (health insurance), HRA, NPS (additional ₹50K)"
                }
            ],
            "investment": [
                {
                    "profile": {"age": 30, "income": 100000, "risk": "MODERATE"},
                    "recommendation": "60% equity, 30% debt, 10% gold for balanced growth"
                }
            ]
        }

    async def analyze_fraud_with_cot(
        self,
        transaction: Dict[str, Any],
        user_history: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Analyze fraud using Chain-of-Thought reasoning
        """
        # Calculate historical statistics if available
        history_context = ""
        if user_history:
            amounts = [abs(t.get("amount", 0)) for t in user_history]
            avg_amount = statistics.mean(amounts) if amounts else 0
            max_amount = max(amounts) if amounts else 0
            typical_merchants = list(set(t.get("merchant", "") for t in user_history[:20]))

            history_context = f"""
            Historical Context:
            - Average transaction: ₹{avg_amount:,.0f}
            - Maximum transaction: ₹{max_amount:,.0f}
            - Typical merchants: {', '.join(typical_merchants[:5])}
            """

        prompt = f"""
        You are an expert fraud detection analyst for Indian financial transactions.
        Analyze this transaction using step-by-step Chain-of-Thought reasoning.

        Transaction Details:
        - Amount: ₹{transaction.get('amount', 0):,.0f}
        - Merchant: {transaction.get('merchant', 'Unknown')}
        - Category: {transaction.get('category', 'Unknown')}
        - Date/Time: {transaction.get('date', 'Not provided')}
        - Payment Method: {transaction.get('payment_method', 'UPI')}

        {history_context}

        Perform detailed Chain-of-Thought analysis:

        Step 1: Amount Analysis
        - Is this amount unusual for the user?
        - How does it compare to typical transactions?
        - Consider Indian context (festivals, weddings, EMIs)

        Step 2: Merchant Verification
        - Is this a recognized/trusted merchant?
        - Any suspicious patterns in merchant name?
        - Does merchant match the category?

        Step 3: Timing Analysis
        - Is the transaction time unusual?
        - Consider Indian business hours and patterns
        - Any rapid succession of transactions?

        Step 4: Behavioral Patterns
        - Does this match user's spending behavior?
        - Any deviation from normal patterns?
        - Consider seasonal factors (Diwali, month-end salary)

        Step 5: Risk Calculation
        - Combine all factors with weights
        - Calculate overall risk score (0-100)
        - Determine confidence level

        Provide your analysis in this exact JSON format:
        {{
            "risk_score": <0-100>,
            "risk_level": "<LOW/MEDIUM/HIGH/CRITICAL>",
            "reasoning_steps": [
                {{"step": "Amount Analysis", "finding": "...", "risk_contribution": <0-25>}},
                {{"step": "Merchant Verification", "finding": "...", "risk_contribution": <0-25>}},
                {{"step": "Timing Analysis", "finding": "...", "risk_contribution": <0-25>}},
                {{"step": "Behavioral Patterns", "finding": "...", "risk_contribution": <0-25>}}
            ],
            "risk_factors": ["factor1", "factor2"],
            "recommended_action": "<ALLOW/MONITOR/VERIFY/BLOCK>",
            "confidence": <0.0-1.0>,
            "explanation": "Brief explanation for the user",
            "indian_context_notes": "Any India-specific considerations"
        }}
        """

        try:
            response = await self.client.aio.models.generate_content(
                model=self.model,
                contents=prompt,
                config=self.configs["fraud"]
            )

            # Parse JSON from response
            result = self._parse_json_response(response.text)

            # Add metadata
            result["model"] = "Gemini CoT"
            result["timestamp"] = datetime.now().isoformat()
            result["analysis_type"] = "chain_of_thought"

            return result

        except Exception as e:
            logger.error(f"Gemini CoT analysis failed: {e}")
            # Fallback to basic analysis
            return self._fallback_fraud_analysis(transaction)

    async def analyze_investment_with_few_shot(
        self,
        user_profile: Dict[str, Any],
        goals: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate investment recommendations using few-shot learning
        """
        # Build few-shot examples
        examples_text = "Here are some examples of personalized investment recommendations:\n\n"
        for example in self.few_shot_examples["investment"]:
            examples_text += f"""
            Profile: Age {example['profile']['age']}, Income ₹{example['profile']['income']}/month, Risk: {example['profile']['risk']}
            Recommendation: {example['recommendation']}
            ---
            """

        prompt = f"""
        You are an expert financial advisor specializing in Indian markets.
        Use the examples below to generate personalized investment recommendations.

        {examples_text}

        Now analyze this user:
        Profile:
        - Age: {user_profile.get('age', 30)}
        - Monthly Income: ₹{user_profile.get('monthly_income', 50000):,}
        - Risk Tolerance: {user_profile.get('risk_tolerance', 'MODERATE')}
        - Investment Experience: {user_profile.get('experience', 'Beginner')}

        Financial Goals:
        {json.dumps(goals[:3], indent=2) if goals else 'No specific goals provided'}

        Provide comprehensive investment recommendations considering:
        1. Indian tax-saving instruments (80C, 80D, NPS)
        2. Optimal asset allocation based on age and risk
        3. Specific mutual funds, stocks, and bonds
        4. SIP amounts for each goal
        5. Emergency fund requirements (post-COVID considerations)

        Format your response as JSON:
        {{
            "asset_allocation": {{
                "equity": <percentage>,
                "debt": <percentage>,
                "gold": <percentage>,
                "real_estate": <percentage>,
                "cash": <percentage>
            }},
            "specific_recommendations": [
                {{
                    "instrument": "name",
                    "type": "MUTUAL_FUND/STOCK/BOND/etc",
                    "allocation_percent": <number>,
                    "expected_return": <number>,
                    "risk_level": "LOW/MEDIUM/HIGH",
                    "reason": "explanation"
                }}
            ],
            "tax_saving_instruments": [
                {{
                    "instrument": "name",
                    "limit": <amount>,
                    "benefit": "explanation"
                }}
            ],
            "sip_plan": {{
                "total_monthly": <amount>,
                "distribution": [
                    {{"fund": "name", "amount": <amount>, "goal": "goal_name"}}
                ]
            }},
            "emergency_fund": {{
                "recommended_amount": <amount>,
                "current_coverage_months": <number>,
                "build_strategy": "explanation"
            }},
            "review_frequency": "MONTHLY/QUARTERLY/ANNUAL",
            "key_advice": ["advice1", "advice2", "advice3"]
        }}
        """

        try:
            response = await self.client.aio.models.generate_content(
                model=self.model,
                contents=prompt,
                config=self.configs["investment"]
            )

            result = self._parse_json_response(response.text)
            result["analysis_method"] = "few_shot_learning"
            result["timestamp"] = datetime.now().isoformat()

            return result

        except Exception as e:
            logger.error(f"Gemini investment analysis failed: {e}")
            return self._fallback_investment_analysis(user_profile, goals)

    async def analyze_with_self_consistency(
        self,
        query: str,
        context: Dict[str, Any],
        passes: int = 3
    ) -> Dict[str, Any]:
        """
        Perform self-consistency check with multiple inference passes
        """
        results = []

        for i in range(passes):
            # Vary temperature slightly for each pass
            temp_config = types.GenerateContentConfig(
                temperature=0.7 + (i * 0.1),
                top_p=0.95,
                max_output_tokens=2048,
                response_mime_type="text/plain"
            )

            prompt = f"""
            Analyze this financial query and provide detailed recommendations.

            Query: {query}

            Context:
            {json.dumps(context, indent=2)}

            Provide a comprehensive analysis considering:
            - Indian financial regulations and tax laws
            - Current market conditions
            - User's financial situation
            - Risk-return tradeoffs

            Format as JSON with:
            {{
                "recommendation": "main recommendation",
                "confidence_score": <0.0-1.0>,
                "key_points": ["point1", "point2"],
                "risks": ["risk1", "risk2"],
                "action_items": ["action1", "action2"]
            }}
            """

            try:
                response = await self.client.aio.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config=temp_config
                )

                result = self._parse_json_response(response.text)
                results.append(result)

            except Exception as e:
                logger.warning(f"Pass {i+1} failed: {e}")
                continue

        # Aggregate results using majority voting and averaging
        if not results:
            return {"error": "All consistency passes failed"}

        aggregated = self._aggregate_consistency_results(results)
        aggregated["analysis_method"] = "self_consistency"
        aggregated["passes"] = len(results)
        aggregated["consensus_level"] = self._calculate_consensus(results)

        return aggregated

    async def explain_financial_concept(
        self,
        concept: str,
        user_level: str = "beginner"
    ) -> Dict[str, Any]:
        """
        Explain financial concepts with step-by-step breakdown
        """
        prompt = f"""
        Explain the financial concept "{concept}" for a {user_level} Indian investor.

        Use Chain-of-Thought to break down the explanation:

        Step 1: Simple Definition
        - What is it in simple terms?
        - Real-world analogy

        Step 2: How It Works
        - Break down the mechanism
        - Step-by-step process

        Step 3: Indian Context
        - How it applies in India
        - Relevant regulations/laws
        - Tax implications

        Step 4: Practical Examples
        - Real scenarios with numbers
        - Common use cases in India

        Step 5: Benefits & Risks
        - Advantages
        - Potential pitfalls
        - Who should consider it

        Step 6: Action Steps
        - How to get started
        - Resources to learn more

        Provide response as JSON:
        {{
            "concept": "{concept}",
            "simple_definition": "...",
            "analogy": "...",
            "how_it_works": ["step1", "step2"],
            "indian_context": {{
                "regulations": ["..."],
                "tax_implications": "..."
            }},
            "examples": [
                {{"scenario": "...", "calculation": "..."}}
            ],
            "benefits": ["..."],
            "risks": ["..."],
            "suitable_for": ["..."],
            "action_steps": ["..."],
            "complexity_level": "BASIC/INTERMEDIATE/ADVANCED"
        }}
        """

        try:
            response = await self.client.aio.models.generate_content(
                model=self.model,
                contents=prompt,
                config=self.configs["general"]
            )

            result = self._parse_json_response(response.text)
            result["explanation_type"] = "chain_of_thought"

            return result

        except Exception as e:
            logger.error(f"Concept explanation failed: {e}")
            return {
                "concept": concept,
                "error": "Failed to generate explanation",
                "fallback": f"Please search for '{concept}' in our knowledge base"
            }

    def _parse_json_response(self, text: str) -> Dict[str, Any]:
        """
        Parse JSON from Gemini response, handling various formats
        """
        try:
            # Try to find JSON in the response
            import re
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())

            # If no JSON found, try to parse the entire response
            return json.loads(text)

        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON from Gemini response")
            # Return a structured fallback
            return {
                "raw_response": text,
                "parse_error": True,
                "timestamp": datetime.now().isoformat()
            }

    def _aggregate_consistency_results(self, results: List[Dict]) -> Dict[str, Any]:
        """
        Aggregate multiple analysis results for consistency
        """
        if not results:
            return {}

        # Extract common fields
        aggregated = {
            "recommendation": self._most_common([r.get("recommendation", "") for r in results]),
            "confidence_score": statistics.mean([r.get("confidence_score", 0.5) for r in results]),
            "key_points": self._merge_lists([r.get("key_points", []) for r in results]),
            "risks": self._merge_lists([r.get("risks", []) for r in results]),
            "action_items": self._merge_lists([r.get("action_items", []) for r in results])
        }

        return aggregated

    def _calculate_consensus(self, results: List[Dict]) -> float:
        """
        Calculate consensus level among multiple results
        """
        if len(results) <= 1:
            return 1.0

        # Compare recommendations
        recommendations = [r.get("recommendation", "") for r in results]
        unique_recommendations = len(set(recommendations))

        # Lower consensus if recommendations differ
        consensus = 1.0 - (unique_recommendations - 1) * 0.2

        return max(0.0, min(1.0, consensus))

    def _most_common(self, items: List[str]) -> str:
        """
        Find most common item in list
        """
        if not items:
            return ""
        from collections import Counter
        return Counter(items).most_common(1)[0][0]

    def _merge_lists(self, lists: List[List]) -> List:
        """
        Merge multiple lists and remove duplicates while preserving order
        """
        seen = set()
        merged = []
        for lst in lists:
            for item in lst:
                if item not in seen:
                    seen.add(item)
                    merged.append(item)
        return merged[:5]  # Limit to top 5

    def _fallback_fraud_analysis(self, transaction: Dict) -> Dict[str, Any]:
        """
        Fallback fraud analysis when Gemini fails
        """
        # Simple rule-based analysis
        amount = abs(transaction.get("amount", 0))
        risk_score = min(100, amount / 1000)  # Simple linear scaling

        return {
            "risk_score": risk_score,
            "risk_level": "HIGH" if risk_score > 70 else "MEDIUM" if risk_score > 40 else "LOW",
            "reasoning_steps": [
                {"step": "Fallback Analysis", "finding": "Using rule-based detection", "risk_contribution": risk_score}
            ],
            "risk_factors": ["Amount-based analysis only"],
            "recommended_action": "VERIFY" if risk_score > 50 else "ALLOW",
            "confidence": 0.3,
            "explanation": "Basic analysis performed due to AI service unavailability",
            "fallback": True
        }

    def _fallback_investment_analysis(self, user_profile: Dict, goals: List) -> Dict[str, Any]:
        """
        Fallback investment analysis when Gemini fails
        """
        age = user_profile.get("age", 30)
        equity_percent = min(80, 100 - age)

        return {
            "asset_allocation": {
                "equity": equity_percent,
                "debt": 100 - equity_percent - 10,
                "gold": 10,
                "real_estate": 0,
                "cash": 0
            },
            "specific_recommendations": [
                {
                    "instrument": "Nifty 50 Index Fund",
                    "type": "MUTUAL_FUND",
                    "allocation_percent": equity_percent * 0.6,
                    "expected_return": 12,
                    "risk_level": "MEDIUM",
                    "reason": "Diversified large-cap exposure"
                }
            ],
            "fallback": True,
            "message": "Basic recommendations based on age-based allocation"
        }


# Singleton instance
_gemini_analyzer = None

def get_gemini_analyzer() -> GeminiAdvancedAnalyzer:
    """
    Get singleton instance of Gemini analyzer
    """
    global _gemini_analyzer
    if _gemini_analyzer is None:
        _gemini_analyzer = GeminiAdvancedAnalyzer()
    return _gemini_analyzer