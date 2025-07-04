#!/usr/bin/env python3
"""
Fair Meeting Planner Example: Global Team Challenge

This script demonstrates the Fair Meeting Planner with a realistic hard case:
6 team members across different continents with varying work schedules and importance weights.

Features demonstrated:
1. Global timezone analysis
2. Multiple optimization strategies
3. Fairness analysis
4. Calendar export
"""

import sys
from pathlib import Path
from typing import Dict, Any, List
import pandas as pd
import numpy as np
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from fairmeeting.schemas import Participant, Meeting
from fairmeeting.solver import ilp_solver
from fairmeeting.export import generate_ics
from fairmeeting.cost import DefaultCostFunction
from fairmeeting.timezones import get_time_in_tz
import yaml

console = Console()


class FridayAvoidanceCostFunction(DefaultCostFunction):
    """
    Cost function that heavily penalizes Friday afternoon meetings
    to demonstrate custom cost function capabilities.
    """

    def __call__(self, local_t: pd.Timestamp, p: Participant) -> float:
        base_cost = super().__call__(local_t, p)

        # Add huge penalty for Friday afternoon (after 2 PM)
        if local_t.weekday() == 4 and local_t.hour >= 14:  # Friday after 2 PM
            return base_cost + 50.0

        return base_cost


def load_participants() -> List[Participant]:
    """Load participants from YAML file."""
    try:
        with open("participants.yaml", "r") as f:
            data = yaml.safe_load(f)
        return [Participant(**p_data) for p_data in data["participants"]]
    except FileNotFoundError:
        console.print("[bold red]Error:[/bold red] participants.yaml not found!")
        sys.exit(1)


def analyze_team_distribution(participants: List[Participant]):
    """Display comprehensive team analysis."""
    console.print("\n" + "=" * 80)
    console.print("[bold blue]🌍 GLOBAL TEAM ANALYSIS[/bold blue]")
    console.print("=" * 80)

    # Create distribution table
    table = Table(title="Team Member Global Distribution")
    table.add_column("Name", style="cyan", width=18)
    table.add_column("Timezone", style="green", width=20)
    table.add_column("Work Hours", style="yellow", width=15)
    table.add_column("Weight", style="magenta", width=8)
    table.add_column("Current Time", style="blue", width=12)

    now_utc = pd.Timestamp.now(tz="UTC")

    for p in participants:
        local_time = get_time_in_tz(now_utc, p.tz)
        table.add_row(
            p.name,
            p.tz.replace("_", " "),
            f"{p.work_start}-{p.work_end}",
            f"{p.weight:.1f}",
            local_time.strftime("%H:%M"),
        )

    console.print(table)

    # Time zone spread analysis
    console.print("\n[bold]Challenge Analysis:[/bold]")
    console.print(
        f"• Team spans [yellow]{len(set(p.tz for p in participants))}[/yellow] different timezones"
    )
    console.print(
        f"• Weighted participants: [cyan]{sum(1 for p in participants if p.weight != 1.0)}[/cyan]"
    )
    console.print(
        "• Time spread: Approximately [red]18 hours[/red] from US West Coast to Australia"
    )


def run_optimization_scenario(
    participants: List[Participant], scenario_name: str, cost_function, horizon: int = 3
) -> Dict[str, Any]:
    """Run a single optimization scenario."""

    meeting = Meeting(
        participants=participants,
        duration_minutes=60,
        allowed_weekdays=["Mon", "Tue", "Wed", "Thu", "Fri"],
        horizon=horizon,
        min_gap_between_meetings=0,
    )

    with Progress(
        SpinnerColumn(),
        TextColumn(f"[bold yellow]{scenario_name}[/bold yellow]"),
        console=console,
    ) as progress:
        task = progress.add_task("Optimizing...", total=None)
        solution = ilp_solver(meeting, cost_function=cost_function)
        progress.update(task, completed=100)

    return {"solution": solution, "meeting": meeting, "scenario_name": scenario_name}


