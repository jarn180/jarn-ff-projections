"""Start/Sit Optimizer for Fantasy Football lineup decisions."""

from typing import Dict, List, Any, Tuple, Optional
import json
import os


class StartSitOptimizer:
    """Optimizes fantasy football lineup decisions based on projections."""

    # Standard Sleeper roster positions
    ROSTER_POSITIONS = {
        'QB': 1,
        'RB': 2,
        'WR': 2,
        'TE': 1,
        'FLEX': 1,  # RB/WR/TE
        'K': 1,
        'DEF': 1,
        'BN': 6  # Bench
    }

    FLEX_POSITIONS = ['RB', 'WR', 'TE']

    def __init__(self):
        """Initialize optimizer."""
        self.projections_cache = self._load_projections()
        self.sleeper_players = {}

    def _load_projections(self) -> Dict[str, Any]:
        """Load projections from cache file.

        Returns:
            Dict of cached projections
        """
        cache_file = 'data/projections_cache.json'
        if os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                return json.load(f)
        return {'projections': [], 'total_players': 0}

    def map_sleeper_to_projections(self, sleeper_player_id: str, sleeper_player: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Map Sleeper player to our projection data.

        Args:
            sleeper_player_id: Sleeper player ID
            sleeper_player: Sleeper player data

        Returns:
            Projection data or None if not found
        """
        full_name = sleeper_player.get('full_name', '').lower()
        position = sleeper_player.get('position', '')

        # Try to find matching projection
        for proj in self.projections_cache.get('projections', []):
            proj_name = proj.get('player_name', '').lower()
            proj_position = proj.get('position', '')

            # Exact match
            if proj_name == full_name and proj_position == position:
                return proj

            # Partial match (handles name variations)
            if full_name in proj_name or proj_name in full_name:
                if proj_position == position:
                    return proj

        return None

    def get_player_projection(self, player_name: str, position: str, scoring_format: str = 'PPR') -> float:
        """Get projected points for a player.

        Args:
            player_name: Player's full name
            position: Player position (QB, RB, WR, TE)
            scoring_format: Scoring format (PPR, HALF_PPR, STANDARD)

        Returns:
            Projected points (0 if not found)
        """
        player_name_lower = player_name.lower()

        for proj in self.projections_cache.get('projections', []):
            proj_name = proj.get('player_name', '').lower()
            proj_position = proj.get('position', '')

            if proj_position == position:
                if proj_name == player_name_lower or player_name_lower in proj_name or proj_name in player_name_lower:
                    # Get scoring for format
                    scoring = proj.get('scoring', {})
                    return scoring.get(scoring_format, 0)

        return 0

    def optimize_lineup(
        self,
        roster_players: List[Dict[str, Any]],
        sleeper_players_db: Dict[str, Any],
        scoring_format: str = 'PPR',
        roster_config: Optional[Dict[str, int]] = None
    ) -> Dict[str, Any]:
        """Optimize lineup to maximize projected points.

        Args:
            roster_players: List of player IDs on roster
            sleeper_players_db: Sleeper player database
            scoring_format: Scoring format to use
            roster_config: Custom roster configuration (optional)

        Returns:
            Dict with optimized starters, bench, and analysis
        """
        if roster_config is None:
            roster_config = self.ROSTER_POSITIONS.copy()

        # Get player projections
        player_projections = []
        for player_id in roster_players:
            if not player_id:
                continue

            player_data = sleeper_players_db.get(player_id, {})
            full_name = player_data.get('full_name', 'Unknown')
            position = player_data.get('position', '')
            injury_status = player_data.get('injury_status', '')

            # Skip DEF and K for now (no projections)
            if position in ['DEF', 'K']:
                player_projections.append({
                    'player_id': player_id,
                    'name': full_name,
                    'position': position,
                    'projection': 0,
                    'injury_status': injury_status
                })
                continue

            projection = self.get_player_projection(full_name, position, scoring_format)

            player_projections.append({
                'player_id': player_id,
                'name': full_name,
                'position': position,
                'projection': projection,
                'injury_status': injury_status
            })

        # Sort by projection (highest first)
        player_projections.sort(key=lambda x: x['projection'], reverse=True)

        # Build optimal lineup
        starters = {
            'QB': [],
            'RB': [],
            'WR': [],
            'TE': [],
            'FLEX': [],
            'K': [],
            'DEF': []
        }
        bench = []
        used_players = set()

        # Fill primary positions first
        for position in ['QB', 'RB', 'WR', 'TE', 'K', 'DEF']:
            max_starters = roster_config.get(position, 0)
            position_players = [p for p in player_projections if p['position'] == position and p['player_id'] not in used_players]

            for i, player in enumerate(position_players):
                if i < max_starters:
                    starters[position].append(player)
                    used_players.add(player['player_id'])

        # Fill FLEX with best remaining RB/WR/TE
        flex_count = roster_config.get('FLEX', 0)
        flex_eligible = [p for p in player_projections if p['position'] in self.FLEX_POSITIONS and p['player_id'] not in used_players]

        for i, player in enumerate(flex_eligible):
            if i < flex_count:
                starters['FLEX'].append(player)
                used_players.add(player['player_id'])

        # Remaining players go to bench
        bench = [p for p in player_projections if p['player_id'] not in used_players]

        # Calculate total projected points
        total_projection = sum(
            sum(p['projection'] for p in players)
            for players in starters.values()
        )

        # Find start/sit recommendations
        recommendations = self._generate_recommendations(starters, bench)

        return {
            'starters': starters,
            'bench': bench,
            'total_projection': round(total_projection, 2),
            'scoring_format': scoring_format,
            'recommendations': recommendations
        }

    def _generate_recommendations(self, starters: Dict[str, List], bench: List[Dict]) -> List[Dict[str, Any]]:
        """Generate start/sit swap recommendations.

        Args:
            starters: Current starting lineup
            bench: Current bench players

        Returns:
            List of recommended swaps
        """
        recommendations = []

        # Check each bench player against starters in their position
        for bench_player in bench:
            position = bench_player['position']
            bench_proj = bench_player['projection']

            # Check primary position
            if position in starters and starters[position]:
                for starter in starters[position]:
                    if bench_proj > starter['projection']:
                        gain = bench_proj - starter['projection']
                        recommendations.append({
                            'action': 'swap',
                            'bench_player': bench_player['name'],
                            'bench_projection': bench_proj,
                            'starter_player': starter['name'],
                            'starter_projection': starter['projection'],
                            'position': position,
                            'projected_gain': round(gain, 2)
                        })

            # Check FLEX if eligible
            if position in self.FLEX_POSITIONS and 'FLEX' in starters and starters['FLEX']:
                for flex_starter in starters['FLEX']:
                    if bench_proj > flex_starter['projection']:
                        gain = bench_proj - flex_starter['projection']
                        recommendations.append({
                            'action': 'swap',
                            'bench_player': bench_player['name'],
                            'bench_projection': bench_proj,
                            'starter_player': flex_starter['name'],
                            'starter_projection': flex_starter['projection'],
                            'position': 'FLEX',
                            'projected_gain': round(gain, 2)
                        })

        # Sort by projected gain
        recommendations.sort(key=lambda x: x['projected_gain'], reverse=True)

        return recommendations[:5]  # Return top 5 recommendations
