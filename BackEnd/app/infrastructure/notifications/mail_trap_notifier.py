import httpx
import logging
from app.core.patient_management.services import Notifier

logger = logging.getLogger(__name__)
class MailtrapEmailNotifier(Notifier):
    def __init__(
        self, 
        api_token: str, 
        inbox_id: str, 
        recipient_emails_str: str,  
        sender_email: str
    ):
        self.api_token = api_token
        self.inbox_id = inbox_id
        self.sender_email = sender_email
        self.api_url = f"https://sandbox.api.mailtrap.io/api/send/{inbox_id}"
        
        raw_list = [email.strip() for email in recipient_emails_str.split(",") if email.strip()]
        self.recipients = raw_list[:3]  

    async def send_urgent_alert(self, scan_id: str, probability: float) -> bool:
        if not self.recipients:
            logger.warning(f"Mailtrap notification skipped for scan {scan_id}: No recipient emails configured.")
            return False

        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        
        email_body = self._format_alert_body(scan_id, probability)

        #  Map email strings dynamically to Mailtrap's expected "to" field layout
        to_field_payload = [{"email": email} for email in self.recipients]

        payload = {
            "from": {"email": self.sender_email, "name": "AI Diagnostic Engine (Sandbox)"},
            "to": to_field_payload,  #  Now sends to your actual dynamic list
            "subject": f" CRITICAL: Urgent Analysis Complete [Ref: {scan_id}]",
            "text": email_body,
            "category": "Urgent Alerts"
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.api_url, json=payload, headers=headers, timeout=5.0)
                if response.status_code == 200:
                    logger.info(f"Mailtrap alert successfully sent for scan {scan_id}")
                else:
                    logger.error(f"Mailtrap API returned {response.status_code} for scan {scan_id}")
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Mailtrap delivery failed for scan {scan_id}: {e}")
            return False