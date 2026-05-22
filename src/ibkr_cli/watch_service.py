from __future__ import annotations

from typing import Dict, Optional


def detect_state_change(previous: Optional[Dict[str, object]], current: Dict[str, object]) -> Optional[str]:
    if previous is None:
        return None
    previous_status = previous.get("status")
    current_status = current.get("status")
    if previous_status == current_status:
        return None
    if current_status == "needs_reauth":
        return "needs_reauth"
    if previous_status == "needs_reauth" and current_status == "ok":
        return "recovered"
    if current_status == "gateway_down":
        return "gateway_down"
    if current_status == "api_down":
        return "api_down"
    if current_status == "ok":
        return "recovered"
    return current_status if isinstance(current_status, str) else None


def build_state_change_event(
    event: str,
    previous: Dict[str, object],
    current: Dict[str, object],
) -> Dict[str, object]:
    return {
        "event": event,
        "previous_status": previous.get("status"),
        "current_status": current.get("status"),
        "gateway": current.get("gateway"),
        "profile": current.get("profile"),
        "needs_reauth": current.get("needs_reauth"),
        "last_error": current.get("last_error"),
        "current": current,
    }
