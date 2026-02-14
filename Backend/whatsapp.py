import requests

from config import Settings


class WhatsAppClient:
    def __init__(self, settings: Settings) -> None:
        self._token = settings.whatsapp_token
        self._phone_id = settings.whatsapp_phone_id

    def is_configured(self) -> bool:
        return bool(self._token and self._phone_id)

    def send_text(self, to_number: str, message: str) -> tuple[str, str | None]:
        if not self.is_configured():
            return "skipped", "missing_credentials"

        url = f"https://graph.facebook.com/v19.0/{self._phone_id}/messages"
        headers = {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": to_number,
            "type": "text",
            "text": {"body": message},
        }

        response = requests.post(url, headers=headers, json=payload, timeout=15)
        if response.status_code >= 300:
            return "error", f"{response.status_code}: {response.text}"
        return "sent", None
