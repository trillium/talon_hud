"""Bridge: pipes Twitch chat messages from the standalone client into the HUD EventLog."""
from talon import actions, app, cron


_job = None
_callback_registered = False


def _on_message(msg):
    try:
        actions.user.hud_add_log("event", f"{msg.username}: {msg.text}")
    except Exception as e:
        print(f"Twitch HUD bridge: hud_add_log failed: {e}")


def _try_bridge():
    """Attempt to import the client and register the HUD callback."""
    global _callback_registered
    try:
        from user.trillium_talon.trillium.plugin.twitch.twitch_irc import client

        if not _callback_registered:
            client.on_message(_on_message)
            _callback_registered = True
            print("Twitch HUD bridge: callback registered")

    except Exception as e:
        print(f"Twitch HUD bridge: not ready yet: {e}")


def on_ready():
    global _job
    # Run once after a short delay, then stop polling
    _job = cron.after("3s", _try_bridge)

app.register("ready", on_ready)
