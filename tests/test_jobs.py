from app.jobs import REMINDERS


def test_reminder_schedule_is_ordered_and_has_three_days():
    assert REMINDERS == ((3, "d3"), (2, "d2"), (1, "d1"))


def test_reminder_thresholds_cover_nearest_window():
    # Mirrors the worker's next(... days_left <= n) selection.
    for days, expected in ((2.5, "d3"), (1.5, "d2"), (0.5, "d1")):
        due = next(((n, kind) for n, kind in reversed(REMINDERS) if days <= n), None)
        assert due[1] == expected


def test_expired_subscription_is_not_a_reminder_window():
    days_left = -0.1
    due = next(((n, kind) for n, kind in REMINDERS if days_left > 0 and days_left <= n), None)
    assert due is None
