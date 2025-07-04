# Quick Start

This guide will get you up and running with `fair-meeting-planner` in just a few minutes.

## 1. Installation

First, install the package using pip:

```bash
pip install fair-meeting-planner
```

## 2. Create a Participants File

Create a YAML file named `participants.yaml` with the details of your team members.

```yaml
participants:
  - name: Alice
    tz: America/Los_Angeles
    work_start: "09:00"
    work_end: "17:00"
  - name: Bob
    tz: Europe/Berlin
    work_start: "09:00"
    work_end: "17:00"
  - name: Charlie
    tz: Asia/Kolkata
    work_start: "09:00"
    work_end: "17:00"
```

## 3. Run the Planner

Now, run the `fairmeeting` command, pointing it to your participants file:

```bash
fairmeeting participants.yaml --horizon 4 --ics meetings.ics
```

This command will:
- Find the 4 fairest meeting slots for your team.
- Print a table with the schedule to your console.
- Save a `meetings.ics` file that you can import into your calendar.

## 4. View the Output

You will see a table like this in your terminal:

```
                             Fair Meeting Plan (4 Occurrences)
┏━━━━━━━━━━━━┳━━━━━━━━━━━━━━━���━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Occurrence ┃       UTC Time        ┃ Alice (America/Los_An… ) ┃    Bob (Europe/Berlin)   ┃   Charlie (Asia/Kolkata) ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│     1      │ 2025-07-07 16:00      │       Mon 09:00          │        Mon 18:00         │        Mon 21:30         │
│     2      │ 2025-07-08 06:00      │       Mon 23:00          │        Tue 08:00         │        Tue 11:30         │
│     3      │ 2025-07-09 14:00      │       Wed 07:00          │        Wed 16:00         │        Wed 19:30         │
│     4      │ 2025-07-10 22:00      │       Thu 15:00          │        Fri 00:00         │        Fri 03:30         │
└────────────┴───────────────────────┴──────────────────────────┴──────────────────────────┴──────────────────────────┘

Max Total Cost (lower is better): 4.50
Success: Calendar file saved to meetings.ics
```
