"""
app.py — main application glue

- loads config
- indexes music_dir
- starts a keyboard handler
- updates e-ink periodically (throttled)
- sends playlist to mpv via IPC on ENTER
"""
import time
import threading
from pathlib import Path

from config import load_config
from library.indexer import scan_playlists
from player.mpv_ipc import MPVIPC
from ui.eink_213bc import EInkDisplay
from input.keyboard_evdev import KeyboardHandler

def main():
    cfg = load_config()
    music_dir = cfg["music_dir"]
    mpv = MPVIPC(cfg.get("mpv_ipc_socket", "/tmp/mpv-sock"))
    ui = EInkDisplay(cfg)

    playlists = scan_playlists(music_dir)
    filtered = playlists[:]
    selected = 0
    now_playing = None
    lock = threading.Lock()

    def refresh_ui():
        with lock:
            ui.render(filtered, selected, now_playing)

    def on_filter_update(text):
        nonlocal filtered, selected
        with lock:
            filtered = [p for p in playlists if text.lower() in p["name"].lower()]
            selected = 0
            ui.render(filtered, selected, now_playing)

    def on_down():
        nonlocal selected
        with lock:
            if not filtered:
                return
            selected = (selected + 1) % len(filtered)
            ui.render(filtered, selected, now_playing)

    def on_enter():
        nonlocal now_playing
        with lock:
            if not filtered:
                return
            pl = filtered[selected]
            now_playing = f"Playing: {pl['name']}"
            ui.render(filtered, selected, now_playing)
            try:
                mpv.play_playlist(pl["tracks"])
            except Exception:
                pass

    kb = KeyboardHandler(on_filter_update, on_down, on_enter)
    kb.start()

    # periodic index refresh + UI refresh
    try:
        while True:
            playlists = scan_playlists(music_dir)
            # simple: reset filter when playlists change
            filtered = playlists
            refresh_ui()
            time.sleep(cfg.get("refresh_interval", 8))
    except KeyboardInterrupt:
        kb.stop()

if __name__ == "__main__":
    main()
"""
