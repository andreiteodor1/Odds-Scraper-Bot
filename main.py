'''

# main.py
from api_client import OddsAPIClient
from data_processor import TradingDataProcessor


def run_trader_poc():
    print("--- Initializing Super Trader POC ---\n")

    # 1. Initialize our modules
    client = OddsAPIClient()
    processor = TradingDataProcessor()

    # 2. Fetch the data (Network Layer)
    raw_data = client.fetch_live_odds()

    # 3. Process the data (Quant Layer)
    if raw_data:
        df = processor.flatten_to_dataframe(raw_data)

        # --- CHANGED: Sort chronologically first, then by Match, then by Bookmaker ---
        df = df.sort_values(by=['Kickoff', 'Match', 'Bookmaker'])

        # We can print the table again to see the chronological order
        print("\n--- Live Market Analysis ---")
        print(df.to_string(index=False))

        # processor.analyze_market_efficiency(df)


if __name__ == "__main__":
    run_trader_poc()
'''
# main.py
from api_client import OddsAPIClient
from data_processor import TradingDataProcessor
from discord_notifier import DiscordNotifier
import config
import time
from datetime import datetime

# Stores alerts we already sent
seen_alerts = set()


def run_trader_poc(client, processor, notifier):
    print(f"\n Scan Initiated at {datetime.now().strftime('%H:%M:%S')}")

    raw_data = client.fetch_live_odds()

    if raw_data:
        df = processor.flatten_to_dataframe(raw_data)

        if not df.empty:
            value_df = processor.find_value_bets(df)

            if value_df is not None:
                new_alerts_found = False

                print("\n Initiating Discord Alerts")
                for index, row in value_df.iterrows():
                    match = row['Match']
                    bookie = row['Bookmaker']

                    # Check Home Win
                    if row['1 (EV %)'] > 0:
                        alert_id = f"{match}_{bookie}_1"
                        if alert_id not in seen_alerts:
                            notifier.send_value_alert(match, bookie, "Home Win (1)", row['1 (Odds)'], row['1 (EV %)'])
                            seen_alerts.add(alert_id)
                            new_alerts_found = True
                            time.sleep(1)

                            # Check Draw
                    if row['X (EV %)'] > 0:
                        alert_id = f"{match}_{bookie}_X"
                        if alert_id not in seen_alerts:
                            notifier.send_value_alert(match, bookie, "Draw (X)", row['X (Odds)'], row['X (EV %)'])
                            seen_alerts.add(alert_id)
                            new_alerts_found = True
                            time.sleep(1)

                    # Check Away Win
                    if row['2 (EV %)'] > 0:
                        alert_id = f"{match}_{bookie}_2"
                        if alert_id not in seen_alerts:
                            notifier.send_value_alert(match, bookie, "Away Win (2)", row['2 (Odds)'], row['2 (EV %)'])
                            seen_alerts.add(alert_id)
                            new_alerts_found = True
                            time.sleep(1)

                if not new_alerts_found:
                    print("Value bets exist, but no NEW alerts to send.")
            else:
                pass  # No EV bets found
        else:
            print("Dataframe is empty.")
    else:
        print("API call failed or mock data missing.")


if __name__ == "__main__":
    print(" STARTING SUPERBET TRADING BOT")

    api_client = OddsAPIClient()
    data_processor = TradingDataProcessor()
    discord_bot = DiscordNotifier(config.DISCORD_WEBHOOK_URL)

    # Infinite loop for fetching live data every 5 minutes, with API premium subscription
    while True:
        try:
            run_trader_poc(api_client, data_processor, discord_bot)

            print("\n Retrying in 5 minutes. ")
            time.sleep(300)

        except KeyboardInterrupt:
            print("\n Bot manually stopped by user.")
            break
        except Exception as e:
            print(f"\n CRITICAL ERROR: {e}")
            time.sleep(60)