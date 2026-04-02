"""Polls Twitch Helix API for stream status and writes to mode indicator state file."""
import json
from datetime import datetime, timezone
from pathlib import Path

from talon import app, cron, settings

STATE_FILE = Path.home() / ".talon" / "user" / "trillium_talon" / "trillium" / "plugin" / "mode_indicator" / "mode_indicator_state.json"

_job = None


def _format_uptime(started_at: str) -> str:
    """Convert ISO started_at to a human-readable uptime string."""
    try:
        start = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
        delta = datetime.now(timezone.utc) - start
        total_seconds = int(delta.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes = remainder // 60
        if hours > 0:
            return f"{hours}h {minutes}m"
        return f"{minutes}m"
    except Exception:
        return ""


def _write_stream_state(live: bool, viewers: int = 0, game: str = "", title: str = "", uptime: str = ""):
    """Merge stream data into the mode indicator state JSON."""
    try:
        on_disk = json.loads(STATE_FILE.read_text()) if STATE_FILE.exists() else {}
    except Exception:
        on_disk = {}

    on_disk["stream_live"] = live
    on_disk["stream_viewers"] = viewers
    on_disk["stream_game"] = game
    on_disk["stream_title"] = title
    on_disk["stream_uptime"] = uptime

    with open(STATE_FILE, "w") as f:
        json.dump(on_disk, f, indent=2)


def _poll_status():
    """Check stream status and write to state file."""
    try:
        channel = settings.get("user.twitch_channel")
        if not channel:
            return

        from user.trillium_talon.trillium.plugin.twitch.twitch_helix import get_stream_status

        status = get_stream_status(channel)
        if status is not None:
            uptime = _format_uptime(status.started_at)
            _write_stream_state(True, status.viewer_count, status.game_name, status.title, uptime)
        else:
            _write_stream_state(False)
    except Exception as e:
        print(f"Twitch status poller: error: {e}")


def on_ready():
    global _job
    interval = settings.get("user.twitch_helix_poll_interval", "30s")
    _job = cron.interval(interval, _poll_status)


app.register("ready", on_ready)
