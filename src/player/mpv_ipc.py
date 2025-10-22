"""
mpv_ipc.py — very small MPV JSON IPC client using a unix domain socket.

NOTE: This is a minimal implementation suitable for the starter app.
"""
import json
import socket
import os
from typing import List

class MPVIPC:
    def __init__(self, socket_path="/tmp/mpv-sock", timeout=1.0):
        self.socket_path = socket_path
        self.sock = None
        self.timeout = timeout

    def _connect(self):
        if self.sock:
            return
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            self.sock.connect(self.socket_path)
            self.sock.settimeout(self.timeout)
        except Exception:
            self.sock.close()
            self.sock = None
            raise

    def _send(self, obj):
        self._connect()
        self.sock.sendall((json.dumps(obj) + "\n").encode("utf-8"))

    def command(self, args: List):
        req = {"command": args}
        try:
            self._send(req)
        except Exception:
            # reconnect once
            self.sock = None
            try:
                self._send(req)
            except Exception:
                pass

    def play_playlist(self, tracks: List[str]):
        """
        Replace mpv playlist with a .m3u virtual list by loading the first file with replace,
        then appending the remaining files. This is not perfect but works as a starter approach.
        """
        if not tracks:
            return
        # clear playlist
        try:
            self.command(["playlist-clear"])
        except Exception:
            pass
        # load first track (replace)
        try:
            self.command(["loadfile", tracks[0], "replace"])
            for t in tracks[1:]:
                self.command(["loadfile", t, "append"])
        except Exception:
            # best effort
            pass

    def close(self):
        try:
            if self.sock:
                self.sock.close()
        finally:
            self.sock = None
