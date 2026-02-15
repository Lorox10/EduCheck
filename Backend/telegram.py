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

    def send_text(self, chat_id: str, message: str) -> tuple[str, str | None]:
        """
        Envía un mensaje de texto via Telegram.
        
        Args:
            chat_id: ID de chat de Telegram o número de teléfono del destinatario
            message: Mensaje a enviar
            
        Returns:
            Tupla (status, error):
            - status: "sent", "skipped" o "error"
            - error: Mensaje de error si aplica
        """
        print(f"[TELEGRAM.send_text] Iniciando - token={'***' if self.token else 'VACIO'}, chat_id={chat_id}")
        
        if not self.token:
            print("[TELEGRAM.send_text] Token no configurado")
            return "skipped", "Telegram no configurado"

        try:
            payload = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "HTML",
            }
            url = f"{self.base_url}/sendMessage"
            print(f"[TELEGRAM.send_text] URL: {url}")
            print(f"[TELEGRAM.send_text] Payload: chat_id={chat_id}, message_len={len(message)}")
            
            response = requests.post(
                url,
                json=payload,
                timeout=10,
            )
            print(f"[TELEGRAM.send_text] Response status: {response.status_code}")
            print(f"[TELEGRAM.send_text] Response body: {response.text}")
            
            response.raise_for_status()

            if response.json().get("ok"):
                print("[TELEGRAM.send_text] ✓ Mensaje enviado correctamente")
                return "sent", None
            else:
                error = response.json().get("description", "Unknown error")
                print(f"[TELEGRAM.send_text] Error en respuesta: {error}")
                return "error", error

        except requests.RequestException as e:
            print(f"[TELEGRAM.send_text] RequestException: {str(e)}")
            return "error", str(e)
        except Exception as e:
            print(f"[TELEGRAM.send_text] Unexpected error: {str(e)}")
            return "error", f"Unexpected error: {str(e)}"
