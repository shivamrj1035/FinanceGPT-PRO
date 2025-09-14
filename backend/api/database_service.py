"""
Database Service for FinanceGPT Pro
Handles storage and retrieval of AI predictions and insights
"""

import sqlite3
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import os

logger = logging.getLogger(__name__)

class DatabaseService:
    """
    Service for storing AI predictions and insights in SQLite database
    """

    def __init__(self, db_path: str = "financebot.db"):
        self.db_path = db_path
        self.init_ai_tables()

    def init_ai_tables(self):
        """Initialize AI-specific tables if they don't exist"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # AI Predictions table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS ai_predictions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL,
                        prediction_type TEXT NOT NULL,
                        input_data TEXT,
                        prediction_result TEXT,
                        confidence_score REAL,
                        model_version TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # AI Insights table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS ai_insights (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL,
                        insight_type TEXT NOT NULL,
                        context_data TEXT,
                        insights TEXT,
                        recommendations TEXT,
                        confidence_score REAL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Fraud Detection History
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS fraud_detections (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL,
                        transaction_id TEXT,
                        transaction_data TEXT,
                        risk_score REAL,
                        risk_level TEXT,
                        risk_factors TEXT,
                        recommended_action TEXT,
                        ai_analysis TEXT,
                        model_version TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # User Preferences for AI
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS user_ai_preferences (
                        user_id TEXT PRIMARY KEY,
                        ai_enabled BOOLEAN DEFAULT 1,
                        notification_threshold REAL DEFAULT 0.7,
                        preferred_analysis_type TEXT DEFAULT 'balanced',
                        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                conn.commit()
                logger.info("AI database tables initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize AI tables: {e}")

    async def store_fraud_prediction(
        self,
        user_id: str,
        transaction_data: Dict[str, Any],
        prediction_result: Dict[str, Any]
    ) -> bool:
        """Store fraud detection prediction"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    INSERT INTO fraud_detections (
                        user_id, transaction_id, transaction_data, risk_score,
                        risk_level, risk_factors, recommended_action,
                        ai_analysis, model_version
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_id,
                    transaction_data.get("id", "unknown"),
                    json.dumps(transaction_data),
                    prediction_result.get("risk_score", 0),
                    prediction_result.get("risk_level", "UNKNOWN"),
                    json.dumps(prediction_result.get("risk_factors", [])),
                    prediction_result.get("recommended_action", "MONITOR"),
                    json.dumps(prediction_result.get("ai_analysis", {})),
                    prediction_result.get("model_version", "1.0")
                ))

                conn.commit()
                return True

        except Exception as e:
            logger.error(f"Failed to store fraud prediction: {e}")
            return False

    async def store_ai_insight(
        self,
        user_id: str,
        insight_type: str,
        context_data: Dict[str, Any],
        insights: Dict[str, Any]
    ) -> bool:
        """Store AI-generated insights"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    INSERT INTO ai_insights (
                        user_id, insight_type, context_data, insights,
                        recommendations, confidence_score
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    user_id,
                    insight_type,
                    json.dumps(context_data),
                    json.dumps(insights),
                    json.dumps(insights.get("recommendations", [])),
                    insights.get("confidence", 0)
                ))

                conn.commit()
                return True

        except Exception as e:
            logger.error(f"Failed to store AI insight: {e}")
            return False

    async def get_fraud_history(
        self,
        user_id: str,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """Get fraud detection history for user"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)

            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT * FROM fraud_detections
                    WHERE user_id = ? AND created_at >= ?
                    ORDER BY created_at DESC
                    LIMIT 100
                """, (user_id, cutoff_date.isoformat()))

                rows = cursor.fetchall()
                return [
                    {
                        "id": row["id"],
                        "transaction_id": row["transaction_id"],
                        "risk_score": row["risk_score"],
                        "risk_level": row["risk_level"],
                        "risk_factors": json.loads(row["risk_factors"]) if row["risk_factors"] else [],
                        "recommended_action": row["recommended_action"],
                        "ai_analysis": json.loads(row["ai_analysis"]) if row["ai_analysis"] else {},
                        "created_at": row["created_at"]
                    }
                    for row in rows
                ]

        except Exception as e:
            logger.error(f"Failed to get fraud history: {e}")
            return []

    async def get_ai_insights_history(
        self,
        user_id: str,
        insight_type: Optional[str] = None,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """Get AI insights history for user"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)

            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                if insight_type:
                    cursor.execute("""
                        SELECT * FROM ai_insights
                        WHERE user_id = ? AND insight_type = ? AND created_at >= ?
                        ORDER BY created_at DESC
                        LIMIT 50
                    """, (user_id, insight_type, cutoff_date.isoformat()))
                else:
                    cursor.execute("""
                        SELECT * FROM ai_insights
                        WHERE user_id = ? AND created_at >= ?
                        ORDER BY created_at DESC
                        LIMIT 50
                    """, (user_id, cutoff_date.isoformat()))

                rows = cursor.fetchall()
                return [
                    {
                        "id": row["id"],
                        "insight_type": row["insight_type"],
                        "insights": json.loads(row["insights"]) if row["insights"] else {},
                        "recommendations": json.loads(row["recommendations"]) if row["recommendations"] else [],
                        "confidence_score": row["confidence_score"],
                        "created_at": row["created_at"]
                    }
                    for row in rows
                ]

        except Exception as e:
            logger.error(f"Failed to get AI insights history: {e}")
            return []

    async def get_user_ai_stats(self, user_id: str) -> Dict[str, Any]:
        """Get AI usage statistics for user"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Fraud detection stats
                cursor.execute("""
                    SELECT
                        COUNT(*) as total_checks,
                        AVG(risk_score) as avg_risk_score,
                        SUM(CASE WHEN risk_level = 'HIGH' THEN 1 ELSE 0 END) as high_risk_count,
                        SUM(CASE WHEN risk_level = 'CRITICAL' THEN 1 ELSE 0 END) as critical_risk_count
                    FROM fraud_detections
                    WHERE user_id = ? AND created_at >= date('now', '-30 days')
                """, (user_id,))

                fraud_stats = cursor.fetchone()

                # AI insights stats
                cursor.execute("""
                    SELECT
                        insight_type,
                        COUNT(*) as count,
                        AVG(confidence_score) as avg_confidence
                    FROM ai_insights
                    WHERE user_id = ? AND created_at >= date('now', '-30 days')
                    GROUP BY insight_type
                """, (user_id,))

                insights_stats = cursor.fetchall()

                return {
                    "fraud_detection": {
                        "total_checks": fraud_stats[0] if fraud_stats[0] else 0,
                        "average_risk_score": round(fraud_stats[1], 2) if fraud_stats[1] else 0,
                        "high_risk_alerts": fraud_stats[2] if fraud_stats[2] else 0,
                        "critical_risk_alerts": fraud_stats[3] if fraud_stats[3] else 0
                    },
                    "insights_generated": [
                        {
                            "type": row[0],
                            "count": row[1],
                            "average_confidence": round(row[2], 2) if row[2] else 0
                        }
                        for row in insights_stats
                    ] if insights_stats else [],
                    "period": "30 days"
                }

        except Exception as e:
            logger.error(f"Failed to get AI stats: {e}")
            return {"error": "Failed to retrieve statistics"}

    async def update_user_ai_preferences(
        self,
        user_id: str,
        preferences: Dict[str, Any]
    ) -> bool:
        """Update user's AI preferences"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    INSERT OR REPLACE INTO user_ai_preferences (
                        user_id, ai_enabled, notification_threshold,
                        preferred_analysis_type, last_updated
                    ) VALUES (?, ?, ?, ?, ?)
                """, (
                    user_id,
                    preferences.get("ai_enabled", True),
                    preferences.get("notification_threshold", 0.7),
                    preferences.get("preferred_analysis_type", "balanced"),
                    datetime.now().isoformat()
                ))

                conn.commit()
                return True

        except Exception as e:
            logger.error(f"Failed to update AI preferences: {e}")
            return False


# Singleton instance
_database_service = None

def get_database_service() -> DatabaseService:
    """Get singleton instance of database service"""
    global _database_service
    if _database_service is None:
        _database_service = DatabaseService()
    return _database_service