# Pi MP3 E-Ink

Minimal Raspberry Pi 3B Bluetooth MP3 player with a Waveshare 2.13" e-ink display and keyboard control.

Quick start
1. Clone this repo to ~/pi-mp3-eink on your Raspberry Pi 3B and change to the repo directory.
2. Run the installer as your regular user from the repo root:
   ```bash
   ./install.sh
   ```
   This will install packages, enable SPI (if raspi-config exists), create a Python venv (.venv), install Python dependencies, clone the Waveshare e-Paper repo into ~/e-Paper, and enable/start user systemd services.
3. Copy `config.example.yaml` to `config.yaml` and set `music_dir`.
4. Pair a Bluetooth speaker with `bluetoothctl` (see below).
5. Reboot and verify both user services are running:
   ```bash
   systemctl --user status mpv.service pi-mp3-eink.service
   ```

First boot checklist
- Ensure linger is enabled so user services run on boot:
  ```bash
  sudo loginctl enable-linger $USER
  ```
- Pair and connect your Bluetooth speaker using `bluetoothctl`:
  - `scan on`
  - `pair <MAC>`
  - `trust <MAC>`
  - `connect <MAC>`
- Verify PulseAudio sinks with `pactl list short sinks` and select the sink if necessary.
- Set `music_dir` in `config.yaml` and create subfolders as playlists.

Keyboard controls
- Typing characters filters playlist names.
- SPACE → move the selection down the playlist list (wraps).
- ENTER → play the selected playlist (adds tracks to mpv via IPC).

Troubleshooting
- SPI / E-ink
  - Ensure SPI is enabled: `raspi-config nonint do_spi 0` or run `raspi-config` and enable SPI under Interface Options.
  - If the Waveshare driver import fails, verify `~/e-Paper` exists and that the Python drivers were installed into the virtualenv.
- Keyboard / evdev
  - If keys are not detected, add your user to the input group: `sudo usermod -aG input $USER` and re-login.
- MPV IPC
  - mpv runs with `--input-ipc-server=/tmp/mpv-sock`. Verify the socket exists and the mpv.service is running.

License
- MIT, see LICENSE file.
