"""
Notification Service - Handle alerts and notifications
"""

from sqlalchemy.orm import Session
from models import Alert, User
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class NotificationService:
    """
    Service class for notifications and alerts
    """

    @staticmethod
    def create_alert(
        db: Session,
        alert_data: Dict[str, Any]
    ) -> Alert:
        """
        Create a new alert
        """
        # Generate alert ID
        last_alert = db.query(Alert).order_by(Alert.id.desc()).first()
        alert_id = f"ALERT{(last_alert.id + 1):03d}" if last_alert else "ALERT001"

        alert = Alert(alert_id=alert_id, **alert_data)
        db.add(alert)
        db.commit()
        db.refresh(alert)

        logger.info(f"Created alert: {alert_id} - {alert.title}")

        # Trigger notification channels (in production, this would send actual notifications)
        NotificationService._send_notifications(alert)

        return alert

    @staticmethod
    def _send_notifications(alert: Alert):
        """
        Send notifications through various channels
        """
        # In production, integrate with:
        # - Email service (SendGrid, AWS SES)
        # - SMS service (Twilio, AWS SNS)
        # - Push notifications (Firebase, OneSignal)

        if alert.severity in ["HIGH", "CRITICAL"]:
            logger.info(f"📧 Would send email for alert: {alert.title}")
            logger.info(f"📱 Would send SMS for alert: {alert.title}")
            logger.info(f"🔔 Would send push notification for alert: {alert.title}")
        else:
            logger.info(f"📬 In-app notification created for: {alert.title}")

    @staticmethod
    def get_user_alerts(
        db: Session,
        user_id: str,
        unread_only: bool = False,
        limit: int = 50
    ) -> List[Alert]:
        """
        Get user's alerts
        """
        query = db.query(Alert).filter_by(user_id=user_id)

        if unread_only:
            query = query.filter_by(is_read=False)

        # Order by severity and date
        severity_order = {
            "CRITICAL": 0,
            "HIGH": 1,
            "MEDIUM": 2,
            "LOW": 3,
            "INFO": 4
        }

        alerts = query.all()
        sorted_alerts = sorted(
            alerts,
            key=lambda x: (
                severity_order.get(x.severity, 5),
                -x.created_at.timestamp()
            )
        )

        return sorted_alerts[:limit]

    @staticmethod
    def mark_alert_read(
        db: Session,
        alert_id: str
    ) -> Optional[Alert]:
        """
        Mark alert as read
        """
        alert = db.query(Alert).filter_by(alert_id=alert_id).first()

        if alert:
            alert.is_read = True
            alert.read_at = datetime.utcnow()
            db.commit()
            db.refresh(alert)

        return alert

    @staticmethod
    def dismiss_alert(
        db: Session,
        alert_id: str
    ) -> Optional[Alert]:
        """
        Dismiss an alert
        """
        alert = db.query(Alert).filter_by(alert_id=alert_id).first()

        if alert:
            alert.is_dismissed = True
            alert.dismissed_at = datetime.utcnow()
            db.commit()
            db.refresh(alert)

        return alert

    @staticmethod
    def create_fraud_alert(
        db: Session,
        user_id: str,
        transaction_data: Dict[str, Any],
        risk_score: int
    ) -> Alert:
        """
        Create a fraud alert for suspicious transaction
        """
        severity = "CRITICAL" if risk_score > 80 else "HIGH" if risk_score > 60 else "MEDIUM"

        alert_data = {
            "user_id": user_id,
            "type": "FRAUD",
            "title": f"🚨 Suspicious Transaction Detected",
            "message": (
                f"Unusual transaction of ₹{abs(transaction_data['amount']):,.2f} "
                f"from {transaction_data['merchant']} detected. "
                f"Risk Score: {risk_score}/100. "
                "Immediate action required."
            ),
            "severity": severity,
            "related_entity_type": "transaction",
            "related_entity_id": transaction_data.get("transaction_id"),
            "action_required": True,
            "action_type": "VERIFY",
            "action_deadline": datetime.utcnow() + timedelta(hours=24)
        }

        return NotificationService.create_alert(db, alert_data)

    @staticmethod
    def create_goal_alert(
        db: Session,
        user_id: str,
        goal_data: Dict[str, Any]
    ) -> Alert:
        """
        Create alert for goal progress
        """
        if goal_data["status"] == "BEHIND":
            severity = "MEDIUM"
            title = f"⚠️ Goal Behind Schedule: {goal_data['name']}"
            message = (
                f"Your '{goal_data['name']}' goal is {goal_data['behind_percentage']:.1f}% "
                f"behind schedule. Current: ₹{goal_data['current_amount']:,.0f}, "
                f"Target: ₹{goal_data['target_amount']:,.0f}"
            )
        elif goal_data["status"] == "ACHIEVED":
            severity = "INFO"
            title = f"🎉 Goal Achieved: {goal_data['name']}"
            message = f"Congratulations! You've achieved your '{goal_data['name']}' goal!"
        else:
            return None

        alert_data = {
            "user_id": user_id,
            "type": "GOAL",
            "title": title,
            "message": message,
            "severity": severity,
            "related_entity_type": "goal",
            "related_entity_id": goal_data.get("goal_id")
        }

        return NotificationService.create_alert(db, alert_data)

    @staticmethod
    def create_bill_reminder(
        db: Session,
        user_id: str,
        bill_data: Dict[str, Any]
    ) -> Alert:
        """
        Create bill payment reminder
        """
        alert_data = {
            "user_id": user_id,
            "type": "BILL",
            "title": f"📅 Bill Due: {bill_data['name']}",
            "message": (
                f"Your {bill_data['name']} bill of ₹{bill_data['amount']:,.2f} "
                f"is due on {bill_data['due_date']}. "
                "Set up auto-pay to avoid late fees."
            ),
            "severity": "MEDIUM",
            "action_required": True,
            "action_type": "PAY",
            "action_deadline": datetime.fromisoformat(bill_data['due_date'])
        }

        return NotificationService.create_alert(db, alert_data)

    @staticmethod
    def create_investment_alert(
        db: Session,
        user_id: str,
        investment_data: Dict[str, Any]
    ) -> Alert:
        """
        Create investment-related alert
        """
        alert_type = investment_data.get("alert_type", "performance")

        if alert_type == "performance":
            if investment_data["returns_percentage"] > 20:
                title = f"📈 Excellent Returns: {investment_data['name']}"
                message = f"Your {investment_data['name']} has generated {investment_data['returns_percentage']:.1f}% returns!"
                severity = "INFO"
            else:
                title = f"📉 Poor Performance: {investment_data['name']}"
                message = f"Your {investment_data['name']} is underperforming. Consider reviewing your portfolio."
                severity = "LOW"
        elif alert_type == "maturity":
            title = f"📆 Investment Maturing: {investment_data['name']}"
            message = f"Your {investment_data['name']} is maturing on {investment_data['maturity_date']}."
            severity = "MEDIUM"
        else:
            return None

        alert_data = {
            "user_id": user_id,
            "type": "INVESTMENT",
            "title": title,
            "message": message,
            "severity": severity,
            "related_entity_type": "investment",
            "related_entity_id": investment_data.get("investment_id")
        }

        return NotificationService.create_alert(db, alert_data)

    @staticmethod
    def get_alert_summary(
        db: Session,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Get summary of user's alerts
        """
        alerts = db.query(Alert).filter_by(user_id=user_id).all()

        unread_alerts = [a for a in alerts if not a.is_read]
        action_required = [a for a in alerts if a.action_required and not a.is_dismissed]

        # Group by type
        alerts_by_type = {}
        for alert in unread_alerts:
            if alert.type not in alerts_by_type:
                alerts_by_type[alert.type] = []
            alerts_by_type[alert.type].append({
                "alert_id": alert.alert_id,
                "title": alert.title,
                "severity": alert.severity,
                "created_at": alert.created_at.isoformat()
            })

        return {
            "total_alerts": len(alerts),
            "unread_count": len(unread_alerts),
            "action_required_count": len(action_required),
            "alerts_by_type": alerts_by_type,
            "critical_alerts": [
                {
                    "alert_id": a.alert_id,
                    "title": a.title,
                    "message": a.message
                }
                for a in unread_alerts if a.severity == "CRITICAL"
            ]
        }