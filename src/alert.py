"""Alert dispatching and event logging.

Consumes crowd count events and behavior alerts, dispatching them
via configured channels (console, sound, webhook) and logging to
a structured JSONL file.
"""

import json
import logging
import os
from datetime import datetime, timezone

import requests


logger = logging.getLogger("crowd_analysis")


class AlertManager:
    """Dispatches alerts and logs events.

    Attributes:
        crowd_thresholds: Mapping of zone name -> max crowd count.
        console_enabled: Whether to print alerts to console.
        sound_enabled: Whether to play OS alert sound.
        webhook_url: Optional URL for HTTP POST alerts.
        log_file: Path to JSONL event log.
        _active_alerts: Tracks which zones currently have active threshold alerts.
    """

    def __init__(
        self,
        crowd_thresholds: dict[str, int],
        console_enabled: bool = True,
        sound_enabled: bool = False,
        webhook_url: str | None = None,
        log_file: str = "logs/events.jsonl",
    ):
        """Initialize the alert manager.

        Args:
            crowd_thresholds: Dict of zone_name -> max crowd before alert.
            console_enabled: Enable console alert output.
            sound_enabled: Enable OS beep on alert.
            webhook_url: Optional webhook endpoint for HTTP POST alerts.
            log_file: Path to append structured event logs.
        """
        self.crowd_thresholds = crowd_thresholds
        self.console_enabled = console_enabled
        self.sound_enabled = sound_enabled
        self.webhook_url = webhook_url
        self.log_file = log_file
        self._active_alerts: set[str] = set()

        # Ensure log directory exists
        if log_file:
            os.makedirs(os.path.dirname(log_file), exist_ok=True)

    def process(
        self,
        roi_counts: dict[str, int],
        behavior_events: list,
    ) -> list[str]:
        """Process crowd counts and behavior events, dispatch alerts.

        Args:
            roi_counts: Dict of zone_name -> person count.
            behavior_events: List of BehaviorEvent objects.

        Returns:
            List of alert message strings dispatched this frame.
        """
        messages: list[str] = []

        # --- Crowd threshold alerts ---
        for zone_name, threshold in self.crowd_thresholds.items():
            count = roi_counts.get(zone_name, 0)
            if count >= threshold and zone_name not in self._active_alerts:
                msg = f"⚠ CROWD ALERT: {zone_name} has {count} persons (threshold: {threshold})"
                messages.append(msg)
                self._active_alerts.add(zone_name)
            elif count < threshold and zone_name in self._active_alerts:
                msg = f"✓ CLEARED: {zone_name} back to {count} persons"
                messages.append(msg)
                self._active_alerts.discard(zone_name)

        # --- Behavior alerts ---
        for event in behavior_events:
            msg = f"🚨 {event.behavior_type.value.upper()}: [{event.zone_name}] {event.details}"
            messages.append(msg)

        # --- Dispatch ---
        for msg in messages:
            self._dispatch(msg)

        return messages

    def _dispatch(self, message: str):
        """Send an alert through all enabled channels.

        Args:
            message: Alert message string.
        """
        # Console
        if self.console_enabled:
            logger.warning(message)

        # Sound
        if self.sound_enabled:
            print("\a", end="", flush=True)  # OS bell

        # Webhook
        if self.webhook_url:
            self._send_webhook(message)

        # Log to file
        self._log_event(message)

    def _send_webhook(self, message: str):
        """POST alert to webhook endpoint.

        Args:
            message: Alert message string.
        """
        try:
            payload = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "message": message,
            }
            requests.post(self.webhook_url, json=payload, timeout=2)
        except Exception as e:
            logger.error(f"Webhook failed: {e}")

    def _log_event(self, message: str):
        """Append a JSON line to the event log file.

        Args:
            message: Alert message string.
        """
        if not self.log_file:
            return
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message": message,
        }
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception as e:
            logger.error(f"Log write failed: {e}")
