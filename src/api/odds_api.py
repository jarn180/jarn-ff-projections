"""
Client for The Odds API to fetch player props
"""

import os
import requests
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class OddsAPIClient:
    """Client for interacting with The Odds API."""

    BASE_URL = "https://api.the-odds-api.com/v4"

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the API client.

        Args:
            api_key: The Odds API key. If not provided, will look for ODDS_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("ODDS_API_KEY")
        if not self.api_key:
            raise ValueError("API key is required. Set ODDS_API_KEY environment variable or pass api_key parameter.")

    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """Make a request to The Odds API.

        Args:
            endpoint: API endpoint path
            params: Query parameters

        Returns:
            JSON response as dictionary
        """
        url = f"{self.BASE_URL}/{endpoint}"
        params = params or {}
        params["apiKey"] = self.api_key

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()

            # Check remaining requests
            remaining = response.headers.get("x-requests-remaining")
            if remaining:
                print(f"API Requests Remaining: {remaining}")

            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from The Odds API: {e}")
            raise

    def get_player_props(self, sport: str = "americanfootball_nfl",
                        regions: str = "us",
                        markets: Optional[List[str]] = None) -> List[Dict]:
        """Fetch player props for a given sport.

        Args:
            sport: Sport key (default: americanfootball_nfl)
            regions: Regions to get odds from (default: us)
            markets: List of prop markets to fetch. If None, fetches all available.
                    Common markets: player_pass_tds, player_pass_yds, player_rush_yds,
                    player_receptions, player_reception_yds, player_anytime_td

        Returns:
            List of events with player props
        """
        params = {
            "regions": regions,
            "oddsFormat": "decimal",
        }

        if markets:
            params["markets"] = ",".join(markets)

        endpoint = f"sports/{sport}/events"
        events = self._make_request(endpoint, params)

        # Now fetch props for each event
        all_props = []
        for event in events:
            event_id = event.get("id")
            if event_id:
                props = self.get_event_props(sport, event_id, regions, markets)
                if props:
                    all_props.append(props)

        return all_props

    def get_event_props(self, sport: str, event_id: str,
                       regions: str = "us",
                       markets: Optional[List[str]] = None) -> Dict:
        """Fetch player props for a specific event.

        Args:
            sport: Sport key
            event_id: Event ID
            regions: Regions to get odds from
            markets: List of prop markets to fetch

        Returns:
            Event props data
        """
        params = {
            "regions": regions,
            "oddsFormat": "decimal",
        }

        if markets:
            params["markets"] = ",".join(markets)

        endpoint = f"sports/{sport}/events/{event_id}/odds"
        return self._make_request(endpoint, params)

    def get_available_markets(self, sport: str = "americanfootball_nfl") -> List[str]:
        """Get list of available prop markets for a sport.

        Args:
            sport: Sport key

        Returns:
            List of available market keys
        """
        # This would typically come from the API, but we'll define common ones
        # The Odds API documentation lists these
        return [
            "player_pass_tds",
            "player_pass_yds",
            "player_pass_completions",
            "player_pass_attempts",
            "player_pass_interceptions",
            "player_rush_yds",
            "player_rush_attempts",
            "player_receptions",
            "player_reception_yds",
            "player_anytime_td",
            "player_first_td",
            "player_last_td",
        ]


def parse_player_props(api_response: Dict) -> Dict[str, Dict]:
    """Parse API response into structured player props.

    Args:
        api_response: Raw API response from get_event_props

    Returns:
        Dictionary mapping player names to their props
    """
    players = {}

    if not api_response or "bookmakers" not in api_response:
        return players

    # Extract game info
    home_team = api_response.get("home_team", "")
    away_team = api_response.get("away_team", "")
    commence_time = api_response.get("commence_time", "")

    for bookmaker in api_response.get("bookmakers", []):
        for market in bookmaker.get("markets", []):
            market_key = market.get("key")

            for outcome in market.get("outcomes", []):
                player_name = outcome.get("description")
                if not player_name:
                    continue

                if player_name not in players:
                    players[player_name] = {
                        "name": player_name,
                        "props": {},
                        "game_info": {
                            "home_team": home_team,
                            "away_team": away_team,
                            "commence_time": commence_time,
                        }
                    }

                # Store the line/point value for this prop
                point = outcome.get("point")
                if point and market_key:
                    if market_key not in players[player_name]["props"]:
                        players[player_name]["props"][market_key] = []

                    players[player_name]["props"][market_key].append({
                        "value": point,
                        "bookmaker": bookmaker.get("title"),
                        "price": outcome.get("price"),
                    })

    # Average the props from multiple bookmakers
    for player_name, player_data in players.items():
        for prop_key, prop_values in player_data["props"].items():
            if prop_values:
                avg_value = sum(p["value"] for p in prop_values) / len(prop_values)
                player_data["props"][prop_key] = avg_value

    return players


def detect_position(player_props: Dict) -> str:
    """Detect player position based on available props.

    Args:
        player_props: Player props dictionary

    Returns:
        Position string (QB, RB, WR, TE)
    """
    props = player_props.get("props", {})

    # QB: Has passing yards
    if "player_pass_yds" in props or "player_pass_tds" in props:
        return "QB"

    # Get stats
    has_rush = "player_rush_yds" in props or "player_rush_attempts" in props
    has_rec = "player_receptions" in props or "player_reception_yds" in props

    rush_yds = props.get("player_rush_yds", 0)
    rec_yds = props.get("player_reception_yds", 0)
    receptions = props.get("player_receptions", 0)

    # RB: Has rushing yards and either no receiving or rush-heavy
    if has_rush and has_rec:
        # If rushing yards are higher, definitely RB
        if rush_yds > rec_yds:
            return "RB"
        # If close, but has decent rushing, still RB
        elif rush_yds > 30:
            return "RB"

    if has_rush and not has_rec:
        return "RB"

    # For receiving-only players (WR vs TE)
    if has_rec:
        # First, check for known TEs by name (most reliable method)
        te_keywords = [
            'kelce', 'kittle', 'andrews', 'pitts', 'goedert', 'hockenson',
            'schultz', 'ertz', 'engram', 'kmet', 'kincaid', 'laporta',
            'njoku', 'freiermuth', 'henry', 'gesicki', 'tonyan', 'bates',
            'likely', 'gray', 'everett', 'conklin', 'hooper', 'uzomah',
            'thomas', 'dulcich', 'bellinger', 'otton', 'kraft', 'ferguson'
        ]
        player_name_lower = player_props.get('name', '').lower()
        if any(keyword in player_name_lower for keyword in te_keywords):
            return "TE"

        # Calculate yards per catch if possible
        ypc = rec_yds / receptions if receptions > 0 else 0

        # Only classify as TE if multiple indicators suggest it:
        # 1. Very low receiving yards (under 25) AND low YPC (under 8)
        # 2. OR moderate yards (25-35) with very low YPC (under 7) and high volume (4+ catches)

        if rec_yds < 25 and ypc < 8 and receptions >= 3:
            return "TE"

        if rec_yds >= 25 and rec_yds < 35 and ypc < 7 and receptions >= 4:
            return "TE"

        # Everyone else with receiving props = WR
        # This includes all WR3s, WR4s, deep threats, possession WRs, etc.
        return "WR"

    # Default to WR if can't determine
    return "WR"
