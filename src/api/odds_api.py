"""
Client for The Odds API to fetch player props
"""

import os
import requests
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


# Game-level markets. The bulk /odds endpoint returns these for every game in
# one request, so they're fetched once instead of once per event.
GAME_LINE_MARKETS = {"h2h", "spreads", "totals"}


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
        # Quota tracking, read from response headers
        self.requests_made = 0
        self.credits_used = 0
        self.credits_remaining = None

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

            # Track quota usage (summarized once by the caller, not per request)
            self.requests_made += 1
            last_cost = response.headers.get("x-requests-last")
            if last_cost:
                self.credits_used += int(float(last_cost))
            remaining = response.headers.get("x-requests-remaining")
            if remaining:
                self.credits_remaining = int(float(remaining))

            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from The Odds API: {e}")
            raise

    def get_player_props(self, sport: str = "americanfootball_nfl",
                        regions: str = "us",
                        markets: Optional[List[str]] = None,
                        max_days_ahead: Optional[int] = 6) -> List[Dict]:
        """Fetch player props for a given sport.

        Args:
            sport: Sport key (default: americanfootball_nfl)
            regions: Regions to get odds from (default: us)
            markets: List of prop markets to fetch. If None, fetches all available.
                    Common markets: player_pass_tds, player_pass_yds, player_rush_yds,
                    player_receptions, player_reception_yds, player_anytime_td.
                    Game lines (spreads/totals/h2h) are fetched in one bulk request.
            max_days_ahead: Only fetch games within this many days of the next
                    kickoff (one NFL week). None fetches every listed game.

        Returns:
            List of events with player props
        """
        prop_markets = [m for m in markets or [] if m not in GAME_LINE_MARKETS] or None
        line_markets = [m for m in markets or [] if m in GAME_LINE_MARKETS]

        # Listing events is free; only list games that haven't kicked off yet
        # (props for started games are off the board but would still cost credits)
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        events = self._make_request(f"sports/{sport}/events",
                                    {"commenceTimeFrom": now})
        events = self._upcoming_week(events, max_days_ahead)

        # Game lines for every game in a single request (cost = markets x regions,
        # once) instead of being bundled into each per-event request
        lines_by_event = {}
        if line_markets and events:
            bulk = self._make_request(f"sports/{sport}/odds", {
                "regions": regions,
                "oddsFormat": "decimal",
                "markets": ",".join(line_markets),
                "eventIds": ",".join(e["id"] for e in events if e.get("id")),
            })
            lines_by_event = {e.get("id"): e for e in bulk}

        # Player props still have to be fetched per event
        all_props = []
        for event in events:
            event_id = event.get("id")
            if not event_id:
                continue
            if markets and not prop_markets:
                props = dict(event)  # game lines only, nothing per-event to fetch
            else:
                props = self.get_event_props(sport, event_id, regions, prop_markets)
            if not props:
                continue
            # Merge the game lines in as extra bookmaker entries so downstream
            # parsing sees the same shape as a combined request
            lines = lines_by_event.get(event_id)
            if lines:
                props.setdefault("bookmakers", []).extend(lines.get("bookmakers", []))
            all_props.append(props)

        return all_props

    @staticmethod
    def _upcoming_week(events: List[Dict], max_days_ahead: Optional[int]) -> List[Dict]:
        """Keep only events within max_days_ahead of the earliest listed game,
        so games a week or more out (props usually not posted yet) are skipped."""
        if not max_days_ahead or not events:
            return events

        def start(e):
            return datetime.fromisoformat(e["commence_time"].replace("Z", "+00:00"))

        timed = [e for e in events if e.get("commence_time")]
        if not timed:
            return events
        cutoff = min(start(e) for e in timed) + timedelta(days=max_days_ahead)
        return [e for e in timed if start(e) < cutoff]

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


def compute_implied_totals(api_response: Dict) -> Dict[str, float]:
    """Derive implied team point totals from the spreads + totals markets.

    Vegas doesn't publish a team total directly, but it's implied by the
    game total (over/under) and the point spread:
        team_implied_total = game_total / 2 - team_spread / 2
    (a favorite's spread is negative, so it nets a higher implied total)

    Args:
        api_response: Raw event odds response (same shape as parse_player_props)

    Returns:
        {"home": float, "away": float}, or {} if spreads/totals weren't
        available for this event (e.g. not yet posted by any bookmaker).
    """
    home_team = api_response.get("home_team", "")
    away_team = api_response.get("away_team", "")

    total_lines = []
    home_spreads = []
    away_spreads = []

    for bookmaker in api_response.get("bookmakers", []):
        for market in bookmaker.get("markets", []):
            key = market.get("key")
            if key == "totals":
                for outcome in market.get("outcomes", []):
                    if outcome.get("point") is not None:
                        total_lines.append(outcome["point"])
            elif key == "spreads":
                for outcome in market.get("outcomes", []):
                    point = outcome.get("point")
                    if point is None:
                        continue
                    if outcome.get("name") == home_team:
                        home_spreads.append(point)
                    elif outcome.get("name") == away_team:
                        away_spreads.append(point)

    if not total_lines or not (home_spreads or away_spreads):
        return {}

    avg_total = sum(total_lines) / len(total_lines)
    result = {}

    if home_spreads:
        avg_home_spread = sum(home_spreads) / len(home_spreads)
        result["home"] = round(avg_total / 2 - avg_home_spread / 2, 1)
    if away_spreads:
        avg_away_spread = sum(away_spreads) / len(away_spreads)
        result["away"] = round(avg_total / 2 - avg_away_spread / 2, 1)

    # If only one side had a spread line, derive the other from the total
    if "home" in result and "away" not in result:
        result["away"] = round(avg_total - result["home"], 1)
    if "away" in result and "home" not in result:
        result["home"] = round(avg_total - result["away"], 1)

    return result


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
    implied_totals = compute_implied_totals(api_response)

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
                            "home_implied_total": implied_totals.get("home"),
                            "away_implied_total": implied_totals.get("away"),
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
