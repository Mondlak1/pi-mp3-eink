"""
indexer.py — scan music_dir for playlists (subfolders) and .m3u files.

Returns a list of playlist dicts:
  {"name": <name>, "tracks": ["/abs/path/to/file.mp3", ...]}
"""
import os
from pathlib import Path
from typing import List, Dict

AUDIO_EXTS = {'.mp3', '.ogg', '.wav', '.flac', '.m4a'}

def read_m3u(path: Path) -> List[str]:
    tracks = []
    try:
        for line in path.read_text(encoding='utf-8').splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            p = Path(line)
            if not p.is_absolute():
                p = (path.parent / p).resolve()
            if p.exists():
                tracks.append(str(p))
    except Exception:
        pass
    return tracks

def scan_playlists(music_dir: str) -> List[Dict]:
    root = Path(music_dir)
    playlists = []
    if not root.exists():
        return []
    # Subfolders as playlists
    for child in sorted(root.iterdir()):
        if child.is_dir():
            tracks = []
            for p in sorted(child.rglob("*")):
                if p.suffix.lower() in AUDIO_EXTS:
                    tracks.append(str(p.resolve()))
            if tracks:
                playlists.append({"name": child.name, "tracks": tracks})
    # .m3u files in music_dir
    for m in sorted(root.glob("*.m3u")):
        tracks = read_m3u(m)
        if tracks:
            playlists.append({"name": m.stem, "tracks": tracks})
    return playlists
