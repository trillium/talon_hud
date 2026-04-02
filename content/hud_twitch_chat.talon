tag: user.talon_hud_visible
-
twitch chat show:  user.hud_add_log("event", "Twitch chat bridge is active")
twitch chat hide:  user.hud_add_log("event", "Twitch chat bridge running in background")
twitch viewers:    user.hud_add_log("event", user.twitch_stream_status())
twitch connect:    user.twitch_chat_connect()
twitch disconnect: user.twitch_chat_disconnect()
