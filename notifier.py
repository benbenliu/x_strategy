from abc import ABC, abstractmethod
import requests
import os

class Notifier(ABC):
    @abstractmethod
    def send_message(self, message: str):
        pass

class TgNotifier(Notifier):
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"

    def send_message(self, message: str):
        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            raise Exception(f"Failed to send Telegram message: {response.text}")

# Example usage
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    # Retrieve bot token and chat ID from environment variables
    bot_token = os.getenv("SIGNAL_BOT_TOKEN")
    chat_id = os.getenv("JACKIE_SIGNAL_CHAT_ID")

    if not bot_token or not chat_id:
        print("Please set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID environment variables.")
    else:
        notifier = TgNotifier(bot_token, chat_id)
        notifier.send_message("this is the third trading bot message")