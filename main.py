"""
Main orchestrator for Weekly FPL Automation.
Runs data collection, analytical optimization, browser automation, and summary generation.
"""

import sys
import os
import argparse
import logging
from pathlib import Path
from datetime import datetime

# Add local package directory to path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from config import FPL_TEAM_ID, DRY_RUN, HEADLESS, REPORTS_DIR
from fpl_client import FPLClient
from optimizer import FPLOptimizer
from browser_automation import FPLBrowserAutomation
from models import OptimizationResult

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("FPLWorkflow")


def generate_markdown_report(
    result: OptimizationResult,
    browser_result: dict,
    manager_info: dict,
    bank: float,
    team_value: float
) -> str:
    """Generates a comprehensive markdown summary report of the gameweek execution."""
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    mgr_name = manager_info.get("name", "FPL Manager")
    overall_pts = manager_info.get("summary_overall_points", 0)
    overall_rnk = manager_info.get("summary_overall_rank", 0)

    # Format Starting XI table
    starters_md = []
    for p in result.starting_11:
        badge = ""
        if p.id == result.captain.id:
            badge = " **(C)**"
        elif p.id == result.vice_captain.id:
            badge = " **(VC)**"

        opp_str = f"{p.next_opponent_short_name} ({'H' if p.next_is_home else 'A'})"
        starters_md.append(
            f"| `{p.position_name}` | **{p.web_name}**{badge} | {p.team_short_name} | {opp_str} | FDR {p.fdr} | £{p.now_cost:.1f}m | {p.form} | **{p.expected_value:.2f}** |"
        )
    starters_table = "\n".join(starters_md)

    # Format Bench table
    bench_md = []
    bench_labels = ["Sub GK", "1st Sub", "2nd Sub", "3rd Sub"]
    for i, p in enumerate(result.bench):
        label = bench_labels[i]
        opp_str = f"{p.next_opponent_short_name} ({'H' if p.next_is_home else 'A'})"
        bench_md.append(
            f"| **{label}** | `{p.position_name}` | {p.web_name} | {p.team_short_name} | {opp_str} | FDR {p.fdr} | **{p.expected_value:.2f}** | {p.fitness_label} |"
        )
    bench_table = "\n".join(bench_md)

    # Transfer section
    if result.recommended_transfer:
        tx = result.recommended_transfer
        transfer_section = f"""
### 🔄 Recommended Free Transfer
> [!IMPORTANT]
> **Action**: Transfer **OUT** {tx.player_out.web_name} ➔ Transfer **IN** {tx.player_in.web_name}
> - **Player Out**: {tx.player_out.web_name} ({tx.player_out.team_short_name}, £{tx.player_out.now_cost:.1f}m) — *{tx.player_out.fitness_label}*
> - **Player In**: **{tx.player_in.web_name}** ({tx.player_in.team_short_name}, £{tx.player_in.now_cost:.1f}m, Form: {tx.player_in.form}, Next: {tx.player_in.next_opponent_short_name})
> - **Net Financial Impact**: £{tx.cost_diff:+.1f}m (Remaining Bank: £{bank - tx.cost_diff:.1f}m)
> - **Projected Points Delta**: **+{tx.expected_point_gain:+.2f} pts**
> - **Rationale**: {tx.reasoning}
"""
    else:
        transfer_section = """
### 🔄 Transfer Recommendation
> [!NOTE]
> **No transfer required.** Squad has full health and no red-flagged players. Free transfer rolled over to next gameweek.
"""

    # Red flag alerts
    if result.red_flagged_players:
        injury_rows = "\n".join([
            f"- 🔴 **{p.web_name}** ({p.position_name}, {p.team_short_name}): {p.news or 'Unavailable'} (Chance: {p.chance_of_playing_next_round or 0}%)"
            for p in result.red_flagged_players
        ])
        injury_section = f"""
> [!WARNING]
> **Squad Health Alert — Red Flags Detected:**
{injury_rows}
"""
    else:
        injury_section = "> [!NOTE]\n> All 15 squad members are fit and available for selection."

    # Execution status
    exec_status = browser_result.get("status", "COMPLETED")
    exec_mode = browser_result.get("mode", "AUTOMATED")

    report = f"""# ⚽ Fantasy Premier League — Gameweek {result.gameweek} Automated Report
**Execution Timestamp**: `{now_str}`  
**Team**: **{mgr_name}** (ID: `{manager_info.get('id', FPL_TEAM_ID)}`) | Overall Rank: `{overall_rnk:,}` | Total Points: `{overall_pts:,}`  
**Squad Valuation**: `£{team_value:.1f}m` | Bank: `£{bank:.1f}m` | **Target Formation**: `{result.formation}`

---

## 📋 Executive Summary
- **Optimal Starting XI EV**: **{result.total_expected_points:.2f} expected points** (Captaincy doubled)
- **Captain (C)**: **{result.captain.web_name}** ({result.captain.team_short_name}) — EV: {result.captain.expected_value:.2f} (FDR {result.captain.fdr})
- **Vice-Captain (VC)**: **{result.vice_captain.web_name}** ({result.vice_captain.team_short_name}) — EV: {result.vice_captain.expected_value:.2f} (FDR {result.vice_captain.fdr})
- **Browser Execution**: `{exec_status}` (`{exec_mode}`)

{injury_section}

{transfer_section}

---

## 🏆 Optimal Starting XI ({result.formation})

| Pos | Player | Club | Fixture | FDR | Cost | Form | Expected Pts |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
{starters_table}

---

## 🪑 Bench Ordering & Safeguards

| Slot | Pos | Player | Club | Fixture | FDR | Expected Pts | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
{bench_table}

> [!TIP]
> **Bench Logic**: Backup Goalkeeper `{result.bench[0].web_name}` is fixed at bench position 1. Outfield substitutes `{result.bench[1].web_name}`, `{result.bench[2].web_name}`, and `{result.bench[3].web_name}` are strictly ranked by expected points and legal formation viability so that any unplayed starter is replaced by the highest upside legal option.

---

## 🤖 Browser Automation Execution Log
```text
""" + "\n".join(browser_result.get("logs", [])) + """
```
"""
    return report


