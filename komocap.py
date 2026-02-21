#!/usr/bin/env python3
"""
KomoCap v3.3.0 — Screen Capture Suite for Kali Linux
======================================================
Professional screenshot and screen recording tool for Linux.

Install:
    sudo apt install python3-pyqt5 ffmpeg scrot xdotool slop
    pip3 install Pillow --break-system-packages

For audio recording on Kali Linux (PipeWire):
    sudo apt install pipewire pipewire-pulse wireplumber
    systemctl --user enable --now pipewire pipewire-pulse wireplumber

Launch:
    python3 komocap.py
    or after install: komocap

Save location (default): ~/KomoCap/
    Screenshots  -> ~/KomoCap/Screenshots/
    Recordings   -> ~/KomoCap/Recordings/
"""

import sys, os, subprocess, datetime, json, time, threading, shutil, signal
from pathlib import Path

# ── PyQt5 ─────────────────────────────────────────────────────────
try:
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QPushButton, QLabel, QComboBox, QSlider, QCheckBox, QLineEdit,
        QFileDialog, QTabWidget, QGroupBox, QSpinBox, QSystemTrayIcon,
        QMenu, QAction, QMessageBox, QFrame, QRubberBand, QDesktopWidget,
        QShortcut, QListWidget, QListWidgetItem, QStatusBar, QTextEdit,
        QSplitter, QScrollArea, QDialog, QDialogButtonBox, QProgressBar,
        QSizePolicy, QAbstractItemView
    )
    from PyQt5.QtCore import (
        Qt, QTimer, QRect, QSize, QPoint, QThread, pyqtSignal, QEvent
    )
    from PyQt5.QtGui import (
        QColor, QPainter, QPen, QBrush, QIcon, QPixmap, QFont,
        QKeySequence, QCursor, QImage, QPainterPath, QFontMetrics, QPalette
    )
except ImportError:
    print("ERROR: PyQt5 not found.\n  sudo apt install python3-pyqt5")
    sys.exit(1)

try:
    from PIL import Image, ImageGrab
    PIL_OK = True
except ImportError:
    PIL_OK = False

# ── Constants ─────────────────────────────────────────────────────
APP_NAME    = "KomoCap"
VERSION     = "3.3.0"
HOME        = Path.home()
DEFAULT_ROOT = HOME / "KomoCap"
CONFIG_PATH  = HOME / ".komocap3.json"

# ══════════════════════════════════════════════════════════════════
#  STYLESHEET  — high-contrast, accessible, professional dark theme
# ══════════════════════════════════════════════════════════════════
STYLE = """
QMainWindow, QDialog { background: #1a1a2e; }
QWidget { background: #1a1a2e; color: #ffffff;
          font-family: 'Segoe UI', Ubuntu, Arial, sans-serif; font-size: 13px; }

/* Tabs */
QTabWidget::pane { border: 2px solid #0f3460; background: #16213e;
                   border-radius: 0 8px 8px 8px; }
QTabBar::tab { background: #0f3460; color: #90b0d0; padding: 11px 24px;
               border: none; margin-right: 3px; border-radius: 6px 6px 0 0;
               font-size: 12px; font-weight: 700; min-width: 100px; }
QTabBar::tab:selected { background: #e94560; color: #ffffff; }
QTabBar::tab:hover:!selected { background: #1a4a80; color: #ffffff; }

/* Buttons — base */
QPushButton { background: #0f3460; color: #d0e8ff; border: 1px solid #1a4a80;
              border-radius: 7px; padding: 9px 18px; font-size: 12px;
              font-weight: 700; min-height: 22px; }
QPushButton:hover { background: #1a4a80; border-color: #74b9ff; color: #ffffff; }
QPushButton:pressed { background: #e94560; border-color: #e94560; color: #ffffff; }
QPushButton:disabled { background: #141428; color: #404060; border-color: #202040; }

/* Primary — capture */
QPushButton#btnCapture { background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                            stop:0 #e94560, stop:1 #c0314c);
                          color: #ffffff; border: none; border-radius: 8px;
                          padding: 14px 30px; font-size: 14px; font-weight: 800;
                          letter-spacing: 1px; }
QPushButton#btnCapture:hover { background: #ff5577; }
QPushButton#btnCapture:disabled { background: #1e1e3e; color: #404060; }

/* Primary — record */
QPushButton#btnRecord { background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                            stop:0 #00b894, stop:1 #008f75);
                         color: #ffffff; border: none; border-radius: 8px;
                         padding: 14px 30px; font-size: 14px; font-weight: 800;
                         letter-spacing: 1px; }
QPushButton#btnRecord:hover { background: #00d4a8; }
QPushButton#btnRecord:disabled { background: #1e1e3e; color: #404060; }

/* Stop */
QPushButton#btnStop { background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                          stop:0 #d63031, stop:1 #a02020);
                       color: #ffffff; border: none; border-radius: 8px;
                       padding: 14px 30px; font-size: 14px; font-weight: 800;
                       letter-spacing: 1px; }
QPushButton#btnStop:hover { background: #ff4444; }
QPushButton#btnStop:disabled { background: #1e1e3e; color: #404060; }

/* Area select button */
QPushButton#btnSelect { background: #0f3460; color: #74b9ff;
                         border: 2px dashed #2a5090; border-radius: 7px;
                         padding: 9px 18px; font-weight: 700; font-size: 12px; }
QPushButton#btnSelect:hover { border-color: #e94560; color: #e94560;
                               background: #1a1a3e; }
QPushButton#btnSelect:checked { border: 2px solid #00b894; color: #00b894;
                                  background: #0a2020; }

/* Small utility buttons */
QPushButton#btnSmall { background: #0f3460; color: #90b0d0; border: 1px solid #1a4080;
                        border-radius: 5px; padding: 6px 14px; font-size: 11px;
                        font-weight: 600; }
QPushButton#btnSmall:hover { background: #1a4a80; color: #ffffff; }

/* GroupBox */
QGroupBox { border: 1px solid #0f3460; border-radius: 8px; margin-top: 18px;
             padding: 14px 12px 12px 12px; font-size: 11px; font-weight: 800;
             color: #74b9ff; letter-spacing: 1.5px; text-transform: uppercase; }
QGroupBox::title { subcontrol-origin: margin; left: 14px; top: -9px;
                    padding: 0 8px; background: #1a1a2e; color: #74b9ff; }

/* ComboBox */
QComboBox { background: #0f3460; color: #ffffff; border: 1px solid #1a4080;
             border-radius: 6px; padding: 7px 12px; min-width: 110px;
             font-size: 12px; font-weight: 600; }
QComboBox:hover { border-color: #e94560; }
QComboBox::drop-down { border: none; width: 22px; }
QComboBox QAbstractItemView { background: #0f3460; color: #ffffff;
                                border: 1px solid #1a4080;
                                selection-background-color: #e94560;
                                selection-color: #ffffff; outline: none;
                                font-size: 12px; }

/* SpinBox */
QSpinBox { background: #0f3460; color: #ffffff; border: 1px solid #1a4080;
            border-radius: 6px; padding: 6px 10px; font-size: 12px; font-weight: 600; }
QSpinBox:hover { border-color: #e94560; }
QSpinBox::up-button, QSpinBox::down-button { background: #1a4080; border: none; width: 18px; }
QSpinBox::up-button:hover, QSpinBox::down-button:hover { background: #e94560; }

/* LineEdit */
QLineEdit { background: #0f3460; color: #ffffff; border: 1px solid #1a4080;
             border-radius: 6px; padding: 8px 12px; font-size: 12px; }
QLineEdit:focus { border-color: #e94560; }
QLineEdit:read-only { background: #16213e; color: #90b0d0; }

/* TextEdit */
QTextEdit { background: #16213e; color: #d0e8ff; border: 1px solid #0f3460;
             border-radius: 6px; padding: 8px; font-size: 12px; }

/* Slider */
QSlider::groove:horizontal { height: 5px; background: #0f3460; border-radius: 3px; }
QSlider::handle:horizontal { background: #e94560; width: 18px; height: 18px;
                               margin: -7px 0; border-radius: 9px; border: 2px solid #fff; }
QSlider::sub-page:horizontal { background: #e94560; border-radius: 3px; }
QSlider::handle:horizontal:hover { background: #ff5577; }

/* Checkbox */
QCheckBox { color: #d0e8ff; spacing: 10px; font-size: 12px; font-weight: 600; }
QCheckBox::indicator { width: 18px; height: 18px; border: 2px solid #1a4080;
                         border-radius: 4px; background: #0f3460; }
QCheckBox::indicator:checked { background: #00b894; border-color: #00b894; }
QCheckBox::indicator:hover { border-color: #74b9ff; }

/* Labels */
QLabel { color: #d0e8ff; font-size: 12px; }
QLabel#labelTimer { color: #00b894; font-size: 38px; font-weight: 800;
                     letter-spacing: 5px; font-family: 'Courier New', monospace; }
QLabel#labelRecStatus { color: #e94560; font-size: 12px; font-weight: 800;
                          letter-spacing: 2px; }
QLabel#labelGreen { color: #00b894; font-size: 12px; font-weight: 700; }
QLabel#labelHint { color: #5878a0; font-size: 11px; }
QLabel#labelAreaInfo { background: #0a2020; color: #00b894; border: 1px solid #00b894;
                         border-radius: 5px; padding: 5px 12px; font-size: 11px;
                         font-weight: 700; }
QLabel#labelAreaNone { background: #16213e; color: #4a6888; border: 1px dashed #2a4070;
                         border-radius: 5px; padding: 5px 12px; font-size: 11px; }

/* Status bar */
QStatusBar { background: #16213e; color: #74b9ff; border-top: 1px solid #0f3460;
              font-size: 11px; padding: 3px 10px; }
QStatusBar::item { border: none; }

/* List */
QListWidget { background: #16213e; color: #d0e8ff; border: 1px solid #0f3460;
               border-radius: 6px; outline: none; font-size: 12px; }
QListWidget::item { padding: 9px 12px; border-bottom: 1px solid #1a2a4a; }
QListWidget::item:selected { background: #e94560; color: #ffffff; }
QListWidget::item:hover:!selected { background: #0f3460; }

/* Scrollbars */
QScrollBar:vertical { background: #16213e; width: 8px; border-radius: 4px; }
QScrollBar::handle:vertical { background: #0f3460; border-radius: 4px; min-height: 24px; }
QScrollBar::handle:vertical:hover { background: #e94560; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal { background: #16213e; height: 8px; }
QScrollBar::handle:horizontal { background: #0f3460; border-radius: 4px; }
QScrollBar::handle:horizontal:hover { background: #e94560; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }

/* Menu */
QMenu { background: #0f3460; border: 1px solid #1a4080; border-radius: 6px;
         padding: 5px; color: #ffffff; }
QMenu::item { padding: 8px 22px; border-radius: 4px; font-size: 12px; }
QMenu::item:selected { background: #e94560; color: #ffffff; }
QMenu::separator { background: #1a4080; height: 1px; margin: 4px 10px; }
"""


