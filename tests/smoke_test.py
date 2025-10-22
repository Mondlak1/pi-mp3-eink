"""
smoke_test.py — minimal smoke test that mocks an mpv UNIX socket and imports app modules.

Run in CI to verify imports and that the MPV IPC client can connect (mock). Optional test.
"""
import socket
import os
import threading
import time

SOCK = "/tmp/mpv-sock"

def mock_mpv_server(path=SOCK, stop_after=2.0):
    if os.path.exists(path):
        os.unlink(path)
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.bind(path)
    s.listen(1)
    def _accept():
        try:
            conn, _ = s.accept()
            time.sleep(stop_after)
            conn.close()
        finally:
            s.close()
            try:
                os.unlink(path)
            except Exception:
                pass
    t = threading.Thread(target=_accept, daemon=True)
    t.start()
    return t

def run():
    t = mock_mpv_server()
    # import modules to ensure no import errors
    import src.config as cfg  # noqa
    import src.library.indexer as idx  # noqa
    import src.player.mpv_ipc as ipc  # noqa
    time.sleep(0.5)
    print("smoke test imports OK")
    t.join()

if __name__ == "__main__":
    run()
"""
