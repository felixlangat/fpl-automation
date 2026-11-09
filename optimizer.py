"""
FPL Analytical Solver & Optimization Engine.
Determines:
- Optimal Starting XI maximizing expected points under valid FPL formation constraints.
- Bench ordering safeguarding against injuries and formation violations.
- Captain and Vice-Captain picks based on expected ceiling, FDR, and guaranteed fitness.
- Recommended single free transfer when an active player is red-flagged or injured.
"""

from typing import List, Dict, Optional, Tuple
import logging

from config import (
    FDR_MULTIPLIERS, STATUS_FACTORS,
    MIN_KEEPERS, MAX_KEEPERS,
    MIN_DEFENDERS, MAX_DEFENDERS,
    MIN_MIDFIELDERS, MAX_MIDFIELDERS,
    MIN_FORWARDS, MAX_FORWARDS,
    STARTERS_COUNT, MAX_PLAYERS_PER_TEAM
)
from models import Player, Pick, TeamSquad, OptimizationResult, TransferRecommendation

logger = logging.getLogger(__name__)

# Valid FPL Outfield Formations (DEF, MID, FWD) summing to 10
VALID_FORMATIONS = [
    (3, 5, 2),
    (3, 4, 3),
    (4, 4, 2),
    (4, 3, 3),
    (4, 5, 1),
    (5, 3, 2),
    (5, 4, 1),
    (5, 2, 3),
]


