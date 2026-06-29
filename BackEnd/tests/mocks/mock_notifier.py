from app.core.patient_management.services import Notifier

class MockNotificationService(Notifier):
    def __init__(self):
        # In-memory spy tracker to record outbound dispatches
        self.sent_alerts = []
        self.should_succeed = True  # Allows you to simulate network failures easily

    async def send_urgent_alert(self, scan_id: str, probability: float) -> bool:
        if not self.should_succeed:
            return False
            
        # Log the payload for test verification
        self.sent_alerts.append({
            "scan_id": scan_id,
            "probability": probability
        })
        return True