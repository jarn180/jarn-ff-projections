#!/usr/bin/env python3
"""
Update Projections Script
Run this manually to fetch fresh data from The Odds API and cache it
"""

import json
from datetime import datetime
from src.api.odds_api import OddsAPIClient, parse_player_props, detect_position
from src.projections.calculator import ProjectionCalculator
from config.scoring_formats import get_available_formats


def calculate_nfl_week(commence_time_str: str) -> str:
    """Calculate NFL week from game start time using 2026 NFL schedule."""
    if not commence_time_str:
        return "TBD"

    try:
        game_time = datetime.fromisoformat(commence_time_str.replace('Z', '+00:00'))

        # 2026 NFL Season Schedule (start date of each week)
        # Week 1 starts Wednesday, September 9, 2026 (season-opening Kickoff Game)
        week_start_dates_2026 = [
            datetime(2026, 9, 9, tzinfo=game_time.tzinfo),   # Week 1 (Wed)
            datetime(2026, 9, 17, tzinfo=game_time.tzinfo),  # Week 2 (Thu)
            datetime(2026, 9, 24, tzinfo=game_time.tzinfo),  # Week 3 (Thu)
            datetime(2026, 10, 1, tzinfo=game_time.tzinfo),  # Week 4 (Thu)
            datetime(2026, 10, 8, tzinfo=game_time.tzinfo),  # Week 5 (Thu)
            datetime(2026, 10, 15, tzinfo=game_time.tzinfo), # Week 6 (Thu)
            datetime(2026, 10, 22, tzinfo=game_time.tzinfo), # Week 7 (Thu)
            datetime(2026, 10, 29, tzinfo=game_time.tzinfo), # Week 8 (Thu)
            datetime(2026, 11, 5, tzinfo=game_time.tzinfo),  # Week 9 (Thu)
            datetime(2026, 11, 12, tzinfo=game_time.tzinfo), # Week 10 (Thu)
            datetime(2026, 11, 19, tzinfo=game_time.tzinfo), # Week 11 (Thu)
            datetime(2026, 11, 25, tzinfo=game_time.tzinfo), # Week 12 (Wed, Thanksgiving)
            datetime(2026, 12, 3, tzinfo=game_time.tzinfo),  # Week 13 (Thu)
            datetime(2026, 12, 10, tzinfo=game_time.tzinfo), # Week 14 (Thu)
            datetime(2026, 12, 17, tzinfo=game_time.tzinfo), # Week 15 (Thu)
            datetime(2026, 12, 24, tzinfo=game_time.tzinfo), # Week 16 (Thu)
            datetime(2026, 12, 31, tzinfo=game_time.tzinfo), # Week 17 (Thu)
            datetime(2027, 1, 9, tzinfo=game_time.tzinfo),   # Week 18 (Sat)
        ]

        # Find which week the game falls into
        for i, week_start in enumerate(week_start_dates_2026):
            # Check if game is before the next week starts
            if i < len(week_start_dates_2026) - 1:
                next_week_start = week_start_dates_2026[i + 1]
                if week_start <= game_time < next_week_start:
                    return f"Week {i + 1}"
            else:
                # Last week (Week 18)
                if game_time >= week_start:
                    return f"Week {i + 1}"

        # If before Week 1, return Week 1
        if game_time < week_start_dates_2026[0]:
            return "Week 1"

        return "TBD"
    except Exception:
        return "TBD"


def update_projections():
    """Fetch fresh data from The Odds API and save to cache."""
    print("🏈 Fetching player props from The Odds API...")

    # Default markets for projections
    markets = [
        'player_pass_yds',
        'player_pass_tds',
        'player_rush_yds',
        'player_receptions',
        'player_reception_yds'
    ]

    # Initialize API client
    client = OddsAPIClient()

    # Fetch player props
    events = client.get_player_props(sport='americanfootball_nfl', markets=markets)

    if not events:
        print("❌ No events found from The Odds API")
        return

    print(f"✓ Found {len(events)} events")

    # Parse player props from all events
    all_players = {}
    for event in events:
        players = parse_player_props(event)
        all_players.update(players)

    if not all_players:
        print("❌ No player props found in the events")
        return

    print(f"✓ Parsed props for {len(all_players)} players")

    # Calculate projections for all formats
    print("📊 Calculating projections...")
    all_projections = []
    formats = get_available_formats()

    for player_name, player_data in all_players.items():
        # Detect position
        position = detect_position(player_data)

        # Extract game info
        game_info = player_data.get("game_info", {})
        home_team = game_info.get("home_team", "")
        away_team = game_info.get("away_team", "")
        commence_time = game_info.get("commence_time", "")

        # Determine matchup
        matchup = f"{away_team} @ {home_team}" if home_team and away_team else "TBD"
        week = calculate_nfl_week(commence_time)

        for format_name in formats:
            calculator = ProjectionCalculator(format_name)
            projection = calculator.calculate_projection(player_data)

            # Add position and game info
            projection['position'] = position
            projection['matchup'] = matchup
            projection['week'] = week
            projection['game_time'] = commence_time

            all_projections.append(projection)

    # Sort by total points
    all_projections.sort(key=lambda x: x['total_points'], reverse=True)

    # Create cache data
    cache_data = {
        'projections': all_projections,
        'total_players': len(all_players),
        'formats': formats,
        'last_updated': datetime.now().isoformat(),
        'last_updated_display': datetime.now().strftime('%B %d, %Y at %I:%M %p')
    }

    # Save to cache file
    cache_file = 'data/projections_cache.json'
    with open(cache_file, 'w') as f:
        json.dump(cache_data, f, indent=2)

    print(f"✅ Successfully cached {len(all_projections)} projections")
    print(f"📁 Saved to: {cache_file}")
    print(f"🕐 Last updated: {cache_data['last_updated_display']}")


if __name__ == "__main__":
    try:
        update_projections()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
