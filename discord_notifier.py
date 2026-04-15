# discord_notifier.py
import requests


class DiscordNotifier:
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url

    def send_value_alert(self, match, bookie, outcome, odds, ev_percent):
        """Formats and sends a single alert message to the Discord channel."""

        # We use Discord's markdown formatting to make it look professional
        message = (
            f"🚨 VALUE BET DETECTED 🚨\n"
            f"⚽ Match: {match}\n"
            f"🏦 Bookmaker: {bookie}\n"
            f"🎯 Bet: {outcome} at **{odds}**\n"
            f"📈 Your Mathematical Edge: +{ev_percent}%\n"
            f"----------------------------------------"
        )

        payload = {
            "content": message
        }

        try:
            # We POST the data to your secret webhook URL
            response = requests.post(self.webhook_url, json=payload)

            # Discord returns status code 204 if the message was posted successfully
            if response.status_code == 204:
                print(f"✅ Alert successfully sent to Discord for {match}!")
            else:
                print(f"❌ Failed to send Discord alert. Status: {response.status_code}")

        except requests.exceptions.RequestException as e:
            print(f"Discord Network Error: {e}")