# ══════════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════════
def ts():
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

def human_size(path):
    try:
        b = os.path.getsize(path)
        for unit in ["B", "KB", "MB", "GB"]:
            if b < 1024:
                return f"{b:.0f} {unit}"
            b /= 1024
        return f"{b:.1f} GB"
    except Exception:
        return ""

def cmd_ok(name):
    return shutil.which(name) is not None

def ensure_dirs(*dirs):
    for d in dirs:
        os.makedirs(d, exist_ok=True)

def detect_audio_source():
    """
    Detect the best audio input source for ffmpeg.
    Supports PipeWire (Kali Linux default), PulseAudio, and ALSA.
    Returns (driver, source_string).
    """
    # 1. Try PipeWire via pw-cli (Kali Linux default since 2022)
    try:
        r = subprocess.run(
            ["pw-cli", "list-objects", "Node"],
            capture_output=True, text=True, timeout=3
        )
        if r.returncode == 0 and r.stdout.strip():
            # PipeWire is running — use pulse driver which PipeWire implements
            # Try pactl first (works with pipewire-pulse)
            r2 = subprocess.run(
                ["pactl", "list", "short", "sources"],
                capture_output=True, text=True, timeout=3
            )
            if r2.returncode == 0 and r2.stdout.strip():
                lines = r2.stdout.strip().splitlines()
                for line in lines:
                    if "monitor" not in line.lower():
                        parts = line.split()
                        if len(parts) >= 2:
                            return ("pulse", parts[1])
                parts = lines[0].split()
                if len(parts) >= 2:
                    return ("pulse", parts[1])
            return ("pulse", "default")
    except Exception:
        pass

    # 2. Try PulseAudio via pactl
    try:
        r = subprocess.run(
            ["pactl", "list", "short", "sources"],
            capture_output=True, text=True, timeout=3
        )
        if r.returncode == 0 and r.stdout.strip():
            lines = r.stdout.strip().splitlines()
            for line in lines:
                if "monitor" not in line.lower():
                    parts = line.split()
                    if len(parts) >= 2:
                        return ("pulse", parts[1])
            parts = lines[0].split()
            if len(parts) >= 2:
                return ("pulse", parts[1])
            return ("pulse", "default")
    except Exception:
        pass

    # 3. Try pulseaudio --check
    try:
        r = subprocess.run(
            ["pulseaudio", "--check"],
            capture_output=True, timeout=2
        )
        if r.returncode == 0:
            return ("pulse", "default")
    except Exception:
        pass

    # 4. Fallback to ALSA
    try:
        r = subprocess.run(["arecord", "-l"], capture_output=True, text=True, timeout=3)
        if r.returncode == 0 and "card" in r.stdout:
            return ("alsa", "hw:0,0")
    except Exception:
        pass

    # 5. Last resort: try pulse default anyway (pipewire-pulse may answer)
    return ("pulse", "default")


# ══════════════════════════════════════════════════════════════════
#  NATIVE AREA SELECTOR  — uses slop or scrot --select (X11 native)
#  Falls back to a PyQt overlay only if neither tool is available.
# ══════════════════════════════════════════════════════════════════

def _select_area_native():
    """
    Use a native X11 selection tool to let the user drag a region.
    Returns QRect on success, None on cancel/failure.

    Priority:
      1. slop   — dedicated rubber-band selection tool, works with any compositor
      2. scrot -s — built-in selection mode
    """
    # ── 1. slop ──────────────────────────────────────────────────
    if shutil.which("slop"):
        try:
            r = subprocess.run(
                [
                    "slop",
                    "--highlight",
                    "--tolerance=0",
                    "--color=0.91,0.27,0.38,0.4",   # red tint fill
                    "--bordersize=2",
                    "--padding=0",
                    "--format=%x %y %w %h",
                ],
                capture_output=True, text=True, timeout=60
            )
            if r.returncode == 0:
                parts = r.stdout.strip().split()
                if len(parts) == 4:
                    x, y, w, h = int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3])
                    if w > 4 and h > 4:
                        return QRect(x, y, w, h)
            return None   # user pressed ESC / cancelled
        except Exception:
            pass

    # ── 2. scrot --select ────────────────────────────────────────
    if shutil.which("scrot"):
        tmp = f"/tmp/_komocap_sel_{os.getpid()}.png"
        try:
            r = subprocess.run(
                ["scrot", "--select", "--overwrite", tmp],
                capture_output=True, timeout=60
            )
            if r.returncode == 0 and os.path.exists(tmp):
                from PIL import Image as _Img
                img = _Img.open(tmp)
                w, h = img.size
                os.unlink(tmp)
                if w > 4 and h > 4:
                    # scrot --select doesn't tell us x,y — we only get w,h.
                    # Return a QRect at (0,0) with the correct size;
                    # the caller will use the saved file directly.
                    return QRect(0, 0, w, h)
            elif os.path.exists(tmp):
                os.unlink(tmp)
            return None
        except Exception:
            pass

    return None   # nothing available — caller will fall back to PyQt


class AreaSelector(QWidget):
    """
    Full-screen area selector.

    FIRST tries native X11 tools (slop / scrot --select) which work
    perfectly with any compositor / transparent theme.

    Falls back to a pure-PyQt overlay only when neither tool exists.
    The PyQt overlay takes a full-screen screenshot first so it is
    fully opaque — no transparency tricks that break mouse events.
    """
    area_selected = pyqtSignal(QRect)
    cancelled     = pyqtSignal()

    # ── public entry point ────────────────────────────────────────
    def start(self):
        """
        Try native tools first. If they exist, run them in a thread
        and emit signals when done. Otherwise fall back to PyQt overlay.
        """
        if shutil.which("slop") or shutil.which("scrot"):
            self._run_native()
        else:
            self._run_pyqt()

    # ── native path ───────────────────────────────────────────────
    def _run_native(self):
        self._thread = _SlopThread()
        self._thread.done.connect(self._on_native_done)
        self._thread.start()

    def _on_native_done(self, rect):
        if rect.isNull() or rect.width() < 4 or rect.height() < 4:
            self.cancelled.emit()
        else:
            self.area_selected.emit(rect)

    # ── PyQt fallback overlay ─────────────────────────────────────
    def _run_pyqt(self):
        self._overlay = _AreaOverlay()
        self._overlay.area_selected.connect(self.area_selected)
        self._overlay.cancelled.connect(self.cancelled)
        self._overlay.show_overlay()


class _SlopThread(QThread):
    """Runs slop / scrot --select in a background thread."""
    done = pyqtSignal(QRect)

    def run(self):
        rect = _select_area_native()
        self.done.emit(rect if rect else QRect())


