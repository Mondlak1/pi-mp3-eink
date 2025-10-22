"""
config.py — simple config loader
"""
import yaml
from pathlib import Path

DEFAULTS = {
    "music_dir": str(Path.home() / "Music"),
    "display_type": "epd2in13bc",
    "refresh_interval": 8,
    "font_path": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "font_size": 14,
    "mpv_ipc_socket": "/tmp/mpv-sock",
}

def load_config(path: str = None):
    cfg_path = Path(path or Path.cwd() / "config.yaml")
    data = DEFAULTS.copy()
    if cfg_path.exists():
        with open(cfg_path, "r", encoding="utf-8") as f:
            user = yaml.safe_load(f) or {}
            data.update(user)
    return data
