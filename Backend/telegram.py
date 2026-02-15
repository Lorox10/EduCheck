import requests

from config import Settings


class TelegramClient:
    """Cliente para enviar mensajes via Telegram Bot API."""

    def __init__(self, settings: Settings) -> None:
        self.token = settings.telegram_token
        self.chat_id = settings.telegram_chat_id
        self.base_url = f"https://api.telegram.org/bot{self.token}"

    def is_configured(self) -> bool:
        """Verifica si el token y chat_id están configurados."""
        return bool(self.token and self.chat_id)

    def send_text(self, phone: str, message: str) -> tuple[str, str | None]:
        """
        Envía un mensaje de texto via Telegram.
        
        Args:
            phone: Número de teléfono (no usado para Telegram, solo para compatibilidad)
            message: Mensaje a enviar
            
        Returns:
            Tupla (status, error):
            - status: "sent", "skipped" o "error"
            - error: Mensaje de error si aplica
        """
        if not self.is_configured():
            return "skipped", "Telegram no configurado"

        try:
            payload = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "HTML",
            }
            response = requests.post(
                f"{self.base_url}/sendMessage",
                json=payload,
                timeout=10,
            )
            response.raise_for_status()

            if response.json().get("ok"):
                return "sent", None
            else:
                error = response.json().get("description", "Unknown error")
                return "error", error

        except requests.RequestException as e:
            return "error", str(e)
        except Exception as e:
            return "error", f"Unexpected error: {str(e)}"
