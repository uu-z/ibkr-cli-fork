from __future__ import annotations

from typing import Dict, Optional

from ibkr_cli.config import GatewayConfig, ProfileConfig
from ibkr_cli.gateway_service import container_exists, container_running
from ibkr_cli.ib_service import check_api_connection
from ibkr_cli.networking import test_tcp_connection


def gateway_health(
    name: str,
    gateway: GatewayConfig,
    profile: ProfileConfig,
    profile_name: str,
    timeout: float = 2.0,
) -> Dict[str, object]:
    exists = container_exists(gateway.container_name)
    running = container_running(gateway.container_name)
    tcp_result = test_tcp_connection(profile.host, profile.port, timeout=timeout) if running else None
    api_result = check_api_connection(profile, timeout=timeout) if tcp_result and tcp_result.ok else None

    status = "ok"
    needs_reauth = False
    last_error: Optional[str] = None

    if not exists or not running:
        status = "gateway_down"
        last_error = "Gateway container is not running."
    elif tcp_result and not tcp_result.ok:
        status = "gateway_down"
        last_error = tcp_result.error
    elif api_result and not api_result.ok:
        status = "api_down"
        last_error = api_result.error
        lowered = (api_result.error or "").lower()
        if any(token in lowered for token in ("login", "authenticate", "verification", "2fa", "two-factor")):
            status = "needs_reauth"
            needs_reauth = True

    return {
        "ok": status == "ok",
        "gateway": {
            "name": name,
            "container_name": gateway.container_name,
            "vnc_port": gateway.vnc_port,
            "preferred_mode": gateway.preferred_mode,
        },
        "profile": {
            "name": profile_name,
            "host": profile.host,
            "port": profile.port,
            "mode": profile.mode,
        },
        "status": status,
        "container_exists": exists,
        "container_running": running,
        "tcp_ok": bool(tcp_result and tcp_result.ok),
        "api_ok": bool(api_result and api_result.ok),
        "needs_reauth": needs_reauth,
        "last_error": last_error,
        "tcp_connection": tcp_result.to_dict() if tcp_result else None,
        "api_connection": api_result.to_dict() if api_result else None,
    }
