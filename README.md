# KomoCap v3.1.0

**Professional Screenshot & Screen Recording Tool for Kali Linux**

![KomoCap](assets/icons/komocap_128x128.png)

KomoCap is a clean, dark-themed screen capture suite built with PyQt5 — designed specifically for Kali Linux, Debian, and Ubuntu.

---

## Features

- **Full screen**, **area selection**, and **active window** screenshot modes
- **Screen recording** with area selection, FPS control, and quality presets
- **Audio recording** — auto-detects PipeWire (Kali default), PulseAudio, or ALSA
- **Webcam picture-in-picture** overlay during recording
- Screenshot formats: PNG, JPEG, WEBP, BMP, TIFF
- Recording formats: MP4 (H.264), MKV (Lossless)
- System tray icon with quick-access menu
- Capture history viewer with file browser
- Keyboard shortcuts: `F5` screenshot, `F9` start recording, `F10` stop

---

## Requirements

```bash
sudo apt install python3-pyqt5 ffmpeg scrot xdotool
pip3 install Pillow --break-system-packages
```

### Audio on Kali Linux (PipeWire — default since 2022)

```bash
sudo apt install pipewire pipewire-pulse wireplumber
systemctl --user enable --now pipewire pipewire-pulse wireplumber
```

### Audio on older systems (PulseAudio)

```bash
sudo apt install pulseaudio
pulseaudio --start
```

---

## Install

```bash
git clone https://github.com/Maringboy1/KomoCap.git
cd KomoCap
sudo bash install.sh
```

Then launch from terminal or Applications menu → Graphics → KomoCap.

**To add to panel:** right-click your taskbar → Add to Panel → find KomoCap.

---

## Run without installing

```bash
python3 komocap.py
```

---

## Uninstall

```bash
sudo bash uninstall.sh
```

---

## Fixes in v3.1.0

- **Area selection fixed** — overlay now uses `X11BypassWindowManagerHint` + `showFullScreen()` + keyboard grab for reliable dragging on all X11 window managers
- **Screenshot engine** — now uses `scrot` as primary engine (most reliable on X11), with Pillow as fallback
- **Audio detection** — now detects PipeWire first (Kali Linux default), falling back to PulseAudio then ALSA. No longer requires the `pulseaudio` package
- **Area screenshot** — uses `scrot --area` for pixel-accurate region capture
- Correct dependency info in Settings tab

---

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `F5` | Take screenshot |
| `F9` | Start recording |
| `F10` | Stop recording |
| `Ctrl+Q` | Quit |

---

## License

MIT — free to use, modify, and share.
