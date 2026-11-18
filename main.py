import sys
import os
import json
import wave
import random
import plistlib

IS_WINDOWS = sys.platform == "win32"
IS_MACOS = sys.platform == "darwin"
IS_LINUX = sys.platform.startswith("linux")

if IS_WINDOWS:
    import ctypes
    from ctypes import wintypes

from PySide6.QtWidgets import (
    QApplication, QLabel, QMenu, QDialog, QVBoxLayout, QHBoxLayout,
    QCheckBox, QPushButton, QSplashScreen, QComboBox, QFormLayout,
    QSlider, QGroupBox, QTabWidget, QWidget, QSystemTrayIcon
)
from PySide6.QtCore import Qt, QTimer, QPoint, QUrl, Signal, QObject, QAbstractNativeEventFilter
from PySide6.QtGui import QPixmap, QTransform, QAction, QIcon, QActionGroup
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput, QSoundEffect
from PySide6.QtNetwork import QLocalServer, QLocalSocket

HAS_QUARTZ = False
if IS_MACOS:
    try:
        import Quartz
        import objc
        HAS_QUARTZ = True
    except ImportError:
        pass

HAS_XLIB = False
if IS_LINUX:
    try:
        from Xlib import display as xlib_display, X
        HAS_XLIB = True
    except Exception:
        pass

HAS_PYNPUT = False
if not IS_WINDOWS:
    try:
        from pynput import keyboard as pynput_kb
        HAS_PYNPUT = True
    except Exception:
        pass


def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def get_app_dir():
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(os.path.abspath(sys.executable))
        if IS_MACOS and exe_dir.endswith(os.path.join("Contents", "MacOS")):
            return os.path.abspath(os.path.join(exe_dir, "..", "..", ".."))
        return exe_dir
    return os.path.dirname(os.path.abspath(__file__))


def get_config_path():
    if IS_WINDOWS:
        base = os.environ.get("APPDATA") or os.path.expanduser("~")
    elif IS_MACOS:
        base = os.path.expanduser("~/Library/Application Support")
    else:
        base = os.environ.get("XDG_CONFIG_HOME") or os.path.expanduser("~/.config")

    cfg_dir = os.path.join(base, "CrashMascot1998")
    try:
        os.makedirs(cfg_dir, exist_ok=True)
        return os.path.join(cfg_dir, "crash_config.json")
    except Exception:
        return os.path.expanduser("~/.crash_mascot_1998.json")


CONFIG_FILE = get_config_path()
SERVER_NAME = "CrashBandicootDesktop1998_SingleInstance"
HOTKEY_RESCUE_ID = 0x1998
LAUNCH_AGENT_LABEL = "com.hitsujishiroi.crashmascot1998"

OS_DISPLAY_NAME = "Win 10/11" if IS_WINDOWS else ("macOS" if IS_MACOS else "Linux")
HOTKEY_LABEL = "Cmd + Shift + C" if IS_MACOS else "Ctrl + Shift + C"

OST_EDITION_KEYS = ["ps1", "nsane", "all"]

FALLBACK_EN = {
    "_lang_name": "English",
    "menu_start_dance": "Start Dance",
    "menu_stop": "Stop",
    "menu_bring_center": "Bring Crash to Center",
    "menu_clones": "Clones (Multi-Crash)",
    "act_spawn_clone": "➕ Spawn Another Crash",
    "act_dance_all": "🕺 All: Start Dance",
    "act_stop_all": "🛑 All: Stop",
    "act_clear_clones": "🧹 Remove Extra Clones",
    "act_close_this": "Close This Crash",
    "toast_clone_spawned": "Clones active: {count}",
    "menu_character": "Character Pack",
    "menu_animations": "Animations",
    "menu_random_move": "Random Move",
    "move_jiggle": "Jiggle",
    "move_foot_stomp": "Foot Stomp",
    "move_pelvic_thrust": "Pelvic Thrust",
    "move_turn_around": "Turn Around",
    "move_behind_you": "Behind You",
    "menu_pos_fs": "Position & Fullscreen",
    "act_hide_fs": "Auto-Hide in Fullscreen",
    "act_force_fs": "Show Over Fullscreen",
    "act_gravity": "Enable Gravity",
    "act_lock_pos": "Lock Position",
    "act_ghost_mode": "Ghost Mode (Click-Through)",
    "menu_vol_ost": "Volume & Soundtrack",
    "menu_quick_vol": "Quick Volume",
    "act_play_music": "▶ Play Music",
    "act_pause_music": "⏸ Pause Music",
    "act_next_track": "⏭ Next Track",
    "act_prev_track": "⏮ Previous Track",
    "act_mute_all": "Mute All",
    "act_enable_music": "Enable Music",
    "act_sfx": "Sound Effects",
    "ost_ps1": "Original PS1 (1997)",
    "ost_nsane": "N. Sane Trilogy (Remastered)",
    "ost_all": "All Soundtracks (Mixed)",
    "menu_options": "Options",
    "menu_about": "About Crash",
    "menu_exit": "Bye Bye",
    "win_options_title": "Crash Bandicoot - Control Panel",
    "win_about_title": "About Crash Bandicoot Desktop Character",
    "tab_classic": "General && Classic",
    "tab_audio": "Audio && Jukebox",
    "tab_desktop": f"Desktop && {OS_DISPLAY_NAME}",
    "grp_1998": "Original 1998 Rules (MDR Software)",
    "cb_allow_move": "Allow Crash to move around the screen",
    "cb_vary_length": "Vary length of dancing animations",
    "cb_continue_dancing": "Continue dancing after a command",
    "grp_timing": "Animation, Activity & Language",
    "lbl_character": "Character:",
    "lbl_language": "Language:",
    "lbl_dance_speed": "Dance Speed:",
    "lbl_spontaneous": "Spontaneous Dances:",
    "spd_slow": "0.5x (Slow)",
    "spd_normal": "1.0x (Original 1998)",
    "spd_fast": "1.5x (Fast)",
    "spd_turbo": "2.0x (Turbo)",
    "idle_never": "Never (Stand Still)",
    "idle_rarely": "Rarely",
    "idle_normal": "Normal (1998)",
    "idle_hyper": "Hyperactive",
    "btn_mute_all": "Mute All Audio",
    "btn_unmute_all": "Unmute All Audio (MUTED)",
    "grp_music": "Music Jukebox & Soundtrack Edition",
    "cb_enable_music": "Enable Music",
    "lbl_ost_style": "Soundtrack Style:",
    "lbl_selected_track": "Selected Track:",
    "opt_random_track": "Random Track",
    "lbl_now_playing": "Now Playing: {track}",
    "btn_prev": "⏮ Previous",
    "btn_play": "▶ Play",
    "btn_pause": "⏸ Pause",
    "btn_next": "⏭ Next",
    "cb_autoplay": "Auto-advance to next track when song ends",
    "grp_sfx": "Sound Effects (SFX)",
    "cb_enable_sfx": "Enable SFX",
    "grp_display": "Display & Multi-Monitor",
    "lbl_scale": "Sprite Scale:",
    "lbl_opacity": "Opacity:",
    "lbl_screen": "Active Screen:",
    "scale_1x": "1x (Original 1998)",
    "scale_2x": "2x (HD)",
    "scale_3x": "3x (Full HD)",
    "scale_4x": "4x (4K)",
    "lbl_monitor_item": "Monitor {num} ({w}x{h})",
    "grp_fs": "Fullscreen & Gaming Behavior",
    "cb_hide_fs": "Auto-Hide && Pause in Fullscreen / Exclusive Games",
    "cb_force_fs": "Show Over Fullscreen (Force Always-On-Top)",
    "grp_sys": "Desktop Physics, Position & Startup",
    "cb_gravity": "Enable Gravity on Desktop (Free float when unchecked)",
    "cb_lock_pos": "Lock Position on Screen (Stay pinned in place)",
    "cb_splash": "Show Startup Splash Screen (Crash 2 Logo)",
    "cb_startup": f"Run Crash automatically at {OS_DISPLAY_NAME} Startup",
    "cb_ghost": "Ghost Mode (Mouse clicks pass through Crash)",
    "lbl_hotkey_info": f"Rescue Hotkey: {HOTKEY_LABEL} (Unlocks & Centers)",
    "btn_reset_1998": "Reset 1998 Defaults",
    "btn_apply_ok": "Apply && OK",
    "txt_no_tracks": "No tracks found",
    "toast_now_playing": "♪ Now Playing: {track}",
    "toast_rescued": "Crash rescued to center!"
}

DEFAULT_SETTINGS = {
    "character_id": "default_crash",
    "language": "en",
    "allow_move": True,
    "vary_length": True,
    "continue_dancing": True,
    "anim_speed": 1.0,
    "idle_frequency": 2,
    "mute_all": False,
    "music_on": True,
    "sfx_on": True,
    "music_volume": 0.45,
    "sfx_volume": 0.55,
    "ost_edition": "ps1",
    "current_track": "__RANDOM__",
    "playlist_autoplay": True,
    "scale": 2,
    "opacity": 1.0,
    "gravity_on": True,
    "lock_position": False,
    "pinned_x": None,
    "pinned_y": None,
    "ghost_mode": False,
    "hide_fullscreen": True,
    "force_over_fullscreen": False,
    "monitor_index": 0,
    "show_splash": True,
    "run_at_startup": False
}

CLASSIC_1998_PRESET = {
    "allow_move": True,
    "vary_length": True,
    "continue_dancing": True,
    "anim_speed": 1.0,
    "idle_frequency": 2,
    "mute_all": False,
    "music_on": True,
    "sfx_on": True,
    "music_volume": 0.50,
    "sfx_volume": 0.60,
    "ost_edition": "ps1",
    "playlist_autoplay": False,
    "scale": 1,
    "opacity": 1.0,
    "gravity_on": False,
    "lock_position": False,
    "ghost_mode": False,
    "hide_fullscreen": False,
    "force_over_fullscreen": False,
    "monitor_index": 0,
    "show_splash": True,
    "run_at_startup": False
}


