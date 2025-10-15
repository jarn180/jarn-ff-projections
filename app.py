#!/usr/bin/env python3
"""
Fantasy Football Projections Web App
Flask application for viewing Vegas-based projections
"""

from flask import Flask, render_template, jsonify, request
from src.api.odds_api import OddsAPIClient, parse_player_props, detect_position
from src.api.sleeper_api import SleeperAPIClient
from src.projections.calculator import ProjectionCalculator
from src.optimizer.start_sit import StartSitOptimizer
from src.notifications.sms_service import TextbeltSMSService, SMSSubscriberManager
from config.scoring_formats import get_available_formats
from datetime import datetime
import traceback
import re

app = Flask(__name__)
sleeper_client = SleeperAPIClient()
optimizer = StartSitOptimizer()
sms_service = TextbeltSMSService()
subscriber_manager = SMSSubscriberManager()


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


@app.route('/optimizer')
def optimizer_page():
    """Optimizer page."""
    return render_template('optimizer.html')


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


# Sleeper Integration Routes

@app.route('/api/sleeper/user/<username>', methods=['GET'])
def get_sleeper_user(username):
    """Get Sleeper user by username."""
    try:
        user = sleeper_client.get_user(username)
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404

        return jsonify({
            'success': True,
            'user': user
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/sleeper/user/<user_id>/leagues', methods=['GET'])
def get_sleeper_leagues(user_id):
    """Get user's leagues."""
    try:
        season = request.args.get('season', '2024')
        leagues = sleeper_client.get_user_leagues(user_id, season)

        return jsonify({
            'success': True,
            'leagues': leagues,
            'count': len(leagues)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/sleeper/league/<league_id>', methods=['GET'])
def get_sleeper_league(league_id):
    """Get league details."""
    try:
        league = sleeper_client.get_league(league_id)
        if not league:
            return jsonify({
                'success': False,
                'error': 'League not found'
            }), 404

        return jsonify({
            'success': True,
            'league': league
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/sleeper/league/<league_id>/roster/<user_id>', methods=['GET'])
def get_sleeper_roster(league_id, user_id):
    """Get user's roster in a league."""
    try:
        roster = sleeper_client.get_user_roster(league_id, user_id)
        if not roster:
            return jsonify({
                'success': False,
                'error': 'Roster not found'
            }), 404

        # Get player data
        players_db = sleeper_client.get_all_players()

        # Enrich roster with player names
        enriched_players = []
        for player_id in roster.get('players', []):
            player_data = players_db.get(player_id, {})
            enriched_players.append({
                'player_id': player_id,
                'name': player_data.get('full_name', 'Unknown'),
                'position': player_data.get('position', ''),
                'team': player_data.get('team', ''),
                'injury_status': player_data.get('injury_status', '')
            })

        return jsonify({
            'success': True,
            'roster': {
                **roster,
                'enriched_players': enriched_players
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/sleeper/optimize', methods=['POST'])
def optimize_lineup():
    """Optimize lineup for maximum projected points."""
    try:
        data = request.get_json()
        league_id = data.get('league_id')
        user_id = data.get('user_id')
        scoring_format = data.get('scoring_format', 'PPR')

        if not league_id or not user_id:
            return jsonify({
                'success': False,
                'error': 'league_id and user_id are required'
            }), 400

        # Get roster
        roster = sleeper_client.get_user_roster(league_id, user_id)
        if not roster:
            return jsonify({
                'success': False,
                'error': 'Roster not found'
            }), 404

        # Get all players database
        players_db = sleeper_client.get_all_players()

        # Get league settings for roster configuration
        league = sleeper_client.get_league(league_id)
        roster_positions = league.get('roster_positions', []) if league else None

        # Convert roster_positions list to dict if available
        roster_config = None
        if roster_positions:
            roster_config = {}
            for pos in roster_positions:
                roster_config[pos] = roster_config.get(pos, 0) + 1

        # Optimize lineup
        result = optimizer.optimize_lineup(
            roster.get('players', []),
            players_db,
            scoring_format,
            roster_config
        )

        return jsonify({
            'success': True,
            'optimization': result
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# SMS Notification Routes

@app.route('/api/sms/subscribe', methods=['POST'])
def sms_subscribe():
    """Subscribe a phone number to SMS notifications."""
    try:
        data = request.get_json()
        phone = data.get('phone')
        region = data.get('region', 'us')

        if not phone:
            return jsonify({
                'success': False,
                'error': 'Phone number is required'
            }), 400

        # Validate phone number format (basic validation)
        phone_clean = re.sub(r'\D', '', phone)
        if len(phone_clean) < 10:
            return jsonify({
                'success': False,
                'error': 'Invalid phone number format'
            }), 400

        # Add subscriber
        added = subscriber_manager.add_subscriber(phone_clean, region)

        if not added:
            return jsonify({
                'success': False,
                'error': 'Phone number already subscribed'
            }), 400

        # Send confirmation SMS
        message = "Welcome to Fantasy Football Projections! You'll receive updates when new projections are added. Reply STOP to unsubscribe."
        result = sms_service.send_sms(phone_clean, message, region)

        if result.get('success'):
            return jsonify({
                'success': True,
                'message': 'Successfully subscribed! Check your phone for confirmation.',
                'subscriber_count': subscriber_manager.get_subscriber_count()
            })
        else:
            # Remove subscriber if SMS failed
            subscriber_manager.remove_subscriber(phone_clean)
            return jsonify({
                'success': False,
                'error': f"Failed to send confirmation SMS: {result.get('error', 'Unknown error')}"
            }), 500

    except Exception as e:
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/sms/unsubscribe', methods=['POST'])
def sms_unsubscribe():
    """Unsubscribe a phone number from SMS notifications."""
    try:
        data = request.get_json()
        phone = data.get('phone')

        if not phone:
            return jsonify({
                'success': False,
                'error': 'Phone number is required'
            }), 400

        # Clean phone number
        phone_clean = re.sub(r'\D', '', phone)

        # Remove subscriber
        removed = subscriber_manager.remove_subscriber(phone_clean)

        if removed:
            return jsonify({
                'success': True,
                'message': 'Successfully unsubscribed from SMS notifications',
                'subscriber_count': subscriber_manager.get_subscriber_count()
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Phone number not found in subscribers'
            }), 404

    except Exception as e:
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/sms/status', methods=['GET'])
def sms_status():
    """Get SMS notification system status."""
    try:
        subscriber_count = subscriber_manager.get_subscriber_count()
        quota = sms_service.check_quota()

        return jsonify({
            'success': True,
            'subscriber_count': subscriber_count,
            'quota_remaining': quota,
            'is_free_tier': sms_service.is_free_tier
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/sms/test', methods=['POST'])
def sms_test():
    """Test SMS sending (admin only - requires authentication in production)."""
    try:
        data = request.get_json()
        phone = data.get('phone')

        if not phone:
            return jsonify({
                'success': False,
                'error': 'Phone number is required'
            }), 400

        phone_clean = re.sub(r'\D', '', phone)
        message = "Test message from Fantasy Football Projections SMS system"

        result = sms_service.send_sms(phone_clean, message)

        return jsonify({
            'success': result.get('success', False),
            'message': 'Test SMS sent' if result.get('success') else 'Failed to send test SMS',
            'details': result
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
