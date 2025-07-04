# Welcome to Fair Meeting Planner

`fair-meeting-planner` is a Python library that finds fair, repeatable meeting times for globally distributed teams.

It provides a command-line tool and a Python API to solve the complex problem of scheduling meetings across multiple timezones while respecting everyone's working hours and minimizing "meeting fatigue."

## Key Features

- **Fairness-driven Scheduling:** Uses a cost-based optimization model to find times that are fair for all participants.
- **Recurring Meetings:** Plan a whole series of meetings at once, with built-in rotation to distribute inconvenient slots evenly.
- **ICS Export:** Generate standard `.ics` files that can be imported into any calendar application.
- **Simple CLI:** A straightforward command-line interface for easy use.
- **Extensible:** Designed to be extended with custom cost functions and scheduling logic.
