"""
Advanced Prompting Strategies for Financial AI
Implements various prompting techniques for enhanced AI responses
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime


class PromptingStrategies:
    """
    Collection of advanced prompting strategies for financial analysis
    """

    @staticmethod
    def chain_of_thought_prompt(
        task: str,
        context: Dict[str, Any],
        steps: Optional[List[str]] = None
    ) -> str:
        """
        Generate Chain-of-Thought prompt for step-by-step reasoning
        """
        if not steps:
            steps = [
                "Understanding the Problem",
                "Gathering Relevant Information",
                "Analyzing Key Factors",
                "Evaluating Options",
                "Making Recommendations",
                "Providing Justification"
            ]

        prompt = f"""
        Task: {task}

        Context:
        {json.dumps(context, indent=2)}

        Please solve this step-by-step using Chain-of-Thought reasoning:

        """

        for i, step in enumerate(steps, 1):
            prompt += f"""
        Step {i}: {step}
        - Analyze this aspect thoroughly
        - Show your reasoning process
        - Connect to previous steps
        """

        prompt += """

        Final Answer:
        Based on the above analysis, provide your comprehensive response.
        """

        return prompt

    @staticmethod
    def few_shot_prompt(
        task: str,
        examples: List[Dict[str, Any]],
        query: Dict[str, Any]
    ) -> str:
        """
        Generate Few-Shot learning prompt with examples
        """
        prompt = f"""
        Learn from these examples to solve similar problems:

        """

        for i, example in enumerate(examples, 1):
            prompt += f"""
        Example {i}:
        Input: {json.dumps(example.get('input', {}), indent=2)}
        Analysis: {example.get('analysis', '')}
        Output: {json.dumps(example.get('output', {}), indent=2)}
        ---
        """

        prompt += f"""

        Now solve this similar problem:
        Input: {json.dumps(query, indent=2)}

        Apply the same reasoning pattern from the examples above.
        """

        return prompt

    @staticmethod
    def self_reflection_prompt(
        initial_response: str,
        task: str
    ) -> str:
        """
        Generate self-reflection prompt for improving initial response
        """
        return f"""
        Initial Response: {initial_response}

        Task: {task}

        Please critically evaluate the initial response:

        1. Accuracy Check:
           - Are all facts and figures correct?
           - Are there any logical inconsistencies?

        2. Completeness:
           - Did we address all aspects of the task?
           - What important points might be missing?

        3. Clarity:
           - Is the explanation clear and understandable?
           - Can we simplify complex concepts?

        4. Improvements:
           - What specific improvements can be made?
           - Are there better alternatives?

        Provide an improved response incorporating these reflections.
        """

    @staticmethod
    def role_based_prompt(
        role: str,
        task: str,
        constraints: Optional[List[str]] = None
    ) -> str:
        """
        Generate role-based prompt for specialized expertise
        """
        role_descriptions = {
            "fraud_analyst": "You are a senior fraud detection analyst with 15 years of experience in Indian banking sector",
            "investment_advisor": "You are a SEBI-registered investment advisor specializing in wealth management for HNI clients",
            "tax_consultant": "You are a chartered accountant with expertise in Indian tax laws and optimization strategies",
            "credit_analyst": "You are a senior credit risk analyst working with CIBIL and other credit bureaus",
            "financial_planner": "You are a certified financial planner helping middle-class Indian families achieve their goals"
        }

        prompt = f"""
        Role: {role_descriptions.get(role, f"You are an expert {role}")}

        Task: {task}
        """

        if constraints:
            prompt += "\n\nConstraints:\n"
            for constraint in constraints:
                prompt += f"- {constraint}\n"

        prompt += """

        Provide your expert analysis considering:
        - Your professional experience
        - Industry best practices
        - Regulatory compliance
        - Risk considerations
        - Practical implementation
        """

        return prompt

    @staticmethod
    def tree_of_thoughts_prompt(
        problem: str,
        branches: int = 3
    ) -> str:
        """
        Generate Tree-of-Thoughts prompt for exploring multiple solution paths
        """
        return f"""
        Problem: {problem}

        Explore {branches} different approaches to solve this problem:

        Approach 1:
        - Initial thought:
        - Pros:
        - Cons:
        - Viability score (1-10):

        Approach 2:
        - Initial thought:
        - Pros:
        - Cons:
        - Viability score (1-10):

        Approach 3:
        - Initial thought:
        - Pros:
        - Cons:
        - Viability score (1-10):

        Evaluation:
        - Compare all approaches
        - Select the best approach
        - Justify your selection

        Final Solution:
        Implement the selected approach with detailed steps.
        """

    @staticmethod
    def zero_shot_cot_prompt(task: str) -> str:
        """
        Generate Zero-Shot Chain-of-Thought prompt
        """
        return f"""
        {task}

        Let's think step by step to solve this problem:

        First, I'll identify the key components...
        Next, I'll analyze the relationships...
        Then, I'll consider the implications...
        Finally, I'll formulate my recommendation...

        Please show all your reasoning.
        """

    @staticmethod
    def constrained_generation_prompt(
        task: str,
        format_spec: Dict[str, Any],
        constraints: List[str]
    ) -> str:
        """
        Generate prompt with specific output constraints
        """
        return f"""
        Task: {task}

        Output Format Requirements:
        {json.dumps(format_spec, indent=2)}

        Constraints:
        {chr(10).join(f"- {c}" for c in constraints)}

        Ensure your response:
        1. Strictly follows the specified format
        2. Meets all constraints
        3. Is valid JSON
        4. Contains all required fields
        5. Uses appropriate data types
        """

    @staticmethod
    def socratic_prompt(
        topic: str,
        initial_question: str
    ) -> str:
        """
        Generate Socratic questioning prompt for deep analysis
        """
        return f"""
        Topic: {topic}
        Initial Question: {initial_question}

        Let's explore this through Socratic questioning:

        1. Clarification:
           - What exactly do we mean by this?
           - Can you give me an example?

        2. Assumptions:
           - What assumptions are we making?
           - What if the opposite were true?

        3. Evidence:
           - What evidence supports this?
           - How can we verify this?

        4. Perspectives:
           - What would others say about this?
           - What are the alternatives?

        5. Implications:
           - What follows from this?
           - How does this connect to what we know?

        6. Questions about the question:
           - Why is this question important?
           - What does this question assume?

        Synthesize your insights into a comprehensive answer.
        """

    @staticmethod
    def adversarial_prompt(
        claim: str,
        context: Dict[str, Any]
    ) -> str:
        """
        Generate adversarial prompt to test robustness
        """
        return f"""
        Claim: {claim}
        Context: {json.dumps(context, indent=2)}

        Challenge this claim by:

        1. Playing Devil's Advocate:
           - What are the strongest counter-arguments?
           - What evidence contradicts this claim?

        2. Identifying Weaknesses:
           - What are the logical flaws?
           - What assumptions might be wrong?

        3. Alternative Explanations:
           - What other explanations exist?
           - Which is most plausible?

        4. Stress Testing:
           - Under what conditions would this fail?
           - What are the edge cases?

        Final Assessment:
        After critical analysis, is the original claim valid? Why or why not?
        """

    @staticmethod
    def multi_persona_prompt(
        task: str,
        personas: List[str]
    ) -> str:
        """
        Generate multi-persona prompt for diverse perspectives
        """
        prompt = f"""
        Task: {task}

        Analyze this from multiple expert perspectives:

        """

        persona_descriptions = {
            "conservative_investor": "Risk-averse investor focusing on capital preservation",
            "aggressive_trader": "High-risk trader seeking maximum returns",
            "financial_regulator": "SEBI/RBI official ensuring compliance",
            "tax_optimizer": "CA focused on legal tax minimization",
            "retail_customer": "Average middle-class Indian saver"
        }

        for persona in personas:
            desc = persona_descriptions.get(persona, persona)
            prompt += f"""
        As a {desc}:
        - Key concerns:
        - Recommendations:
        - Warnings:
        ---
        """

        prompt += """

        Synthesis:
        Combine all perspectives into a balanced recommendation.
        """

        return prompt


class PromptTemplates:
    """
    Pre-built prompt templates for common financial tasks
    """

    FRAUD_DETECTION = """
    Analyze this transaction for fraud risk:

    Transaction: {transaction}
    User History Summary: {history_summary}

    Consider:
    1. Amount anomalies
    2. Merchant reputation
    3. Timing patterns
    4. Geographic factors
    5. User behavior deviation

    Provide risk score (0-100) with detailed reasoning.
    """

    INVESTMENT_ADVICE = """
    Generate personalized investment advice:

    Profile: {user_profile}
    Goals: {financial_goals}
    Market Conditions: {market_context}

    Recommend:
    1. Asset allocation
    2. Specific instruments
    3. Investment timeline
    4. Risk management
    5. Tax optimization

    Consider Indian market context and regulations.
    """

    TAX_PLANNING = """
    Optimize tax strategy for:

    Income Details: {income_structure}
    Current Investments: {investments}
    Deductions Claimed: {current_deductions}

    Suggest:
    1. Section 80C investments
    2. Section 80D optimization
    3. HRA/LTA claims
    4. Capital gains planning
    5. Advance tax management

    Ensure compliance with latest Indian tax laws.
    """

    CREDIT_IMPROVEMENT = """
    Analyze and improve credit score:

    Current Score: {credit_score}
    Credit History: {credit_history}
    Current Debts: {debt_details}

    Provide:
    1. Score improvement potential
    2. Specific action items
    3. Timeline for improvement
    4. Priority order of actions
    5. Expected score after improvements

    Follow CIBIL/Experian scoring models.
    """

    BUDGET_OPTIMIZATION = """
    Optimize monthly budget:

    Income: {monthly_income}
    Fixed Expenses: {fixed_expenses}
    Variable Expenses: {variable_expenses}
    Savings Goals: {savings_targets}

    Recommend:
    1. Expense reduction opportunities
    2. Savings increase strategies
    3. Emergency fund building
    4. Debt payoff plan
    5. Investment allocation

    Use 50-30-20 rule adapted for Indian context.
    """


class PromptEnhancer:
    """
    Enhance prompts with additional context and techniques
    """

    @staticmethod
    def add_indian_context(prompt: str) -> str:
        """
        Add Indian financial context to prompts
        """
        indian_context = """

        Indian Financial Context:
        - Consider GST implications
        - Account for TDS requirements
        - Include UPI payment patterns
        - Consider festival spending (Diwali, Holi)
        - Account for monsoon/seasonal impacts
        - Include EPF/PPF/NPS considerations
        - Consider joint family financial dynamics
        """

        return prompt + indian_context

    @staticmethod
    def add_confidence_calibration(prompt: str) -> str:
        """
        Add confidence calibration to prompts
        """
        calibration = """

        Confidence Calibration:
        - Provide confidence score (0-100%) for each recommendation
        - Explicitly state uncertainties
        - Identify assumptions made
        - Highlight areas needing more data
        - Suggest validation methods
        """

        return prompt + calibration

    @staticmethod
    def add_ethical_considerations(prompt: str) -> str:
        """
        Add ethical guidelines to prompts
        """
        ethics = """

        Ethical Considerations:
        - Ensure recommendations are in client's best interest
        - Avoid conflicts of interest
        - Maintain transparency about risks
        - Respect privacy and confidentiality
        - Comply with regulatory requirements
        - Consider social and environmental impact
        """

        return prompt + ethics

    @staticmethod
    def add_explanation_requirements(prompt: str) -> str:
        """
        Add explanation requirements for transparency
        """
        explanation = """

        Explanation Requirements:
        - Explain reasoning in simple terms
        - Provide step-by-step justification
        - Use examples and analogies
        - Highlight key decision factors
        - Explain technical terms
        - Provide references where applicable
        """

        return prompt + explanation


# Export utilities
__all__ = [
    'PromptingStrategies',
    'PromptTemplates',
    'PromptEnhancer'
]