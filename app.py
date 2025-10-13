#!/usr/bin/env python3
"""
Fantasy Football Projections Web App
Flask application for viewing Vegas-based projections
"""

from flask import Flask, render_template, jsonify, request
from src.api.odds_api import OddsAPIClient, parse_player_props, detect_position
from src.projections.calculator import ProjectionCalculator
from config.scoring_formats import get_available_formats
from datetime import datetime
import traceback

app = Flask(__name__)


def calculate_nfl_week(commence_time_str: str) -> str:
    """Calculate NFL week from game start time.

    Args:
        commence_time_str: ISO format timestamp

    Returns:
        Week string (e.g., "Week 10")
    """
    if not commence_time_str:
        return "TBD"

    try:
        game_time = datetime.fromisoformat(commence_time_str.replace('Z', '+00:00'))

        # NFL season typically starts first Thursday after Labor Day (early September)
        # This is a simplified calculation
        year = game_time.year

        # Approximate season start (adjust this for actual season)
        # For 2024-2025 season, Week 1 starts around September 5, 2024
        season_start = datetime(2024, 9, 5, tzinfo=game_time.tzinfo) if year == 2024 else datetime(year, 9, 7, tzinfo=game_time.tzinfo)

        # Calculate week number
        days_since_start = (game_time - season_start).days
        week_num = max(1, min(18, (days_since_start // 7) + 1))

        return f"Week {week_num}"
    except Exception:
        return "TBD"


@app.route('/')
def index():
    """Main page."""
    return render_template('index.html')


@app.route('/api/projections', methods=['GET'])
def get_projections():
    """API endpoint to fetch projections from cache.

    No API calls are made - data is read from cached file.
    Run update_projections.py to refresh the cache.
    """
    try:
        import json
        import os

        # Read from cache file
        cache_file = 'data/projections_cache.json'

        if not os.path.exists(cache_file):
            return jsonify({
                'success': False,
                'error': 'No cached data found. Please run: python update_projections.py'
            }), 404

        with open(cache_file, 'r') as f:
            cache_data = json.load(f)

        return jsonify({
            'success': True,
            'projections': cache_data['projections'],
            'total_players': cache_data['total_players'],
            'formats': cache_data['formats'],
            'last_updated': cache_data.get('last_updated_display', 'Unknown')
        })

    except Exception as e:
        print(f"Error reading cache: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Error loading cached data: {str(e)}'
        }), 500


@app.route('/api/formats', methods=['GET'])
def get_formats():
    """Get available scoring formats."""
    return jsonify({
        'success': True,
        'formats': get_available_formats()
    })


@app.route('/api/markets', methods=['GET'])
def get_markets():
    """Get available prop markets."""
    client = OddsAPIClient()
    markets = client.get_available_markets()
    return jsonify({
        'success': True,
        'markets': markets
    })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