class CharacterManager:
    DEFAULT_ANIM_RANGES = {
        "Neutral": [0, 0],
        "Jiggle": [1, 15],
        "Foot Stomp": [16, 30],
        "Pelvic Thrust": [31, 45],
        "Turn Around": [46, 79],
        "Behind You": [81, 159]
    }

    def __init__(self):
        self.characters = {
            "default_crash": {
                "id": "default_crash",
                "name": "Crash Bandicoot (1998)",
                "sprites_dir": resource_path("assets/sprites"),
                "audio_dir": resource_path("assets/audio"),
                "animations": dict(self.DEFAULT_ANIM_RANGES)
            }
        }
        self.scan_external_characters()

    def scan_external_characters(self):
        user_chars = os.path.join(os.path.dirname(CONFIG_FILE), "characters")
        search_roots = [
            os.path.join(get_app_dir(), "characters"),
            user_chars,
            resource_path("characters")
        ]
        seen = set()
        for root_dir in search_roots:
            if not os.path.isdir(root_dir):
                continue
            for folder in sorted(os.listdir(root_dir)):
                char_path = os.path.join(root_dir, folder)
                if not os.path.isdir(char_path) or folder in seen:
                    continue
                sprites_dir = os.path.join(char_path, "sprites")
                if not os.path.isdir(sprites_dir):
                    continue
                seen.add(folder)
                meta_file = os.path.join(char_path, "character.json")
                char_name = folder.replace("_", " ")
                anims = dict(self.DEFAULT_ANIM_RANGES)
                if os.path.exists(meta_file):
                    try:
                        with open(meta_file, "r", encoding="utf-8") as f:
                            meta = json.load(f)
                            char_name = meta.get("name", char_name)
                            if isinstance(meta.get("animations"), dict):
                                anims.update(meta["animations"])
                    except Exception:
                        pass
                audio_dir = os.path.join(char_path, "audio")
                if not os.path.isdir(audio_dir):
                    audio_dir = resource_path("assets/audio")
                self.characters[folder] = {
                    "id": folder,
                    "name": char_name,
                    "sprites_dir": sprites_dir,
                    "audio_dir": audio_dir,
                    "animations": anims
                }

    def get_character(self, char_id):
        return self.characters.get(char_id) or self.characters["default_crash"]


class LanguageManager:
    def __init__(self):
        self.languages = {"en": dict(FALLBACK_EN)}
        self.load_all_languages()

    def load_all_languages(self):
        lang_dir = resource_path("assets/lang")
        if not os.path.isdir(lang_dir):
            return
        for fname in sorted(os.listdir(lang_dir)):
            if fname.lower().endswith(".json") and not fname.upper().startswith("TEMPLATE"):
                code = os.path.splitext(fname)[0]
                full_path = os.path.join(lang_dir, fname)
                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        loaded = json.load(f)
                        merged = dict(FALLBACK_EN)
                        # Mantener etiquetas específicas del SO actual en la pestaña y opciones
                        merged.update(loaded)
                        merged["tab_desktop"] = f"Desktop && {OS_DISPLAY_NAME}"
                        self.languages[code] = merged
                except Exception:
                    pass

    def available_languages(self):
        items = []
        if "en" in self.languages:
            items.append(("en", self.languages["en"].get("_lang_name", "English")))
        for code, data in self.languages.items():
            if code != "en":
                items.append((code, data.get("_lang_name", code)))
        return items

    def tr(self, lang_code, key, **kwargs):
        lang_dict = self.languages.get(lang_code) or self.languages["en"]
        text = lang_dict.get(key, FALLBACK_EN.get(key, key))
        if kwargs:
            try:
                return text.format(**kwargs)
            except Exception:
                return text
        return text


class WinGlobalHotkeyFilter(QAbstractNativeEventFilter):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    def nativeEventFilter(self, eventType, message):
        if IS_WINDOWS and eventType == b"windows_generic_MSG":
            msg = wintypes.MSG.from_address(int(message))
            if msg.message == 0x0312 and msg.wParam == HOTKEY_RESCUE_ID:
                self.callback()
                return True, 0
        return False, 0


class UnixHotkeyBridge(QObject):
    triggered = Signal()

    def __init__(self, callback):
        super().__init__()
        self.triggered.connect(callback)
        self.listener = None
        if HAS_PYNPUT:
            combo = "<cmd>+<shift>+c" if IS_MACOS else "<ctrl>+<shift>+c"
            try:
                self.listener = pynput_kb.GlobalHotKeys({combo: self.triggered.emit})
                self.listener.daemon = True
                self.listener.start()
            except Exception:
                self.listener = None

    def stop(self):
        if self.listener:
            try:
                self.listener.stop()
            except Exception:
                pass


class RetroToast(QLabel):
    def __init__(self):
        super().__init__()
        flags = Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool | Qt.WindowTransparentForInput
        if IS_LINUX:
            flags |= Qt.X11BypassWindowManagerHint
        self.setWindowFlags(flags)
        self.setStyleSheet(
            "background-color: rgba(25, 25, 30, 225);"
            "color: #ff9f1a;"
            "border: 2px solid #ff9f1a;"
            "border-radius: 6px;"
            "padding: 6px 12px;"
            "font-family: sans-serif;"
            "font-size: 12px;"
            "font-weight: bold;"
        )
        self.hide_timer = QTimer(self)
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.hide)

    def show_message(self, text, anchor_rect, duration_ms=2200):
        self.setText(text)
        self.adjustSize()
        min_y = 35 if IS_MACOS else 12
        x = anchor_rect.left() + (anchor_rect.width() - self.width()) // 2
        y = max(min_y, anchor_rect.top() - self.height() - 8)
        self.move(x, y)
        self.show()
        self.raise_()
        self.hide_timer.start(duration_ms)


