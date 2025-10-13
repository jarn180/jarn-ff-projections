"""API module for fetching player props."""

from .odds_api import OddsAPIClient, parse_player_props, detect_position

__all__ = ['OddsAPIClient', 'parse_player_props', 'detect_position']
