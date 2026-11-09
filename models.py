"""
Data models representing FPL entities, squad selections, and optimization results.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class Player:
    id: int
    web_name: str
    first_name: str
    second_name: str
    element_type: int  # 1: GKP, 2: DEF, 3: MID, 4: FWD
    team_id: int
    team_short_name: str = ""
    team_name: str = ""
    now_cost: float = 0.0  # in millions, e.g. 10.5
    selling_price: float = 0.0
    status: str = "a"  # 'a', 'd', 'i', 's', 'u'
    chance_of_playing_this_round: Optional[int] = 100
    chance_of_playing_next_round: Optional[int] = 100
    news: str = ""
    form: float = 0.0
    points_per_game: float = 0.0
    total_points: int = 0
    ep_next: float = 0.0  # Expected points from FPL API
    ep_this: float = 0.0
    selected_by_percent: float = 0.0
    next_opponent_id: Optional[int] = None
    next_opponent_short_name: str = ""
    next_is_home: bool = True
    fdr: int = 3  # Fixture Difficulty Rating 1-5
    expected_value: float = 0.0  # Computed by optimizer

    @property
    def position_name(self) -> str:
        names = {1: "GKP", 2: "DEF", 3: "MID", 4: "FWD"}
        return names.get(self.element_type, "UNKNOWN")

    @property
    def is_red_flagged(self) -> bool:
        """True if the player is injured, suspended, unavailable or 0% chance."""
        if self.status in ("i", "s", "u", "n"):
            return True
        if self.chance_of_playing_next_round is not None and self.chance_of_playing_next_round == 0:
            return True
        return False

    @property
    def is_doubtful(self) -> bool:
        """True if the player has a yellow flag (25% - 75% chance)."""
        if self.status == "d":
            return True
        if self.chance_of_playing_next_round is not None and 0 < self.chance_of_playing_next_round < 100:
            return True
        return False

    @property
    def fitness_label(self) -> str:
        if self.is_red_flagged:
            return f"RED FLAG: {self.news or 'Unavailable'}"
        if self.is_doubtful:
            chance = self.chance_of_playing_next_round or 50
            return f"DOUBTFUL ({chance}%): {self.news or 'Knock/Doubt'}"
        return "FIT"


@dataclass
class Pick:
    element: int  # Player ID
    position: int  # 1-15 (1-11 starter, 12 bench GK, 13-15 bench outfield)
    multiplier: int  # 1 for starter, 2 for captain, 3 for triple captain, 0 for bench
    is_captain: bool
    is_vice_captain: bool
    player: Optional[Player] = None


@dataclass
class TeamSquad:
    team_id: int
    gameweek: int
    picks: List[Pick]
    bank: float = 0.0  # in millions
    team_value: float = 0.0  # in millions
    free_transfers: int = 1


@dataclass
class TransferRecommendation:
    player_out: Player
    player_in: Player
    cost_diff: float
    expected_point_gain: float
    reasoning: str


@dataclass
class OptimizationResult:
    gameweek: int
    formation: str
    starting_11: List[Player]
    bench: List[Player]  # 4 players: [0]=Sub GK, [1]=1st Sub, [2]=2nd Sub, [3]=3rd Sub
    captain: Player
    vice_captain: Player
    total_expected_points: float
    red_flagged_players: List[Player] = field(default_factory=list)
    doubtful_players: List[Player] = field(default_factory=list)
    recommended_transfer: Optional[TransferRecommendation] = None
    substitutions_made: List[Dict[str, Any]] = field(default_factory=list)
