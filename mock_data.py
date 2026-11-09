"""
Mock data generator and loader for FPL API.
Provides offline and fallback data for testing and sandbox execution.
"""

import json
from pathlib import Path
from config import DATA_DIR


def generate_mock_fpl_dataset() -> dict:
    teams = [
        {"id": 1, "name": "Arsenal", "short_name": "ARS", "strength": 5},
        {"id": 2, "name": "Aston Villa", "short_name": "AVL", "strength": 4},
        {"id": 3, "name": "Bournemouth", "short_name": "BOU", "strength": 3},
        {"id": 4, "name": "Brentford", "short_name": "BRE", "strength": 3},
        {"id": 5, "name": "Brighton", "short_name": "BHA", "strength": 3},
        {"id": 6, "name": "Chelsea", "short_name": "CHE", "strength": 4},
        {"id": 7, "name": "Crystal Palace", "short_name": "CRY", "strength": 3},
        {"id": 8, "name": "Everton", "short_name": "EVE", "strength": 3},
        {"id": 9, "name": "Fulham", "short_name": "FUL", "strength": 3},
        {"id": 10, "name": "Ipswich", "short_name": "IPS", "strength": 2},
        {"id": 11, "name": "Leicester", "short_name": "LEI", "strength": 2},
        {"id": 12, "name": "Liverpool", "short_name": "LIV", "strength": 5},
        {"id": 13, "name": "Man City", "short_name": "MCI", "strength": 5},
        {"id": 14, "name": "Man Utd", "short_name": "MUN", "strength": 3},
        {"id": 15, "name": "Newcastle", "short_name": "NEW", "strength": 4},
        {"id": 16, "name": "Nott'm Forest", "short_name": "NFO", "strength": 3},
        {"id": 17, "name": "Southampton", "short_name": "SOU", "strength": 2},
        {"id": 18, "name": "Spurs", "short_name": "TOT", "strength": 4},
        {"id": 19, "name": "West Ham", "short_name": "WHU", "strength": 3},
        {"id": 20, "name": "Wolves", "short_name": "WOL", "strength": 2},
    ]

    events = [
        {"id": 12, "name": "Gameweek 12", "is_previous": True, "is_current": False, "is_next": False, "finished": True},
        {"id": 13, "name": "Gameweek 13", "is_previous": False, "is_current": True, "is_next": False, "finished": False, "deadline_time": "2026-11-21T11:00:00Z"},
        {"id": 14, "name": "Gameweek 14", "is_previous": False, "is_current": False, "is_next": True, "finished": False, "deadline_time": "2026-11-28T11:00:00Z"},
    ]

    # GW13 Fixtures
    fixtures = [
        {"id": 121, "event": 13, "team_h": 1, "team_a": 16, "team_h_difficulty": 2, "team_a_difficulty": 4},  # ARS vs NFO
        {"id": 122, "event": 13, "team_h": 2, "team_a": 7,  "team_h_difficulty": 2, "team_a_difficulty": 4},  # AVL vs CRY
        {"id": 123, "event": 13, "team_h": 6, "team_a": 11, "team_h_difficulty": 2, "team_a_difficulty": 4},  # CHE vs LEI
        {"id": 124, "event": 13, "team_h": 8, "team_a": 4,  "team_h_difficulty": 3, "team_a_difficulty": 3},  # EVE vs BRE
        {"id": 125, "event": 13, "team_h": 9, "team_a": 20, "team_h_difficulty": 2, "team_a_difficulty": 3},  # FUL vs WOL
        {"id": 126, "event": 13, "team_h": 13, "team_a": 18, "team_h_difficulty": 3, "team_a_difficulty": 4}, # MCI vs TOT
        {"id": 127, "event": 13, "team_h": 17, "team_a": 12, "team_h_difficulty": 5, "team_a_difficulty": 2}, # SOU vs LIV
        {"id": 128, "event": 13, "team_h": 10, "team_a": 14, "team_h_difficulty": 4, "team_a_difficulty": 2}, # IPS vs MUN
        {"id": 129, "event": 13, "team_h": 15, "team_a": 19, "team_h_difficulty": 2, "team_a_difficulty": 4}, # NEW vs WHU
        {"id": 130, "event": 13, "team_h": 3, "team_a": 5,  "team_h_difficulty": 3, "team_a_difficulty": 3},  # BOU vs BHA
    ]

    # Players pool (Elements)
    elements = [
        # GKs (element_type = 1)
        {
            "id": 1, "web_name": "Raya", "first_name": "David", "second_name": "Raya",
            "element_type": 1, "team": 1, "now_cost": 55, "form": "5.2", "points_per_game": "5.0",
            "total_points": 58, "ep_next": "5.0", "ep_this": "5.0", "status": "a",
            "chance_of_playing_this_round": 100, "chance_of_playing_next_round": 100, "news": "", "selected_by_percent": "31.2"
        },
        {
            "id": 2, "web_name": "Flekken", "first_name": "Mark", "second_name": "Flekken",
            "element_type": 1, "team": 4, "now_cost": 45, "form": "3.8", "points_per_game": "3.9",
            "total_points": 45, "ep_next": "3.5", "ep_this": "3.5", "status": "a",
            "chance_of_playing_this_round": 100, "chance_of_playing_next_round": 100, "news": "", "selected_by_percent": "14.5"
        },
        {
            "id": 3, "web_name": "Pickford", "first_name": "Jordan", "second_name": "Pickford",
            "element_type": 1, "team": 8, "now_cost": 48, "form": "4.0", "points_per_game": "4.1",
            "total_points": 48, "ep_next": "4.0", "ep_this": "4.0", "status": "a",
            "chance_of_playing_this_round": 100, "chance_of_playing_next_round": 100, "news": "", "selected_by_percent": "12.0"
        },

        # DEFs (element_type = 2)
        {
            "id": 10, "web_name": "Gabriel", "first_name": "Gabriel", "second_name": "dos Santos Magalhães",
            "element_type": 2, "team": 1, "now_cost": 62, "form": "6.0", "points_per_game": "5.8",
            "total_points": 64, "ep_next": "6.2", "ep_this": "6.2", "status": "a",
            "chance_of_playing_this_round": 100, "chance_of_playing_next_round": 100, "news": "", "selected_by_percent": "28.5"
        },
        {
            "id": 11, "web_name": "Alexander-Arnold", "first_name": "Trent", "second_name": "Alexander-Arnold",
            "element_type": 2, "team": 12, "now_cost": 70, "form": "5.5", "points_per_game": "5.6",
            "total_points": 62, "ep_next": "6.5", "ep_this": "6.5", "status": "a",
            "chance_of_playing_this_round": 100, "chance_of_playing_next_round": 100, "news": "", "selected_by_percent": "33.0"
        },
        {
            "id": 12, "web_name": "Gvardiol", "first_name": "Josko", "second_name": "Gvardiol",
            "element_type": 2, "team": 13, "now_cost": 60, "form": "5.0", "points_per_game": "5.1",
            "total_points": 56, "ep_next": "5.2", "ep_this": "5.2", "status": "a",
            "chance_of_playing_this_round": 100, "chance_of_playing_next_round": 100, "news": "", "selected_by_percent": "30.1"
        },
        {
            "id": 13, "web_name": "Robinson", "first_name": "Antonee", "second_name": "Robinson",
            "element_type": 2, "team": 9, "now_cost": 47, "form": "4.2", "points_per_game": "4.3",
            "total_points": 46, "ep_next": "4.5", "ep_this": "4.5", "status": "a",
            "chance_of_playing_this_round": 100, "chance_of_playing_next_round": 100, "news": "", "selected_by_percent": "16.8"
        },
        {
            "id": 14, "web_name": "Mazraoui", "first_name": "Noussair", "second_name": "Mazraoui",
            "element_type": 2, "team": 14, "now_cost": 45, "form": "3.5", "points_per_game": "3.6",
            "total_points": 38, "ep_next": "3.8", "ep_this": "3.8", "status": "a",
            "chance_of_playing_this_round": 100, "chance_of_playing_next_round": 100, "news": "", "selected_by_percent": "9.4"
        },
        {
            "id": 15, "web_name": "Konsa", "first_name": "Ezri", "second_name": "Konsa",
            "element_type": 2, "team": 2, "now_cost": 45, "form": "3.8", "points_per_game": "4.0",
            "total_points": 42, "ep_next": "4.0", "ep_this": "4.0", "status": "a",
            "chance_of_playing_this_round": 100, "chance_of_playing_next_round": 100, "news": "", "selected_by_percent": "11.2"
        },
        {
            "id": 16, "web_name": "Ait-Nouri", "first_name": "Rayan", "second_name": "Ait-Nouri",
            "element_type": 2, "team": 20, "now_cost": 47, "form": "4.8", "points_per_game": "4.5",
            "total_points": 49, "ep_next": "4.2", "ep_this": "4.2", "status": "a",
            "chance_of_playing_this_round": 100, "chance_of_playing_next_round": 100, "news": "", "selected_by_percent": "15.0"
        },

        # MIDs (element_type = 3)
        {
            "id": 20, "web_name": "Salah", "first_name": "Mohamed", "second_name": "Salah",
            "element_type": 3, "team": 12, "now_cost": 128, "form": "9.5", "points_per_game": "8.8",
            "total_points": 105, "ep_next": "9.8", "ep_this": "9.8", "status": "a",
            "chance_of_playing_this_round": 100, "chance_of_playing_next_round": 100, "news": "", "selected_by_percent": "52.4"
        },
        {
            "id": 21, "web_name": "Saka", "first_name": "Bukayo", "second_name": "Saka",
            "element_type": 3, "team": 1, "now_cost": 102, "form": "7.8", "points_per_game": "7.2",
            "total_points": 82, "ep_next": "8.0", "ep_this": "8.0", "status": "a",
            "chance_of_playing_this_round": 100, "chance_of_playing_next_round": 100, "news": "", "selected_by_percent": "35.2"
        },
        {
            "id": 22, "web_name": "Palmer", "first_name": "Cole", "second_name": "Palmer",
            "element_type": 3, "team": 6, "now_cost": 109, "form": "7.2", "points_per_game": "7.5",
            "total_points": 88, "ep_next": "7.8", "ep_this": "7.8", "status": "a",
            "chance_of_playing_this_round": 100, "chance_of_playing_next_round": 100, "news": "", "selected_by_percent": "48.0"
        },
        {
            "id": 23, "web_name": "Mbeumo", "first_name": "Bryan", "second_name": "Mbeumo",
            "element_type": 3, "team": 4, "now_cost": 78, "form": "6.5", "points_per_game": "6.2",
            "total_points": 72, "ep_next": "6.8", "ep_this": "6.8", "status": "a",
            "chance_of_playing_this_round": 100, "chance_of_playing_next_round": 100, "news": "", "selected_by_percent": "38.5"
        },
        {
            "id": 24, "web_name": "Rogers", "first_name": "Morgan", "second_name": "Rogers",
            "element_type": 3, "team": 2, "now_cost": 54, "form": "4.5", "points_per_game": "4.2",
            "total_points": 47, "ep_next": "4.8", "ep_this": "4.8", "status": "a",
            "chance_of_playing_this_round": 100, "chance_of_playing_next_round": 100, "news": "", "selected_by_percent": "22.1"
        },
        {
            "id": 25, "web_name": "Son", "first_name": "Heung-min", "second_name": "Son",
            "element_type": 3, "team": 18, "now_cost": 99, "form": "6.0", "points_per_game": "6.1",
            "total_points": 65, "ep_next": "5.5", "ep_this": "5.5", "status": "a",
            "chance_of_playing_this_round": 100, "chance_of_playing_next_round": 100, "news": "", "selected_by_percent": "12.0"
        },
        {
            "id": 26, "web_name": "Semenyo", "first_name": "Antoine", "second_name": "Semenyo",
            "element_type": 3, "team": 3, "now_cost": 57, "form": "4.8", "points_per_game": "4.6",
            "total_points": 50, "ep_next": "4.5", "ep_this": "4.5", "status": "a",
            "chance_of_playing_this_round": 100, "chance_of_playing_next_round": 100, "news": "", "selected_by_percent": "14.0"
        },

        # FWDs (element_type = 4)
        {
            "id": 30, "web_name": "Haaland", "first_name": "Erling", "second_name": "Haaland",
            "element_type": 4, "team": 13, "now_cost": 152, "form": "8.0", "points_per_game": "8.2",
            "total_points": 95, "ep_next": "8.5", "ep_this": "8.5", "status": "a",
            "chance_of_playing_this_round": 100, "chance_of_playing_next_round": 100, "news": "", "selected_by_percent": "65.4"
        },
        {
            "id": 31, "web_name": "Wood", "first_name": "Chris", "second_name": "Wood",
            "element_type": 4, "team": 16, "now_cost": 65, "form": "6.8", "points_per_game": "6.4",
            "total_points": 68, "ep_next": "5.2", "ep_this": "5.2", "status": "a",
            "chance_of_playing_this_round": 100, "chance_of_playing_next_round": 100, "news": "", "selected_by_percent": "26.3"
        },
        {
            # Active injured player in squad (Red flag)
            "id": 32, "web_name": "Welbeck", "first_name": "Danny", "second_name": "Welbeck",
            "element_type": 4, "team": 5, "now_cost": 58, "form": "5.5", "points_per_game": "5.4",
            "total_points": 61, "ep_next": "0.0", "ep_this": "0.0", "status": "i",
            "chance_of_playing_this_round": 0, "chance_of_playing_next_round": 0,
            "news": "Back injury - Ruled out for 3 weeks", "selected_by_percent": "18.5"
        },
        {
            # Potential transfer target 1 (Fit, excellent form)
            "id": 33, "web_name": "Cunha", "first_name": "Matheus", "second_name": "Cunha",
            "element_type": 4, "team": 20, "now_cost": 67, "form": "6.5", "points_per_game": "5.8",
            "total_points": 65, "ep_next": "6.2", "ep_this": "6.2", "status": "a",
            "chance_of_playing_this_round": 100, "chance_of_playing_next_round": 100, "news": "", "selected_by_percent": "18.2"
        },
        {
            # Potential transfer target 2 (Fit, budget option)
            "id": 34, "web_name": "Wissa", "first_name": "Yoane", "second_name": "Wissa",
            "element_type": 4, "team": 4, "now_cost": 61, "form": "6.2", "points_per_game": "5.9",
            "total_points": 55, "ep_next": "6.0", "ep_this": "6.0", "status": "a",
            "chance_of_playing_this_round": 100, "chance_of_playing_next_round": 100, "news": "", "selected_by_percent": "12.0"
        },
        {
            "id": 35, "web_name": "Watkins", "first_name": "Ollie", "second_name": "Watkins",
            "element_type": 4, "team": 2, "now_cost": 90, "form": "5.8", "points_per_game": "5.7",
            "total_points": 63, "ep_next": "6.5", "ep_this": "6.5", "status": "a",
            "chance_of_playing_this_round": 100, "chance_of_playing_next_round": 100, "news": "", "selected_by_percent": "31.0"
        },
        {
            "id": 36, "web_name": "Isak", "first_name": "Alexander", "second_name": "Isak",
            "element_type": 4, "team": 15, "now_cost": 84, "form": "6.0", "points_per_game": "5.6",
            "total_points": 58, "ep_next": "6.8", "ep_this": "6.8", "status": "a",
            "chance_of_playing_this_round": 100, "chance_of_playing_next_round": 100, "news": "", "selected_by_percent": "24.5"
        }
    ]

    # User's current squad picks (15 players)
    # Positions: 1-11 Starting XI, 12 Bench GK, 13-15 Bench outfield
    picks = [
        # Starters
        {"element": 1,  "position": 1,  "multiplier": 1, "is_captain": False, "is_vice_captain": False}, # Raya (GKP)
        {"element": 10, "position": 2,  "multiplier": 1, "is_captain": False, "is_vice_captain": False}, # Gabriel (DEF)
        {"element": 11, "position": 3,  "multiplier": 1, "is_captain": False, "is_vice_captain": False}, # Trent (DEF)
        {"element": 12, "position": 4,  "multiplier": 1, "is_captain": False, "is_vice_captain": False}, # Gvardiol (DEF)
        {"element": 20, "position": 5,  "multiplier": 2, "is_captain": True,  "is_vice_captain": False}, # Salah (MID) - Captain
        {"element": 21, "position": 6,  "multiplier": 1, "is_captain": False, "is_vice_captain": True},  # Saka (MID) - Vice Captain
        {"element": 22, "position": 7,  "multiplier": 1, "is_captain": False, "is_vice_captain": False}, # Palmer (MID)
        {"element": 23, "position": 8,  "multiplier": 1, "is_captain": False, "is_vice_captain": False}, # Mbeumo (MID)
        {"element": 24, "position": 9,  "multiplier": 1, "is_captain": False, "is_vice_captain": False}, # Rogers (MID)
        {"element": 30, "position": 10, "multiplier": 1, "is_captain": False, "is_vice_captain": False}, # Haaland (FWD)
        {"element": 32, "position": 11, "multiplier": 1, "is_captain": False, "is_vice_captain": False}, # Welbeck (FWD) - INJURED! Needs transfer / benching
        # Bench
        {"element": 2,  "position": 12, "multiplier": 0, "is_captain": False, "is_vice_captain": False}, # Flekken (GKP bench)
        {"element": 31, "position": 13, "multiplier": 0, "is_captain": False, "is_vice_captain": False}, # Wood (FWD) - Bench 1
        {"element": 13, "position": 14, "multiplier": 0, "is_captain": False, "is_vice_captain": False}, # Robinson (DEF) - Bench 2
        {"element": 14, "position": 15, "multiplier": 0, "is_captain": False, "is_vice_captain": False}, # Mazraoui (DEF) - Bench 3
    ]

    user_entry = {
        "id": 11271513,
        "name": "The Antigravity XI",
        "player_first_name": "Felix",
        "player_last_name": "Manager",
        "summary_overall_points": 680,
        "summary_overall_rank": 85420,
        "summary_event_points": 65,
        "current_event": 13
    }

    picks_response = {
        "active_chip": None,
        "automatic_subs": [],
        "entry_history": {
            "event": 13,
            "points": 65,
            "total_points": 680,
            "rank": 85420,
            "bank": 15,  # £1.5m in the bank
            "value": 1024, # £102.4m total squad value
            "event_transfers": 0,
            "event_transfers_cost": 0,
            "points_on_bench": 12
        },
        "picks": picks
    }

    return {
        "bootstrap": {
            "teams": teams,
            "events": events,
            "elements": elements
        },
        "fixtures": fixtures,
        "entry": user_entry,
        "picks": picks_response
    }


def save_mock_dataset():
    data = generate_mock_fpl_dataset()
    mock_file = DATA_DIR / "mock_fpl_data.json"
    with open(mock_file, "w") as f:
        json.dump(data, f, indent=2)
    return mock_file


if __name__ == "__main__":
    path = save_mock_dataset()
    print(f"Saved mock FPL dataset to {path}")
