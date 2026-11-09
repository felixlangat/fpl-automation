"""
Unit and integration test suite for FPL Weekly Automation.
"""

import unittest
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from models import Player, Pick, TeamSquad
from fpl_client import FPLClient
from optimizer import FPLOptimizer, VALID_FORMATIONS
from browser_automation import FPLBrowserAutomation


class TestFPLPipeline(unittest.TestCase):

    def setUp(self):
        self.client = FPLClient()
        self.squad = self.client.get_squad()
        self.all_players, self.teams_dict = self.client.parse_all_players()
        self.optimizer = FPLOptimizer(self.squad, self.all_players)

    def test_squad_loading(self):
        """Verify squad picks are parsed into 15 valid players."""
        self.assertEqual(len(self.squad.picks), 15)
        self.assertGreater(self.squad.team_value, 80.0)
        self.assertGreaterEqual(self.squad.bank, 0.0)

        # Check positions: 2 GKP, 5 DEF, 5 MID, 3 FWD
        pos_counts = {}
        for pick in self.squad.picks:
            pos_counts[pick.player.element_type] = pos_counts.get(pick.player.element_type, 0) + 1

        self.assertEqual(pos_counts[1], 2, "Squad must have 2 Goalkeepers")
        self.assertEqual(pos_counts[2], 5, "Squad must have 5 Defenders")
        self.assertEqual(pos_counts[3], 5, "Squad must have 5 Midfielders")
        self.assertEqual(pos_counts[4], 3, "Squad must have 3 Forwards")

    def test_player_fitness_flags(self):
        """Verify red flags and doubtful statuses are correctly recognized."""
        injured_player = Player(
            id=999, web_name="InjuredGuy", first_name="A", second_name="B",
            element_type=4, team_id=1, status="i", chance_of_playing_next_round=0
        )
        self.assertTrue(injured_player.is_red_flagged)
        self.assertFalse(injured_player.is_doubtful)

        doubtful_player = Player(
            id=998, web_name="DoubtfulGuy", first_name="C", second_name="D",
            element_type=3, team_id=2, status="d", chance_of_playing_next_round=75
        )
        self.assertFalse(doubtful_player.is_red_flagged)
        self.assertTrue(doubtful_player.is_doubtful)

        fit_player = Player(
            id=997, web_name="FitGuy", first_name="E", second_name="F",
            element_type=2, team_id=3, status="a", chance_of_playing_next_round=100
        )
        self.assertFalse(fit_player.is_red_flagged)
        self.assertFalse(fit_player.is_doubtful)

    def test_lineup_optimization(self):
        """Verify optimization returns a valid Starting XI and formation."""
        result = self.optimizer.optimize_lineup()

        # Check Starting 11 length
        self.assertEqual(len(result.starting_11), 11)

        # Check formation validity
        formation_tuple = tuple(int(x) for x in result.formation.split("-"))
        self.assertIn(formation_tuple, VALID_FORMATIONS)
        self.assertEqual(sum(formation_tuple), 10)

        # Verify exactly 1 Goalkeeper in Starting XI
        gks = [p for p in result.starting_11 if p.element_type == 1]
        self.assertEqual(len(gks), 1)

        # Verify bench length and ordering
        self.assertEqual(len(result.bench), 4)
        self.assertEqual(result.bench[0].element_type, 1, "Slot 0 of bench must be the backup Goalkeeper")

        # Captain & Vice-Captain
        self.assertIsNotNone(result.captain)
        self.assertIsNotNone(result.vice_captain)
        self.assertNotEqual(result.captain.id, result.vice_captain.id)
        self.assertFalse(result.vice_captain.is_red_flagged, "Vice-Captain must be fully fit")

    def test_bench_injury_avoidance(self):
        """Verify red-flagged player is not started and placed last on the bench."""
        result = self.optimizer.optimize_lineup()

        red_flag_ids = {p.id for p in result.red_flagged_players}
        starter_ids = {p.id for p in result.starting_11}

        # Red flagged players should not be in Starting XI if healthy substitutes exist
        for r_id in red_flag_ids:
            self.assertNotIn(r_id, starter_ids)

        # Red flagged player should be placed at the bottom of the bench
        if red_flag_ids:
            last_sub = result.bench[-1]
            self.assertIn(last_sub.id, red_flag_ids)

    def test_transfer_recommendation_logic(self):
        """Verify transfer recommendation respects budget, position, and club limits."""
        result = self.optimizer.optimize_lineup()

        if result.red_flagged_players:
            self.assertIsNotNone(result.recommended_transfer)
            tx = result.recommended_transfer
            self.assertEqual(tx.player_out.element_type, tx.player_in.element_type, "Transfer must be same position")
            self.assertLessEqual(tx.player_in.now_cost, tx.player_out.selling_price + self.squad.bank)
            self.assertFalse(tx.player_in.is_red_flagged)
            self.assertGreater(tx.expected_point_gain, 0.0)

    def test_browser_automation_simulation(self):
        """Verify browser automation simulator produces valid picks payload."""
        result = self.optimizer.optimize_lineup()
        browser = FPLBrowserAutomation(dry_run=True)
        res = browser.execute(result)

        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(res["mode"], "SIMULATION_VERIFIED")
        picks = res["picks_payload"]
        self.assertEqual(len(picks), 15)

        # Verify positions 1-15 are populated
        positions = [p["position"] for p in picks]
        self.assertEqual(positions, list(range(1, 16)))

        # Verify exactly 1 captain and 1 vice captain
        captains = [p for p in picks if p["is_captain"]]
        vcs = [p for p in picks if p["is_vice_captain"]]
        self.assertEqual(len(captains), 1)
        self.assertEqual(len(vcs), 1)
        self.assertEqual(captains[0]["multiplier"], 2)


if __name__ == "__main__":
    unittest.main()
