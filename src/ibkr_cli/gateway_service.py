from __future__ import annotations

import subprocess
from typing import List

from ibkr_cli.config import GatewayConfig


def docker_capture(cmd: list[str]) -> tuple[bool, str]:
    try:
        proc = subprocess.run(
            cmd,
            text=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        return True, proc.stdout.strip()
    except subprocess.CalledProcessError as exc:
        output = (exc.stdout or "").strip()
        return False, output or str(exc)


def docker_sh(cmd: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, text=True, check=check)


def container_exists(name: str) -> bool:
    ok, output = docker_capture(["docker", "ps", "-a", "--filter", f"name=^{name}$", "--format", "{{.Names}}"])
    return ok and output.strip() == name


def container_running(name: str) -> bool:
    ok, output = docker_capture(["docker", "ps", "--filter", f"name=^{name}$", "--format", "{{.Names}}"])
    return ok and output.strip() == name


def docker_run_cmd(
    gateway: GatewayConfig,
    *,
    tws_userid: str,
    tws_password: str,
    vnc_password: str,
) -> List[str]:
    return [
        "docker",
        "run",
        "-d",
        "--name",
        gateway.container_name,
        "--restart",
        "always",
        "-p",
        f"{gateway.host}:{gateway.live_port}:4003",
        "-p",
        f"{gateway.host}:{gateway.paper_port}:4004",
        "-p",
        f"{gateway.host}:{gateway.vnc_port}:5900",
        "-e",
        f"TWS_USERID={tws_userid}",
        "-e",
        f"TWS_PASSWORD={tws_password}",
        "-e",
        f"VNC_SERVER_PASSWORD={vnc_password}",
        "-e",
        f"TRADING_MODE={gateway.preferred_mode}",
        "-e",
        "READ_ONLY_API=no",
        "-e",
        "TWOFA_TIMEOUT_ACTION=restart",
        "-e",
        "RELOGIN_AFTER_TWOFA_TIMEOUT=yes",
        "-e",
        f"AUTO_RESTART_TIME={gateway.auto_restart_time}",
        "-e",
        "TWS_ACCEPT_INCOMING=accept",
        gateway.image,
    ]


def ensure_gateway_running(
    gateway: GatewayConfig,
    *,
    tws_userid: str,
    tws_password: str,
    vnc_password: str,
) -> str:
    if container_running(gateway.container_name):
        return "running"
    if container_exists(gateway.container_name):
        docker_sh(["docker", "start", gateway.container_name])
        return "started"
    docker_sh(
        docker_run_cmd(
            gateway,
            tws_userid=tws_userid,
            tws_password=tws_password,
            vnc_password=vnc_password,
        )
    )
    return "created"


def list_gateway_containers() -> tuple[bool, str]:
    return docker_capture(["docker", "ps", "--format", "table {{.Names}}\t{{.Status}}\t{{.Ports}}"])


def gateway_logs(container_name: str, tail: int) -> subprocess.CompletedProcess[str]:
    return docker_sh(["docker", "logs", "--tail", str(tail), container_name], check=False)


def remove_gateway(container_name: str) -> bool:
    if not container_exists(container_name):
        return False
    docker_sh(["docker", "rm", "-f", container_name], check=False)
    return True