def display_solution_analysis(result: Dict[str, Any]):
    """Display detailed solution analysis."""

    if "error" in result.get("solution", {}):
        console.print(
            f"[bold red]❌ {result['scenario_name']} Failed:[/bold red] {result['solution']['error']}"
        )
        return

    solution = result["solution"]
    meeting = result["meeting"]
    scenario_name = result["scenario_name"]

    console.print(f"\n[bold green]✅ {scenario_name}[/bold green]")

    # Create main schedule table
    schedule_table = Table(title=f"Optimized Schedule ({meeting.horizon} meetings)")
    schedule_table.add_column("#", justify="center", style="bold", width=3)
    schedule_table.add_column("UTC Time", justify="center", style="blue", width=16)

    # Add participant columns (shortened names for display)
    for p in meeting.participants:
        name = p.name.split()[0]  # First name only
        location = p.tz.split("/")[-1]  # City only
        schedule_table.add_column(f"{name}\n({location})", justify="center", width=12)

    # Populate schedule
    participant_total_costs = np.zeros(len(meeting.participants))

    for slot in solution["scheduled_slots"]:
        row = [str(slot["occurrence"] + 1), slot["slot_utc"].strftime("%a %m/%d %H:%M")]

        for i, p in enumerate(meeting.participants):
            local_time = get_time_in_tz(slot["slot_utc"], p.tz)
            cost = slot["participant_costs"][i]
            participant_total_costs[i] += cost

            # Color coding based on convenience
            time_str = local_time.strftime("%a %H:%M")
            if cost < 1.0:
                colored_time = f"[green]{time_str}[/green]"
            elif cost < 3.0:
                colored_time = f"[yellow]{time_str}[/yellow]"
            else:
                colored_time = f"[red]{time_str}[/red]"

            row.append(colored_time)

        schedule_table.add_row(*row)

    console.print(schedule_table)

    # Fairness metrics
    console.print("\n[bold]📊 Fairness Metrics:[/bold]")
    console.print(
        f"• Maximum Total Cost: [yellow]{solution['max_total_cost']:.2f}[/yellow]"
    )
    console.print(
        f"• Average Cost per Person: [cyan]{np.mean(participant_total_costs):.2f}[/cyan]"
    )
    console.print(
        f"• Cost Standard Deviation: [magenta]{np.std(participant_total_costs):.2f}[/magenta]"
    )

    # Individual fairness analysis
    fairness_table = Table(title="Individual Impact Analysis")
    fairness_table.add_column("Participant", style="cyan")
    fairness_table.add_column("Total Cost", style="yellow")
    fairness_table.add_column("Avg per Meeting", style="green")
    fairness_table.add_column("Impact Level", style="magenta")

    for i, p in enumerate(meeting.participants):
        total_cost = participant_total_costs[i]
        avg_cost = total_cost / meeting.horizon

        if avg_cost < 1.0:
            impact = "😊 Minimal"
        elif avg_cost < 2.0:
            impact = "🙂 Low"
        elif avg_cost < 4.0:
            impact = "😐 Moderate"
        else:
            impact = "😞 High"

        fairness_table.add_row(
            p.name.split()[0],  # First name
            f"{total_cost:.1f}",
            f"{avg_cost:.1f}",
            impact,
        )

    console.print(fairness_table)

    return result


def save_calendar(result: Dict[str, Any], filename: str):
    """Save solution to ICS calendar file."""
    if "error" in result.get("solution", {}):
        return

    solution = result["solution"]
    meeting = result["meeting"]

    ics_content = generate_ics(meeting, solution["scheduled_slots"])
    with open(filename, "w") as f:
        f.write(ics_content)

    console.print(f"[bold green]💾 Calendar saved:[/bold green] {filename}")


def main():
    """Main demonstration function."""

    console.print(
        Panel.fit(
            "[bold blue]🚀 FAIR MEETING PLANNER DEMONSTRATION[/bold blue]\n\n"
            "Solving the challenge of scheduling fair meetings\n"
            "for a global team across multiple continents.\n\n"
            "[italic]Testing different optimization strategies...[/italic]",
            border_style="blue",
        )
    )

    # Load and analyze team
    participants = load_participants()
    console.print(f"\n[bold]Loaded team of {len(participants)} members[/bold]")
    analyze_team_distribution(participants)

    # Scenario 1: Standard optimization
    console.print("\n" + "=" * 80)
    console.print("[bold]SCENARIO 1: STANDARD FAIR OPTIMIZATION[/bold]")
    console.print("Objective: Minimize maximum individual burden across all meetings")

    result1 = run_optimization_scenario(
        participants, "Standard Fair Scheduling", DefaultCostFunction(), horizon=3
    )
    display_solution_analysis(result1)
    save_calendar(result1, "standard_schedule.ics")

    # Scenario 2: Friday avoidance
    console.print("\n" + "=" * 80)
    console.print("[bold]SCENARIO 2: FRIDAY-AVOIDANCE OPTIMIZATION[/bold]")
    console.print("Objective: Heavily penalize Friday afternoon meetings")

    result2 = run_optimization_scenario(
        participants,
        "Friday Avoidance Strategy",
        FridayAvoidanceCostFunction(),
        horizon=3,
    )
    display_solution_analysis(result2)
    save_calendar(result2, "friday_avoidance_schedule.ics")

    # Comparison
    console.print("\n" + "=" * 80)
    console.print("[bold blue]📈 STRATEGY COMPARISON[/bold blue]")
    console.print("=" * 80)

    comparison_table = Table(title="Optimization Strategy Results")
    comparison_table.add_column("Strategy", style="cyan")
    comparison_table.add_column("Max Cost", style="yellow")
    comparison_table.add_column("Success", style="green")
    comparison_table.add_column("Best Use Case", style="magenta")

    strategies = [
        (result1, "Standard", "General team meetings"),
        (result2, "Friday Avoidance", "Teams with weekend transitions"),
    ]

    for result, name, use_case in strategies:
        if "error" not in result.get("solution", {}):
            max_cost = result["solution"]["max_total_cost"]
            comparison_table.add_row(name, f"{max_cost:.2f}", "✅", use_case)
        else:
            comparison_table.add_row(name, "N/A", "❌", use_case)

    console.print(comparison_table)

    # Final summary
    console.print("\n")
    console.print(
        Panel.fit(
            "[bold green]🎯 DEMONSTRATION COMPLETE[/bold green]\n\n"
            "Key Insights:\n"
            "• Fair scheduling across 18-hour time spread is challenging but solvable\n"
            "• Custom cost functions allow tailoring to team preferences\n"
            "• The algorithm successfully balances individual impacts\n"
            "• Generated .ics files can be imported into any calendar app\n\n"
            "[italic]This demonstrates the power of mathematical optimization\n"
            "for complex scheduling problems![/italic]",
            border_style="green",
        )
    )

    console.print("\n[bold]Files generated:[/bold]")
    for filename in ["standard_schedule.ics", "friday_avoidance_schedule.ics"]:
        try:
            with open(filename, "r"):
                console.print(f"• {filename} ✅")
        except FileNotFoundError:
            console.print(f"• {filename} ❌")


if __name__ == "__main__":
    main()
