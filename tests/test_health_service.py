import unittest
from unittest.mock import patch

from ibkr_cli.config import GatewayConfig, ProfileConfig
from ibkr_cli.health_service import gateway_health
from ibkr_cli.ib_service import ApiConnectionResult
from ibkr_cli.networking import ConnectionResult


class HealthServiceTests(unittest.TestCase):
    def gateway(self) -> GatewayConfig:
        return GatewayConfig(
            container_name="ib-a",
            live_port=4001,
            paper_port=4002,
            vnc_port=5901,
            profile_live="ib-a-live",
            profile_paper="ib-a-paper",
        )

    def profile(self) -> ProfileConfig:
        return ProfileConfig(host="127.0.0.1", port=4002, client_id=1, mode="paper")

    @patch("ibkr_cli.health_service.container_exists", return_value=False)
    @patch("ibkr_cli.health_service.container_running", return_value=False)
    def test_gateway_health_reports_gateway_down_when_container_missing(self, _running, _exists) -> None:
        payload = gateway_health("ib-a", self.gateway(), self.profile(), profile_name="ib-a-paper")

        self.assertEqual(payload["status"], "gateway_down")
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["last_error"], "Gateway container is not running.")

    @patch("ibkr_cli.health_service.check_api_connection")
    @patch("ibkr_cli.health_service.test_tcp_connection")
    @patch("ibkr_cli.health_service.container_exists", return_value=True)
    @patch("ibkr_cli.health_service.container_running", return_value=True)
    def test_gateway_health_reports_ok_when_tcp_and_api_pass(self, _running, _exists, mock_tcp, mock_api) -> None:
        mock_tcp.return_value = ConnectionResult(ok=True, host="127.0.0.1", port=4002, timeout=2.0, latency_ms=1.0)
        mock_api.return_value = ApiConnectionResult(
            ok=True,
            host="127.0.0.1",
            port=4002,
            client_id=1,
            timeout=2.0,
            managed_accounts=["DUQ355139"],
            latency_ms=80.0,
            server_version=178,
            error=None,
        )

        payload = gateway_health("ib-a", self.gateway(), self.profile(), profile_name="ib-a-paper")

        self.assertEqual(payload["status"], "ok")
        self.assertTrue(payload["api_ok"])
        self.assertFalse(payload["needs_reauth"])

    @patch("ibkr_cli.health_service.check_api_connection")
    @patch("ibkr_cli.health_service.test_tcp_connection")
    @patch("ibkr_cli.health_service.container_exists", return_value=True)
    @patch("ibkr_cli.health_service.container_running", return_value=True)
    def test_gateway_health_reports_needs_reauth_from_api_error_text(self, _running, _exists, mock_tcp, mock_api) -> None:
        mock_tcp.return_value = ConnectionResult(ok=True, host="127.0.0.1", port=4002, timeout=2.0, latency_ms=1.0)
        mock_api.return_value = ApiConnectionResult(
            ok=False,
            host="127.0.0.1",
            port=4002,
            client_id=1,
            timeout=2.0,
            managed_accounts=[],
            error="Two-factor authentication required",
        )

        payload = gateway_health("ib-a", self.gateway(), self.profile(), profile_name="ib-a-paper")

        self.assertEqual(payload["status"], "needs_reauth")
        self.assertTrue(payload["needs_reauth"])
