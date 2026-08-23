#!/usr/bin/env bash
set -euo pipefail

REPO_RAW="https://raw.githubusercontent.com/FritsGroen/bunkerleiden-prototype/main"
APP_DIR="/opt/bunker-morse"
WEB_DIR="$APP_DIR/www"
SERVICE="/etc/systemd/system/bunker-morse.service"
RUN_USER="${SUDO_USER:-orangepi}"

if [ "$(id -u)" -ne 0 ]; then
  echo "Gebruik: sudo bash install_morse_bridge.sh"
  exit 1
fi

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y python3-aiohttp python3-serial curl

install -d -m 0755 "$APP_DIR" "$WEB_DIR"

curl -fsSL "$REPO_RAW/museum/museum_morse_bridge.py" -o "$APP_DIR/museum_morse_bridge.py"
chmod 0755 "$APP_DIR/museum_morse_bridge.py"

# Lokale museumkopie: blijft werken zonder internet zodra hij is geïnstalleerd.
curl -fsSL "$REPO_RAW/morse.html" -o "$WEB_DIR/morse.html"
curl -fsSL "$REPO_RAW/stichting-bunker-leiden-dark.png" -o "$WEB_DIR/stichting-bunker-leiden-dark.png"
curl -fsSL "$REPO_RAW/morse%20baumeister%20t1.png" -o "$WEB_DIR/morse baumeister t1.png"
curl -fsSL "$REPO_RAW/morse%20taster%20baumeister%20T1%20interactief%20animated" -o "$WEB_DIR/morse taster baumeister T1 interactief animated"

cat > "$SERVICE" <<EOF
[Unit]
Description=Bunker Leiden Morse ESP32 bridge
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$RUN_USER
SupplementaryGroups=dialout
Environment=MORSE_SERIAL=/dev/ttyUSB0
Environment=MORSE_BAUD=115200
Environment=MORSE_PORT=8765
Environment=MORSE_WEB_ROOT=$WEB_DIR
ExecStart=/usr/bin/python3 $APP_DIR/museum_morse_bridge.py
Restart=always
RestartSec=2

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable --now bunker-morse.service
sleep 2

echo
echo "=== Bunker Morse status ==="
systemctl --no-pager --full status bunker-morse.service | sed -n '1,14p' || true
echo
curl -fsS http://127.0.0.1:8765/status || true
echo
echo
echo "Museum Morse: http://$(hostname -I | awk '{print $1}'):8765/"
echo "ESP32: /dev/ttyUSB0 @ 115200 baud"
