import logging
from app.core.patient_management.services import Notifier

# Set up a simple logger
logger = logging.getLogger(__name__)

class ConsoleNotifier(Notifier):
    """
    A mock notifier that prints alerts to the console.
    Perfect for local development and testing without external dependencies.
    """

    async def send_urgent_alert(self, scan_id: str, probability: float) -> bool:
        # Log it properly
        logger.info(
            f"[MOCK NOTIFICATION] Urgent alert for scan: {scan_id} | "
            f"Highest Probability: {probability * 100:.1f}%"
        )
        # Also print it so it's clearly visible in the terminal
        alert_text = self._format_alert_body(scan_id, probability)
        print(alert_text)
        # Simulate successful delivery
        return True