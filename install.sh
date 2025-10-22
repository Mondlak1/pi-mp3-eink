#!/usr/bin/env bash
set -euo pipefail

# install.sh — installer for Pi MP3 E-Ink bootstrap (user-level install)
# Run as the regular user (not root). It will ask for sudo when needed.

REPO_DIR="$(cd "");
APP_DIR="$HOME/pi-mp3-eink"
VENV_DIR="$REPO_DIR/.venv"
SYSTEMD_USER_DIR="$HOME/.config/systemd/user"

echo "This installer will set up the app in: ${REPO_DIR}"

# Ensure apt operations run with sudo
if [ "$EUID" -eq 0 ]; then
    echo "Please run install.sh as your regular user, not root. Exiting."
    exit 1
fi

echo "Updating package lists..."
sudo apt-get update

echo "Installing system packages..."
sudo apt-get install -y mpv pulseaudio pulseaudio-module-bluetooth bluez \
    python3-venv python3-pip python3-pil python3-spidev python3-rpi.gpio \
    dbus-user-session fonts-dejavu evtest git

# Enable SPI if raspi-config is available (best-effort)
if command -v raspi-config >/dev/null 2>&1; then
    echo "Enabling SPI via raspi-config (non-interactive)..."
sudo raspi-config nonint do_spi 0 || true
else
    echo "raspi-config not found; please enable SPI via raspi-config if using a Raspberry Pi."
fi

# Create systemd user dir
mkdir -p "${SYSTEMD_USER_DIR}"

# Create virtualenv in-place
if [ ! -d "${VENV_DIR}" ]; then
    echo "Creating virtualenv at ${VENV_DIR}..."
    python3 -m venv "${VENV_DIR}"
fi

"${VENV_DIR}/bin/pip" install --upgrade pip
"${VENV_DIR}/bin/pip" install -r "${REPO_DIR}/requirements.txt"

# Clone Waveshare e-Paper into $HOME/e-Paper for local drivers
EPAPER_DIR="$HOME/e-Paper"
if [ ! -d "${EPAPER_DIR}" ]; then
    echo "Cloning Waveshare e-Paper drivers to ${EPAPER_DIR}..."
    git clone https://github.com/waveshareteam/e-Paper "${EPAPER_DIR}" || true
fi

# Try to install the python drivers from the cloned repo's Python folder (best-effort)
if [ -d "${EPAPER_DIR}/python" ]; then
    echo "Installing Waveshare python drivers into virtualenv..."
    "${VENV_DIR}/bin/pip" install -e "${EPAPER_DIR}/python" || true
else
    echo "Waveshare python folder not found at ${EPAPER_DIR}/python — please inspect the e-Paper repo and install drivers manually into the virtualenv."
fi

# Install systemd user units
install -m 644 "${REPO_DIR}/systemd/mpv.service" "${SYSTEMD_USER_DIR}/mpv.service"
install -m 644 "${REPO_DIR}/systemd/pi-mp3-eink.service" "${SYSTEMD_USER_DIR}/pi-mp3-eink.service"

# Reload user systemd and enable/start units
systemctl --user daemon-reload
systemctl --user enable mpv.service pi-mp3-eink.service
systemctl --user start mpv.service pi-mp3-eink.service

# Ensure user services run at boot
sudo loginctl enable-linger "$USER" || true

echo "Install complete. Please copy config.example.yaml to config.yaml and set music_dir."
