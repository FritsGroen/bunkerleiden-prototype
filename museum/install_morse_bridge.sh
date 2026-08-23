#!/usr/bin/env bash
set -euo pipefail

REPO_RAW="https://raw.githubusercontent.com/FritsGroen/bunkerleiden-prototype/main"
APP_DIR="/opt/bunker-morse"
WEB_DIR="$APP_DIR/www"
TLS_DIR="$APP_DIR/tls"
SERVICE="/etc/systemd/system/bunker-morse.service"
RUN_USER="${SUDO_USER:-orangepi}"
PI_IP="${MORSE_IP:-192.168.0.68}"

if [ "$(id -u)" -ne 0 ]; then
  echo "Gebruik: sudo bash install_morse_bridge.sh"
  exit 1
fi

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y python3-aiohttp python3-serial curl openssl

install -d -m 0755 "$APP_DIR" "$WEB_DIR" "$TLS_DIR"

curl -fsSL "$REPO_RAW/museum/museum_morse_bridge.py" -o "$APP_DIR/museum_morse_bridge.py"
chmod 0755 "$APP_DIR/museum_morse_bridge.py"

# Lokale museumkopie: blijft werken zonder internet zodra hij is geïnstalleerd.
curl -fsSL "$REPO_RAW/morse.html" -o "$WEB_DIR/morse.html"
curl -fsSL "$REPO_RAW/stichting-bunker-leiden-dark.png" -o "$WEB_DIR/stichting-bunker-leiden-dark.png"
curl -fsSL "$REPO_RAW/morse%20baumeister%20t1.png" -o "$WEB_DIR/morse%20baumeister%20t1.png"
curl -fsSL "$REPO_RAW/morse%20taster%20baumeister%20T1%20interactief%20animated" -o "$WEB_DIR/morse%20taster%20baumeister%20T1%20interactief%20animated"

# Maak één lokale CA en een servercertificaat voor de Orange Pi. De CA hoeft
# maar één keer in Windows Trusted Root te worden geïmporteerd.
if [ ! -f "$TLS_DIR/bunker-morse-ca.key" ] || [ ! -f "$TLS_DIR/bunker-morse-ca.crt" ]; then
  openssl genrsa -out "$TLS_DIR/bunker-morse-ca.key" 2048
  openssl req -x509 -new -nodes -key "$TLS_DIR/bunker-morse-ca.key" -sha256 -days 3650 \
    -out "$TLS_DIR/bunker-morse-ca.crt" -subj "/CN=Bunker Leiden Museum CA" \
    -addext "basicConstraints=critical,CA:TRUE" \
    -addext "keyUsage=critical,keyCertSign,cRLSign"
fi

cat > "$TLS_DIR/server.ext" <<EOF
subjectAltName=IP:$PI_IP,DNS:orangepizero2w,DNS:orangepizero2w.local
extendedKeyUsage=serverAuth
keyUsage=digitalSignature,keyEncipherment
basicConstraints=CA:FALSE
EOF

openssl genrsa -out "$TLS_DIR/server.key" 2048
openssl req -new -key "$TLS_DIR/server.key" -out "$TLS_DIR/server.csr" -subj "/CN=$PI_IP"
openssl x509 -req -in "$TLS_DIR/server.csr" \
  -CA "$TLS_DIR/bunker-morse-ca.crt" -CAkey "$TLS_DIR/bunker-morse-ca.key" -CAcreateserial \
  -out "$TLS_DIR/server.crt" -days 365 -sha256 -extfile "$TLS_DIR/server.ext"
chmod 0600 "$TLS_DIR"/*.key
chmod 0644 "$TLS_DIR"/*.crt

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
Environment=MORSE_CERT=$TLS_DIR/server.crt
Environment=MORSE_KEY=$TLS_DIR/server.key
ExecStart=/usr/bin/python3 $APP_DIR/museum_morse_bridge.py
Restart=always
RestartSec=2

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable --now bunker-morse.service
systemctl restart bunker-morse.service
sleep 2

echo
echo "=== Bunker Morse status ==="
systemctl --no-pager --full status bunker-morse.service | sed -n '1,14p' || true
echo
curl -kfsS "https://127.0.0.1:8765/status" || true
echo
echo
echo "Museum Morse lokaal: https://$PI_IP:8765/"
echo "GitHub museumbrug: wss://$PI_IP:8765/ws"
echo "ESP32: /dev/ttyUSB0 @ 115200 baud"
echo "Windows CA-bestand: $TLS_DIR/bunker-morse-ca.crt"
