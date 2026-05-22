import unittest

from ibkr_cli.watch_service import build_state_change_event, detect_state_change


class WatchServiceTests(unittest.TestCase):
    def test_detect_state_change_returns_none_when_status_is_unchanged(self) -> None:
        previous = {"status": "ok", "needs_reauth": False}
        current = {"status": "ok", "needs_reauth": False}

        event = detect_state_change(previous, current)

        self.assertIsNone(event)

    def test_detect_state_change_returns_needs_reauth_event(self) -> None:
        previous = {"status": "ok", "needs_reauth": False}
        current = {"status": "needs_reauth", "needs_reauth": True}

        event = detect_state_change(previous, current)

        self.assertEqual(event, "needs_reauth")

    def test_detect_state_change_returns_recovered_event(self) -> None:
        previous = {"status": "needs_reauth", "needs_reauth": True}
        current = {"status": "ok", "needs_reauth": False}

        event = detect_state_change(previous, current)

        self.assertEqual(event, "recovered")

    def test_build_state_change_event_contains_previous_and_current_status(self) -> None:
        previous = {"status": "api_down", "needs_reauth": False}
        current = {"status": "ok", "needs_reauth": False, "gateway": {"name": "ib-a"}, "profile": {"name": "ib-a-paper"}}

        payload = build_state_change_event("recovered", previous, current)

        self.assertEqual(payload["event"], "recovered")
        self.assertEqual(payload["previous_status"], "api_down")
        self.assertEqual(payload["current_status"], "ok")
        self.assertEqual(payload["gateway"]["name"], "ib-a")
