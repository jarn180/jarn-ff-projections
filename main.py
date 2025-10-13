#!/usr/bin/env python3
"""
Fantasy Football Projections CLI
Main entry point for generating projections from Vegas props
"""

import argparse
import json
import sys
from typing import List
from tabulate import tabulate

from src.api.odds_api import OddsAPIClient, parse_player_props
from src.projections.calculator import ProjectionCalculator
from config.scoring_formats import get_available_formats


def format_projections_table(projections: List[dict]) -> str:
    """Format projections as a table for display.

    Args:
        projections: List of projection dictionaries

    Returns:
        Formatted table string
    """
    if not projections:
        return "No projections available."

    # Group by player
    players = {}
    for proj in projections:
        player = proj["player"]
        if player not in players:
            players[player] = {}
        players[player][proj["format"]] = proj["total_points"]

    # Create table
    headers = ["Player"] + sorted(set(proj["format"] for proj in projections))
    rows = []

    for player, formats in sorted(players.items()):
        row = [player]
        for format_name in headers[1:]:
            points = formats.get(format_name, 0.0)
            row.append(f"{points:.2f}")
        rows.append(row)

    return tabulate(rows, headers=headers, tablefmt="grid")


def format_detailed_projection(projection: dict) -> str:
    """Format a detailed projection breakdown.

    Args:
        projection: Projection dictionary

    Returns:
        Formatted string with breakdown
    """
    output = []
    output.append(f"\n{'='*60}")
    output.append(f"Player: {projection['player']}")
    output.append(f"Format: {projection['format']}")
    output.append(f"Total Points: {projection['total_points']:.2f}")
    output.append(f"{'-'*60}")

    output.append("\nPoints Breakdown:")
    for category, points in projection["breakdown"].items():
        if points != 0:
            output.append(f"  {category.capitalize()}: {points:.2f}")

    if projection.get("stats"):
        output.append("\nProjected Stats:")
        for stat, value in projection["stats"].items():
            stat_display = stat.replace("player_", "").replace("_", " ").title()
            output.append(f"  {stat_display}: {value:.2f}")

    output.append(f"{'='*60}\n")

    return "\n".join(output)


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="Generate fantasy football projections from Vegas props",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Get projections for all players in all formats
  python main.py

  # Get projections for specific format
  python main.py --format PPR

  # Get detailed breakdown
  python main.py --detailed

  # Specify specific markets to fetch
  python main.py --markets player_pass_yds player_pass_tds

  # Export to JSON
  python main.py --output projections.json
        """
    )

    parser.add_argument(
        "--format",
        "-f",
        choices=get_available_formats(),
        help="Scoring format (default: all formats)",
    )

    parser.add_argument(
        "--detailed",
        "-d",
        action="store_true",
        help="Show detailed breakdown for each projection",
    )

    parser.add_argument(
        "--markets",
        "-m",
        nargs="+",
        help="Specific prop markets to fetch (default: all)",
    )

    parser.add_argument(
        "--sport",
        "-s",
        default="americanfootball_nfl",
        help="Sport key (default: americanfootball_nfl)",
    )

    parser.add_argument(
        "--output",
        "-o",
        help="Output file path (JSON format)",
    )

    parser.add_argument(
        "--api-key",
        help="The Odds API key (overrides ODDS_API_KEY env var)",
    )

    args = parser.parse_args()

    try:
        # Initialize API client
        print("Initializing API client...")
        client = OddsAPIClient(api_key=args.api_key)

        # Fetch player props
        print(f"Fetching player props for {args.sport}...")
        if args.markets:
            print(f"Markets: {', '.join(args.markets)}")

        events = client.get_player_props(
            sport=args.sport,
            markets=args.markets
        )

        if not events:
            print("No events found. The season may not have started or there are no available props.")
            return

        print(f"Found {len(events)} events with player props.")

        # Parse player props from all events
        all_players = {}
        for event in events:
            players = parse_player_props(event)
            all_players.update(players)

        if not all_players:
            print("No player props found in the events.")
            return

        print(f"Parsed props for {len(all_players)} players.")

        # Calculate projections
        print("\nCalculating projections...")
        all_projections = []

        formats = [args.format] if args.format else get_available_formats()

        for player_name, player_data in all_players.items():
            for format_name in formats:
                calculator = ProjectionCalculator(format_name)
                projection = calculator.calculate_projection(player_data)
                all_projections.append(projection)

        # Sort by total points (descending) for first format
        all_projections.sort(key=lambda x: x["total_points"], reverse=True)

        # Output results
        if args.output:
            # Export to JSON
            with open(args.output, "w") as f:
                json.dump(all_projections, f, indent=2)
            print(f"\nProjections exported to {args.output}")
        else:
            # Display in terminal
            if args.detailed:
                for projection in all_projections:
                    print(format_detailed_projection(projection))
            else:
                print("\n" + format_projections_table(all_projections))

        print(f"\nTotal projections generated: {len(all_projections)}")

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
