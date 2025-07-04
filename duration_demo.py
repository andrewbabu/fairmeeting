#!/usr/bin/env python3
"""
Demonstration of how meeting duration could affect slot generation
"""

import pandas as pd


def current_slot_generation(duration_minutes):
    """Current implementation - duration is ignored"""
    start_date = pd.to_datetime("2025-07-07").tz_localize("UTC")
    candidate_slots = []

    # Current: Fixed hours regardless of duration
    reasonable_hours = range(8, 18, 2)  # 8, 10, 12, 14, 16

    current_day = start_date
    for hour in reasonable_hours:
        slot_time = current_day.replace(hour=hour, minute=0, second=0)
        candidate_slots.append(slot_time)

    return candidate_slots


def duration_aware_slot_generation(duration_minutes):
    """How it could work - duration affects slot intervals"""
    start_date = pd.to_datetime("2025-07-07").tz_localize("UTC")
    candidate_slots = []

    # Calculate interval based on duration
    if duration_minutes <= 30:
        interval_minutes = 30  # 30-min slots for short meetings
    elif duration_minutes <= 60:
        interval_minutes = 60  # 1-hour slots for medium meetings
    elif duration_minutes <= 90:
        interval_minutes = 90  # 1.5-hour slots for longer meetings
    else:
        interval_minutes = 120  # 2-hour slots for very long meetings

    # Generate slots from 8 AM to 6 PM with duration-based intervals
    current_time = start_date.replace(hour=8, minute=0, second=0)
    end_time = start_date.replace(hour=18, minute=0, second=0)

    while current_time <= end_time:
        candidate_slots.append(current_time)
        current_time += pd.Timedelta(minutes=interval_minutes)

    return candidate_slots


def main():
    print("=== Current Slot Generation (Duration Ignored) ===")
    for duration in [30, 60, 90, 120]:
        slots = current_slot_generation(duration)
        print(f"\nDuration: {duration} minutes")
        print("Candidate slots:")
        for slot in slots:
            print(f"  {slot.strftime('%H:%M')}")
        print(f"Total slots: {len(slots)}")

    print("\n" + "=" * 60)
    print("=== Duration-Aware Slot Generation (Proposed) ===")
    for duration in [30, 60, 90, 120]:
        slots = duration_aware_slot_generation(duration)
        print(f"\nDuration: {duration} minutes")
        print("Candidate slots:")
        for slot in slots:
            print(f"  {slot.strftime('%H:%M')}")
        print(f"Total slots: {len(slots)}")


if __name__ == "__main__":
    main()
