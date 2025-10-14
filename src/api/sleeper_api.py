"""Sleeper API Client for league integration and roster management."""

import requests
from typing import Dict, List, Optional, Any
from datetime import datetime


class SleeperAPIClient:
    """Client for interacting with Sleeper Fantasy API."""

    BASE_URL = "https://api.sleeper.app/v1"

    def __init__(self):
        """Initialize Sleeper API client."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Fantasy-Football-Projections/1.0'
        })

    def get_user(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user information by username.

        Args:
            username: Sleeper username

        Returns:
            User data dict or None if not found
        """
        try:
            response = self.session.get(f"{self.BASE_URL}/user/{username}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching user: {e}")
            return None

    def get_user_leagues(self, user_id: str, season: str = "2025", sport: str = "nfl") -> List[Dict[str, Any]]:
        """Get all leagues for a user in a given season.

        Args:
            user_id: Sleeper user ID
            season: Season year (default: 2025)
            sport: Sport type (default: nfl)

        Returns:
            List of league dicts
        """
        try:
            response = self.session.get(f"{self.BASE_URL}/user/{user_id}/leagues/{sport}/{season}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching leagues: {e}")
            return []

    def get_league(self, league_id: str) -> Optional[Dict[str, Any]]:
        """Get league information.

        Args:
            league_id: Sleeper league ID

        Returns:
            League data dict or None if not found
        """
        try:
            response = self.session.get(f"{self.BASE_URL}/league/{league_id}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching league: {e}")
            return None

    def get_league_rosters(self, league_id: str) -> List[Dict[str, Any]]:
        """Get all rosters in a league.

        Args:
            league_id: Sleeper league ID

        Returns:
            List of roster dicts
        """
        try:
            response = self.session.get(f"{self.BASE_URL}/league/{league_id}/rosters")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching rosters: {e}")
            return []

    def get_league_users(self, league_id: str) -> List[Dict[str, Any]]:
        """Get all users in a league.

        Args:
            league_id: Sleeper league ID

        Returns:
            List of user dicts
        """
        try:
            response = self.session.get(f"{self.BASE_URL}/league/{league_id}/users")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching league users: {e}")
            return []

    def get_matchups(self, league_id: str, week: int) -> List[Dict[str, Any]]:
        """Get matchups for a specific week.

        Args:
            league_id: Sleeper league ID
            week: Week number (1-18)

        Returns:
            List of matchup dicts
        """
        try:
            response = self.session.get(f"{self.BASE_URL}/league/{league_id}/matchups/{week}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching matchups: {e}")
            return []

    def get_all_players(self) -> Dict[str, Any]:
        """Get all NFL players from Sleeper.

        Returns:
            Dict mapping player_id to player data
        """
        try:
            response = self.session.get(f"{self.BASE_URL}/players/nfl")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching players: {e}")
            return {}

    def get_user_roster(self, league_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific user's roster in a league.

        Args:
            league_id: Sleeper league ID
            user_id: Sleeper user ID

        Returns:
            Roster dict or None if not found
        """
        rosters = self.get_league_rosters(league_id)
        for roster in rosters:
            if roster.get('owner_id') == user_id:
                return roster
        return None
