#!/bin/bash
# ============================================================
#  KomoCap v3.1.0 — Installer for Kali Linux / Debian / Ubuntu
# ============================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_NAME="KomoCap"
INSTALL_DIR="/opt/komocap"
BIN_PATH="/usr/local/bin/komocap"
DESKTOP_DIR="/usr/share/applications"
ICON_BASE="/usr/share/icons/hicolor"
PIXMAPS="/usr/share/pixmaps"

echo ""
echo "  ██╗  ██╗ ██████╗ ███╗   ███╗ ██████╗  ██████╗ █████╗ ██████╗"
echo "  ██║ ██╔╝██╔═══██╗████╗ ████║██╔═══██╗██╔════╝██╔══██╗██╔══██╗"
echo "  █████╔╝ ██║   ██║██╔████╔██║██║   ██║██║     ███████║██████╔╝"
echo "  ██╔═██╗ ██║   ██║██║╚██╔╝██║██║   ██║██║     ██╔══██║██╔═══╝"
echo "  ██║  ██╗╚██████╔╝██║ ╚═╝ ██║╚██████╔╝╚██████╗██║  ██║██║"
echo "  ╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═╝ ╚═════╝  ╚═════╝╚═╝  ╚═╝╚═╝  v3.1.0"
echo ""
echo "  Screen Capture Suite for Kali Linux"
echo "============================================================"
echo ""

# Check root
if [ "$EUID" -ne 0 ]; then
    echo "[ERROR] Please run as root: sudo bash install.sh"
    exit 1
fi

echo "[1/6] Installing system dependencies..."
apt-get install -y python3-pyqt5 ffmpeg scrot xdotool slop 2>&1 | grep -E "(install|already|error)" || true

echo "[2/6] Installing Python dependencies..."
pip3 install Pillow --break-system-packages --quiet || pip install Pillow --break-system-packages --quiet || echo "  [WARN] Could not install Pillow via pip — install manually if needed"

echo "[3/6] Copying application files..."
mkdir -p "$INSTALL_DIR"
cp "$SCRIPT_DIR/komocap.py"  "$INSTALL_DIR/komocap.py"
cp "$SCRIPT_DIR/komocap.svg" "$INSTALL_DIR/komocap.svg" 2>/dev/null || true
chmod 755 "$INSTALL_DIR/komocap.py"

echo "[4/6] Creating launcher..."
cat > "$BIN_PATH" << 'EOF'
#!/bin/bash
exec python3 /opt/komocap/komocap.py "$@"
EOF
chmod 755 "$BIN_PATH"

echo "[5/6] Installing icons..."
# Convert SVG to PNG at multiple sizes using rsvg-convert or inkscape or python
install_icon_png() {
    local size="$1"
    local dest="$ICON_BASE/${size}x${size}/apps"
    mkdir -p "$dest"
    local out="$dest/komocap.png"
    if command -v rsvg-convert &>/dev/null; then
        rsvg-convert -w "$size" -h "$size" "$INSTALL_DIR/komocap.svg" > "$out" 2>/dev/null && return
    fi
    if command -v inkscape &>/dev/null; then
        inkscape -w "$size" -h "$size" "$INSTALL_DIR/komocap.svg" -o "$out" 2>/dev/null && return
    fi
    if command -v convert &>/dev/null; then
        convert -background none -resize "${size}x${size}" "$INSTALL_DIR/komocap.svg" "$out" 2>/dev/null && return
    fi
    # Python fallback using cairosvg if available
    python3 -c "
import sys
try:
    import cairosvg
    cairosvg.svg2png(url='$INSTALL_DIR/komocap.svg', write_to='$out', output_width=$size, output_height=$size)
except Exception as e:
    sys.exit(1)
" 2>/dev/null && return
    # Last resort: copy SVG as placeholder
    cp "$INSTALL_DIR/komocap.svg" "$out" 2>/dev/null || true
}

for sz in 16 32 48 64 128 256; do
    install_icon_png "$sz"
done

mkdir -p "$PIXMAPS"
cp "$ICON_BASE/128x128/apps/komocap.png" "$PIXMAPS/komocap.png" 2>/dev/null || \
    cp "$INSTALL_DIR/komocap.svg" "$PIXMAPS/komocap.png" 2>/dev/null || true

# Update icon cache
gtk-update-icon-cache "$ICON_BASE" 2>/dev/null || true

echo "[6/6] Creating desktop entry..."
cat > "$DESKTOP_DIR/komocap.desktop" << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=KomoCap
GenericName=Screen Capture
Comment=Screenshot and screen recording tool for Kali Linux
Exec=komocap
Icon=komocap
Terminal=false
Categories=Graphics;Photography;Utility;
Keywords=screenshot;capture;record;screen;video;
StartupNotify=true
StartupWMClass=KomoCap
EOF

chmod 644 "$DESKTOP_DIR/komocap.desktop"

# Refresh desktop database
update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true

echo ""
echo "============================================================"
echo "  ✓  KomoCap v3.1.0 installed successfully!"
echo ""
echo "  Launch:   komocap"
echo "  Or find it in your Applications menu → Graphics"
echo ""
echo "  To add to panel: right-click the panel → Add to Panel"
echo "  then find KomoCap in the launcher list."
echo ""
echo "  Audio setup for Kali Linux (PipeWire):"
echo "    systemctl --user enable --now pipewire pipewire-pulse wireplumber"
echo "============================================================"
echo ""
