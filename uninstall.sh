#!/bin/bash
# KomoCap Uninstaller
set -e

if [ "$EUID" -ne 0 ]; then
    echo "[ERROR] Please run as root: sudo bash uninstall.sh"
    exit 1
fi

echo "Uninstalling KomoCap..."

rm -rf  /opt/komocap
rm -f   /usr/local/bin/komocap
rm -f   /usr/share/applications/komocap.desktop
rm -f   /usr/share/pixmaps/komocap.png
for sz in 16 32 48 64 128 256; do
    rm -f "/usr/share/icons/hicolor/${sz}x${sz}/apps/komocap.png"
done

gtk-update-icon-cache /usr/share/icons/hicolor/ 2>/dev/null || true
update-desktop-database /usr/share/applications 2>/dev/null || true

echo "✓  KomoCap uninstalled."
echo "  Config file kept at: ~/.komocap3.json  (delete manually if desired)"
echo "  Captures kept at:    ~/KomoCap/         (delete manually if desired)"
