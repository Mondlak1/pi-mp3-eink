"""
eink_213bc.py — minimal e-ink wrapper using Waveshare epd2in13bc with fallback.

Draws the playlist list and now-playing info using Pillow.
"""
import time
from PIL import Image, ImageDraw, ImageFont

# Try both possible Waveshare driver names. The Waveshare repo is cloned to ~/e-Paper
try:
    # preferred import from installed waveshare package (if pip installed from e-Paper/python)
    from waveshare_epd import epd2in13bc as epd_driver
except Exception:
    try:
        from waveshare_epd import epd2in13b_V3 as epd_driver
    except Exception:
        epd_driver = None  # headless / CI fallback

class EInkDisplay:
    def __init__(self, config):
        self.config = config
        self.width = 250
        self.height = 122
        self.font = ImageFont.truetype(config.get("font_path"), config.get("font_size", 14))
        self.epd = None
        if epd_driver:
            try:
                self.epd = epd_driver.EPD()
                self.epd.init()
                self.width = self.epd.width
                self.height = self.epd.height
            except Exception:
                self.epd = None

        # last rendered timestamp (for throttling)
        self._last_render = 0

    def _new_canvas(self):
        # 3-color display (black, white, red) — we'll use an RGB image as convenience.
        return Image.new('RGB', (self.width, self.height), (255, 255, 255))

    def render(self, playlists, selected_index, now_playing=None):
        # throttle external calls to avoid too frequent refreshes
        interval = int(self.config.get("refresh_interval", 8))
        now = time.time()
        if now - self._last_render < interval:
            return
        self._last_render = now

        img = self._new_canvas()
        draw = ImageDraw.Draw(img)

        # Header: now playing
        header = now_playing or "Idle"
        draw.text((4, 2), header, font=self.font, fill=(0, 0, 0))

        # Playlist list
        y = 24
        for i, pl in enumerate(playlists):
            prefix = "→ " if i == selected_index else "  "
            text = f"{prefix}{pl['name']}"
            draw.text((4, y), text, font=self.font, fill=(0, 0, 0))
            y += self.config.get("font_size", 14) + 2
            if y > self.height - 10:
                break

        # Send to display if driver is available
        if self.epd:
            try:
                # Convert to 1-bit or the format required by driver; here we use a simple conversion.
                bw = img.convert('1')
                self.epd.display(self.epd.getbuffer(bw))
            except Exception:
                pass
        else:
            # headless: save a preview for debugging
            try:
                img.save("/tmp/pi-mp3-eink-preview.png")
            except Exception:
                pass