def load_global_settings():
    data = dict(DEFAULT_SETTINGS)
    legacy_path = "crash_config.json"
    source_path = CONFIG_FILE if os.path.exists(CONFIG_FILE) else (legacy_path if os.path.exists(legacy_path) else None)
    if source_path:
        try:
            with open(source_path, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                old_ed = loaded.get("ost_edition", "")
                if "N. Sane" in old_ed:
                    loaded["ost_edition"] = "nsane"
                elif "All" in old_ed:
                    loaded["ost_edition"] = "all"
                elif "PS1" in old_ed:
                    loaded["ost_edition"] = "ps1"
                if loaded.get("current_track") == "Random Track":
                    loaded["current_track"] = "__RANDOM__"
                data.update(loaded)
        except Exception:
            pass
    return data


class AboutDialog(QDialog):
    def __init__(self, mascot, parent=None):
        super().__init__(parent)
        self.setWindowTitle(mascot.tr("win_about_title"))
        if mascot.primary_mascot.settings.get("language") == "ar":
            self.setLayoutDirection(Qt.RightToLeft)
        layout = QVBoxLayout(self)
        lbl = QLabel()
        pix = QPixmap(resource_path("assets/about.png"))
        if not pix.isNull():
            lbl.setPixmap(pix)
        else:
            lbl.setText(
                f"Crash Bandicoot Desktop Character (1998)\n"
                f"Produced for SCEE by MDR Software Ltd.\n"
                f"Remastered Edition ({OS_DISPLAY_NAME}) by @Hitsuji_Shiroi (2026)"
            )
        btn = QPushButton("OK")
        btn.clicked.connect(self.accept)
        layout.addWidget(lbl)
        layout.addWidget(btn)


class OptionsDialog(QDialog):
    SPEED_VALUES = [0.5, 1.0, 1.5, 2.0]

    def __init__(self, mascot, parent=None):
        super().__init__(parent)
        self.mascot = mascot
        self.primary = mascot.primary_mascot
        self.settings = self.primary.settings
        self.setFixedSize(520, 610)

        self.tabs = QTabWidget()
        self.tabs.addTab(self._build_classic_tab(), "")
        self.tabs.addTab(self._build_audio_tab(), "")
        self.tabs.addTab(self._build_desktop_tab(), "")

        bottom_row = QHBoxLayout()
        self.btn_reset = QPushButton()
        self.btn_reset.clicked.connect(self.reset_defaults)
        self.btn_ok = QPushButton()
        self.btn_ok.clicked.connect(self.save_and_close)
        bottom_row.addWidget(self.btn_reset)
        bottom_row.addStretch()
        bottom_row.addWidget(self.btn_ok)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.tabs)
        main_layout.addLayout(bottom_row)

        self.retranslate_ui()
        self.load_ui_from_dict(self.settings)

    def tr_key(self, key, **kwargs):
        return self.primary.lang_mgr.tr(self.current_lang_code(), key, **kwargs)

    def current_lang_code(self):
        if hasattr(self, "combo_lang") and self.combo_lang.currentData():
            return self.combo_lang.currentData()
        return self.settings.get("language", "en")

    def _build_classic_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        self.grp_rules = QGroupBox()
        lay_rules = QVBoxLayout(self.grp_rules)
        self.cb_move = QCheckBox()
        self.cb_vary = QCheckBox()
        self.cb_continue = QCheckBox()
        for w in (self.cb_move, self.cb_vary, self.cb_continue):
            lay_rules.addWidget(w)

        self.grp_timing = QGroupBox()
        form = QFormLayout(self.grp_timing)

        self.combo_char = QComboBox()
        for cid, cdata in self.primary.char_mgr.characters.items():
            self.combo_char.addItem(cdata["name"], cid)
        idx_char = self.combo_char.findData(self.settings.get("character_id", "default_crash"))
        if idx_char != -1:
            self.combo_char.setCurrentIndex(idx_char)

        self.combo_lang = QComboBox()
        for code, name in self.primary.lang_mgr.available_languages():
            self.combo_lang.addItem(name, code)
        idx_lang = self.combo_lang.findData(self.settings.get("language", "en"))
        if idx_lang != -1:
            self.combo_lang.setCurrentIndex(idx_lang)
        self.combo_lang.currentIndexChanged.connect(self.on_language_changed)

        self.combo_speed = QComboBox()
        self.combo_idle = QComboBox()

        self.lbl_character = QLabel()
        self.lbl_language = QLabel()
        self.lbl_dance_speed = QLabel()
        self.lbl_spontaneous = QLabel()

        form.addRow(self.lbl_character, self.combo_char)
        form.addRow(self.lbl_language, self.combo_lang)
        form.addRow(self.lbl_dance_speed, self.combo_speed)
        form.addRow(self.lbl_spontaneous, self.combo_idle)

        layout.addWidget(self.grp_rules)
        layout.addWidget(self.grp_timing)
        layout.addStretch()
        return tab

    def _build_audio_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        self.btn_mute_all = QPushButton()
        self.btn_mute_all.setCheckable(True)
        self.btn_mute_all.toggled.connect(self.update_audio_controls_state)
        layout.addWidget(self.btn_mute_all)

        self.grp_music = QGroupBox()
        lay_music = QVBoxLayout(self.grp_music)

        row_m_vol = QHBoxLayout()
        self.cb_music = QCheckBox()
        self.slider_music_vol = QSlider(Qt.Horizontal)
        self.slider_music_vol.setRange(0, 100)
        self.slider_music_vol.valueChanged.connect(
            lambda v: self.primary.audio_output.setVolume(0.0 if self.btn_mute_all.isChecked() else v / 100.0)
        )
        row_m_vol.addWidget(self.cb_music)
        row_m_vol.addWidget(self.slider_music_vol)

        form_ost = QFormLayout()
        self.combo_edition = QComboBox()
        self.combo_edition.currentIndexChanged.connect(self.on_edition_changed)

        self.combo_track = QComboBox()
        self.combo_track.currentIndexChanged.connect(self.on_track_selected)

        self.lbl_ost_style = QLabel()
        self.lbl_selected_track = QLabel()
        form_ost.addRow(self.lbl_ost_style, self.combo_edition)
        form_ost.addRow(self.lbl_selected_track, self.combo_track)

        self.lbl_now_playing = QLabel()
        self.lbl_now_playing.setStyleSheet("font-weight: bold; color: #d35400;")

        row_transport = QHBoxLayout()
        self.btn_prev = QPushButton()
        self.btn_play_pause = QPushButton()
        self.btn_next = QPushButton()
        self.btn_prev.clicked.connect(lambda: self._step_track(-1))
        self.btn_play_pause.clicked.connect(self.on_play_pause_clicked)
        self.btn_next.clicked.connect(lambda: self._step_track(1))
        for b in (self.btn_prev, self.btn_play_pause, self.btn_next):
            row_transport.addWidget(b)

        self.cb_autoplay = QCheckBox()

        lay_music.addLayout(row_m_vol)
        lay_music.addLayout(form_ost)
        lay_music.addWidget(self.lbl_now_playing)
        lay_music.addLayout(row_transport)
        lay_music.addWidget(self.cb_autoplay)

        self.grp_sfx = QGroupBox()
        row_sfx = QHBoxLayout(self.grp_sfx)
        self.cb_sfx = QCheckBox()
        self.slider_sfx_vol = QSlider(Qt.Horizontal)
        self.slider_sfx_vol.setRange(0, 100)
        row_sfx.addWidget(self.cb_sfx)
        row_sfx.addWidget(self.slider_sfx_vol)

        layout.addWidget(self.grp_music)
        layout.addWidget(self.grp_sfx)
        layout.addStretch()
        return tab

    def _build_desktop_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        self.grp_display = QGroupBox()
        form_vis = QFormLayout(self.grp_display)
        self.combo_scale = QComboBox()
        self.slider_opacity = QSlider(Qt.Horizontal)
        self.slider_opacity.setRange(30, 100)
        self.combo_monitor = QComboBox()

        self.lbl_scale = QLabel()
        self.lbl_opacity = QLabel()
        self.lbl_screen = QLabel()
        form_vis.addRow(self.lbl_scale, self.combo_scale)
        form_vis.addRow(self.lbl_opacity, self.slider_opacity)
        form_vis.addRow(self.lbl_screen, self.combo_monitor)

        self.grp_fs = QGroupBox()
        lay_fs = QVBoxLayout(self.grp_fs)
        self.cb_hide_fs = QCheckBox()
        self.cb_force_fs = QCheckBox()
        self.cb_hide_fs.toggled.connect(lambda c: self.cb_force_fs.setChecked(False) if c else None)
        self.cb_force_fs.toggled.connect(lambda c: self.cb_hide_fs.setChecked(False) if c else None)
        lay_fs.addWidget(self.cb_hide_fs)
        lay_fs.addWidget(self.cb_force_fs)

        self.grp_sys = QGroupBox()
        lay_sys = QVBoxLayout(self.grp_sys)
        self.cb_gravity = QCheckBox()
        self.cb_lock_pos = QCheckBox()
        self.cb_splash = QCheckBox()
        self.cb_startup = QCheckBox()
        self.cb_ghost = QCheckBox()
        self.lbl_hotkey_info = QLabel()
        self.lbl_hotkey_info.setStyleSheet("color: #666666; font-size: 11px;")
        self.cb_gravity.toggled.connect(lambda c: self.cb_lock_pos.setChecked(False) if c else None)
        for w in (self.cb_gravity, self.cb_lock_pos, self.cb_splash, self.cb_startup, self.cb_ghost, self.lbl_hotkey_info):
            lay_sys.addWidget(w)

        layout.addWidget(self.grp_display)
        layout.addWidget(self.grp_fs)
        layout.addWidget(self.grp_sys)
        layout.addStretch()
        return tab

    def retranslate_ui(self):
        code = self.current_lang_code()
        self.setLayoutDirection(Qt.RightToLeft if code == "ar" else Qt.LeftToRight)
        self.setWindowTitle(self.tr_key("win_options_title"))

        self.tabs.setTabText(0, self.tr_key("tab_classic"))
        self.tabs.setTabText(1, self.tr_key("tab_audio"))
        self.tabs.setTabText(2, self.tr_key("tab_desktop"))

        self.grp_rules.setTitle(self.tr_key("grp_1998"))
        self.cb_move.setText(self.tr_key("cb_allow_move"))
        self.cb_vary.setText(self.tr_key("cb_vary_length"))
        self.cb_continue.setText(self.tr_key("cb_continue_dancing"))

        self.grp_timing.setTitle(self.tr_key("grp_timing"))
        self.lbl_character.setText(self.tr_key("lbl_character"))
        self.lbl_language.setText(self.tr_key("lbl_language"))
        self.lbl_dance_speed.setText(self.tr_key("lbl_dance_speed"))
        self.lbl_spontaneous.setText(self.tr_key("lbl_spontaneous"))

        cur_spd_idx = max(0, self.combo_speed.currentIndex())
        self.combo_speed.blockSignals(True)
        self.combo_speed.clear()
        self.combo_speed.addItems([
            self.tr_key("spd_slow"),
            self.tr_key("spd_normal"),
            self.tr_key("spd_fast"),
            self.tr_key("spd_turbo")
        ])
        self.combo_speed.setCurrentIndex(cur_spd_idx)
        self.combo_speed.blockSignals(False)

        cur_idle_idx = max(0, self.combo_idle.currentIndex())
        self.combo_idle.blockSignals(True)
        self.combo_idle.clear()
        self.combo_idle.addItems([
            self.tr_key("idle_never"),
            self.tr_key("idle_rarely"),
            self.tr_key("idle_normal"),
            self.tr_key("idle_hyper")
        ])
        self.combo_idle.setCurrentIndex(cur_idle_idx)
        self.combo_idle.blockSignals(False)

        self.grp_music.setTitle(self.tr_key("grp_music"))
        self.cb_music.setText(self.tr_key("cb_enable_music"))
        self.lbl_ost_style.setText(self.tr_key("lbl_ost_style"))
        self.lbl_selected_track.setText(self.tr_key("lbl_selected_track"))

        cur_ed_key = self.combo_edition.currentData() or self.settings.get("ost_edition", "ps1")
        self.combo_edition.blockSignals(True)
        self.combo_edition.clear()
        for ed_key in OST_EDITION_KEYS:
            self.combo_edition.addItem(self.tr_key(f"ost_{ed_key}"), ed_key)
        idx_ed = self.combo_edition.findData(cur_ed_key)
        if idx_ed != -1:
            self.combo_edition.setCurrentIndex(idx_ed)
        self.combo_edition.blockSignals(False)

        cur_trk_data = self.combo_track.currentData() or self.settings.get("current_track", "__RANDOM__")
        self.populate_tracks(cur_ed_key, cur_trk_data)

        self.btn_prev.setText(self.tr_key("btn_prev"))
        self.btn_next.setText(self.tr_key("btn_next"))
        self.cb_autoplay.setText(self.tr_key("cb_autoplay"))

        self.grp_sfx.setTitle(self.tr_key("grp_sfx"))
        self.cb_sfx.setText(self.tr_key("cb_enable_sfx"))

        self.grp_display.setTitle(self.tr_key("grp_display"))
        self.lbl_scale.setText(self.tr_key("lbl_scale"))
        self.lbl_opacity.setText(self.tr_key("lbl_opacity"))
        self.lbl_screen.setText(self.tr_key("lbl_screen"))

        cur_scale_idx = max(0, self.combo_scale.currentIndex())
        self.combo_scale.blockSignals(True)
        self.combo_scale.clear()
        self.combo_scale.addItems([
            self.tr_key("scale_1x"),
            self.tr_key("scale_2x"),
            self.tr_key("scale_3x"),
            self.tr_key("scale_4x")
        ])
        self.combo_scale.setCurrentIndex(cur_scale_idx)
        self.combo_scale.blockSignals(False)

        cur_mon_idx = max(0, self.combo_monitor.currentIndex())
        self.combo_monitor.blockSignals(True)
        self.combo_monitor.clear()
        for idx, scr in enumerate(QApplication.screens()):
            geo = scr.geometry()
            self.combo_monitor.addItem(self.tr_key("lbl_monitor_item", num=idx + 1, w=geo.width(), h=geo.height()))
        self.combo_monitor.setCurrentIndex(min(cur_mon_idx, self.combo_monitor.count() - 1))
        self.combo_monitor.blockSignals(False)

        self.grp_fs.setTitle(self.tr_key("grp_fs"))
        self.cb_hide_fs.setText(self.tr_key("cb_hide_fs"))
        self.cb_force_fs.setText(self.tr_key("cb_force_fs"))

        self.grp_sys.setTitle(self.tr_key("grp_sys"))
        self.cb_gravity.setText(self.tr_key("cb_gravity"))
        self.cb_lock_pos.setText(self.tr_key("cb_lock_pos"))
        self.cb_splash.setText(self.tr_key("cb_splash"))
        self.cb_startup.setText(self.tr_key("cb_startup"))
        self.cb_ghost.setText(self.tr_key("cb_ghost"))
        self.lbl_hotkey_info.setText(self.tr_key("lbl_hotkey_info"))

        self.btn_reset.setText(self.tr_key("btn_reset_1998"))
        self.btn_ok.setText(self.tr_key("btn_apply_ok"))

        self.update_audio_controls_state(self.btn_mute_all.isChecked())
        self.refresh_transport_ui()

    def on_language_changed(self):
        self.settings["language"] = self.current_lang_code()
        self.retranslate_ui()
        self.primary.rebuild_tray_menu()

    def load_ui_from_dict(self, cfg, first_track_on_reset=False):
        self.cb_move.setChecked(cfg["allow_move"])
        self.cb_vary.setChecked(cfg["vary_length"])
        self.cb_continue.setChecked(cfg["continue_dancing"])

        idx_spd = self.SPEED_VALUES.index(cfg["anim_speed"]) if cfg["anim_speed"] in self.SPEED_VALUES else 1
        self.combo_speed.setCurrentIndex(idx_spd)
        self.combo_idle.setCurrentIndex(cfg["idle_frequency"])

        self.btn_mute_all.setChecked(cfg["mute_all"])
        self.cb_music.setChecked(cfg["music_on"])
        self.slider_music_vol.setValue(int(cfg["music_volume"] * 100))

        self.combo_edition.blockSignals(True)
        idx_ed = self.combo_edition.findData(cfg["ost_edition"])
        if idx_ed != -1:
            self.combo_edition.setCurrentIndex(idx_ed)
        self.combo_edition.blockSignals(False)

        self.populate_tracks(cfg["ost_edition"], cfg.get("current_track", "__RANDOM__"))
        if first_track_on_reset and self.combo_track.count() > 1:
            self.combo_track.setCurrentIndex(1)

        self.cb_autoplay.setChecked(cfg["playlist_autoplay"])
        self.cb_sfx.setChecked(cfg["sfx_on"])
        self.slider_sfx_vol.setValue(int(cfg["sfx_volume"] * 100))

        self.combo_scale.setCurrentIndex(min(cfg["scale"] - 1, 3))
        self.slider_opacity.setValue(int(cfg["opacity"] * 100))
        self.combo_monitor.setCurrentIndex(min(cfg["monitor_index"], self.combo_monitor.count() - 1))
        self.cb_hide_fs.setChecked(cfg["hide_fullscreen"])
        self.cb_force_fs.setChecked(cfg["force_over_fullscreen"])
        self.cb_gravity.setChecked(cfg["gravity_on"])
        self.cb_lock_pos.setChecked(cfg["lock_position"])
        self.cb_splash.setChecked(cfg["show_splash"])
        self.cb_startup.setChecked(cfg["run_at_startup"])
        self.cb_ghost.setChecked(cfg["ghost_mode"])

        self.update_audio_controls_state(self.btn_mute_all.isChecked())
        self.refresh_transport_ui()

    def populate_tracks(self, edition_key, preferred_track="__RANDOM__"):
        self.combo_track.blockSignals(True)
        self.combo_track.clear()
        self.combo_track.addItem(self.tr_key("opt_random_track"), "__RANDOM__")
        tracks_dict = self.primary.get_tracks_for_edition(edition_key)
        for name in tracks_dict.keys():
            self.combo_track.addItem(name, name)
        idx = self.combo_track.findData(preferred_track)
        self.combo_track.setCurrentIndex(idx if idx != -1 else 0)
        self.combo_track.blockSignals(False)

    def on_edition_changed(self):
        ed_key = self.combo_edition.currentData()
        self.settings["ost_edition"] = ed_key
        self.settings["current_track"] = "__RANDOM__"
        self.populate_tracks(ed_key, "__RANDOM__")
        self.primary.load_track_by_choice("__RANDOM__", auto_play=self.primary.is_music_playing())
        self.refresh_transport_ui()

    def on_track_selected(self):
        track_val = self.combo_track.currentData()
        if track_val:
            self.settings["current_track"] = track_val
            self.primary.load_track_by_choice(track_val, auto_play=True)
            self.refresh_transport_ui()

    def _step_track(self, delta):
        self.settings["ost_edition"] = self.combo_edition.currentData()
        self.primary.step_track(delta, show_toast=True)
        self.combo_track.blockSignals(True)
        idx = self.combo_track.findData(self.primary.current_playing_name)
        if idx != -1:
            self.combo_track.setCurrentIndex(idx)
        self.combo_track.blockSignals(False)
        self.refresh_transport_ui()

    def on_play_pause_clicked(self):
        self.settings["ost_edition"] = self.combo_edition.currentData()
        if not self.cb_music.isChecked():
            self.cb_music.setChecked(True)
            self.settings["music_on"] = True
        self.primary.toggle_play_pause_music()
        self.refresh_transport_ui()

    def refresh_transport_ui(self):
        track_display = self.primary.current_playing_name or self.tr_key("txt_no_tracks")
        self.lbl_now_playing.setText(self.tr_key("lbl_now_playing", track=track_display))
        self.btn_play_pause.setText(self.tr_key("btn_pause") if self.primary.is_music_playing() else self.tr_key("btn_play"))

    def update_audio_controls_state(self, is_muted):
        self.btn_mute_all.setText(self.tr_key("btn_unmute_all") if is_muted else self.tr_key("btn_mute_all"))
        for w in (
            self.cb_music, self.slider_music_vol, self.combo_edition,
            self.combo_track, self.btn_prev, self.btn_play_pause,
            self.btn_next, self.cb_autoplay, self.cb_sfx, self.slider_sfx_vol
        ):
            w.setEnabled(not is_muted)

    def reset_defaults(self):
        self.load_ui_from_dict(CLASSIC_1998_PRESET, first_track_on_reset=True)

    def save_and_close(self):
        self.settings.update({
            "character_id": self.combo_char.currentData(),
            "language": self.current_lang_code(),
            "allow_move": self.cb_move.isChecked(),
            "vary_length": self.cb_vary.isChecked(),
            "continue_dancing": self.cb_continue.isChecked(),
            "anim_speed": self.SPEED_VALUES[self.combo_speed.currentIndex()],
            "idle_frequency": self.combo_idle.currentIndex(),
            "mute_all": self.btn_mute_all.isChecked(),
            "music_on": self.cb_music.isChecked(),
            "music_volume": self.slider_music_vol.value() / 100.0,
            "ost_edition": self.combo_edition.currentData(),
            "current_track": self.combo_track.currentData(),
            "playlist_autoplay": self.cb_autoplay.isChecked(),
            "sfx_on": self.cb_sfx.isChecked(),
            "sfx_volume": self.slider_sfx_vol.value() / 100.0,
            "scale": self.combo_scale.currentIndex() + 1,
            "opacity": self.slider_opacity.value() / 100.0,
            "monitor_index": self.combo_monitor.currentIndex(),
            "hide_fullscreen": self.cb_hide_fs.isChecked(),
            "force_over_fullscreen": self.cb_force_fs.isChecked(),
            "gravity_on": self.cb_gravity.isChecked(),
            "lock_position": self.cb_lock_pos.isChecked(),
            "show_splash": self.cb_splash.isChecked(),
            "run_at_startup": self.cb_startup.isChecked(),
            "ghost_mode": self.cb_ghost.isChecked()
        })
        self.accept()


