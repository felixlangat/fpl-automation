"""
Configuration settings for FPL Weekly Automation.
Loads configuration from environment variables with sensible defaults.
"""

import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
SCREENSHOT_DIR = BASE_DIR / "screenshots"
REPORTS_DIR = BASE_DIR / "reports"

# Ensure runtime directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# Load local .env file if present
env_file = BASE_DIR / ".env"
if env_file.exists():
    try:
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    key = key.strip()
                    val = val.strip().strip("'\"")
                    if key not in os.environ:
                        os.environ[key] = val
    except Exception as e:
        pass

# FPL Credentials & Account Configuration
FPL_EMAIL = os.environ.get("FPL_EMAIL", "")
FPL_PASSWORD = os.environ.get("FPL_PASSWORD", "")
FPL_TEAM_ID = int(os.environ.get("FPL_TEAM_ID", "11271513"))

# Execution Modes
HEADLESS = os.environ.get("FPL_HEADLESS", "true").lower() in ("true", "1", "yes")
DRY_RUN = os.environ.get("FPL_DRY_RUN", "false").lower() in ("true", "1", "yes")
BROWSER_TIMEOUT_MS = int(os.environ.get("FPL_BROWSER_TIMEOUT", "30000"))

# Official FPL API Endpoints
FPL_BASE_URL = "https://fantasy.premierleague.com"
BOOTSTRAP_URL = f"{FPL_BASE_URL}/api/bootstrap-static/"
FIXTURES_URL = f"{FPL_BASE_URL}/api/fixtures/"
ENTRY_URL = f"{FPL_BASE_URL}/api/entry/{{team_id}}/"
PICKS_URL = f"{FPL_BASE_URL}/api/entry/{{team_id}}/event/{{event_id}}/picks/"
TRANSFERS_URL = f"{FPL_BASE_URL}/api/entry/{{team_id}}/transfers/"

# FPL Formation Rules
MIN_KEEPERS = 1
MAX_KEEPERS = 1
MIN_DEFENDERS = 3
MAX_DEFENDERS = 5
MIN_MIDFIELDERS = 2
MAX_MIDFIELDERS = 5
MIN_FORWARDS = 1
MAX_FORWARDS = 3
STARTERS_COUNT = 11
SQUAD_SIZE = 15
MAX_PLAYERS_PER_TEAM = 3

# Element Type mapping
ELEMENT_TYPES = {
    1: "GKP",
    2: "DEF",
    3: "MID",
    4: "FWD"
}

# FDR (Fixture Difficulty Rating 1-5) Multiplier for expected points
FDR_MULTIPLIERS = {
    1: 1.25,  # Easiest
    2: 1.10,
    3: 1.00,  # Neutral
    4: 0.85,
    5: 0.70   # Hardest
}

# Injury / Status Penalty Factors
STATUS_FACTORS = {
    "a": 1.00,  # Available
    "d": 0.50,  # Doubtful (default if chance not specified)
    "i": 0.00,  # Injured (Red flag)
    "s": 0.00,  # Suspended (Red flag)
    "u": 0.00,  # Unavailable (Red flag)
    "n": 0.00,  # Not available (Red flag)
}
