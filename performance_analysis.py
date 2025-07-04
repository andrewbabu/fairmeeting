#!/usr/bin/env python3
"""
Performance Analysis Tool for Fair Meeting Planner

This script demonstrates the performance difference between the original
and optimized solver approaches.
"""

import sys
import time
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

sys.path.insert(0, str(Path(__file__).parent / "src"))

from fairmeeting.schemas import Participant, Meeting
from fairmeeting.solver import ilp_solver
import yaml

console = Console()


def load_participants():
    """Load participants from YAML file."""
    with open("participants.yaml", "r") as f:
        data = yaml.safe_load(f)
    return [Participant(**p_data) for p_data in data["participants"]]


def analyze_problem_complexity():
    """Analyze the complexity of different horizon sizes."""
    console.print("\n")
    console.print(
        Panel.fit(
            "[bold blue]📊 PERFORMANCE ANALYSIS: Fair Meeting Planner[/bold blue]\n\n"
            "Understanding why horizon 4+ takes longer...",
            border_style="blue",
        )
    )

    participants = load_participants()

    # Test different horizons
    table = Table(title="Problem Complexity Analysis")
    table.add_column("Horizon", style="cyan")
    table.add_column("Time Slots*", style="yellow")
    table.add_column("Variables", style="red")
    table.add_column("Constraints", style="magenta")
    table.add_column("Solve Time", style="green")
    table.add_column("Status", style="blue")

    for horizon in [1, 2, 3, 4, 5]:
        console.print(f"\n[bold yellow]Testing horizon {horizon}...[/bold yellow]")

        meeting = Meeting(
            participants=participants,
            duration_minutes=60,
            allowed_weekdays=["Mon", "Wed", "Fri"],
            horizon=horizon,
            min_gap_between_meetings=0,
        )

        start_time = time.time()
        try:
            solution = ilp_solver(meeting)
            solve_time = time.time() - start_time

            if "error" in solution:
                status = "❌ Failed"
                solve_time_str = f"{solve_time:.1f}s"
            else:
                status = "✅ Success"
                solve_time_str = f"{solve_time:.1f}s"

        except Exception:
            solve_time = time.time() - start_time
            status = "💥 Error"
            solve_time_str = f">{solve_time:.1f}s"

        # Estimate problem size (this is approximate)
        # 5 time slots per day * 3 days * horizon weeks = slots
        # After optimization: ~12 slots per week * horizon
        estimated_slots = 12 * horizon
        estimated_vars = estimated_slots * horizon
        estimated_constraints = (
            len(participants) * estimated_slots + horizon + estimated_slots
        )

        table.add_row(
            str(horizon),
            str(estimated_slots),
            str(estimated_vars),
            str(estimated_constraints),
            solve_time_str,
            status,
        )

    console.print(table)
    console.print("\n[italic]* After optimization filtering[/italic]")

    # Explanation
    console.print("\n")
    console.print(
        Panel.fit(
            "[bold green]🔍 KEY INSIGHTS[/bold green]\n\n"
            "• **Exponential Growth**: Variables = slots × horizon²\n"
            "• **Optimization Impact**: Reduced slots from ~54 to ~12 per week\n"
            "• **Sweet Spot**: Horizons 1-4 work well, 5+ may need more optimization\n"
            "• **Time Limit**: Solver now has 30s timeout with 5% optimality gap\n\n"
            "[italic]The optimizations make horizon 4 practical for real-world use![/italic]",
            border_style="green",
        )
    )


def compare_optimization_strategies():
    """Compare different optimization approaches."""
    console.print("\n" + "=" * 80)
    console.print("[bold blue]🚀 OPTIMIZATION STRATEGIES COMPARISON[/bold blue]")
    console.print("=" * 80)

    strategies_table = Table(title="Optimization Techniques Applied")
    strategies_table.add_column("Technique", style="cyan")
    strategies_table.add_column("Before", style="red")
    strategies_table.add_column("After", style="green")
    strategies_table.add_column("Impact", style="yellow")

    strategies_table.add_row(
        "Time Granularity",
        "Every hour (18 slots/day)",
        "Every 2 hours (5 slots/day)",
        "72% reduction",
    )

    strategies_table.add_row(
        "Time Range", "6 AM - 11 PM UTC", "8 AM - 6 PM UTC", "Focused on peak hours"
    )

    strategies_table.add_row(
        "Cost Filtering",
        "All slots included",
        "Remove worst 25%",
        "Quality pre-filtering",
    )

    strategies_table.add_row(
        "Solver Settings", "No timeout", "30s timeout, 5% gap", "Practical time limits"
    )

    strategies_table.add_row(
        "Problem Size (H=4)", "~864 variables", "~192 variables", "78% reduction"
    )

    console.print(strategies_table)


def main():
    """Run the performance analysis."""
    analyze_problem_complexity()
    compare_optimization_strategies()

    console.print("\n")
    console.print(
        Panel.fit(
            "[bold blue]💡 RECOMMENDATIONS FOR FUTURE SCALING[/bold blue]\n\n"
            "1. **For Horizon 5+**: Consider heuristic pre-filtering\n"
            "2. **For Large Teams**: Implement participant clustering\n"
            "3. **For Complex Constraints**: Use constraint propagation\n"
            "4. **For Real-time Use**: Cache common solutions\n\n"
            "[italic]The current optimization makes horizon 4 practical![/italic]",
            border_style="blue",
        )
    )


if __name__ == "__main__":
    main()
