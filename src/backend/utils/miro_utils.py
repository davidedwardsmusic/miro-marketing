from datetime import datetime

def to_datetime(timestamp: str) -> datetime | None:
    """
    Convert an ISO 8601 timestamp string to a Python datetime object.

    Args:
        timestamp: ISO 8601 formatted timestamp string (e.g., "2025-01-01T00:00:00Z")

    Returns:
        datetime object if parsing succeeds, None if timestamp is empty or invalid
    """
    if not timestamp:
        return None

    try:
        # Handle ISO 8601 format with 'Z' suffix (UTC)
        if timestamp.endswith('Z'):
            timestamp = timestamp[:-1] + '+00:00'

        # Parse the timestamp
        return datetime.fromisoformat(timestamp)
    except (ValueError, AttributeError):
        # Return None if parsing fails
        return None