def run_pipeline(
    team_id: int = FPL_TEAM_ID,
    gameweek: int = None,
    dry_run: bool = DRY_RUN,
    headless: bool = HEADLESS,
    output_artifact_path: str = None
) -> int:
    """Executes the full end-to-end FPL automation pipeline."""
    logger.info("Initializing FPL Weekly Automation Pipeline...")
    logger.info(f"Target Team ID: {team_id} | Dry Run: {dry_run} | Headless: {headless}")

    # 1. DATA COLLECTION
    client = FPLClient(team_id=team_id)
    target_gw = gameweek or client.get_current_or_next_gameweek()
    logger.info(f"Target Gameweek: {target_gw}")

    logger.info("Fetching FPL player statistics, fixtures, and manager picks...")
    squad = client.get_squad(team_id=team_id, event_id=target_gw)
    all_players, teams_dict = client.parse_all_players()
    manager_info = client.get_user_entry(team_id)

    logger.info(f"Loaded squad: {len(squad.picks)} players | Bank: £{squad.bank:.1f}m | Value: £{squad.team_value:.1f}m")

    # 2. OPTIMIZATION LOGIC
    logger.info("Executing analytical solver for lineup, captaincy, and bench order...")
    optimizer = FPLOptimizer(squad, all_players)
    opt_result = optimizer.optimize_lineup()

    logger.info(f"Optimization complete! Best Formation: {opt_result.formation} | Total EV: {opt_result.total_expected_points}")
    logger.info(f"Captain: {opt_result.captain.web_name} | Vice-Captain: {opt_result.vice_captain.web_name}")
    if opt_result.recommended_transfer:
        logger.info(f"Transfer: {opt_result.recommended_transfer.reasoning}")

    # 3. BROWSER AUTOMATION
    logger.info("Executing browser automation via Playwright...")
    browser = FPLBrowserAutomation(
        team_id=team_id,
        headless=headless,
        dry_run=dry_run
    )
    browser_result = browser.execute(opt_result)

    # 4. REPORT & ARTIFACT GENERATION
    logger.info("Generating Gameweek report and audit artifact...")
    report_md = generate_markdown_report(
        result=opt_result,
        browser_result=browser_result,
        manager_info=manager_info,
        bank=squad.bank,
        team_value=squad.team_value
    )

    # Save to local reports directory
    report_file = REPORTS_DIR / f"gw{target_gw}_summary.md"
    with open(report_file, "w") as f:
        f.write(report_md)
    logger.info(f"Saved local report to {report_file}")

    # Save to Antigravity conversation artifact directory if requested
    if output_artifact_path:
        out_p = Path(output_artifact_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        with open(out_p, "w") as f:
            f.write(report_md)
        logger.info(f"Saved summary artifact to {output_artifact_path}")

    logger.info("Pipeline completed successfully!")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Weekly FPL Automation Workflow")
    parser.add_argument("--team-id", type=int, default=FPL_TEAM_ID, help="FPL Team ID")
    parser.add_argument("--gameweek", type=int, default=None, help="Target Gameweek")
    parser.add_argument("--dry-run", action="store_true", default=DRY_RUN, help="Run in simulation mode")
    parser.add_argument("--headed", action="store_true", default=False, help="Run browser visibly (not headless)")
    parser.add_argument("--output-artifact", type=str, default=None, help="Path to write markdown summary artifact")

    args = parser.parse_args()
    return run_pipeline(
        team_id=args.team_id,
        gameweek=args.gameweek,
        dry_run=args.dry_run,
        headless=not args.headed,
        output_artifact_path=args.output_artifact
    )


if __name__ == "__main__":
    sys.exit(main())
