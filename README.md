# ⚽ FPL Weekly Automation Workflow

A fully automated, analytical Fantasy Premier League lineup optimizer and browser automation engine built for headless scheduled execution every Tuesday morning.

## 🚀 Features

1. **Official FPL Data Collection (`fpl_client.py`)**:
   - Fetches live player stats, form, points per game, upcoming fixtures, and FDR (Fixture Difficulty Rating 1-5).
   - Real-time injury and suspension status tracking (`status`, `chance_of_playing_next_round`, `news`).
   - Resilient caching and offline fallback for air-gapped or sandboxed runs.

2. **Analytical Lineup & Transfer Optimizer (`optimizer.py`)**:
   - **Formations**: Evaluates all 8 valid FPL formations (`3-5-2`, `3-4-3`, `4-4-2`, `4-3-3`, `4-5-1`, `5-3-2`, `5-4-1`, `5-2-3`).
   - **Expected Value (EV) Model**: Blends `ep_next`, form, season PPG, fixture difficulty ratings (FDR), home venue advantage, and fitness chance.
   - **Bench Ordering**: Sub GK fixed at position 12. Outfield subs (positions 13-15) prioritized by expected points and legal formation safeguards.
   - **Captain & Vice-Captain**: Selects the highest ceiling starter as Captain, with a guaranteed 100% fit Vice-Captain from a complementary match.
   - **Single Free Transfer**: Detects any active red-flagged/injured players and recommends the best replacement within budget (`selling_price + bank`) and club limits (`<= 3` per Premier League team).

3. **Browser Automation (`browser_automation.py`)**:
   - Headless Playwright script that navigates to `fantasy.premierleague.com`.
   - Handles OneTrust cookie consent.
   - Secure login via Premier League SSO using `FPL_EMAIL` and `FPL_PASSWORD` environment variables.
   - Navigates to `/squad-selection`, applies substitutions, sets Captain and Vice-Captain.
   - Clicks **"Save Your Team"** to lock in the gameweek picks.
   - Captures audit screenshots in `screenshots/`.
   - Includes verified simulation dry-run mode for testing without live credentials.

4. **Headless Execution & Reporting (`main.py`)**:
   - Orchestrates the full pipeline and generates markdown gameweek summary artifacts.
   - Packaged as an Antigravity scheduled automation sidecar running every Tuesday morning.

---

## 🛠️ Usage

### Quick Test / Simulation Run
```bash
python3 /Users/felix-pc/.gemini/antigravity/scratch/fpl_automation/main.py --dry-run
```

### Run with Specific Team ID
```bash
python3 /Users/felix-pc/.gemini/antigravity/scratch/fpl_automation/main.py --team-id <YOUR_TEAM_ID>
```

### Live Run with Playwright
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```
2. Configure environment credentials in `.env`:
   ```bash
   export FPL_EMAIL="your_email@example.com"
   export FPL_PASSWORD="your_password"
   export FPL_TEAM_ID=1234567
   ```
3. Execute:
   ```bash
   python3 main.py
   ```

### Run Unit Tests
```bash
python3 test_fpl_pipeline.py
```
