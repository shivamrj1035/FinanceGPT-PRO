"""
AI Models Package for FinanceGPT Pro
Combines basic financial models with advanced Gemini AI integration
"""

# Import basic financial models
from .financial_models import (
    FraudDetectionModel,
    SpendingPatternAnalyzer,
    InvestmentRecommendationEngine,
    CreditScorePredictor,
    fraud_detector,
    spending_analyzer,
    investment_engine,
    credit_predictor
)

# Import advanced Gemini integration
from .advanced_gemini import (
    GeminiAdvancedAnalyzer,
    get_gemini_analyzer
)

# Import prompting strategies
from .prompting_strategies import (
    PromptingStrategies,
    PromptTemplates,
    PromptEnhancer
)

# Import consistency checker
from .consistency_checker import (
    ConsistencyChecker,
    get_consistency_checker
)

# Version info
__version__ = "2.0.0"
__author__ = "FinanceGPT Pro Team"

# Export all public APIs
__all__ = [
    # Basic Models
    'FraudDetectionModel',
    'SpendingPatternAnalyzer',
    'InvestmentRecommendationEngine',
    'CreditScorePredictor',
    'fraud_detector',
    'spending_analyzer',
    'investment_engine',
    'credit_predictor',

    # Advanced Gemini
    'GeminiAdvancedAnalyzer',
    'get_gemini_analyzer',

    # Prompting
    'PromptingStrategies',
    'PromptTemplates',
    'PromptEnhancer',

    # Consistency
    'ConsistencyChecker',
    'get_consistency_checker'
]