class CrashMascot1998(QLabel):
    DANCE_MOVES = [
        ("Jiggle", "move_jiggle"),
        ("Foot Stomp", "move_foot_stomp"),
        ("Pelvic Thrust", "move_pelvic_thrust"),
        ("Turn Around", "move_turn_around"),
        ("Behind You", "move_behind_you")
    ]

    def __init__(self, settings, lang_mgr, char_mgr, is_clone=False, primary_mascot=None, spawn_offset=0):
        super().__init__()
        flags = Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool
        if IS_MACOS:
            flags |= Qt.NoDropShadowWindowHint
        elif IS_LINUX:
            flags |= Qt.X11BypassWindowManagerHint
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        self.is_clone = is_clone
        self.primary_mascot = self if not is_clone else primary_mascot
        self.clones = [] if not is_clone else None

        self.settings = settings if not is_clone else dict(primary_mascot.settings)
        if is_clone:
            self.settings["lock_position"] = False
            self.settings["pinned_x"] = None
            self.settings["pinned_y"] = None

        self.lang_mgr = lang_mgr
        self.char_mgr = char_mgr
        self.toast = RetroToast() if not is_clone else primary_mascot.toast

        self._xdisp = None
        if IS_LINUX and HAS_XLIB:
            try:
                self._xdisp = xlib_display.Display()
            except Exception:
                self._xdisp = None

        self.current_state = "Neutral"
        self.is_full_dance_mode = False
        self.single_move_mode = False
        self.move_ticks_remaining = 0
        self.frame_index = 0
        self.direction = random.choice([-1, 1]) if is_clone else 1
        self.is_dragging = False
        self.velocity_y = 0
        self.drag_offset = QPoint()

        self.hidden_by_fullscreen = False
        self.music_was_playing_before_fs = False
        self.music_user_paused = False
        self.current_playing_name = ""

        if not is_clone:
            self.audio_output = QAudioOutput()
            self.music_player = QMediaPlayer()
            self.music_player.setAudioOutput(self.audio_output)
            self.music_player.mediaStatusChanged.connect(self.on_media_status_changed)
        else:
            self.audio_output = primary_mascot.audio_output
            self.music_player = primary_mascot.music_player

        self.sfx_players = []
        self.load_character_assets(self.settings.get("character_id", "default_crash"))

        self.apply_audio_settings()
        self.apply_window_settings(move_to_screen=True, spawn_offset=spawn_offset)

        if not is_clone:
            self.setup_tray_icon()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.update_timer_speed()

        self.fs_timer = QTimer(self)
        self.fs_timer.timeout.connect(self.check_fullscreen_state)
        self.fs_timer.start(500)

        if not is_clone and IS_WINDOWS:
            try:
                ctypes.windll.user32.RegisterHotKey(None, HOTKEY_RESCUE_ID, 0x0002 | 0x0004 | 0x4000, 0x43)
            except Exception:
                pass

    # --- Gestión de Clones (Multi-Crash) ---
    def all_instances(self):
        p = self.primary_mascot
        return [p] + list(p.clones)

    def spawn_clone(self):
        p = self.primary_mascot
        offset = ((len(p.clones) + 1) * 55) * (1 if len(p.clones) % 2 == 0 else -1)
        clone = CrashMascot1998(
            p.settings, p.lang_mgr, p.char_mgr,
            is_clone=True, primary_mascot=p, spawn_offset=offset
        )
        p.clones.append(clone)
        clone.show()
        if p.is_full_dance_mode:
            clone.start_dance()
        p.rebuild_tray_menu()
        p.toast.show_message(p.tr("toast_clone_spawned", count=len(p.all_instances())), clone.geometry())

    def remove_this_clone(self):
        if not self.is_clone:
            return
        p = self.primary_mascot
        self.timer.stop()
        self.fs_timer.stop()
        if self in p.clones:
            p.clones.remove(self)
        p.rebuild_tray_menu()
        self.close()
        self.deleteLater()

    def clear_all_clones(self):
        p = self.primary_mascot
        for c in list(p.clones):
            c.timer.stop()
            c.fs_timer.stop()
            c.close()
            c.deleteLater()
        p.clones.clear()
        p.rebuild_tray_menu()
        p.toast.show_message(p.tr("toast_clone_spawned", count=1), p.geometry())

    def dance_all_instances(self):
        for inst in self.all_instances():
            inst.start_dance()

    def stop_all_instances(self):
        for inst in self.all_instances():
            inst.stop_crash()

    def rescue_character(self):
        p = self.primary_mascot
        for idx, inst in enumerate(p.all_instances()):
            inst.settings.update({
                "ghost_mode": False,
                "lock_position": False,
                "pinned_x": None,
                "pinned_y": None
            })
            inst.hidden_by_fullscreen = False
            offset = (idx * 50) * (1 if idx % 2 == 0 else -1)
            inst.apply_window_settings(move_to_screen=True, spawn_offset=offset)
            inst.raise_()
        p.save_settings()
        p.activateWindow()
        p.rebuild_tray_menu()
        p.toast.show_message(p.tr("toast_rescued"), p.geometry())

    def tr(self, key, **kwargs):
        return self.primary_mascot.lang_mgr.tr(self.primary_mascot.settings.get("language", "en"), key, **kwargs)

    def save_settings(self):
        if self.is_clone:
            return
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=2)
        except Exception:
            pass

    def configure_os_startup(self, enable):
        try:
            if IS_WINDOWS:
                startup_dir = os.path.join(
                    os.environ.get("APPDATA", ""),
                    r"Microsoft\Windows\Start Menu\Programs\Startup"
                )
                if not os.path.isdir(startup_dir):
                    return
                bat_path = os.path.join(startup_dir, "CrashBandicootDesktop1998.bat")
                if enable:
                    if getattr(sys, 'frozen', False):
                        target = f'start "" "{sys.executable}"'
                    else:
                        script_path = os.path.abspath(__file__)
                        target = f'cd /d "{os.path.dirname(script_path)}"\nstart "" pyw "{script_path}"'
                    with open(bat_path, "w", encoding="utf-8") as f:
                        f.write(f"@echo off\n{target}\n")
                elif os.path.exists(bat_path):
                    os.remove(bat_path)

            elif IS_MACOS:
                launch_dir = os.path.expanduser("~/Library/LaunchAgents")
                os.makedirs(launch_dir, exist_ok=True)
                plist_path = os.path.join(launch_dir, f"{LAUNCH_AGENT_LABEL}.plist")
                if enable:
                    prog_args = [sys.executable] if getattr(sys, 'frozen', False) else [sys.executable, os.path.abspath(__file__)]
                    with open(plist_path, "wb") as f:
                        plistlib.dump({"Label": LAUNCH_AGENT_LABEL, "ProgramArguments": prog_args, "RunAtLoad": True}, f)
                elif os.path.exists(plist_path):
                    os.remove(plist_path)

            elif IS_LINUX:
                xdg_config = os.environ.get("XDG_CONFIG_HOME") or os.path.expanduser("~/.config")
                autostart_dir = os.path.join(xdg_config, "autostart")
                os.makedirs(autostart_dir, exist_ok=True)
                desktop_path = os.path.join(autostart_dir, "CrashBandicootDesktop1998.desktop")
                if enable:
                    exec_cmd = f'"{sys.executable}"' if getattr(sys, 'frozen', False) else f'"{sys.executable}" "{os.path.abspath(__file__)}"'
                    with open(desktop_path, "w", encoding="utf-8") as f:
                        f.write(
                            "[Desktop Entry]\nType=Application\nName=Crash Bandicoot Desktop Character (1998)\n"
                            f"Exec={exec_cmd}\nTerminal=false\nX-GNOME-Autostart-enabled=true\n"
                        )
                elif os.path.exists(desktop_path):
                    os.remove(desktop_path)
        except Exception:
            pass

    def _get_mac_windows(self):
        if not HAS_QUARTZ:
            return []
        try:
            my_pid = os.getpid()
            options = Quartz.kCGWindowListOptionOnScreenOnly | Quartz.kCGWindowListExcludeDesktopElements
            win_list = Quartz.CGWindowListCopyWindowInfo(options, Quartz.kCGNullWindowID)
            result = []
            for win in win_list:
                if win.get("kCGWindowLayer", 0) != 0 or win.get("kCGWindowOwnerPID") == my_pid:
                    continue
                bounds = win.get("kCGWindowBounds")
                if bounds:
                    result.append((int(bounds.get("X", 0)), int(bounds.get("Y", 0)), int(bounds.get("Width", 0)), int(bounds.get("Height", 0))))
            return result
        except Exception:
            return []

    def _get_x11_active_window_info(self):
        if not self._xdisp:
            return None
        try:
            root = self._xdisp.screen().root
            atom_active = self._xdisp.intern_atom("_NET_ACTIVE_WINDOW")
            prop = root.get_full_property(atom_active, X.AnyPropertyType)
            if not prop or not prop.value:
                return None
            win_id = prop.value[0]
            if not win_id or win_id == int(self.winId()):
                return None
            win = self._xdisp.create_resource_object("window", win_id)
            is_fs_atom = False
            state_prop = win.get_full_property(self._xdisp.intern_atom("_NET_WM_STATE"), X.AnyPropertyType)
            if state_prop and state_prop.value and self._xdisp.intern_atom("_NET_WM_STATE_FULLSCREEN") in state_prop.value:
                is_fs_atom = True
            geom = win.get_geometry()
            coords = win.translate_coords(root, 0, 0)
            return {"x": coords.x, "y": coords.y, "w": geom.width, "h": geom.height, "is_fs_atom": is_fs_atom}
        except Exception:
            return None

    def is_fullscreen_active(self):
        try:
            screens = QApplication.screens()
            mon_geo = screens[min(self.settings.get("monitor_index", 0), len(screens) - 1)].geometry()

            if IS_WINDOWS:
                state = ctypes.c_int()
                if ctypes.windll.shell32.SHQueryUserNotificationState(ctypes.byref(state)) == 0 and state.value in (2, 3, 4):
                    return True
                hwnd = ctypes.windll.user32.GetForegroundWindow()
                if not hwnd or hwnd == int(self.winId()):
                    return False
                class_buf = ctypes.create_unicode_buffer(256)
                ctypes.windll.user32.GetClassNameW(hwnd, class_buf, 256)
                if class_buf.value in ("Progman", "WorkerW", "Shell_TrayWnd", "Shell_SecondaryTrayWnd"):
                    return False
                rect = wintypes.RECT()
                if ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(rect)):
                    return rect.left <= mon_geo.left() + 2 and rect.top <= mon_geo.top() + 2 and rect.right >= mon_geo.right() - 1 and rect.bottom >= mon_geo.bottom() - 1

            elif IS_MACOS:
                for x, y, w, h in self._get_mac_windows():
                    if x <= mon_geo.left() + 2 and y <= mon_geo.top() + 2 and (x + w) >= mon_geo.right() - 1 and (y + h) >= mon_geo.bottom() - 1:
                        return True

            elif IS_LINUX:
                info = self._get_x11_active_window_info()
                if info:
                    if info["is_fs_atom"]:
                        return True
                    return info["x"] <= mon_geo.left() + 2 and info["y"] <= mon_geo.top() + 2 and (info["x"] + info["w"]) >= mon_geo.right() - 1 and (info["y"] + info["h"]) >= mon_geo.bottom() - 1
        except Exception:
            pass
        return False

    def check_fullscreen_state(self):
        if self.settings.get("force_over_fullscreen", False):
            if self.hidden_by_fullscreen:
                self.hidden_by_fullscreen = False
                self.show()
            if IS_WINDOWS:
                try:
                    ctypes.windll.user32.SetWindowPos(int(self.winId()), -1, 0, 0, 0, 0, 0x0013)
                except Exception:
                    pass
            else:
                self.raise_()
            return

        if self.settings.get("hide_fullscreen", True):
            fs_now = self.is_fullscreen_active()
            if fs_now and not self.hidden_by_fullscreen:
                self.hidden_by_fullscreen = True
                if not self.is_clone:
                    self.music_was_playing_before_fs = self.is_music_playing()
                    if self.music_was_playing_before_fs:
                        self.music_player.pause()
                self.hide()
            elif not fs_now and self.hidden_by_fullscreen:
                self.hidden_by_fullscreen = False
                self.show()
                if not self.is_clone and self.music_was_playing_before_fs and self.settings["music_on"] and not self.settings.get("mute_all", False):
                    self.music_player.play()
        elif self.hidden_by_fullscreen:
            self.hidden_by_fullscreen = False
            self.show()

    def load_character_assets(self, char_id):
        self.active_char = self.char_mgr.get_character(char_id)
        self.settings["character_id"] = self.active_char["id"]
        self.reload_sprites()
        self.ost_catalog, self.sfx_list = self.classify_audios(self.active_char["audio_dir"])

        for eff in self.sfx_players:
            eff.deleteLater()
        self.sfx_players = []
        for sfx_path in self.sfx_list:
            eff = QSoundEffect(self)
            eff.setSource(QUrl.fromLocalFile(sfx_path))
            self.sfx_players.append(eff)

        if not self.is_clone:
            was_playing = self.is_music_playing()
            self.load_track_by_choice(self.settings.get("current_track", "__RANDOM__"), auto_play=was_playing)
        self.apply_audio_settings()

    def set_character(self, char_id):
        for inst in self.all_instances():
            inst.load_character_assets(char_id)
            inst.apply_window_settings(move_to_screen=False)
        self.primary_mascot.save_settings()
        self.primary_mascot.rebuild_tray_menu()

    def get_wav_duration(self, filepath):
        try:
            with wave.open(filepath, 'rb') as w:
                rate = w.getframerate()
                return w.getnframes() / float(rate) if rate > 0 else 0
        except Exception:
            return 5.0 if os.path.getsize(filepath) > 40 * 1024 else 1.0

    def classify_audios(self, audio_dir):
        catalog = {"ps1": {}, "nsane": {}, "all": {}}
        sfx = []
        if not os.path.isdir(audio_dir):
            return catalog, sfx

        for root, _, files in os.walk(audio_dir):
            rel_folder = os.path.relpath(root, audio_dir).lower()
            for fname in sorted(files):
                lower_f = fname.lower()
                if not lower_f.endswith((".mp3", ".wav", ".ogg")):
                    continue
                full_path = os.path.join(root, fname)
                clean_name = os.path.splitext(fname)[0]

                if lower_f.endswith(".wav"):
                    duration = self.get_wav_duration(full_path)
                    if duration <= 3.0:
                        sfx.append(full_path)
                        continue
                    clean_name = f"{clean_name} ({int(duration)}s)"

                if "nsane" in rel_folder or "n. sane" in lower_f or "remaster" in lower_f:
                    catalog["nsane"][clean_name] = full_path
                    catalog["all"][f"[N. Sane] {clean_name}"] = full_path
                else:
                    catalog["ps1"][clean_name] = full_path
                    catalog["all"][f"[PS1] {clean_name}"] = full_path

        return catalog, sfx

    def get_tracks_for_edition(self, edition_key=None):
        p = self.primary_mascot
        ed = edition_key or p.settings.get("ost_edition", "ps1")
        if ed == "ps1":
            return p.ost_catalog.get("ps1") or p.ost_catalog.get("all", {})
        if ed == "nsane":
            return p.ost_catalog.get("nsane") or p.ost_catalog.get("all", {})
        return p.ost_catalog.get("all", {})

    def is_music_playing(self):
        return self.primary_mascot.music_player.playbackState() == QMediaPlayer.PlayingState

    def load_track_by_choice(self, choice, auto_play=True, show_toast=False):
        p = self.primary_mascot
        tracks_dict = p.get_tracks_for_edition()
        if not tracks_dict:
            p.current_playing_name = ""
            return
        names = list(tracks_dict.keys())
        chosen_name = random.choice(names) if (choice == "__RANDOM__" or choice not in tracks_dict) else choice
        path = tracks_dict[chosen_name]
        if os.path.exists(path):
            p.current_playing_name = chosen_name
            p.music_player.setSource(QUrl.fromLocalFile(path))
            if auto_play and not p.hidden_by_fullscreen and p.settings["music_on"] and not p.settings.get("mute_all", False):
                p.music_user_paused = False
                p.music_player.play()
            if show_toast and not p.hidden_by_fullscreen:
                p.toast.show_message(p.tr("toast_now_playing", track=chosen_name), self.geometry())

    def step_track(self, delta, from_end=False, show_toast=False):
        p = self.primary_mascot
        tracks_dict = p.get_tracks_for_edition()
        if not tracks_dict:
            return
        names = list(tracks_dict.keys())
        cur_idx = names.index(p.current_playing_name) if p.current_playing_name in names else 0
        target_name = names[(cur_idx + delta) % len(names)]
        if not from_end:
            p.settings["current_track"] = target_name
            p.save_settings()
        should_play = True if from_end else (p.is_music_playing() or not p.music_user_paused)
        self.load_track_by_choice(target_name, auto_play=should_play, show_toast=show_toast)

    def on_media_status_changed(self, status):
        if status != QMediaPlayer.EndOfMedia or not self.settings["music_on"] or self.settings.get("mute_all", False) or self.music_user_paused:
            return
        if self.settings.get("current_track") == "__RANDOM__":
            self.load_track_by_choice("__RANDOM__", auto_play=True)
        elif self.settings.get("playlist_autoplay", True):
            self.step_track(1, from_end=True)
        else:
            self.music_player.setPosition(0)
            self.music_player.play()

    def toggle_play_pause_music(self):
        p = self.primary_mascot
        if p.is_music_playing():
            p.music_user_paused = True
            p.music_player.pause()
        else:
            if not p.music_player.source().isValid():
                p.load_track_by_choice(p.settings.get("current_track", "__RANDOM__"), auto_play=False)
            if p.music_player.source().isValid():
                p.settings["music_on"] = True
                p.settings["mute_all"] = False
                p.music_user_paused = False
                p.apply_audio_settings()
                p.music_player.play()
                p.save_settings()

    def set_quick_volume(self, level):
        p = self.primary_mascot
        p.settings["music_volume"] = level
        p.settings["mute_all"] = False
        p.save_settings()
        p.apply_audio_settings()

    def set_ost_edition(self, edition_key):
        p = self.primary_mascot
        p.settings["ost_edition"] = edition_key
        p.settings["current_track"] = "__RANDOM__"
        p.save_settings()
        self.load_track_by_choice("__RANDOM__", auto_play=p.is_music_playing(), show_toast=True)

    def apply_audio_settings(self):
        p = self.primary_mascot
        is_muted = p.settings.get("mute_all", False)
        if not self.is_clone:
            self.audio_output.setVolume(0.0 if is_muted else p.settings.get("music_volume", 0.45))
            if is_muted or not p.settings["music_on"] or p.hidden_by_fullscreen:
                self.music_player.pause()
        sfx_vol = 0.0 if is_muted else p.settings.get("sfx_volume", 0.55)
        for eff in self.sfx_players:
            eff.setVolume(sfx_vol)

    def play_random_sfx(self):
        p = self.primary_mascot
        if not self.hidden_by_fullscreen and not p.settings.get("mute_all", False) and p.settings["sfx_on"] and self.sfx_players:
            random.choice(self.sfx_players).play()

    def apply_window_settings(self, move_to_screen=False, spawn_offset=0):
        self.setWindowOpacity(self.settings.get("opacity", 1.0))
        ghost = self.settings.get("ghost_mode", False)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, ghost)

        if IS_MACOS and HAS_QUARTZ:
            try:
                view = objc.objc_object(c_void_p=int(self.winId()))
                ns_window = view.window()
                if ns_window:
                    ns_window.setIgnoresMouseEvents_(ghost)
            except Exception:
                pass
        elif IS_LINUX and self._xdisp:
            try:
                from Xlib.ext import shape
                win = self._xdisp.create_resource_object("window", int(self.winId()))
                if ghost:
                    win.shape_rectangles(shape.SO.Set, shape.SK.Input, 0, 0, 0, [])
                else:
                    win.shape_mask(shape.SO.Set, shape.SK.Input, 0, 0, 0)
                self._xdisp.flush()
            except Exception:
                pass

        screens = QApplication.screens()
        self.screen_rect = screens[min(self.settings.get("monitor_index", 0), len(screens) - 1)].availableGeometry()
        self.update_sprite()

        if self.settings.get("lock_position", False) and self.settings.get("pinned_x") is not None:
            self.move(self.settings["pinned_x"], self.settings["pinned_y"])
        elif move_to_screen or not self.screen_rect.contains(self.geometry().center()):
            base_x = self.screen_rect.left() + (self.screen_rect.width() - self.width()) // 2 + spawn_offset
            clamped_x = max(self.screen_rect.left(), min(base_x, self.screen_rect.right() - self.width()))
            self.move(clamped_x, self.screen_rect.bottom() - self.height() - 5)
        if not self.hidden_by_fullscreen:
            self.show()

    def update_timer_speed(self):
        self.timer.start(max(25, int(95 / self.settings.get("anim_speed", 1.0))))

    def reload_sprites(self):
        anim_ranges = self.active_char["animations"]
        sprites_dir = self.active_char["sprites_dir"]
        self.animations = {}
        for state_name, (start_idx, end_idx) in anim_ranges.items():
            self.animations[state_name] = self.load_range(sprites_dir, start_idx, end_idx)

    def load_range(self, sprites_dir, start_idx, end_idx):
        frames = []
        s = self.settings["scale"]
        for i in range(start_idx, end_idx + 1):
            pix = QPixmap(os.path.join(sprites_dir, f"frame_{i:03d}.png"))
            if not pix.isNull():
                frames.append(pix.scaled(pix.width() * s, pix.height() * s, Qt.KeepAspectRatio, Qt.FastTransformation))
        return frames

    def update_sprite(self):
        frames = self.animations.get(self.current_state) or self.animations.get("Neutral", [])
        if not frames:
            return
        pix = frames[self.frame_index % len(frames)]
        if self.direction == -1:
            pix = pix.transformed(QTransform().scale(-1, 1))
        self.setPixmap(pix)
        self.resize(pix.size())

    def get_active_window_top(self):
        center_x = self.x() + self.width() // 2
        if IS_WINDOWS:
            try:
                hwnd = ctypes.windll.user32.GetForegroundWindow()
                if hwnd and hwnd != int(self.winId()):
                    rect = wintypes.RECT()
                    if ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(rect)):
                        if rect.left <= center_x <= rect.right and rect.top > self.screen_rect.top() + 40:
                            return rect.top
            except Exception:
                pass
        elif IS_MACOS:
            best_top = self.screen_rect.bottom()
            min_valid_top = self.screen_rect.top() + 38
            for x, y, w, h in self._get_mac_windows():
                if w > 60 and h > 60 and x <= center_x <= (x + w) and y > min_valid_top:
                    if y < best_top:
                        best_top = y
                        break
            return best_top
        elif IS_LINUX:
            info = self._get_x11_active_window_info()
            if info and info["x"] <= center_x <= (info["x"] + info["w"]) and info["y"] > self.screen_rect.top() + 40:
                return info["y"]
        return self.screen_rect.bottom()

    def tick(self):
        if self.is_dragging or self.hidden_by_fullscreen:
            return

        locked = self.settings.get("lock_position", False)
        if locked:
            px, py = self.settings.get("pinned_x"), self.settings.get("pinned_y")
            if px is not None and py is not None and (self.x() != px or self.y() != py):
                self.move(px, py)

        self.frame_index += 1

        if self.settings.get("gravity_on", True) and not locked:
            floor_y = self.screen_rect.bottom() - self.height()
            win_top = self.get_active_window_top() - self.height()
            target_y = win_top if (self.y() <= win_top + 12 and win_top < floor_y) else floor_y

            if self.y() < target_y:
                self.velocity_y += 5
                new_y = min(self.y() + self.velocity_y, target_y)
                self.move(self.x(), new_y)
                if new_y == target_y:
                    self.velocity_y = 0
                self.update_sprite()
                return
            self.velocity_y = 0

        if self.current_state == "Pelvic Thrust" and self.settings["allow_move"] and not locked:
            new_x = self.x() + (8 * self.direction)
            if new_x <= self.screen_rect.left():
                new_x, self.direction = self.screen_rect.left(), 1
            elif new_x + self.width() >= self.screen_rect.right():
                new_x, self.direction = self.screen_rect.right() - self.width(), -1
            self.move(new_x, self.y())

        if self.current_state != "Neutral":
            self.move_ticks_remaining -= 1
            if self.move_ticks_remaining <= 0:
                if self.is_full_dance_mode:
                    self.pick_next_dance_move()
                elif self.single_move_mode:
                    self.single_move_mode = False
                    if self.settings["continue_dancing"]:
                        self.start_dance()
                    else:
                        self.stop_crash()
                else:
                    self.current_state = "Neutral"
        else:
            prob = [0.0, 0.004, 0.015, 0.06][min(self.settings.get("idle_frequency", 2), 3)]
            if random.random() < prob:
                move_state = random.choice([m[0] for m in self.DANCE_MOVES])
                self.trigger_single_move(move_state, from_idle=True)

        self.update_sprite()

    def get_move_duration(self):
        return random.randint(15, 32) if self.settings["vary_length"] else 20

    def pick_next_dance_move(self):
        self.current_state = random.choice([m[0] for m in self.DANCE_MOVES])
        self.frame_index = 0
        self.move_ticks_remaining = self.get_move_duration()
        if random.random() < 0.4:
            self.direction = random.choice([-1, 1])
        self.play_random_sfx()

    def start_dance(self):
        p = self.primary_mascot
        self.is_full_dance_mode = True
        self.single_move_mode = False
        self.pick_next_dance_move()
        if not self.is_clone:
            if not p.music_player.source().isValid():
                p.load_track_by_choice(p.settings.get("current_track", "__RANDOM__"), auto_play=False)
            if (
                not p.hidden_by_fullscreen
                and not p.settings.get("mute_all", False)
                and p.settings["music_on"]
                and not p.music_user_paused
                and p.music_player.source().isValid()
            ):
                p.music_player.play()

    def stop_crash(self):
        self.is_full_dance_mode = False
        self.single_move_mode = False
        self.current_state = "Neutral"
        self.frame_index = 0
        if not self.is_clone:
            self.music_player.stop()
        self.update_sprite()

    def trigger_single_move(self, move_name, from_idle=False):
        self.is_full_dance_mode = False
        self.single_move_mode = not from_idle
        self.current_state = move_name
        self.frame_index = 0
        self.move_ticks_remaining = self.get_move_duration()
        self.play_random_sfx()

    def toggle_quick_setting(self, key):
        p = self.primary_mascot
        if key in ("lock_position", "gravity_on", "ghost_mode"):
            self.settings[key] = not self.settings[key]
            if key == "lock_position":
                self.settings["pinned_x"] = self.x() if self.settings["lock_position"] else None
                self.settings["pinned_y"] = self.y() if self.settings["lock_position"] else None
            elif key == "gravity_on" and self.settings["gravity_on"]:
                self.settings.update({"lock_position": False, "pinned_x": None, "pinned_y": None})
            if not self.is_clone:
                p.save_settings()
            self.apply_window_settings(move_to_screen=False)
        else:
            p.settings[key] = not p.settings[key]
            if key == "hide_fullscreen" and p.settings["hide_fullscreen"]:
                p.settings["force_over_fullscreen"] = False
            elif key == "force_over_fullscreen" and p.settings["force_over_fullscreen"]:
                p.settings["hide_fullscreen"] = False
            p.save_settings()
            for inst in p.all_instances():
                inst.settings[key] = p.settings[key]
                inst.settings["hide_fullscreen"] = p.settings["hide_fullscreen"]
                inst.settings["force_over_fullscreen"] = p.settings["force_over_fullscreen"]
                inst.check_fullscreen_state()
                inst.apply_audio_settings()

        p.rebuild_tray_menu()

    def open_options(self):
        p = self.primary_mascot
        old_char = p.settings.get("character_id", "default_crash")
        old_scale = p.settings["scale"]
        old_mon = p.settings.get("monitor_index", 0)
        old_startup = p.settings.get("run_at_startup", False)

        if OptionsDialog(self, self).exec():
            locked = p.settings.get("lock_position", False)
            p.settings["pinned_x"] = p.x() if locked else None
            p.settings["pinned_y"] = p.y() if locked else None
            p.save_settings()

            if p.settings.get("run_at_startup", False) != old_startup:
                p.configure_os_startup(p.settings["run_at_startup"])

            for inst in p.all_instances():
                if inst.is_clone:
                    keep_x, keep_y = inst.x(), inst.y()
                    inst.settings.update(p.settings)
                    inst.settings["lock_position"] = False
                    inst.settings["pinned_x"] = None
                    inst.settings["pinned_y"] = None

                if p.settings.get("character_id") != old_char:
                    inst.load_character_assets(p.settings["character_id"])
                elif p.settings["scale"] != old_scale:
                    inst.reload_sprites()

                inst.update_timer_speed()
                inst.check_fullscreen_state()
                inst.apply_audio_settings()
                inst.apply_window_settings(move_to_screen=(p.settings.get("monitor_index", 0) != old_mon))
                if inst.is_clone and p.settings.get("monitor_index", 0) == old_mon:
                    inst.move(keep_x, keep_y)

            p.rebuild_tray_menu()

    # --- Menús Dinámicos Multi-idioma ---
    def _make_check_action(self, text_key, setting_key, parent_menu, enabled=True, use_primary=False):
        target_cfg = self.primary_mascot.settings if use_primary else self.settings
        act = QAction(self.tr(text_key), self, checkable=True)
        act.setChecked(target_cfg.get(setting_key, False))
        act.setEnabled(enabled)
        act.triggered.connect(lambda: self.toggle_quick_setting(setting_key))
        parent_menu.addAction(act)
        return act

    def _populate_clones_menu(self, menu):
        p = self.primary_mascot
        total = len(p.all_instances())
        clone_menu = menu.addMenu(f"{self.tr('menu_clones')} ({total})")
        clone_menu.addAction(self.tr("act_spawn_clone"), self.spawn_clone)
        clone_menu.addSeparator()
        clone_menu.addAction(self.tr("act_dance_all"), self.dance_all_instances)
        clone_menu.addAction(self.tr("act_stop_all"), self.stop_all_instances)
        if total > 1:
            clone_menu.addSeparator()
            clone_menu.addAction(self.tr("act_clear_clones"), self.clear_all_clones)

    def _populate_character_menu(self, menu):
        if len(self.char_mgr.characters) <= 1:
            return
        char_menu = menu.addMenu(self.tr("menu_character"))
        grp = QActionGroup(self)
        grp.setExclusive(True)
        cur_cid = self.primary_mascot.settings.get("character_id", "default_crash")
        for cid, cdata in self.char_mgr.characters.items():
            act = QAction(cdata["name"], self, checkable=True)
            act.setChecked(cid == cur_cid)
            act.triggered.connect(lambda checked=False, c=cid: self.set_character(c))
            grp.addAction(act)
            char_menu.addAction(act)

    def _populate_position_menu(self, menu):
        self._make_check_action("act_hide_fs", "hide_fullscreen", menu, use_primary=True)
        self._make_check_action("act_force_fs", "force_over_fullscreen", menu, use_primary=True)
        menu.addSeparator()
        self._make_check_action("act_gravity", "gravity_on", menu)
        self._make_check_action("act_lock_pos", "lock_position", menu)

    def _populate_audio_menu(self, menu):
        p = self.primary_mascot
        is_muted = p.settings.get("mute_all", False)
        now_title = p.current_playing_name or self.tr("txt_no_tracks")
        act_now = QAction(f"♪ {now_title}", self)
        act_now.setEnabled(False)
        menu.addAction(act_now)

        for key, slot in (
            ("act_pause_music" if self.is_music_playing() else "act_play_music", self.toggle_play_pause_music),
            ("act_next_track", lambda: self.step_track(1, show_toast=True)),
            ("act_prev_track", lambda: self.step_track(-1, show_toast=True))
        ):
            act = QAction(self.tr(key), self)
            act.setEnabled(not is_muted)
            act.triggered.connect(slot)
            menu.addAction(act)

        menu.addSeparator()

        qvol_menu = menu.addMenu(self.tr("menu_quick_vol"))
        qvol_menu.setEnabled(not is_muted)
        vol_group = QActionGroup(self)
        vol_group.setExclusive(True)
        cur_vol = round(p.settings.get("music_volume", 0.45), 2)
        for pct, val in (("25%", 0.25), ("50%", 0.50), ("75%", 0.75), ("100%", 1.00)):
            act_v = QAction(pct, self, checkable=True)
            act_v.setChecked(abs(cur_vol - val) < 0.06)
            act_v.triggered.connect(lambda checked=False, v=val: self.set_quick_volume(v))
            vol_group.addAction(act_v)
            qvol_menu.addAction(act_v)

        self._make_check_action("act_mute_all", "mute_all", menu, use_primary=True)
        menu.addSeparator()
        self._make_check_action("act_enable_music", "music_on", menu, enabled=not is_muted, use_primary=True)
        self._make_check_action("act_sfx", "sfx_on", menu, enabled=not is_muted, use_primary=True)
        menu.addSeparator()

        ost_group = QActionGroup(self)
        ost_group.setExclusive(True)
        current_ed = p.settings.get("ost_edition", "ps1")
        for ed_key in OST_EDITION_KEYS:
            act_ed = QAction(self.tr(f"ost_{ed_key}"), self, checkable=True)
            act_ed.setChecked(ed_key == current_ed)
            act_ed.setEnabled(not is_muted)
            act_ed.triggered.connect(lambda checked=False, k=ed_key: self.set_ost_edition(k))
            ost_group.addAction(act_ed)
            menu.addAction(act_ed)

    def rebuild_tray_menu(self):
        if self.is_clone:
            return
        tray_menu = QMenu()
        tray_menu.addAction(self.tr("menu_start_dance"), self.dance_all_instances)
        tray_menu.addAction(self.tr("menu_stop"), self.stop_all_instances)
        tray_menu.addAction(self.tr("menu_bring_center"), self.rescue_character)
        tray_menu.addSeparator()
        self._populate_clones_menu(tray_menu)
        self._populate_character_menu(tray_menu)
        self._populate_position_menu(tray_menu.addMenu(self.tr("menu_pos_fs")))
        self._populate_audio_menu(tray_menu.addMenu(self.tr("menu_vol_ost")))
        self._make_check_action("act_ghost_mode", "ghost_mode", tray_menu)
        tray_menu.addSeparator()
        tray_menu.addAction(f"{self.tr('menu_options')}...", self.open_options)
        tray_menu.addAction(self.tr("menu_exit"), QApplication.quit)
        self.tray.setContextMenu(tray_menu)

    def setup_tray_icon(self):
        self.tray = QSystemTrayIcon(self)
        icon_pix = QPixmap(resource_path("assets/sprites/frame_000.png"))
        if not icon_pix.isNull():
            self.tray.setIcon(QIcon(icon_pix))
        self.tray.setToolTip("Crash Bandicoot Desktop Character (1998)")
        self.rebuild_tray_menu()
        self.tray.activated.connect(lambda r: self.rescue_character() if r == QSystemTrayIcon.DoubleClick else None)
        self.tray.show()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and not self.settings.get("lock_position", False):
            self.is_dragging = True
            self.velocity_y = 0
            self.drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
        elif event.button() == Qt.RightButton:
            self.show_menu(event.globalPosition().toPoint())

    def mouseMoveEvent(self, event):
        if self.is_dragging and not self.settings.get("lock_position", False) and (event.buttons() & Qt.LeftButton):
            self.move(event.globalPosition().toPoint() - self.drag_offset)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_dragging = False

    def show_menu(self, pos):
        menu = QMenu(self)
        if self.primary_mascot.settings.get("language") == "ar":
            menu.setLayoutDirection(Qt.RightToLeft)

        menu.addAction(self.tr("menu_start_dance"), self.start_dance)
        menu.addAction(self.tr("menu_stop"), self.stop_crash)
        menu.addSeparator()

        self._populate_clones_menu(menu)
        self._populate_character_menu(menu)

        anim_menu = menu.addMenu(self.tr("menu_animations"))
        anim_menu.addAction(
            self.tr("menu_random_move"),
            lambda: self.trigger_single_move(random.choice([m[0] for m in self.DANCE_MOVES]))
        )
        anim_menu.addSeparator()
        for move_state, move_key in self.DANCE_MOVES:
            anim_menu.addAction(self.tr(move_key), lambda checked=False, m=move_state: self.trigger_single_move(m))

        menu.addSeparator()
        self._populate_position_menu(menu.addMenu(self.tr("menu_pos_fs")))
        self._populate_audio_menu(menu.addMenu(self.tr("menu_vol_ost")))
        menu.addAction(self.tr("menu_options"), self.open_options)
        menu.addAction(self.tr("menu_about"), lambda: AboutDialog(self, self).exec())
        menu.addSeparator()
        if self.is_clone:
            menu.addAction(self.tr("act_close_this"), self.remove_this_clone)
        menu.addAction(self.tr("menu_exit"), QApplication.quit)
        menu.exec(pos)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    probe_socket = QLocalSocket()
    probe_socket.connectToServer(SERVER_NAME)
    if probe_socket.waitForConnected(250):
        probe_socket.write(b"RESCUE")
        probe_socket.flush()
        probe_socket.waitForBytesWritten(250)
        probe_socket.disconnectFromServer()
        sys.exit(0)

    QLocalServer.removeServer(SERVER_NAME)
    instance_server = QLocalServer()
    instance_server.listen(SERVER_NAME)

    saved_settings = load_global_settings()
    lang_manager = LanguageManager()
    char_manager = CharacterManager()

    splash_path = resource_path("assets/splash.png")
    use_splash = saved_settings.get("show_splash", True) and os.path.exists(splash_path)

    splash = QSplashScreen(QPixmap(splash_path)) if use_splash else None
    if splash:
        splash.show()

    crash = CrashMascot1998(saved_settings, lang_manager, char_manager)

    if IS_WINDOWS:
        win_filter = WinGlobalHotkeyFilter(crash.rescue_character)
        app.installNativeEventFilter(win_filter)
        app.aboutToQuit.connect(lambda: ctypes.windll.user32.UnregisterHotKey(None, HOTKEY_RESCUE_ID))
    else:
        unix_hotkeys = UnixHotkeyBridge(crash.rescue_character)
        app.aboutToQuit.connect(unix_hotkeys.stop)

    def handle_secondary_instance():
        conn = instance_server.nextPendingConnection()
        if conn:
            conn.close()
        crash.rescue_character()

    instance_server.newConnection.connect(handle_secondary_instance)

    QTimer.singleShot(2000 if splash else 0, lambda: (splash.finish(crash) if splash else None, crash.show()))
    sys.exit(app.exec())
