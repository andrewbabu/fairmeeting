# Cookbook

This section provides examples of more advanced usage patterns.

## Customizing Meeting Parameters

You can control various aspects of the meeting search through command-line arguments.

### Changing Meeting Duration

Use the `--duration` flag to set the meeting length in minutes.

```bash
fairmeeting participants.yaml --duration 90
```

### Specifying Allowed Days

Use the `--weekdays` flag to provide a comma-separated list of days when the meeting can occur.

```bash
fairmeeting participants.yaml --weekdays "Mon,Wed,Fri"
```

## Using the Python API

For more complex integrations, you can use the `fairmeeting` Python API.

```python
from fairmeeting.schemas import Participant, Meeting
from fairmeeting.solver import ilp_solver
from fairmeeting.export import generate_ics

# 1. Define participants
participants = [
    Participant(name="Alice", tz="America/Los_Angeles", work_start="09:00", work_end="17:00"),
    Participant(name="Bob", tz="Europe/Berlin", work_start="09:00", work_end="17:00"),
]

# 2. Define the meeting
meeting = Meeting(
    participants=participants,
    duration_minutes=45,
    allowed_weekdays=["Tue", "Thu"],
    horizon=4,
    min_gap_between_meetings=0
)

# 3. Solve for the best slots
solution = ilp_solver(meeting)

# 4. Generate an ICS file
if "scheduled_slots" in solution:
    ics_content = generate_ics(meeting, solution['scheduled_slots'])
    with open("my_meetings.ics", "w") as f:
        f.write(ics_content)
    print("ICS file generated successfully.")
```

## Using a Custom Cost Function

The real power of `fairmeeting` comes from its extensibility. You can provide your own cost function to tailor the definition of "fairness" to your team's needs.

For example, let's create a cost function that heavily penalizes meetings on Fridays.

```python
from fairmeeting.schemas import Participant, Meeting
from fairmeeting.solver import ilp_solver
from fairmeeting.cost import DefaultCostFunction
import pandas as pd

# 1. Define a custom cost function
class FridayPenaltyCost(DefaultCostFunction):
    def __call__(self, local_t: pd.Timestamp, p: Participant) -> float:
        # Get the base cost from the default function
        base_cost = super().__call__(local_t, p)
        # Add a heavy penalty for Fridays
        if local_t.weekday() == 4: # Monday is 0, Friday is 4
            return base_cost + 10
        return base_cost

# 2. Define participants and meeting
participants = [
    Participant(name="Alice", tz="America/Los_Angeles", work_start="09:00", work_end="17:00"),
    Participant(name="Bob", tz="Europe/Berlin", work_start="09:00", work_end="17:00"),
]
meeting = Meeting(
    participants=participants,
    duration_minutes=60,
    allowed_weekdays=["Mon", "Tue", "Wed", "Thu", "Fri"],
    horizon=2,
    min_gap_between_meetings=0
)

# 3. Solve using the custom cost function
solution = ilp_solver(meeting, cost_function=FridayPenaltyCost())

# You can then process the solution as usual
print(solution)

```
