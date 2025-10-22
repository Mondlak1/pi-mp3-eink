"""
keyboard_evdev.py — simple text filter + keys using python-evdev

Behavior:
- typing characters append to filter buffer (backspace supported)
- SPACE -> move selection down
- ENTER -> trigger play callback
"""
import threading
import time
from evdev import InputDevice, categorize, ecodes, list_devices
from select import select

KEY_ENTER = ecodes.KEY_ENTER
KEY_SPACE = ecodes.KEY_SPACE
KEY_BACKSPACE = ecodes.KEY_BACKSPACE

def find_keyboard_device():
    # Return the first /dev/input/event* that looks like a keyboard (simple heuristic)
    for dev_path in list_devices():
        try:
            dev = InputDevice(dev_path)
            if ecodes.EV_KEY in dev.capabilities():
                return dev_path
        except Exception:
            continue
    return None

class KeyboardHandler(threading.Thread):
    def __init__(self, on_filter_update, on_down, on_enter, device_path=None):
        super().__init__(daemon=True)
        self.on_filter_update = on_filter_update
        self.on_down = on_down
        self.on_enter = on_enter
        self.device_path = device_path or find_keyboard_device()
        self._stop = threading.Event()
        self._buffer = ""

    def run(self):
        if not self.device_path:
            # no device available
            return
        try:
            dev = InputDevice(self.device_path)
        except Exception:
            return
        try:
            dev.grab()  # try to avoid multiple readers
        except Exception:
            pass
        for event in dev.read_loop():
            if event.type != ecodes.EV_KEY:
                continue
            if event.value != 1:  # only key down events
                continue
            code = event.code
            if code == KEY_SPACE:
                self.on_down()
            elif code == KEY_ENTER:
                self.on_enter()
            elif code == KEY_BACKSPACE:
                self._buffer = self._buffer[:-1]
                self.on_filter_update(self._buffer)
            else:
                # map code to a printable char if possible
                try:
                    ch = ecodes.KEY[event.code].lstrip("KEY_")
                    if len(ch) == 1:
                        self._buffer += ch.lower()
                        self.on_filter_update(self._buffer)
                except Exception:
                    pass
            if self._stop.is_set():
                break

    def stop(self):
        self._stop.set()
"""
