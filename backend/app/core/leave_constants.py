LEAVE_TYPES = ("casual", "sick", "paid")

LEAVE_TYPE_LABELS = {
    "casual": "Casual Leave",
    "sick": "Sick Leave",
    "paid": "Paid Leave",
    "annual": "Paid Leave",  # legacy alias
}

DEFAULT_LEAVE_TOTALS = {
    "casual": 12,
    "sick": 12,
    "paid": 24,
}

VALID_LEAVE_STATUSES = ("pending", "approved", "rejected", "clarification_requested", "cancelled")


def normalize_leave_type(leave_type: str) -> str:
    lt = (leave_type or "").strip().lower()
    if lt in ("annual", "pl", "paid leave"):
        return "paid"
    if lt in ("cl", "casual leave", "casual"):
        return "casual"
    if lt in ("sl", "sick leave", "sick"):
        return "sick"
    return lt if lt in LEAVE_TYPES else "paid"
