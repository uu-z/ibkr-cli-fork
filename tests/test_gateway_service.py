import unittest
from unittest.mock import patch

from ibkr_cli.config import GatewayConfig
from ibkr_cli.gateway_service import docker_run_cmd, ensure_gateway_running


class GatewayServiceTests(unittest.TestCase):
    def gateway(self) -> GatewayConfig:
        return GatewayConfig(
            container_name="ib-a",
            live_port=4001,
            paper_port=4002,
            vnc_port=5901,
            profile_live="ib-a-live",
            profile_paper="ib-a-paper",
        )

    def test_docker_run_cmd_uses_restart_always_and_expected_ports(self) -> None:
        cmd = docker_run_cmd(
            self.gateway(),
            tws_userid="user",
            tws_password="pass",
            vnc_password="dev",
        )

        self.assertIn("always", cmd)
        self.assertIn("127.0.0.1:4002:4004", cmd)
        self.assertIn("127.0.0.1:5901:5900", cmd)

    @patch("ibkr_cli.gateway_service.docker_sh")
    @patch("ibkr_cli.gateway_service.container_exists", return_value=False)
    @patch("ibkr_cli.gateway_service.container_running", return_value=False)
    def test_ensure_gateway_running_creates_missing_container(self, _running, _exists, mock_sh) -> None:
        state = ensure_gateway_running(
            self.gateway(),
            tws_userid="user",
            tws_password="pass",
            vnc_password="dev",
        )

        self.assertEqual(state, "created")
        run_cmd = mock_sh.call_args.args[0]
        self.assertEqual(run_cmd[:3], ["docker", "run", "-d"])

    @patch("ibkr_cli.gateway_service.docker_sh")
    @patch("ibkr_cli.gateway_service.container_exists", return_value=True)
    @patch("ibkr_cli.gateway_service.container_running", return_value=False)
    def test_ensure_gateway_running_starts_stopped_container(self, _running, _exists, mock_sh) -> None:
        state = ensure_gateway_running(
            self.gateway(),
            tws_userid="user",
            tws_password="pass",
            vnc_password="dev",
        )

        self.assertEqual(state, "started")
        self.assertEqual(mock_sh.call_args.args[0], ["docker", "start", "ib-a"])
