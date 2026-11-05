import time
import uuid
from typing import List, Dict, Any, Optional

class AlertEvent:
    def __init__(self, alert_type: str, severity: str, title: str, description: str, zone_id: Optional[str] = None):
        self.alert_id = f"alt-{uuid.uuid4().hex[:8]}"
        self.timestamp = time.time()
        self.formatted_time = time.strftime("%H:%M:%S")
        self.alert_type = alert_type
        self.severity = severity  # 'info', 'warning', 'high', 'critical'
        self.title = title
        self.description = description
        self.zone_id = zone_id
        self.acknowledged = False
        self.resolved = False

    def to_dict(self) -> Dict[str, Any]:
        badge_colors = {
            "info": "blue",
            "warning": "amber",
            "high": "orange",
            "critical": "rose"
        }
        return {
            "id": self.alert_id,
            "timestamp": self.timestamp,
            "time": self.formatted_time,
            "type": self.alert_type,
            "severity": self.severity,
            "title": self.title,
            "desc": self.description,
            "zone_id": self.zone_id,
            "acknowledged": self.acknowledged,
            "resolved": self.resolved,
            "badge_color": badge_colors.get(self.severity, "slate")
        }

class AlertEngine:
    """
    Intelligent Alert & Notification Engine with cooldown deduplication.
    Prevents operator fatigue while ensuring safety anomalies are highlighted.
    """
    def __init__(self, cooldown_seconds: float = 30.0):
        self.cooldown_seconds = cooldown_seconds
        self.alerts: List[AlertEvent] = []
        self._last_alert_times: Dict[str, float] = {}

    def trigger(self, alert_type: str, severity: str, title: str, description: str, zone_id: Optional[str] = None) -> Optional[AlertEvent]:
        key = f"{alert_type}_{zone_id or 'global'}"
        now = time.time()
        
        # Check cooldown
        if key in self._last_alert_times:
            if now - self._last_alert_times[key] < self.cooldown_seconds:
                return None  # Suppressed by cooldown

        event = AlertEvent(alert_type, severity, title, description, zone_id)
        self.alerts.insert(0, event)  # Prepend newest
        if len(self.alerts) > 100:
            self.alerts.pop()
        self._last_alert_times[key] = now
        return event

    def acknowledge(self, alert_id: str) -> bool:
        for alert in self.alerts:
            if alert.alert_id == alert_id:
                alert.acknowledged = True
                return True
        return False

    def get_recent(self, limit: int = 10, severity_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        filtered = self.alerts
        if severity_filter:
            filtered = [a for a in filtered if a.severity == severity_filter]
        return [a.to_dict() for a in filtered[:limit]]
