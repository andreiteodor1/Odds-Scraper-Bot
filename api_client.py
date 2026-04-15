import requests
import json
import config


class OddsAPIClient:
    def __init__(self):
        self.api_key = config.API_KEY
        self.base_url = config.BASE_URL
        self.sport = config.SPORT

    def fetch_live_odds(self):
        if config.USE_MOCK_DATA:
            print("🔧 MOCK MODE ON: Loading data from local file (no API credits used)")
            try:
                with open('mock_data.json', 'r') as f:
                    return json.load(f)
            except FileNotFoundError:
                print("Error: mock_data.json not found")
                return None
        url = f'{self.base_url}/{self.sport}/odds'
        params = {
            'apiKey': self.api_key,
            'regions': config.REGIONS,
            'markets': config.MARKETS,
            'oddsFormat': config.ODDS_FORMAT
        }

        print(f"Connecting to Odds API for {self.sport}...")
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            with open('mock_data.json', 'w') as f:
                json.dump(data, f)

            requests_left = response.headers.get('x-requests-remaining', 'Unknown')
            print(f"SUCCESS! Data retrieved. (API requests remaining this month: {requests_left})")
            return data

        except requests.exceptions.RequestException as e:
            print(f"NETWORK ERROR: {e}")
            return None