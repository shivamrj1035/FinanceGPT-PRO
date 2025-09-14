"""
Consistency Checker for AI Model Outputs
Validates and ensures consistency across multiple AI responses
"""

import json
import statistics
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import hashlib
from collections import Counter
import logging

logger = logging.getLogger(__name__)


class ConsistencyChecker:
    """
    Validates consistency across multiple AI model outputs
    """

    def __init__(self):
        self.confidence_threshold = 0.7
        self.consensus_threshold = 0.6

    def check_numerical_consistency(
        self,
        values: List[float],
        tolerance: float = 0.1
    ) -> Dict[str, Any]:
        """
        Check consistency of numerical predictions
        """
        if not values:
            return {"consistent": False, "error": "No values provided"}

        mean_val = statistics.mean(values)
        std_dev = statistics.stdev(values) if len(values) > 1 else 0
        cv = std_dev / mean_val if mean_val != 0 else float('inf')

        # Check if coefficient of variation is within tolerance
        is_consistent = cv <= tolerance

        return {
            "consistent": is_consistent,
            "mean": round(mean_val, 2),
            "std_dev": round(std_dev, 2),
            "coefficient_of_variation": round(cv, 3),
            "min": min(values),
            "max": max(values),
            "range": max(values) - min(values),
            "confidence": 1 - cv if cv < 1 else 0
        }

    def check_categorical_consistency(
        self,
        categories: List[str]
    ) -> Dict[str, Any]:
        """
        Check consistency of categorical predictions
        """
        if not categories:
            return {"consistent": False, "error": "No categories provided"}

        counter = Counter(categories)
        total = len(categories)
        most_common = counter.most_common(1)[0]

        consensus_ratio = most_common[1] / total
        is_consistent = consensus_ratio >= self.consensus_threshold

        return {
            "consistent": is_consistent,
            "consensus": most_common[0],
            "consensus_ratio": round(consensus_ratio, 2),
            "distribution": dict(counter),
            "entropy": self._calculate_entropy(counter, total),
            "confidence": consensus_ratio
        }

    def check_risk_score_consistency(
        self,
        risk_scores: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Check consistency of risk scoring across models
        """
        if not risk_scores:
            return {"consistent": False, "error": "No risk scores provided"}

        # Extract numerical scores
        scores = [s.get("risk_score", 0) for s in risk_scores]
        levels = [s.get("risk_level", "UNKNOWN") for s in risk_scores]
        actions = [s.get("recommended_action", "UNKNOWN") for s in risk_scores]

        # Check numerical consistency
        score_consistency = self.check_numerical_consistency(scores, tolerance=0.15)

        # Check categorical consistency
        level_consistency = self.check_categorical_consistency(levels)
        action_consistency = self.check_categorical_consistency(actions)

        # Overall consistency
        overall_consistent = (
            score_consistency["consistent"] and
            level_consistency["consistent"] and
            action_consistency["consistent"]
        )

        # Aggregate risk factors
        all_factors = []
        for score in risk_scores:
            all_factors.extend(score.get("risk_factors", []))

        factor_frequency = Counter(all_factors)

        return {
            "consistent": overall_consistent,
            "score_consistency": score_consistency,
            "level_consistency": level_consistency,
            "action_consistency": action_consistency,
            "aggregated_score": score_consistency["mean"],
            "consensus_level": level_consistency.get("consensus", "UNKNOWN"),
            "consensus_action": action_consistency.get("consensus", "UNKNOWN"),
            "common_risk_factors": dict(factor_frequency.most_common(5)),
            "confidence": min(
                score_consistency.get("confidence", 0),
                level_consistency.get("confidence", 0),
                action_consistency.get("confidence", 0)
            )
        }

    def check_investment_consistency(
        self,
        recommendations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Check consistency of investment recommendations
        """
        if not recommendations:
            return {"consistent": False, "error": "No recommendations provided"}

        # Extract allocation percentages
        equity_allocations = []
        debt_allocations = []
        gold_allocations = []

        for rec in recommendations:
            allocation = rec.get("asset_allocation", {})
            equity_allocations.append(allocation.get("equity", 0))
            debt_allocations.append(allocation.get("debt", 0))
            gold_allocations.append(allocation.get("gold", 0))

        # Check consistency of each asset class
        equity_consistency = self.check_numerical_consistency(equity_allocations, tolerance=0.1)
        debt_consistency = self.check_numerical_consistency(debt_allocations, tolerance=0.1)
        gold_consistency = self.check_numerical_consistency(gold_allocations, tolerance=0.15)

        # Extract specific fund recommendations
        all_funds = []
        for rec in recommendations:
            funds = rec.get("specific_recommendations", [])
            all_funds.extend([f.get("instrument", "") for f in funds])

        fund_frequency = Counter(all_funds)

        # Overall consistency
        overall_consistent = (
            equity_consistency["consistent"] and
            debt_consistency["consistent"] and
            gold_consistency["consistent"]
        )

        return {
            "consistent": overall_consistent,
            "allocation_consistency": {
                "equity": equity_consistency,
                "debt": debt_consistency,
                "gold": gold_consistency
            },
            "consensus_allocation": {
                "equity": round(equity_consistency["mean"], 1),
                "debt": round(debt_consistency["mean"], 1),
                "gold": round(gold_consistency["mean"], 1)
            },
            "popular_funds": dict(fund_frequency.most_common(5)),
            "confidence": min(
                equity_consistency.get("confidence", 0),
                debt_consistency.get("confidence", 0),
                gold_consistency.get("confidence", 0)
            )
        }

    def validate_json_structure(
        self,
        responses: List[str],
        expected_schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate JSON structure consistency across responses
        """
        valid_responses = []
        invalid_responses = []

        for i, response in enumerate(responses):
            try:
                parsed = json.loads(response) if isinstance(response, str) else response
                is_valid = self._validate_schema(parsed, expected_schema)

                if is_valid:
                    valid_responses.append(parsed)
                else:
                    invalid_responses.append({"index": i, "reason": "Schema mismatch"})

            except json.JSONDecodeError as e:
                invalid_responses.append({"index": i, "reason": str(e)})

        validity_ratio = len(valid_responses) / len(responses) if responses else 0

        return {
            "valid": validity_ratio >= 0.8,
            "validity_ratio": validity_ratio,
            "valid_count": len(valid_responses),
            "invalid_count": len(invalid_responses),
            "invalid_responses": invalid_responses,
            "valid_responses": valid_responses
        }

    def aggregate_responses(
        self,
        responses: List[Dict[str, Any]],
        strategy: str = "weighted_average"
    ) -> Dict[str, Any]:
        """
        Aggregate multiple responses into a single consensus response
        """
        if not responses:
            return {"error": "No responses to aggregate"}

        if strategy == "weighted_average":
            return self._weighted_average_aggregation(responses)
        elif strategy == "majority_vote":
            return self._majority_vote_aggregation(responses)
        elif strategy == "confidence_weighted":
            return self._confidence_weighted_aggregation(responses)
        else:
            return self._simple_average_aggregation(responses)

    def detect_anomalies(
        self,
        responses: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Detect anomalous responses that deviate significantly
        """
        if len(responses) < 3:
            return {"anomalies_detected": False, "reason": "Insufficient data"}

        anomalies = []

        # Check for numerical anomalies
        if all("risk_score" in r for r in responses):
            scores = [r["risk_score"] for r in responses]
            mean_score = statistics.mean(scores)
            std_score = statistics.stdev(scores)

            for i, score in enumerate(scores):
                z_score = abs((score - mean_score) / std_score) if std_score > 0 else 0
                if z_score > 2:  # More than 2 standard deviations
                    anomalies.append({
                        "response_index": i,
                        "type": "numerical",
                        "value": score,
                        "z_score": round(z_score, 2)
                    })

        # Check for categorical anomalies
        if all("risk_level" in r for r in responses):
            levels = [r["risk_level"] for r in responses]
            level_counter = Counter(levels)

            for i, level in enumerate(levels):
                if level_counter[level] == 1 and len(level_counter) > 1:
                    anomalies.append({
                        "response_index": i,
                        "type": "categorical",
                        "value": level,
                        "reason": "Unique category"
                    })

        return {
            "anomalies_detected": len(anomalies) > 0,
            "anomaly_count": len(anomalies),
            "anomalies": anomalies,
            "clean_response_indices": [
                i for i in range(len(responses))
                if i not in [a["response_index"] for a in anomalies]
            ]
        }

    def calculate_consensus_score(
        self,
        responses: List[Dict[str, Any]]
    ) -> float:
        """
        Calculate overall consensus score across responses
        """
        if len(responses) < 2:
            return 1.0  # Single response has perfect consensus with itself

        scores = []

        # Check numerical fields
        numerical_fields = ["risk_score", "confidence", "expected_return"]
        for field in numerical_fields:
            if all(field in r for r in responses):
                values = [r[field] for r in responses]
                consistency = self.check_numerical_consistency(values)
                scores.append(consistency.get("confidence", 0))

        # Check categorical fields
        categorical_fields = ["risk_level", "recommended_action", "category"]
        for field in categorical_fields:
            if all(field in r for r in responses):
                values = [r[field] for r in responses]
                consistency = self.check_categorical_consistency(values)
                scores.append(consistency.get("confidence", 0))

        return statistics.mean(scores) if scores else 0.0

    def _calculate_entropy(self, counter: Counter, total: int) -> float:
        """
        Calculate Shannon entropy for categorical distribution
        """
        import math
        entropy = 0
        for count in counter.values():
            if count > 0:
                p = count / total
                entropy -= p * math.log2(p)
        return round(entropy, 3)

    def _validate_schema(self, data: Dict, schema: Dict) -> bool:
        """
        Simple schema validation
        """
        for key, expected_type in schema.items():
            if key not in data:
                return False
            if not isinstance(data[key], expected_type):
                return False
        return True

    def _weighted_average_aggregation(self, responses: List[Dict]) -> Dict:
        """
        Aggregate using weighted average based on confidence
        """
        if not responses:
            return {}

        # Extract weights (confidence scores)
        weights = [r.get("confidence", 0.5) for r in responses]
        total_weight = sum(weights)

        if total_weight == 0:
            return self._simple_average_aggregation(responses)

        aggregated = {}

        # Aggregate numerical fields
        numerical_fields = ["risk_score", "expected_return", "confidence_score"]
        for field in numerical_fields:
            if all(field in r for r in responses):
                weighted_sum = sum(r[field] * w for r, w in zip(responses, weights))
                aggregated[field] = round(weighted_sum / total_weight, 2)

        # For categorical, use highest confidence response
        categorical_fields = ["risk_level", "recommended_action"]
        for field in categorical_fields:
            if all(field in r for r in responses):
                max_conf_idx = weights.index(max(weights))
                aggregated[field] = responses[max_conf_idx][field]

        return aggregated

    def _majority_vote_aggregation(self, responses: List[Dict]) -> Dict:
        """
        Aggregate using majority voting for categorical fields
        """
        if not responses:
            return {}

        aggregated = {}

        # All fields that appear in all responses
        common_fields = set.intersection(*[set(r.keys()) for r in responses])

        for field in common_fields:
            values = [r[field] for r in responses]

            if all(isinstance(v, (int, float)) for v in values):
                # Numerical field - use median
                aggregated[field] = statistics.median(values)
            elif all(isinstance(v, str) for v in values):
                # Categorical field - use mode
                counter = Counter(values)
                aggregated[field] = counter.most_common(1)[0][0]
            elif all(isinstance(v, list) for v in values):
                # List field - merge unique items
                merged = []
                for lst in values:
                    merged.extend(lst)
                aggregated[field] = list(set(merged))[:5]  # Top 5 unique

        return aggregated

    def _confidence_weighted_aggregation(self, responses: List[Dict]) -> Dict:
        """
        Aggregate based on confidence scores with outlier removal
        """
        # First detect and remove anomalies
        anomaly_result = self.detect_anomalies(responses)
        clean_indices = anomaly_result.get("clean_response_indices", range(len(responses)))
        clean_responses = [responses[i] for i in clean_indices]

        if not clean_responses:
            return self._simple_average_aggregation(responses)

        return self._weighted_average_aggregation(clean_responses)

    def _simple_average_aggregation(self, responses: List[Dict]) -> Dict:
        """
        Simple average aggregation as fallback
        """
        if not responses:
            return {}

        aggregated = {}
        common_fields = set.intersection(*[set(r.keys()) for r in responses])

        for field in common_fields:
            values = [r[field] for r in responses]

            if all(isinstance(v, (int, float)) for v in values):
                aggregated[field] = statistics.mean(values)
            else:
                # For non-numerical, take first value
                aggregated[field] = values[0]

        return aggregated


# Singleton instance
_consistency_checker = None

def get_consistency_checker() -> ConsistencyChecker:
    """
    Get singleton instance of consistency checker
    """
    global _consistency_checker
    if _consistency_checker is None:
        _consistency_checker = ConsistencyChecker()
    return _consistency_checker