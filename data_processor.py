import pandas as pd


class TradingDataProcessor:
    def __init__(self):
        pass

    def calculate_true_odds_and_ev(self, home_odds, draw_odds, away_odds):

        if not home_odds or not draw_odds or not away_odds:
            return 0, 0, 0, 0, 0, 0, 0

        # 1. Calculate implied probabilities
        p_home = 1 / home_odds
        p_draw = 1 / draw_odds
        p_away = 1 / away_odds

        # 2. Calculate the margin (Total Book)
        margin = p_home + p_draw + p_away

        # 3. Calculate True Probabilities (removing the margin)
        true_p_home = p_home / margin
        true_p_draw = p_draw / margin
        true_p_away = p_away / margin

        # 4. Convert back to True Odds
        true_home = round(1 / true_p_home, 2)
        true_draw = round(1 / true_p_draw, 2)
        true_away = round(1 / true_p_away, 2)

        # 5. Calculate Expected Value (EV) for each outcome
        ev_home = round(((home_odds / true_home) - 1) * 100, 2)
        ev_draw = round(((draw_odds / true_draw) - 1) * 100, 2)
        ev_away = round(((away_odds / true_away) - 1) * 100, 2)

        margin_percentage = round((margin - 1) * 100, 2)

        return margin_percentage, true_home, true_draw, true_away, ev_home, ev_draw, ev_away

    def flatten_to_dataframe(self, raw_data):
        if not raw_data:
            return pd.DataFrame()

        processed_rows = []

        for event in raw_data:
            match_name = f"{event['home_team']} vs {event['away_team']}"
            raw_time = event.get('commence_time', '')
            formatted_time = pd.to_datetime(raw_time).strftime('%Y-%m-%d %H:%M') if raw_time else "Unknown"

            for bookmaker in event['bookmakers']:
                # Filter out betting exchanges because their liquidity messes up our true odds math
                if bookmaker['title'] in ['Betfair', 'Smarkets', 'Matchbook']:
                    continue

                for market in bookmaker['markets']:
                    if market['key'] == 'h2h':
                        home_odds = draw_odds = away_odds = 0
                        for outcome in market['outcomes']:
                            if outcome['name'] == event['home_team']:
                                home_odds = outcome['price']
                            elif outcome['name'] == event['away_team']:
                                away_odds = outcome['price']
                            elif outcome['name'] == 'Draw':
                                draw_odds = outcome['price']

                        # Run our new Quant math
                        margin, t_home, t_draw, t_away, ev_home, ev_draw, ev_away = self.calculate_true_odds_and_ev(
                            home_odds, draw_odds, away_odds)

                        processed_rows.append({
                            'Kickoff': formatted_time,
                            'Match': match_name,
                            'Bookmaker': bookmaker['title'],
                            '1 (Odds)': home_odds,
                            '1 (True)': t_home,
                            '1 (EV %)': ev_home,
                            'X (Odds)': draw_odds,
                            'X (True)': t_draw,
                            'X (EV %)': ev_draw,
                            '2 (Odds)': away_odds,
                            '2 (True)': t_away,
                            '2 (EV %)': ev_away
                        })

        return pd.DataFrame(processed_rows)

    def find_value_bets(self, df):
        #Filters the dataframe to only show profitable (+EV) bets.
        print("\n SCANNING FOR VALUE BETS (+EV)")

        # Find any row where EV is greater than 0%
        value_bets = df[(df['1 (EV %)'] > 0) | (df['X (EV %)'] > 0) | (df['2 (EV %)'] > 0)]

        if value_bets.empty:
            print("No +EV bets found in the current market.")
            return None

        print(f"Found {len(value_bets)} potential Value Bets!")
        return value_bets