class _AreaOverlay(QWidget):
    """
    Pure-PyQt fullscreen overlay (fallback when slop/scrot not available).
    Takes a screenshot first so the window is fully opaque — avoids all
    compositor / transparency issues with mouse event delivery.
    """
    area_selected = pyqtSignal(QRect)
    cancelled     = pyqtSignal()

    def __init__(self):
        super().__init__()
        screen        = QDesktopWidget().screenGeometry()
        self._srect   = screen
        self._bg      = None
        self._origin  = QPoint()
        self._sel     = QRect()
        self._drag    = False
        self._done    = False

        self.setGeometry(screen)
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.X11BypassWindowManagerHint
        )
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setCursor(QCursor(Qt.CrossCursor))
        self.setFocusPolicy(Qt.StrongFocus)
        self.setMouseTracking(True)

    def show_overlay(self):
        # Grab screenshot NOW (before window appears)
        self._bg = self._grab_screen()
        self.showFullScreen()
        self.activateWindow()
        self.raise_()
        self.setFocus()
        self.grabKeyboard()

    @staticmethod
    def _grab_screen():
        tmp = f"/tmp/_komocap_bg_{os.getpid()}.png"
        if shutil.which("scrot"):
            try:
                r = subprocess.run(["scrot", "--overwrite", tmp],
                                   capture_output=True, timeout=5)
                if r.returncode == 0 and os.path.exists(tmp):
                    pix = QPixmap(tmp)
                    os.unlink(tmp)
                    if not pix.isNull():
                        return pix
            except Exception:
                pass
        try:
            screen = QApplication.instance().primaryScreen()
            return screen.grabWindow(0)
        except Exception:
            pass
        pix = QPixmap(1920, 1080)
        pix.fill(QColor(20, 20, 40))
        return pix

    def paintEvent(self, _e):
        p = QPainter(self)

        # 1. Real screenshot background
        if self._bg and not self._bg.isNull():
            p.drawPixmap(0, 0, self._bg)
        else:
            p.fillRect(self.rect(), QColor(20, 20, 40))

        # 2. Dark overlay
        p.fillRect(self.rect(), QColor(0, 0, 0, 160))

        sel = self._sel
        if not sel.isNull() and sel.width() > 4 and sel.height() > 4:

            # 3. Reveal original under selection
            if self._bg and not self._bg.isNull():
                p.drawPixmap(sel, self._bg, sel)

            # 4. Red border
            p.setPen(QPen(QColor(233, 69, 96), 2))
            p.setBrush(Qt.NoBrush)
            p.drawRect(sel)

            # 5. Handles
            hs = 8
            corners = [
                sel.topLeft(),    sel.topRight(),
                sel.bottomLeft(), sel.bottomRight(),
                QPoint(sel.center().x(), sel.top()),
                QPoint(sel.center().x(), sel.bottom()),
                QPoint(sel.left(),  sel.center().y()),
                QPoint(sel.right(), sel.center().y()),
            ]
            p.setBrush(QBrush(QColor(233, 69, 96)))
            p.setPen(QPen(QColor(255, 255, 255), 1))
            for pt in corners:
                p.drawRect(pt.x() - hs//2, pt.y() - hs//2, hs, hs)

            # 6. Size badge
            txt  = f"  {sel.width()} × {sel.height()} px  "
            font = QFont("Monospace", 11, QFont.Bold)
            p.setFont(font)
            fm   = QFontMetrics(font)
            tw, th = fm.horizontalAdvance(txt), fm.height()
            bx = max(sel.x(), 4)
            by = sel.y() - th - 10
            if by < 50:
                by = sel.y() + sel.height() + 6
            p.setBrush(QBrush(QColor(233, 69, 96, 230)))
            p.setPen(Qt.NoPen)
            p.drawRoundedRect(bx, by, tw + 6, th + 8, 4, 4)
            p.setPen(QColor(255, 255, 255))
            p.drawText(bx + 3, by + th + 3, txt)

        # 7. Instruction bar
        p.fillRect(0, 0, self.width(), 44, QColor(10, 15, 40, 230))
        p.setPen(QColor(255, 255, 255))
        p.setFont(QFont("Arial", 12, QFont.Bold))
        p.drawText(0, 0, self.width(), 44, Qt.AlignCenter,
                   "Click and drag to select area   ·   Release to confirm   ·   ESC = cancel")

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self._origin = e.pos()
            self._sel    = QRect()
            self._drag   = True
            self.update()

    def mouseMoveEvent(self, e):
        if self._drag:
            self._sel = QRect(self._origin, e.pos()).normalized()
            self.update()

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton and self._drag:
            self._drag = False
            self._sel  = QRect(self._origin, e.pos()).normalized()
            self.update()
            if self._sel.width() > 10 and self._sel.height() > 10:
                self._finish(True)
            else:
                self._finish(False)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self._finish(False)
        elif e.key() in (Qt.Key_Return, Qt.Key_Enter):
            if not self._sel.isNull():
                self._finish(True)

    def _finish(self, ok):
        if self._done:
            return
        self._done = True
        self.releaseKeyboard()
        self.hide()
        if ok:
            self.area_selected.emit(self._sel.normalized())
        else:
            self.cancelled.emit()
        self.close()


# ══════════════════════════════════════════════════════════════════
#  RECORDER THREAD
# ══════════════════════════════════════════════════════════════════
class RecorderThread(QThread):
    sig_status = pyqtSignal(str)
    sig_done   = pyqtSignal(str)
    sig_error  = pyqtSignal(str)

    # quality_index -> (crf, preset)
    QUALITY = {0: (45, "ultrafast"),
               1: (28, "fast"),
               2: (18, "medium"),
               3: (12, "slow"),
               4: (0,  "veryslow")}

    def __init__(self, cfg: dict):
        super().__init__()
        self.cfg   = cfg
        self._proc = None
        self._stop = threading.Event()

    def run(self):
        cfg    = self.cfg
        area   = cfg.get("area")
        fps    = cfg.get("fps", 30)
        qi     = cfg.get("quality", 2)
        audio  = cfg.get("audio", False)
        webcam = cfg.get("webcam", False)
        out    = cfg.get("output", "/tmp/komocap_rec.mp4")

        crf, preset = self.QUALITY.get(qi, (18, "medium"))

        # Screen geometry
        screen = QDesktopWidget().screenGeometry()
        if area and not area.isNull():
            x, y   = area.x(), area.y()
            w, h   = area.width() & ~1, area.height() & ~1
        else:
            x, y   = 0, 0
            w, h   = screen.width() & ~1, screen.height() & ~1

        if w < 2 or h < 2:
            self.sig_error.emit("Selected area is too small.")
            return

        display = os.environ.get("DISPLAY", ":0")
        ext     = ".mkv" if qi == 4 else ".mp4"
        final   = os.path.splitext(out)[0] + ext

        # ── Build ffmpeg command ─────────────────────────────────
        cmd = [
            "ffmpeg", "-y",
            "-f", "x11grab",
            "-r", str(fps),
            "-s", f"{w}x{h}",
            "-i", f"{display}+{x},{y}",
        ]

        audio_idx = None
        if audio:
            driver, src = detect_audio_source()
            audio_idx   = 1
            if driver == "pulse":
                cmd += ["-f", "pulse", "-i", src]
            else:
                cmd += ["-f", "alsa", "-i", src]

        webcam_idx = None
        if webcam and os.path.exists("/dev/video0"):
            webcam_idx = (audio_idx + 1) if audio_idx else 1
            cmd += ["-f", "v4l2", "-i", "/dev/video0"]

        # ── Filters ─────────────────────────────────────────────
        if webcam_idx is not None:
            sz_map  = {"small": "240:180", "medium": "320:240", "large": "480:360"}
            sz      = sz_map.get(cfg.get("webcam_size", "small"), "240:180")
            pos_map = {
                "bottom-right": "W-w-12:H-h-12",
                "bottom-left":  "12:H-h-12",
                "top-right":    "W-w-12:12",
                "top-left":     "12:12",
            }
            overlay = pos_map.get(cfg.get("webcam_pos", "bottom-right"), "W-w-12:H-h-12")
            fc = (f"[{webcam_idx}:v]scale={sz},format=yuv420p[cam];"
                  f"[0:v][cam]overlay={overlay}[out]")
            cmd += ["-filter_complex", fc, "-map", "[out]"]
            if audio_idx:
                cmd += ["-map", f"{audio_idx}:a"]
        else:
            cmd += ["-vf", f"scale={w}:{h}"]

        # ── Codec ────────────────────────────────────────────────
        cmd += [
            "-c:v", "libx264",
            "-crf", str(crf),
            "-preset", preset,
            "-pix_fmt", "yuv420p",
            "-movflags", "+faststart",
        ]
        if audio_idx:
            cmd += ["-c:a", "aac", "-b:a", "192k", "-ac", "2",
                    "-ar", "44100"]

        cmd.append(final)

        # ── Run ──────────────────────────────────────────────────
        try:
            self._proc = subprocess.Popen(
                cmd,
                stdin  = subprocess.PIPE,
                stdout = subprocess.DEVNULL,
                stderr = subprocess.PIPE,
            )
            self.sig_status.emit("RECORDING")
            self._proc.wait()

            stderr_bytes = b""
            try:
                stderr_bytes = self._proc.stderr.read(3000)
            except Exception:
                pass

            if self._stop.is_set() or os.path.exists(final):
                self.sig_done.emit(final)
            else:
                self.sig_error.emit(
                    f"Recording failed (exit {self._proc.returncode}).\n"
                    + stderr_bytes.decode(errors="replace")[-600:]
                )
        except FileNotFoundError:
            self.sig_error.emit("ffmpeg not found.\n  sudo apt install ffmpeg")
        except Exception as e:
            self.sig_error.emit(f"Error: {e}")

    def stop(self):
        self._stop.set()
        if self._proc and self._proc.poll() is None:
            try:
                self._proc.stdin.write(b"q\n")
                self._proc.stdin.flush()
            except Exception:
                pass
            try:
                self._proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._proc.terminate()


# ══════════════════════════════════════════════════════════════════
#  SCREENSHOT WORKER
# ══════════════════════════════════════════════════════════════════
class ScreenshotWorker(QThread):
    sig_done  = pyqtSignal(str)
    sig_error = pyqtSignal(str)

    def __init__(self, cfg: dict):
        super().__init__()
        self.cfg = cfg

    def run(self):
        cfg  = self.cfg
        mode = cfg.get("mode", "full")
        area = cfg.get("area")
        fmt  = cfg.get("format", "PNG")
        q    = cfg.get("quality", 95)
        out  = cfg.get("output")

        ext_map = {"PNG": ".png", "JPEG": ".jpg", "WEBP": ".webp",
                   "BMP": ".bmp", "TIFF": ".tif"}
        path = os.path.splitext(out)[0] + ext_map.get(fmt, ".png")

        try:
            if mode == "window":
                img = self._grab_window()
            elif mode == "area" and area and not area.isNull():
                img = self._grab_area(area)
            else:
                img = self._grab_full()

            if img is None:
                self.sig_error.emit("Screenshot capture returned no image. Check display.")
                return

            kw = {}
            if fmt == "JPEG":
                kw["quality"] = q
                kw["subsampling"] = 0
                img = img.convert("RGB")
            elif fmt == "WEBP":
                kw["quality"] = q
            elif fmt == "PNG":
                kw["optimize"] = True

            img.save(path, fmt, **kw)
            self.sig_done.emit(path)

        except Exception as e:
            self.sig_error.emit(str(e))

    def _grab_full(self):
        """Capture full screen — tries scrot first (most reliable on X11), then PIL."""
        if cmd_ok("scrot"):
            tmp = f"/tmp/komocap_ss_{os.getpid()}.png"
            try:
                r = subprocess.run(
                    ["scrot", "--overwrite", tmp],
                    capture_output=True, timeout=8
                )
                if r.returncode == 0 and os.path.exists(tmp):
                    img = Image.open(tmp).copy()
                    os.unlink(tmp)
                    return img
            except Exception:
                pass
        # PIL fallback
        if PIL_OK:
            return ImageGrab.grab()
        raise RuntimeError("No screenshot tool available. Install scrot: sudo apt install scrot")

    def _grab_area(self, area):
        """Capture a specific region — scrot first, then PIL."""
        x, y, w, h = area.x(), area.y(), area.width(), area.height()
        if cmd_ok("scrot"):
            tmp = f"/tmp/komocap_ss_{os.getpid()}.png"
            try:
                r = subprocess.run(
                    ["scrot", "--overwrite",
                     "--area", f"{x},{y},{w},{h}", tmp],
                    capture_output=True, timeout=8
                )
                if r.returncode == 0 and os.path.exists(tmp):
                    img = Image.open(tmp).copy()
                    os.unlink(tmp)
                    return img
            except Exception:
                pass
        # PIL fallback
        if PIL_OK:
            return ImageGrab.grab(bbox=(x, y, x + w, y + h))
        raise RuntimeError("Area capture failed. Install scrot: sudo apt install scrot")

    def _grab_window(self):
        try:
            wid = subprocess.check_output(
                ["xdotool", "getactivewindow"], text=True, timeout=3
            ).strip()
            geo = subprocess.check_output(
                ["xdotool", "getwindowgeometry", "--shell", wid],
                text=True, timeout=3
            )
            info = {}
            for line in geo.strip().splitlines():
                k, _, v = line.partition("=")
                info[k.strip()] = v.strip()
            x = int(info.get("X", 0))
            y = int(info.get("Y", 0))
            w = int(info.get("WIDTH", 1280))
            h = int(info.get("HEIGHT", 720))
            # Use QRect for area grab
            from PyQt5.QtCore import QRect as _QRect
            return self._grab_area(_QRect(x, y, w, h))
        except Exception:
            return self._grab_full()


# ══════════════════════════════════════════════════════════════════
#  CLICKABLE PREVIEW LABEL
# ══════════════════════════════════════════════════════════════════
class PreviewLabel(QLabel):
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self._path = None

    def set_image(self, path):
        self._path = path
        pix = QPixmap(path)
        if not pix.isNull():
            scaled = pix.scaled(
                max(self.width() - 8, 100),
                max(self.height() - 8, 60),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.setPixmap(scaled)
            self.setToolTip(f"Click to open: {path}")

    def mousePressEvent(self, _event):
        if self._path and os.path.exists(self._path):
            subprocess.Popen(["xdg-open", self._path])


# ══════════════════════════════════════════════════════════════════
#  MAIN WINDOW
# ══════════════════════════════════════════════════════════════════
class KomoCap(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME}  {VERSION}")
        self.setMinimumSize(860, 680)
        self.resize(960, 740)
        self.setStyleSheet(STYLE)

        # State
        self.ss_area_rect  = None
        self.ss_mode       = "full"   # full / area / window
        self.rec_area_rect = None
        self.rec_mode_sel  = "full"   # full / area
        self.recorder      = None
        self.ss_worker     = None
        self.rec_seconds   = 0
        self.last_ss_path  = None
        self.recent_files  = []

        self._rec_tick_timer = QTimer()
        self._rec_tick_timer.timeout.connect(self._tick)

        self._load_config()
        ensure_dirs(self.ss_dir, self.rec_dir)
        self._build_ui()
        self._build_shortcuts()
        self._build_tray()
        self._set_status(f"Ready  ·  Files saved to: {self.root_dir}", "ok")

    # ── Config ────────────────────────────────────────────────────
    def _load_config(self):
        defaults = {
            "root_dir":    str(DEFAULT_ROOT),
            "ss_format":   "PNG",
            "ss_quality":  95,
            "ss_delay":    0,
            "rec_fps":     30,
            "rec_quality": 2,
            "rec_audio":   True,
            "rec_webcam":  False,
            "webcam_pos":  "bottom-right",
            "webcam_size": "small",
        }
        try:
            with open(CONFIG_PATH) as f:
                cfg = {**defaults, **json.load(f)}
        except Exception:
            cfg = defaults
        self._apply_paths(cfg)

    def _apply_paths(self, cfg):
        self.config   = cfg
        root          = Path(cfg["root_dir"])
        self.root_dir = str(root)
        self.ss_dir   = str(root / "Screenshots")
        self.rec_dir  = str(root / "Recordings")

    def _save_config(self):
        try:
            with open(CONFIG_PATH, "w") as f:
                json.dump(self.config, f, indent=2)
        except Exception:
            pass

    # ── UI ────────────────────────────────────────────────────────
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root_lay = QVBoxLayout(central)
        root_lay.setContentsMargins(0, 0, 0, 0)
        root_lay.setSpacing(0)
        root_lay.addWidget(self._make_header())

        content = QWidget()
        cl = QVBoxLayout(content)
        cl.setContentsMargins(18, 14, 18, 12)
        self.tabs = QTabWidget()
        self._build_tab_screenshot()
        self._build_tab_recording()
        self._build_tab_history()
        self._build_tab_settings()
        cl.addWidget(self.tabs)
        root_lay.addWidget(content)

        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

    def _make_header(self):
        hdr = QWidget()
        hdr.setFixedHeight(58)
        hdr.setStyleSheet(
            "background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            " stop:0 #0a1628, stop:1 #16213e);"
            "border-bottom: 2px solid #e94560;"
        )
        hl = QHBoxLayout(hdr)
        hl.setContentsMargins(20, 0, 20, 0)

        logo = QLabel()
        logo.setText(
            "<span style='color:#ffffff;font-size:19px;font-weight:900;"
            "letter-spacing:4px;'>KOMO</span>"
            "<span style='color:#e94560;font-size:19px;font-weight:900;"
            "letter-spacing:4px;'>CAP</span>"
            "<span style='color:#4a7aaa;font-size:10px;letter-spacing:2px;'>"
            "  v3.0  Enterprise</span>"
        )
        logo.setTextFormat(Qt.RichText)

        self.hdr_rec_badge = QLabel("  ● REC  00:00  ")
        self.hdr_rec_badge.setStyleSheet(
            "background: #e94560; color: #ffffff; border-radius: 5px;"
            "padding: 4px 12px; font-size: 11px; font-weight: 900; letter-spacing: 1px;"
        )
        self.hdr_rec_badge.setVisible(False)

        self.hdr_path_lbl = QLabel(f"📁  {self.root_dir}")
        self.hdr_path_lbl.setStyleSheet("color: #4a7aaa; font-size: 10px;")

        hl.addWidget(logo)
        hl.addSpacing(16)
        hl.addWidget(self.hdr_rec_badge)
        hl.addStretch()
        hl.addWidget(self.hdr_path_lbl)
        return hdr

    # ──────────────────────────────────────────────────────────────
    #  TAB — SCREENSHOT
    # ──────────────────────────────────────────────────────────────
    def _build_tab_screenshot(self):
        tab = QWidget()
        lay = QVBoxLayout(tab)
        lay.setSpacing(14)

        # Capture Mode
        mg = QGroupBox("Capture Mode")
        ml = QHBoxLayout(mg)
        ml.setSpacing(10)

        self.ss_btn_full   = QPushButton("🖥   Full Screen")
        self.ss_btn_area   = QPushButton("⬚   Select Area")
        self.ss_btn_window = QPushButton("▣   Active Window")
        self.ss_btn_area.setObjectName("btnSelect")

        for b in [self.ss_btn_full, self.ss_btn_area, self.ss_btn_window]:
            b.setCheckable(True)
            b.setMinimumWidth(130)
        self.ss_btn_full.setChecked(True)

        self.ss_btn_full.clicked.connect(lambda: self._ss_set_mode("full"))
        self.ss_btn_area.clicked.connect(self._ss_open_area_selector)
        self.ss_btn_window.clicked.connect(lambda: self._ss_set_mode("window"))

        self.ss_area_label = QLabel("No area selected — using full screen")
        self.ss_area_label.setObjectName("labelAreaNone")

        ml.addWidget(self.ss_btn_full)
        ml.addWidget(self.ss_btn_area)
        ml.addWidget(self.ss_btn_window)
        ml.addSpacing(10)
        ml.addWidget(self.ss_area_label)
        ml.addStretch()
        lay.addWidget(mg)

        # Format & Quality
        fqg = QGroupBox("Format & Quality")
        fql = QHBoxLayout(fqg)
        fql.addWidget(QLabel("Format:"))
        self.ss_fmt = QComboBox()
        self.ss_fmt.addItems(["PNG", "JPEG", "WEBP", "BMP", "TIFF"])
        self.ss_fmt.setCurrentText(self.config["ss_format"])
        self.ss_fmt.currentTextChanged.connect(self._ss_fmt_changed)
        fql.addWidget(self.ss_fmt)
        fql.addSpacing(24)
        self._ss_q_lbl = QLabel("Quality:")
        fql.addWidget(self._ss_q_lbl)
        self.ss_quality = QSlider(Qt.Horizontal)
        self.ss_quality.setRange(1, 100)
        self.ss_quality.setValue(self.config["ss_quality"])
        self.ss_quality.setFixedWidth(140)
        self.ss_q_val = QLabel(f"{self.config['ss_quality']}%")
        self.ss_q_val.setObjectName("labelGreen")
        self.ss_q_val.setMinimumWidth(44)
        self.ss_quality.valueChanged.connect(lambda v: self.ss_q_val.setText(f"{v}%"))
        fql.addWidget(self.ss_quality)
        fql.addWidget(self.ss_q_val)
        fql.addStretch()
        self._ss_fmt_changed(self.config["ss_format"])
        lay.addWidget(fqg)

        # Options
        og = QGroupBox("Options")
        ol = QHBoxLayout(og)
        ol.addWidget(QLabel("Capture delay:"))
        self.ss_delay = QSpinBox()
        self.ss_delay.setRange(0, 30)
        self.ss_delay.setSuffix("  sec")
        self.ss_delay.setValue(self.config["ss_delay"])
        ol.addWidget(self.ss_delay)
        ol.addSpacing(28)
        self.ss_clip = QCheckBox("Copy to clipboard after capture")
        ol.addWidget(self.ss_clip)
        ol.addStretch()
        lay.addWidget(og)

        # Preview
        pvg = QGroupBox("Preview — click image to open")
        pvl = QVBoxLayout(pvg)
        self.ss_preview = PreviewLabel("No screenshot yet — press Capture below")
        self.ss_preview.setAlignment(Qt.AlignCenter)
        self.ss_preview.setFixedHeight(175)
        self.ss_preview.setStyleSheet(
            "background: #16213e; border: 1px dashed #1a3060;"
            "border-radius: 6px; color: #405070; font-size: 12px;"
        )
        pvl.addWidget(self.ss_preview)
        lay.addWidget(pvg)
        lay.addStretch()

        # Actions
        ar = QHBoxLayout()
        ar.setSpacing(10)
        self.ss_btn_capture = QPushButton("📷    CAPTURE SCREENSHOT    [ F5 ]")
        self.ss_btn_capture.setObjectName("btnCapture")
        self.ss_btn_capture.clicked.connect(self.take_screenshot)

        btn_open = QPushButton("Open Last")
        btn_open.setObjectName("btnSmall")
        btn_open.clicked.connect(self._open_last_ss)

        btn_folder = QPushButton("Open Folder")
        btn_folder.setObjectName("btnSmall")
        btn_folder.clicked.connect(lambda: subprocess.Popen(["xdg-open", self.ss_dir]))

        ar.addWidget(self.ss_btn_capture)
        ar.addSpacing(6)
        ar.addWidget(btn_open)
        ar.addWidget(btn_folder)
        lay.addLayout(ar)

        self.tabs.addTab(tab, "📷  Screenshot")

    def _ss_fmt_changed(self, fmt):
        lossy = fmt in ("JPEG", "WEBP")
        self.ss_quality.setEnabled(lossy)
        self._ss_q_lbl.setEnabled(lossy)
        self.ss_q_val.setEnabled(lossy)
        if not lossy:
            self.ss_q_val.setText("—")

    def _ss_set_mode(self, mode):
        self.ss_mode = mode
        self.ss_btn_full.setChecked(mode == "full")
        self.ss_btn_area.setChecked(mode == "area")
        self.ss_btn_window.setChecked(mode == "window")
        if mode != "area":
            self.ss_area_rect = None
            self.ss_area_label.setText("No area selected — using full screen")
            self.ss_area_label.setObjectName("labelAreaNone")
            self.ss_area_label.setStyle(self.ss_area_label.style())

    def _ss_open_area_selector(self):
        self.ss_btn_area.setChecked(True)
        self._open_selector("screenshot")

    # ──────────────────────────────────────────────────────────────
    #  TAB — RECORDING
    # ──────────────────────────────────────────────────────────────
    def _build_tab_recording(self):
        tab = QWidget()
        lay = QVBoxLayout(tab)
        lay.setSpacing(14)

        # Area
        ag = QGroupBox("Recording Area")
        al = QHBoxLayout(ag)
        al.setSpacing(10)

        self.rec_btn_full = QPushButton("🖥   Full Screen")
        self.rec_btn_area = QPushButton("⬚   Select Area")
        self.rec_btn_area.setObjectName("btnSelect")

        for b in [self.rec_btn_full, self.rec_btn_area]:
            b.setCheckable(True)
            b.setMinimumWidth(130)
        self.rec_btn_full.setChecked(True)

        self.rec_btn_full.clicked.connect(lambda: self._rec_set_mode("full"))
        self.rec_btn_area.clicked.connect(self._rec_open_area_selector)

        self.rec_area_label = QLabel("No area selected — recording full screen")
        self.rec_area_label.setObjectName("labelAreaNone")

        al.addWidget(self.rec_btn_full)
        al.addWidget(self.rec_btn_area)
        al.addSpacing(10)
        al.addWidget(self.rec_area_label)
        al.addStretch()
        lay.addWidget(ag)

        # Quality
        qg = QGroupBox("Video Quality")
        ql = QHBoxLayout(qg)
        ql.addWidget(QLabel("Frame Rate:"))
        self.rec_fps = QComboBox()
        fps_items = ["10 FPS", "15 FPS", "24 FPS", "30 FPS", "60 FPS"]
        self.rec_fps.addItems(fps_items)
        fps_val = str(self.config["rec_fps"])
        fps_match = next((i for i, x in enumerate(fps_items) if x.startswith(fps_val)), 3)
        self.rec_fps.setCurrentIndex(fps_match)
        ql.addWidget(self.rec_fps)
        ql.addSpacing(24)
        ql.addWidget(QLabel("Quality:"))
        self.rec_quality = QComboBox()
        self.rec_quality.addItems([
            "Low  (fast, small file)",
            "Medium  (balanced)",
            "High  (recommended)",
            "Very High  (large file)",
            "Lossless  (.mkv, huge)",
        ])
        self.rec_quality.setCurrentIndex(self.config["rec_quality"])
        ql.addWidget(self.rec_quality)
        ql.addStretch()
        lay.addWidget(qg)

        # Audio
        audio_g = QGroupBox("Audio Recording")
        aulay   = QVBoxLayout(audio_g)

        row1 = QHBoxLayout()
        self.rec_audio = QCheckBox(
            "Record audio  (PipeWire/PulseAudio auto-detected, falls back to ALSA)"
        )
        self.rec_audio.setChecked(self.config["rec_audio"])
        row1.addWidget(self.rec_audio)
        row1.addStretch()
        btn_test_audio = QPushButton("Detect Audio Sources")
        btn_test_audio.setObjectName("btnSmall")
        btn_test_audio.clicked.connect(self._show_audio_info)
        row1.addWidget(btn_test_audio)
        aulay.addLayout(row1)

        self.audio_src_lbl = QLabel("Source: detecting...")
        self.audio_src_lbl.setObjectName("labelHint")
        aulay.addWidget(self.audio_src_lbl)
        QTimer.singleShot(800, self._detect_and_show_audio)
        lay.addWidget(audio_g)

        # Webcam PiP
        cam_g = QGroupBox("Webcam Picture-in-Picture  (optional)")
        caml  = QVBoxLayout(cam_g)
        row_c1 = QHBoxLayout()
        self.rec_webcam = QCheckBox("Overlay webcam  (requires /dev/video0)")
        self.rec_webcam.setChecked(self.config["rec_webcam"])
        self.rec_webcam.stateChanged.connect(self._toggle_webcam_opts)
        row_c1.addWidget(self.rec_webcam)
        row_c1.addStretch()
        caml.addLayout(row_c1)
        row_c2 = QHBoxLayout()
        row_c2.addWidget(QLabel("Position:"))
        self.rec_wcam_pos = QComboBox()
        self.rec_wcam_pos.addItems(
            ["bottom-right", "bottom-left", "top-right", "top-left"]
        )
        self.rec_wcam_pos.setCurrentText(self.config.get("webcam_pos", "bottom-right"))
        row_c2.addWidget(self.rec_wcam_pos)
        row_c2.addSpacing(20)
        row_c2.addWidget(QLabel("Size:"))
        self.rec_wcam_size = QComboBox()
        self.rec_wcam_size.addItems(["small (240×180)", "medium (320×240)", "large (480×360)"])
        row_c2.addWidget(self.rec_wcam_size)
        row_c2.addStretch()
        caml.addLayout(row_c2)
        self._toggle_webcam_opts(self.config["rec_webcam"])
        lay.addWidget(cam_g)

        # Timer panel
        timer_f = QFrame()
        timer_f.setStyleSheet(
            "background: qlineargradient(x1:0,y1:0,x2:0,y2:1,"
            " stop:0 #16213e, stop:1 #0f1525);"
            "border: 1px solid #0f3460; border-radius: 10px;"
        )
        tf = QHBoxLayout(timer_f)
        tf.setContentsMargins(24, 14, 24, 14)

        timer_left = QVBoxLayout()
        self.rec_timer_lbl = QLabel("00:00")
        self.rec_timer_lbl.setObjectName("labelTimer")
        self.rec_timer_lbl.setAlignment(Qt.AlignCenter)
        self.rec_status_lbl = QLabel("READY TO RECORD")
        self.rec_status_lbl.setObjectName("labelRecStatus")
        self.rec_status_lbl.setStyleSheet("color:#4a6888; font-size:11px; font-weight:700; letter-spacing:2px;")
        self.rec_status_lbl.setAlignment(Qt.AlignCenter)
        timer_left.addWidget(self.rec_timer_lbl)
        timer_left.addWidget(self.rec_status_lbl)
        tf.addLayout(timer_left)
        tf.addStretch()

        timer_right = QVBoxLayout()
        self.rec_est_lbl = QLabel("Estimated size: —")
        self.rec_est_lbl.setObjectName("labelHint")
        self.rec_est_lbl.setAlignment(Qt.AlignRight)
        self.rec_out_lbl = QLabel(f"Save to: {self.rec_dir}")
        self.rec_out_lbl.setObjectName("labelHint")
        self.rec_out_lbl.setAlignment(Qt.AlignRight)
        timer_right.addWidget(self.rec_est_lbl)
        timer_right.addWidget(self.rec_out_lbl)
        tf.addLayout(timer_right)
        lay.addWidget(timer_f)
        lay.addStretch()

        # Buttons
        br = QHBoxLayout()
        br.setSpacing(12)
        self.rec_btn_start = QPushButton("⏺    START RECORDING    [ F9 ]")
        self.rec_btn_start.setObjectName("btnRecord")
        self.rec_btn_start.clicked.connect(self.start_recording)

        self.rec_btn_stop = QPushButton("⏹    STOP RECORDING    [ F10 ]")
        self.rec_btn_stop.setObjectName("btnStop")
        self.rec_btn_stop.setEnabled(False)
        self.rec_btn_stop.clicked.connect(self.stop_recording)

        btn_rec_folder = QPushButton("Open Folder")
        btn_rec_folder.setObjectName("btnSmall")
        btn_rec_folder.clicked.connect(
            lambda: subprocess.Popen(["xdg-open", self.rec_dir])
        )
        br.addWidget(self.rec_btn_start)
        br.addWidget(self.rec_btn_stop)
        br.addSpacing(8)
        br.addWidget(btn_rec_folder)
        lay.addLayout(br)

        self.tabs.addTab(tab, "⏺  Recording")

    def _toggle_webcam_opts(self, state):
        on = bool(state)
        self.rec_wcam_pos.setEnabled(on)
        self.rec_wcam_size.setEnabled(on)

    def _rec_set_mode(self, mode):
        self.rec_mode_sel = mode
        self.rec_btn_full.setChecked(mode == "full")
        self.rec_btn_area.setChecked(mode == "area")
        if mode == "full":
            self.rec_area_rect = None
            self.rec_area_label.setText("No area selected — recording full screen")
            self.rec_area_label.setObjectName("labelAreaNone")
            self.rec_area_label.setStyle(self.rec_area_label.style())

    def _rec_open_area_selector(self):
        self.rec_btn_area.setChecked(True)
        self._open_selector("recording")

    def _detect_and_show_audio(self):
        try:
            drv, src = detect_audio_source()
            self.audio_src_lbl.setText(
                f"Detected: {drv} → {src}"
            )
        except Exception:
            self.audio_src_lbl.setText("Could not detect audio source")

    def _show_audio_info(self):
        drv, src = detect_audio_source()
        QMessageBox.information(
            self, "Audio Source",
            f"Detected audio source:\n\n"
            f"  Driver:  {drv}\n"
            f"  Source:  {src}\n\n"
            f"This will be used when 'Record audio' is enabled.\n\n"
            f"Kali Linux (PipeWire) setup:\n"
            f"  sudo apt install pipewire pipewire-pulse wireplumber\n"
            f"  systemctl --user enable --now pipewire pipewire-pulse wireplumber\n\n"
            f"Legacy PulseAudio setup:\n"
            f"  sudo apt install pulseaudio pavucontrol\n"
            f"  pulseaudio --start\n"
            f"  pavucontrol  (to adjust levels)"
        )

    # ──────────────────────────────────────────────────────────────
    #  TAB — HISTORY
    # ──────────────────────────────────────────────────────────────
    def _build_tab_history(self):
        tab = QWidget()
        lay = QVBoxLayout(tab)
        lay.setSpacing(10)

        top = QHBoxLayout()
        lbl = QLabel("Capture history  (this session + scanned files)")
        lbl.setObjectName("labelHint")
        top.addWidget(lbl)
        top.addStretch()
        scan = QPushButton("Scan ~/KomoCap/")
        scan.setObjectName("btnSmall")
        scan.clicked.connect(self._scan_history)
        clr = QPushButton("Clear List")
        clr.setObjectName("btnSmall")
        clr.clicked.connect(lambda: (self.recent_files.clear(), self._refresh_history()))
        top.addWidget(scan)
        top.addWidget(clr)
        lay.addLayout(top)

        self.hist_list = QListWidget()
        self.hist_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.hist_list.itemDoubleClicked.connect(self._hist_open_item)
        lay.addWidget(self.hist_list)

        bot = QHBoxLayout()
        btn_o = QPushButton("📂  Open")
        btn_o.setObjectName("btnSmall")
        btn_o.clicked.connect(lambda: self._hist_open_item(self.hist_list.currentItem()))
        btn_f = QPushButton("📁  Show in Folder")
        btn_f.setObjectName("btnSmall")
        btn_f.clicked.connect(self._hist_show_folder)
        btn_d = QPushButton("🗑  Delete")
        btn_d.setObjectName("btnSmall")
        btn_d.clicked.connect(self._hist_delete)
        bot.addWidget(btn_o)
        bot.addWidget(btn_f)
        bot.addStretch()
        bot.addWidget(btn_d)
        lay.addLayout(bot)

        self.tabs.addTab(tab, "📁  History")

    def _refresh_history(self):
        self.hist_list.clear()
        for f in self.recent_files[:300]:
            if not os.path.exists(f):
                continue
            ext  = os.path.splitext(f)[1].lower()
            icon = "📷" if ext in (".png",".jpg",".webp",".bmp",".tif") else "🎬"
            sz   = human_size(f)
            ts_  = datetime.datetime.fromtimestamp(
                os.path.getmtime(f)
            ).strftime("%Y-%m-%d  %H:%M:%S")
            item = QListWidgetItem(
                f"{icon}  {os.path.basename(f)}    {sz}    {ts_}"
            )
            item.setData(Qt.UserRole, f)
            self.hist_list.addItem(item)

    def _scan_history(self):
        found = []
        for d in [self.ss_dir, self.rec_dir]:
            if os.path.isdir(d):
                for p in sorted(
                    Path(d).iterdir(),
                    key=lambda x: x.stat().st_mtime,
                    reverse=True
                ):
                    if p.is_file() and p.suffix.lower() in \
                       (".png", ".jpg", ".webp", ".bmp", ".tif", ".mp4", ".mkv"):
                        found.append(str(p))
        self.recent_files = found
        self._refresh_history()
        self._set_status(f"Found {len(found)} file(s) in {self.root_dir}", "ok")

    def _hist_open_item(self, item):
        if not item:
            return
        p = item.data(Qt.UserRole)
        if p and os.path.exists(p):
            subprocess.Popen(["xdg-open", p])

    def _hist_show_folder(self):
        item = self.hist_list.currentItem()
        if item:
            subprocess.Popen(["xdg-open", os.path.dirname(item.data(Qt.UserRole))])

    def _hist_delete(self):
        item = self.hist_list.currentItem()
        if not item:
            return
        p = item.data(Qt.UserRole)
        r = QMessageBox.question(
            self, "Delete File",
            f"Permanently delete:\n{os.path.basename(p)}?",
            QMessageBox.Yes | QMessageBox.No
        )
        if r == QMessageBox.Yes:
            try:
                os.remove(p)
                self.recent_files = [x for x in self.recent_files if x != p]
                self._refresh_history()
                self._set_status(f"Deleted: {os.path.basename(p)}", "ok")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    # ──────────────────────────────────────────────────────────────
    #  TAB — SETTINGS
    # ──────────────────────────────────────────────────────────────
    def _build_tab_settings(self):
        tab = QWidget()
        lay = QVBoxLayout(tab)
        lay.setSpacing(14)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        inner  = QWidget()
        il     = QVBoxLayout(inner)
        il.setSpacing(14)

        # Save location
        sg = QGroupBox("Save Location")
        sl = QVBoxLayout(sg)
        note = QLabel(
            "Default root folder: ~/KomoCap/\n"
            "  Screenshots  →  [root]/Screenshots/\n"
            "  Recordings   →  [root]/Recordings/"
        )
        note.setObjectName("labelHint")
        sl.addWidget(note)
        row_s = QHBoxLayout()
        self.cfg_root_edit = QLineEdit(self.root_dir)
        self.cfg_root_edit.setReadOnly(True)
        row_s.addWidget(self.cfg_root_edit)
        btn_change = QPushButton("Change Folder")
        btn_change.setObjectName("btnSmall")
        btn_change.clicked.connect(self._change_root)
        btn_reset = QPushButton("Reset to Default")
        btn_reset.setObjectName("btnSmall")
        btn_reset.clicked.connect(self._reset_root)
        row_s.addWidget(btn_change)
        row_s.addWidget(btn_reset)
        sl.addLayout(row_s)
        self._btn_open_root = QPushButton(f"📁  Open {self.root_dir}")
        self._btn_open_root.setObjectName("btnSmall")
        self._btn_open_root.clicked.connect(
            lambda: subprocess.Popen(["xdg-open", self.root_dir])
        )
        sl.addWidget(self._btn_open_root)
        il.addWidget(sg)

        # Shortcuts
        hkg = QGroupBox("Keyboard Shortcuts")
        hkl = QVBoxLayout(hkg)
        for key, desc in [
            ("F5",     "Take screenshot"),
            ("F9",     "Start screen recording"),
            ("F10",    "Stop screen recording"),
            ("Ctrl+Q", "Quit KomoCap"),
        ]:
            row = QHBoxLayout()
            badge = QLabel(f"  {key}  ")
            badge.setStyleSheet(
                "background:#0f3460; color:#74b9ff; border:1px solid #1a4080;"
                "border-radius:4px; padding:3px 10px; font-weight:800;"
                "font-size:11px; font-family:monospace;"
            )
            desc_lbl = QLabel(desc)
            desc_lbl.setStyleSheet("color:#d0e8ff; font-size:12px;")
            row.addWidget(badge)
            row.addSpacing(14)
            row.addWidget(desc_lbl)
            row.addStretch()
            hkl.addLayout(row)
        il.addWidget(hkg)

        # Dependencies
        depg = QGroupBox("Dependency Status")
        depl = QVBoxLayout(depg)
        deps = [
            ("ffmpeg",  "Screen recording (REQUIRED)",    "sudo apt install ffmpeg"),
            ("scrot",   "Screenshot capture (REQUIRED)",  "sudo apt install scrot"),
            ("slop",    "Area selection — INSTALL THIS",  "sudo apt install slop"),
            ("xdotool", "Active window capture",          "sudo apt install xdotool"),
            ("pactl",   "PipeWire/PulseAudio audio",      "sudo apt install pipewire-pulse"),
            ("Pillow",  "Image processing",               "pip3 install Pillow --break-system-packages"),
        ]
        for tool, purpose, install_cmd in deps:
            ok  = PIL_OK if tool == "Pillow" else cmd_ok(tool)
            row = QHBoxLayout()
            status = QLabel("✓  OK" if ok else "✗  MISSING")
            status.setStyleSheet(
                f"color:{'#00b894' if ok else '#e94560'}; font-weight:800;"
                f"font-size:11px; min-width:90px;"
            )
            name_l = QLabel(tool)
            name_l.setStyleSheet("color:#74b9ff; font-weight:700; min-width:70px;")
            purp_l = QLabel(purpose)
            purp_l.setStyleSheet("color:#a0c0d8;")
            row.addWidget(status)
            row.addWidget(name_l)
            row.addWidget(purp_l)
            if not ok:
                row.addStretch()
                ic = QLabel(install_cmd)
                ic.setStyleSheet("color:#354860; font-size:10px; font-family:monospace;")
                row.addWidget(ic)
            else:
                row.addStretch()
            depl.addLayout(row)
        il.addWidget(depg)

        # About
        abg = QGroupBox("About KomoCap")
        abl = QVBoxLayout(abg)
        about = QLabel(
            f"<b style='color:#ffffff;font-size:14px;'>KomoCap v{VERSION}</b>"
            f"  <span style='color:#4a7aaa;'>Screen Capture Suite for Kali Linux</span><br><br>"
            f"<b>Screenshot formats:</b> PNG, JPEG, WEBP, BMP, TIFF<br>"
            f"<b>Recording formats:</b> MP4 H.264, MKV Lossless<br>"
            f"<b>Audio:</b> PipeWire (auto) → PulseAudio → ALSA fallback<br>"
            f"<b>Screenshot engine:</b> scrot (X11) → Pillow fallback<br>"
            f"<b>Default save folder:</b> ~/KomoCap/<br>"
            f"<b>Config file:</b> {CONFIG_PATH}<br><br>"
            f"<span style='color:#4a6888;'>Built for Kali Linux · Debian · Ubuntu</span>"
        )
        about.setTextFormat(Qt.RichText)
        about.setStyleSheet("font-size:12px; line-height:1.7;")
        about.setWordWrap(True)
        abl.addWidget(about)
        il.addWidget(abg)

        il.addStretch()
        scroll.setWidget(inner)
        lay.addWidget(scroll)

        save_btn = QPushButton("💾   Save Settings")
        save_btn.setObjectName("btnCapture")
        save_btn.clicked.connect(self._save_all_settings)
        lay.addWidget(save_btn)

        self.tabs.addTab(tab, "⚙  Settings")

    def _change_root(self):
        d = QFileDialog.getExistingDirectory(
            self, "Select KomoCap Root Folder", self.root_dir
        )
        if d:
            self.root_dir = d
            self.ss_dir   = os.path.join(d, "Screenshots")
            self.rec_dir  = os.path.join(d, "Recordings")
            ensure_dirs(self.ss_dir, self.rec_dir)
            self.cfg_root_edit.setText(d)
            self.hdr_path_lbl.setText(f"📁  {d}")
            self.rec_out_lbl.setText(f"Save to: {self.rec_dir}")
            self._btn_open_root.setText(f"📁  Open {d}")
            self.config["root_dir"] = d
            self._set_status(f"Root folder: {d}", "ok")

    def _reset_root(self):
        d = str(DEFAULT_ROOT)
        self.root_dir = d
        self.ss_dir   = str(DEFAULT_ROOT / "Screenshots")
        self.rec_dir  = str(DEFAULT_ROOT / "Recordings")
        ensure_dirs(self.ss_dir, self.rec_dir)
        self.cfg_root_edit.setText(d)
        self.hdr_path_lbl.setText(f"📁  {d}")
        self.rec_out_lbl.setText(f"Save to: {self.rec_dir}")
        self.config["root_dir"] = d
        self._set_status("Reset to ~/KomoCap/", "ok")

    def _save_all_settings(self):
        self.config.update({
            "root_dir":    self.root_dir,
            "ss_format":   self.ss_fmt.currentText(),
            "ss_quality":  self.ss_quality.value(),
            "ss_delay":    self.ss_delay.value(),
            "rec_fps":     int(self.rec_fps.currentText().split()[0]),
            "rec_quality": self.rec_quality.currentIndex(),
            "rec_audio":   self.rec_audio.isChecked(),
            "rec_webcam":  self.rec_webcam.isChecked(),
            "webcam_pos":  self.rec_wcam_pos.currentText(),
            "webcam_size": self.rec_wcam_size.currentText().split("(")[0].strip(),
        })
        self._save_config()
        self._set_status("Settings saved.", "ok")

    # ──────────────────────────────────────────────────────────────
    #  AREA SELECTOR  (shared)
    # ──────────────────────────────────────────────────────────────
    def _open_selector(self, target: str):
        """Hide main window, then launch area selector (native tool or PyQt overlay)."""
        self.hide()
        QApplication.processEvents()
        time.sleep(0.35)   # let the window fully disappear before grabbing screen

        self._active_selector = AreaSelector()
        if target == "screenshot":
            self._active_selector.area_selected.connect(self._on_ss_area_done)
            self._active_selector.cancelled.connect(self._on_ss_area_cancel)
        else:
            self._active_selector.area_selected.connect(self._on_rec_area_done)
            self._active_selector.cancelled.connect(self._on_rec_area_cancel)

        self._active_selector.start()

    def _on_ss_area_done(self, rect: QRect):
        self.ss_area_rect = rect
        self.ss_mode      = "area"
        self.ss_btn_full.setChecked(False)
        self.ss_btn_area.setChecked(True)
        self.ss_btn_window.setChecked(False)
        self.ss_area_label.setText(
            f"{rect.width()} × {rect.height()} px  at  ({rect.x()}, {rect.y()})"
        )
        self.ss_area_label.setObjectName("labelAreaInfo")
        self.ss_area_label.setStyle(self.ss_area_label.style())
        self.show()
        self._set_status(
            f"Area locked: {rect.width()}×{rect.height()} — press Capture", "ok"
        )

    def _on_ss_area_cancel(self):
        if not self.ss_area_rect:
            self._ss_set_mode("full")
        else:
            self.ss_btn_area.setChecked(True)
        self.show()

    def _on_rec_area_done(self, rect: QRect):
        self.rec_area_rect = rect
        self.rec_mode_sel  = "area"
        self.rec_btn_full.setChecked(False)
        self.rec_btn_area.setChecked(True)
        self.rec_area_label.setText(
            f"Recording area locked: {rect.width()} × {rect.height()} px"
            f"  at  ({rect.x()}, {rect.y()})"
        )
        self.rec_area_label.setObjectName("labelAreaInfo")
        self.rec_area_label.setStyle(self.rec_area_label.style())
        self.show()
        self._set_status(
            f"Recording area locked: {rect.width()}×{rect.height()} — press Start", "ok"
        )

    def _on_rec_area_cancel(self):
        if not self.rec_area_rect:
            self._rec_set_mode("full")
        else:
            self.rec_btn_area.setChecked(True)
        self.show()

    # ──────────────────────────────────────────────────────────────
    #  SCREENSHOT
    # ──────────────────────────────────────────────────────────────
    def take_screenshot(self):
        delay = self.ss_delay.value()
        if delay > 0:
            self._set_status(f"Screenshot in {delay}s...", "warn")
            QTimer.singleShot(delay * 1000, self._do_screenshot)
        else:
            self._do_screenshot()

    def _do_screenshot(self):
        fmt  = self.ss_fmt.currentText()
        path = os.path.join(self.ss_dir, f"screenshot_{ts()}")
        ensure_dirs(self.ss_dir)

        self.ss_btn_capture.setEnabled(False)
        self.hide()
        QApplication.processEvents()
        time.sleep(0.22)

        self.ss_worker = ScreenshotWorker({
            "mode":    self.ss_mode,
            "area":    self.ss_area_rect,
            "format":  fmt,
            "quality": self.ss_quality.value(),
            "output":  path,
        })
        self.ss_worker.sig_done.connect(self._on_ss_done)
        self.ss_worker.sig_error.connect(self._on_ss_error)
        self.ss_worker.start()

    def _on_ss_done(self, path: str):
        self.show()
        self.ss_btn_capture.setEnabled(True)
        self.last_ss_path = path
        self.recent_files.insert(0, path)
        self._refresh_history()
        self.ss_preview.set_image(path)
        sz = human_size(path)
        self._set_status(
            f"✓  Screenshot saved: {os.path.basename(path)}  [{sz}]  →  {self.ss_dir}",
            "ok"
        )
        if self.ss_clip.isChecked():
            pix = QPixmap(path)
            if not pix.isNull():
                QApplication.clipboard().setPixmap(pix)

    def _on_ss_error(self, msg: str):
        self.show()
        self.ss_btn_capture.setEnabled(True)
        self._set_status(f"Screenshot error: {msg[:80]}", "error")
        QMessageBox.critical(
            self, "Screenshot Failed",
            f"Could not take screenshot:\n\n{msg}\n\n"
            f"Tips:\n"
            f"  • Make sure Pillow is installed: pip3 install Pillow\n"
            f"  • Make sure an X display is running (DISPLAY={os.environ.get('DISPLAY','?')})"
        )

    def _open_last_ss(self):
        if self.last_ss_path and os.path.exists(self.last_ss_path):
            subprocess.Popen(["xdg-open", self.last_ss_path])
        else:
            self._set_status("No screenshot taken yet", "warn")

    # ──────────────────────────────────────────────────────────────
    #  RECORDING
    # ──────────────────────────────────────────────────────────────
    def start_recording(self):
        if self.recorder and self.recorder.isRunning():
            return

        ensure_dirs(self.rec_dir)
        fps     = int(self.rec_fps.currentText().split()[0])
        qi      = self.rec_quality.currentIndex()
        audio   = self.rec_audio.isChecked()
        webcam  = self.rec_webcam.isChecked()
        area    = self.rec_area_rect if self.rec_mode_sel == "area" else None
        out     = os.path.join(self.rec_dir, f"recording_{ts()}.mp4")

        self.recorder = RecorderThread({
            "fps":         fps,
            "quality":     qi,
            "audio":       audio,
            "webcam":      webcam,
            "webcam_pos":  self.rec_wcam_pos.currentText(),
            "webcam_size": self.rec_wcam_size.currentText().split("(")[0].strip(),
            "area":        area,
            "output":      out,
        })
        self.recorder.sig_status.connect(self._on_rec_status)
        self.recorder.sig_done.connect(self._on_rec_done)
        self.recorder.sig_error.connect(self._on_rec_error)
        self.recorder.start()

        self.rec_seconds = 0
        self._rec_tick_timer.start(1000)
        self.rec_btn_start.setEnabled(False)
        self.rec_btn_stop.setEnabled(True)
        self.rec_status_lbl.setText("● RECORDING")
        self.rec_status_lbl.setStyleSheet(
            "color:#e94560; font-size:13px; font-weight:900; letter-spacing:3px;"
        )
        self.hdr_rec_badge.setVisible(True)

        area_str = (
            f"Area {area.width()}×{area.height()}" if area else "Full Screen"
        )
        self._set_status(
            f"Recording started  ·  {area_str}  ·  {fps} FPS"
            f"  ·  Audio: {'ON' if audio else 'OFF'}", "ok"
        )

    def stop_recording(self):
        if self.recorder:
            self.recorder.stop()
        self._rec_tick_timer.stop()
        self.rec_btn_start.setEnabled(True)
        self.rec_btn_stop.setEnabled(False)
        self.hdr_rec_badge.setVisible(False)
        self.rec_status_lbl.setText("PROCESSING...")
        self.rec_status_lbl.setStyleSheet(
            "color:#f0a30a; font-size:12px; font-weight:700; letter-spacing:2px;"
        )
        self._set_status("Stopping recording — finalizing file...", "warn")

    def _tick(self):
        self.rec_seconds += 1
        m, s = self.rec_seconds // 60, self.rec_seconds % 60
        t    = f"{m:02d}:{s:02d}"
        self.rec_timer_lbl.setText(t)
        self.hdr_rec_badge.setText(f"  ● REC  {t}  ")
        mbps_map = {0: 0.4, 1: 1.5, 2: 3.5, 3: 7.0, 4: 18.0}
        mb = mbps_map.get(self.rec_quality.currentIndex(), 3.5) * self.rec_seconds / 8
        self.rec_est_lbl.setText(f"Estimated size: ~{mb:.1f} MB")

    def _on_rec_status(self, _msg):
        pass  # status already set in start_recording

    def _on_rec_done(self, path: str):
        self._rec_tick_timer.stop()
        self.rec_btn_start.setEnabled(True)
        self.rec_btn_stop.setEnabled(False)
        self.hdr_rec_badge.setVisible(False)
        self.rec_status_lbl.setText("✓  SAVED")
        self.rec_status_lbl.setStyleSheet(
            "color:#00b894; font-size:12px; font-weight:800; letter-spacing:2px;"
        )
        sz = human_size(path)
        self._set_status(
            f"✓  Recording saved: {os.path.basename(path)}  [{sz}]  →  {self.rec_dir}",
            "ok"
        )
        self.recent_files.insert(0, path)
        self._refresh_history()
        self.tabs.setCurrentIndex(2)  # jump to history

    def _on_rec_error(self, msg: str):
        self._rec_tick_timer.stop()
        self.rec_btn_start.setEnabled(True)
        self.rec_btn_stop.setEnabled(False)
        self.hdr_rec_badge.setVisible(False)
        self.rec_status_lbl.setText("ERROR")
        self.rec_status_lbl.setStyleSheet(
            "color:#e94560; font-size:12px; font-weight:800;"
        )
        self._set_status(f"Recording error: {msg[:100]}", "error")
        QMessageBox.critical(
            self, "Recording Failed",
            f"Recording failed:\n\n{msg}\n\n"
            f"Common fixes:\n"
            f"  sudo apt install ffmpeg\n\n"
            f"For audio on Kali Linux (PipeWire):\n"
            f"  sudo apt install pipewire pipewire-pulse wireplumber\n"
            f"  systemctl --user enable --now pipewire pipewire-pulse wireplumber\n\n"
            f"For older PulseAudio setups:\n"
            f"  sudo apt install pulseaudio\n"
            f"  pulseaudio --start"
        )

    # ──────────────────────────────────────────────────────────────
    #  STATUS BAR
    # ──────────────────────────────────────────────────────────────
    def _set_status(self, msg: str, level: str = "ok"):
        c = {"ok": "#74b9ff", "warn": "#f0a30a", "error": "#e94560"}.get(level, "#74b9ff")
        self.statusbar.setStyleSheet(
            f"background:#16213e; color:{c}; border-top:1px solid #0f3460;"
            f"font-size:11px; padding:3px 10px;"
        )
        self.statusbar.showMessage(msg)

    # ──────────────────────────────────────────────────────────────
    #  SHORTCUTS + TRAY
    # ──────────────────────────────────────────────────────────────
    def _build_shortcuts(self):
        QShortcut(QKeySequence("F5"),     self, self.take_screenshot)
        QShortcut(QKeySequence("F9"),     self, self.start_recording)
        QShortcut(QKeySequence("F10"),    self, self.stop_recording)
        QShortcut(QKeySequence("Ctrl+Q"), self, QApplication.quit)

    def _build_tray(self):
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return
        pix = QPixmap(24, 24)
        pix.fill(Qt.transparent)
        p = QPainter(pix)
        p.setRenderHint(QPainter.Antialiasing)
        p.setBrush(QBrush(QColor("#e94560")))
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(2, 2, 20, 20, 5, 5)
        p.setPen(QPen(QColor("#ffffff"), 1.5))
        p.setBrush(Qt.NoBrush)
        p.drawEllipse(6, 8, 8, 8)
        p.setBrush(QBrush(QColor("#ffffff")))
        p.setPen(Qt.NoPen)
        p.drawEllipse(14, 5, 5, 4)
        p.end()

        self.tray = QSystemTrayIcon(QIcon(pix), self)
        m = QMenu()
        m.addAction(QAction("📷  Screenshot  (F5)",     self, triggered=self.take_screenshot))
        m.addAction(QAction("⏺  Start Recording  (F9)", self, triggered=self.start_recording))
        m.addAction(QAction("⏹  Stop Recording  (F10)", self, triggered=self.stop_recording))
        m.addSeparator()
        m.addAction(QAction("Show Window",               self, triggered=self.show))
        m.addAction(QAction(f"📁  Open ~/KomoCap/",
                            self,
                            triggered=lambda: subprocess.Popen(["xdg-open", self.root_dir])))
        m.addSeparator()
        m.addAction(QAction("Quit", self, triggered=QApplication.quit))
        self.tray.setContextMenu(m)
        self.tray.setToolTip(f"KomoCap {VERSION}")
        self.tray.activated.connect(
            lambda r: self.show() if r == QSystemTrayIcon.DoubleClick else None
        )
        self.tray.show()

    # ──────────────────────────────────────────────────────────────
    #  CLOSE
    # ──────────────────────────────────────────────────────────────
    def closeEvent(self, event):
        if self.recorder and self.recorder.isRunning():
            r = QMessageBox.question(
                self, "Recording Active",
                "A recording is running. Stop it and quit?",
                QMessageBox.Yes | QMessageBox.No
            )
            if r == QMessageBox.No:
                event.ignore()
                return
            self.stop_recording()
            time.sleep(1.5)
        self._save_all_settings()
        event.accept()


# ══════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════════
def main():
    if not os.environ.get("DISPLAY") and not os.environ.get("WAYLAND_DISPLAY"):
        print("ERROR: No display. Run inside a desktop session.")
        sys.exit(1)

    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(VERSION)
    app.setQuitOnLastWindowClosed(False)

    f = app.font()
    f.setPointSize(10)
    app.setFont(f)

    win = KomoCap()
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