class FPLOptimizer:
    """Analytical squad optimizer for Fantasy Premier League."""

    def __init__(self, squad: TeamSquad, all_players: Optional[Dict[int, Player]] = None):
        self.squad = squad
        self.all_players = all_players or {}
        self._calculate_expected_values()

    def _calculate_player_ev(self, player: Player) -> float:
        """
        Calculate expected value (EV) for a single player for the upcoming Gameweek.
        Blends official expected points (ep_next), recent form, points per game,
        fixture difficulty rating (FDR), home advantage, and fitness status.
        """
        # Red-flagged players get 0 EV
        if player.is_red_flagged:
            return 0.0

        # Base scoring potential
        if player.ep_next > 0:
            base = 0.55 * player.ep_next + 0.35 * player.form + 0.10 * player.points_per_game
        elif player.form > 0:
            base = 0.70 * player.form + 0.30 * player.points_per_game
        else:
            base = player.points_per_game if player.points_per_game > 0 else 2.0

        # Fixture Difficulty Multiplier (FDR 1 to 5)
        fdr_mult = FDR_MULTIPLIERS.get(player.fdr, 1.0)

        # Home venue advantage (+5% for home games)
        home_mult = 1.05 if player.next_is_home else 0.95

        # Fitness / Chance of playing multiplier
        fitness_mult = 1.0
        if player.is_doubtful:
            if player.chance_of_playing_next_round is not None:
                fitness_mult = max(0.25, player.chance_of_playing_next_round / 100.0)
            else:
                fitness_mult = STATUS_FACTORS.get(player.status, 0.5)
        elif player.status != "a":
            fitness_mult = STATUS_FACTORS.get(player.status, 0.8)

        ev = round(base * fdr_mult * home_mult * fitness_mult, 2)
        return max(0.0, ev)

    def _calculate_expected_values(self):
        """Compute and store expected values for all squad players."""
        for pick in self.squad.picks:
            if pick.player:
                pick.player.expected_value = self._calculate_player_ev(pick.player)

    def optimize_lineup(self) -> OptimizationResult:
        """
        Solves for the optimal Starting 11, bench ordering, and captaincy.
        """
        # Separate squad players by position
        gks: List[Player] = []
        defs: List[Player] = []
        mids: List[Player] = []
        fwds: List[Player] = []

        red_flags: List[Player] = []
        doubtfuls: List[Player] = []

        for pick in self.squad.picks:
            p = pick.player
            if not p:
                continue

            if p.is_red_flagged:
                red_flags.append(p)
            elif p.is_doubtful:
                doubtfuls.append(p)

            if p.element_type == 1:
                gks.append(p)
            elif p.element_type == 2:
                defs.append(p)
            elif p.element_type == 3:
                mids.append(p)
            elif p.element_type == 4:
                fwds.append(p)

        # Sort each position group by EV descending
        gks.sort(key=lambda p: (p.expected_value, -p.fdr, p.form), reverse=True)
        defs.sort(key=lambda p: (p.expected_value, -p.fdr, p.form), reverse=True)
        mids.sort(key=lambda p: (p.expected_value, -p.fdr, p.form), reverse=True)
        fwds.sort(key=lambda p: (p.expected_value, -p.fdr, p.form), reverse=True)

        best_gk = gks[0]
        bench_gk = gks[1] if len(gks) > 1 else None

        # Evaluate all valid outfield formations to find the globally optimal Starting 11
        best_formation_name = ""
        best_starters: List[Player] = []
        best_bench_outfield: List[Player] = []
        max_ev = -1.0

        for n_def, n_mid, n_fwd in VALID_FORMATIONS:
            if len(defs) < n_def or len(mids) < n_mid or len(fwds) < n_fwd:
                continue

            starters_def = defs[:n_def]
            starters_mid = mids[:n_mid]
            starters_fwd = fwds[:n_fwd]

            bench_def = defs[n_def:]
            bench_mid = mids[n_mid:]
            bench_fwd = fwds[n_fwd:]

            current_starters = [best_gk] + starters_def + starters_mid + starters_fwd
            formation_ev = sum(p.expected_value for p in current_starters)

            if formation_ev > max_ev:
                max_ev = formation_ev
                best_formation_name = f"{n_def}-{n_mid}-{n_fwd}"
                best_starters = current_starters
                best_bench_outfield = bench_def + bench_mid + bench_fwd

        # Fallback if no exact standard formation matched (e.g. non-standard squad composition)
        if not best_formation_name or not best_starters:
            logger.info("Applying adaptive formation assembly for squad distribution.")
            best_gk = gks[0] if gks else Player(id=0, web_name="Goalkeeper", first_name="", second_name="", element_type=1, team_id=1)
            bench_gk = gks[1] if len(gks) > 1 else None

            # Select available outfield players up to 10
            all_outfield = defs + mids + fwds
            all_outfield.sort(key=lambda p: (p.expected_value, -p.fdr), reverse=True)
            best_starters = [best_gk] + all_outfield[:10]
            best_bench_outfield = all_outfield[10:]

            cnt_def = sum(1 for p in best_starters if p.element_type == 2)
            cnt_mid = sum(1 for p in best_starters if p.element_type == 3)
            cnt_fwd = sum(1 for p in best_starters if p.element_type == 4)
            best_formation_name = f"{cnt_def}-{cnt_mid}-{cnt_fwd}"
            max_ev = sum(p.expected_value for p in best_starters)

        # Bench Ordering Strategy:
        # Bench Slot 1 (pos 12 in squad picks) is ALWAYS the backup Goalkeeper.
        # Bench Slots 2, 3, 4 (pos 13, 14, 15) are outfield substitutes.
        # Safeguard Rule:
        # If any starting defender is doubtful and the formation uses the minimum 3 defenders,
        # a defender MUST be prioritized as first outfield sub to preserve legal formation!
        ordered_outfield_bench = self._order_bench(best_bench_outfield, best_formation_name, best_starters)

        final_bench = [bench_gk] + ordered_outfield_bench

        # Captain & Vice-Captain Selection
        captain, vice_captain = self._select_captain_and_vice(best_starters)

        # Captain doubles points in total EV calculation
        total_ev_with_captain = max_ev + captain.expected_value

        # Check for free transfer if an active player is red-flagged
        recommended_transfer = None
        if red_flags and self.all_players:
            # Transfer out the highest cost or most impactful red-flagged player
            player_to_replace = sorted(red_flags, key=lambda p: (p.now_cost, p.total_points), reverse=True)[0]
            recommended_transfer = self._find_best_transfer(player_to_replace)

        return OptimizationResult(
            gameweek=self.squad.gameweek,
            formation=best_formation_name,
            starting_11=best_starters,
            bench=final_bench,
            captain=captain,
            vice_captain=vice_captain,
            total_expected_points=round(total_ev_with_captain, 2),
            red_flagged_players=red_flags,
            doubtful_players=doubtfuls,
            recommended_transfer=recommended_transfer
        )

    def _order_bench(
        self,
        bench_outfield: List[Player],
        formation_name: str,
        starters: List[Player]
    ) -> List[Player]:
        """
        Orders outfield bench (positions 13, 14, 15) to maximize expected output
        while safeguarding against formation invalidation.
        """
        bench = list(bench_outfield)
        if not formation_name or "-" not in formation_name:
            formation_name = "4-4-2"
        n_def = int(formation_name.split("-")[0])

        # If starting formation has exactly 3 defenders, any missing defender forces
        # a defender sub. Check if any starting defender is doubtful.
        starter_defs = [p for p in starters if p.element_type == 2]
        has_risky_def = any(p.is_doubtful or p.is_red_flagged for p in starter_defs)

        bench_defs = [p for p in bench if p.element_type == 2]
        other_bench = [p for p in bench if p.element_type != 2]

        if n_def == 3 and has_risky_def and bench_defs:
            # Place top bench defender as first outfield sub to safeguard legal formation
            bench_defs.sort(key=lambda p: (p.expected_value, -p.fdr), reverse=True)
            safeguard_def = bench_defs[0]
            remaining = [p for p in bench if p.id != safeguard_def.id]
            remaining.sort(key=lambda p: (p.expected_value, -p.fdr), reverse=True)
            return [safeguard_def] + remaining

        # Otherwise rank strictly by expected value and fixture ease
        bench.sort(key=lambda p: (p.expected_value, -p.fdr, p.form), reverse=True)
        return bench

    def _select_captain_and_vice(self, starters: List[Player]) -> Tuple[Player, Player]:
        """
        Selects Captain (highest upside/EV with easiest fixture) and Vice-Captain
        (guaranteed 100% fit with second-highest EV).
        """
        if not starters:
            dummy = Player(id=0, web_name="Player", first_name="", second_name="", element_type=1, team_id=1)
            return dummy, dummy

        # Sort starters by EV descending, secondary by fixture ease (lowest FDR)
        sorted_starters = sorted(starters, key=lambda p: (p.expected_value, -p.fdr, p.form), reverse=True)

        captain = sorted_starters[0]
        if len(sorted_starters) == 1:
            return captain, captain

        # Vice-captain must be 100% fit and cannot be the captain
        fit_candidates = [
            p for p in sorted_starters
            if p.id != captain.id and not p.is_red_flagged and not p.is_doubtful and p.status == "a"
        ]

        if fit_candidates:
            # Prefer a vice-captain from a different team/match to mitigate postponement/corrupted fixtures
            diff_team_candidates = [p for p in fit_candidates if p.team_id != captain.team_id]
            vice_captain = diff_team_candidates[0] if diff_team_candidates else fit_candidates[0]
        else:
            vice_captain = sorted_starters[1]

        return captain, vice_captain

    def _find_best_transfer(self, player_out: Player) -> Optional[TransferRecommendation]:
        """
        Finds the single best free transfer replacement for an injured/red-flagged player.
        Adheres to budget (selling_price + bank) and club limits (<= 3 per team).
        """
        max_budget = round(player_out.selling_price + self.squad.bank, 1)

        # Count existing players by team in squad (excluding player_out)
        team_counts: Dict[int, int] = {}
        for pick in self.squad.picks:
            if pick.player and pick.player.id != player_out.id:
                tid = pick.player.team_id
                team_counts[tid] = team_counts.get(tid, 0) + 1

        existing_ids = {pick.player.id for pick in self.squad.picks if pick.player}

        candidates: List[Player] = []
        for p in self.all_players.values():
            # Same position
            if p.element_type != player_out.element_type:
                continue
            # Not already in squad
            if p.id in existing_ids:
                continue
            # Budget constraint
            if p.now_cost > max_budget:
                continue
            # Team quota constraint
            if team_counts.get(p.team_id, 0) >= MAX_PLAYERS_PER_TEAM:
                continue
            # Must be fit (no red or yellow flag)
            if p.is_red_flagged or p.is_doubtful or p.status != "a":
                continue

            # Calculate candidate EV
            p.expected_value = self._calculate_player_ev(p)
            candidates.append(p)

        if not candidates:
            return None

        # Sort candidates by expected value, then form, then FDR
        candidates.sort(key=lambda p: (p.expected_value, p.form, -p.fdr, p.total_points), reverse=True)
        best_in = candidates[0]

        cost_diff = round(best_in.now_cost - player_out.selling_price, 1)
        ev_gain = round(best_in.expected_value - player_out.expected_value, 2)

        reasoning = (
            f"Replace injured {player_out.web_name} ({player_out.fitness_label}) with "
            f"{best_in.web_name} ({best_in.team_short_name}). "
            f"Cost: £{best_in.now_cost:.1f}m (Budget: £{max_budget:.1f}m). "
            f"Form: {best_in.form}, Next: {best_in.next_opponent_short_name} "
            f"({'H' if best_in.next_is_home else 'A'}, FDR {best_in.fdr}). "
            f"Projected point increase: +{ev_gain:.1f} pts."
        )

        return TransferRecommendation(
            player_out=player_out,
            player_in=best_in,
            cost_diff=cost_diff,
            expected_point_gain=ev_gain,
            reasoning=reasoning
        )
