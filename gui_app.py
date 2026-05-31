"""
gui_app.py — Production-grade CustomTkinter GUI for LocalFlow.

Premium dark-mode interface featuring:
  • Real-time status indicator with recording pulse animation
  • Collapsible settings panel for device & Groq API configuration
  • Persistent history vault display (SQLite-backed)
  • System tray integration via pystray (close-to-tray)
  • Non-blocking architecture — hotkeys & AI pipeline run in background threads
"""

import customtkinter as ctk
import threading
import os
import keyboard
from datetime import datetime

try:
    import pystray
    from PIL import Image, ImageDraw, ImageFont
    HAS_TRAY = True
except ImportError:
    HAS_TRAY = False

from audio_recorder import AudioRecorder, DEVICE_INDEX
from ai_brain import AIBrain
from text_injector import TextInjector
from history_vault import HistoryVault


# ══════════════════════════════════════════════════════════════
# Design Tokens  (Tailwind-inspired dark palette)
# ══════════════════════════════════════════════════════════════
class C:
    """Colour constants."""
    BG_DEEP       = "#0a0e1a"
    BG_MAIN       = "#0f172a"
    BG_CARD       = "#1e293b"
    BG_INPUT      = "#0f172a"
    BORDER        = "#334155"
    BORDER_FOCUS  = "#6366f1"
    ACCENT        = "#6366f1"
    ACCENT_HOVER  = "#818cf8"
    GREEN         = "#22c55e"
    GREEN_DIM     = "#16a34a"
    RED           = "#ef4444"
    RED_PULSE     = "#fca5a5"
    AMBER         = "#f59e0b"
    TEXT          = "#f1f5f9"
    TEXT_SEC      = "#94a3b8"
    TEXT_DIM      = "#64748b"
    TRANSPARENT   = "transparent"

FONT = "Segoe UI"


# ══════════════════════════════════════════════════════════════
# Application
# ══════════════════════════════════════════════════════════════
class LocalFlowApp(ctk.CTk):
    """Main LocalFlow desktop application."""

    def __init__(self):
        super().__init__()

        # ── Window ────────────────────────────────────────────
        self.title("LocalFlow")
        self.geometry("540x820")
        self.minsize(480, 700)
        self.configure(fg_color=C.BG_DEEP)
        ctk.set_appearance_mode("dark")

        # ── Backend ───────────────────────────────────────────
        self.recorder = AudioRecorder()
        self.brain    = AIBrain()
        self.injector = TextInjector()
        self.vault    = HistoryVault()

        # ── State ─────────────────────────────────────────────
        self._current_status  = "initializing"
        self._is_processing   = False
        self._lock            = threading.Lock()
        self._pulse_job       = None
        self._tray_icon       = None
        self._settings_open   = False
        self.is_continuous_mode = False

        # ── Build UI ──────────────────────────────────────────
        self._build_header()
        self._build_status_card()
        self._build_settings_section()
        self._build_history_section()
        self._build_footer()

        # ── Populate existing history ─────────────────────────
        self._load_history_from_db()

        # ── Window protocol ───────────────────────────────────
        self.protocol("WM_DELETE_WINDOW", self._on_window_close)

        # ── Launch backend (background) ───────────────────────
        threading.Thread(
            target=self._initialize_backend, daemon=True
        ).start()

    # ══════════════════════════════════════════════════════════
    #  UI CONSTRUCTION
    # ══════════════════════════════════════════════════════════

    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color=C.TRANSPARENT, height=56)
        header.pack(fill="x", padx=24, pady=(20, 0))
        header.pack_propagate(False)

        ctk.CTkLabel(
            header, text="⚡ LocalFlow",
            font=(FONT, 28, "bold"), text_color=C.TEXT,
        ).pack(side="left")

        ctk.CTkLabel(
            header, text="Privacy-First Voice Flow",
            font=(FONT, 12), text_color=C.TEXT_DIM,
        ).pack(side="left", padx=(14, 0), pady=(10, 0))

    # ── Status Card ───────────────────────────────────────────

    def _build_status_card(self):
        card = ctk.CTkFrame(
            self, fg_color=C.BG_CARD, corner_radius=16,
            border_width=1, border_color=C.BORDER,
        )
        card.pack(fill="x", padx=24, pady=(18, 0))

        inner = ctk.CTkFrame(card, fg_color=C.TRANSPARENT)
        inner.pack(padx=28, pady=26)

        self.status_dot = ctk.CTkLabel(
            inner, text="●", font=(FONT, 40), text_color=C.TEXT_DIM,
        )
        self.status_dot.pack()

        self.status_label = ctk.CTkLabel(
            inner, text="INITIALIZING…",
            font=(FONT, 20, "bold"), text_color=C.TEXT_SEC,
        )
        self.status_label.pack(pady=(6, 0))

        self.status_hint = ctk.CTkLabel(
            inner, text="Connecting to Groq cloud…",
            font=(FONT, 12), text_color=C.TEXT_DIM,
        )
        self.status_hint.pack(pady=(4, 0))

    # ── Settings Panel ────────────────────────────────────────

    def _build_settings_section(self):
        self.settings_toggle = ctk.CTkButton(
            self, text="⚙  Settings  ▸",
            font=(FONT, 13), fg_color=C.TRANSPARENT,
            hover_color=C.BG_CARD, text_color=C.TEXT_SEC,
            anchor="w", height=32, command=self._toggle_settings,
        )
        self.settings_toggle.pack(fill="x", padx=24, pady=(14, 0))

        # Container (initially hidden)
        self.settings_frame = ctk.CTkFrame(
            self, fg_color=C.BG_CARD, corner_radius=12,
            border_width=1, border_color=C.BORDER,
        )

        inner = ctk.CTkFrame(self.settings_frame, fg_color=C.TRANSPARENT)
        inner.pack(fill="x", padx=18, pady=18)

        # Device Index
        ctk.CTkLabel(
            inner, text="Input Device Index",
            font=(FONT, 12), text_color=C.TEXT_SEC,
        ).pack(anchor="w")
        self.device_entry = ctk.CTkEntry(
            inner, font=(FONT, 13), fg_color=C.BG_INPUT,
            border_color=C.BORDER, text_color=C.TEXT, height=34,
        )
        self.device_entry.insert(0, str(DEVICE_INDEX))
        self.device_entry.pack(fill="x", pady=(4, 14))

        # Groq API Key
        ctk.CTkLabel(
            inner, text="Groq API Key",
            font=(FONT, 12), text_color=C.TEXT_SEC,
        ).pack(anchor="w")
        self.api_key_entry = ctk.CTkEntry(
            inner, font=(FONT, 13), fg_color=C.BG_INPUT,
            border_color=C.BORDER, text_color=C.TEXT, height=34,
            show="*", placeholder_text="gsk_...",
        )
        self.api_key_entry.insert(0, self.brain.api_key)
        self.api_key_entry.pack(fill="x", pady=(4, 16))

        # Apply button
        ctk.CTkButton(
            inner, text="Apply Settings",
            font=(FONT, 13, "bold"), fg_color=C.ACCENT,
            hover_color=C.ACCENT_HOVER, text_color="#ffffff",
            height=36, corner_radius=8, command=self._apply_settings,
        ).pack(fill="x")

        self.settings_feedback = ctk.CTkLabel(
            inner, text="", font=(FONT, 11), text_color=C.GREEN,
        )
        self.settings_feedback.pack(pady=(8, 0))

    # ── History Panel ─────────────────────────────────────────

    def _build_history_section(self):
        bar = ctk.CTkFrame(self, fg_color=C.TRANSPARENT, height=30)
        bar.pack(fill="x", padx=24, pady=(14, 0))
        bar.pack_propagate(False)

        ctk.CTkLabel(
            bar, text="📋  History",
            font=(FONT, 13), text_color=C.TEXT_SEC,
        ).pack(side="left")

        ctk.CTkButton(
            bar, text="Clear", font=(FONT, 11),
            fg_color=C.TRANSPARENT, hover_color=C.BG_CARD,
            text_color=C.TEXT_DIM, width=50, height=26,
            command=self._clear_history,
        ).pack(side="right")

        self.history_box = ctk.CTkTextbox(
            self, font=(FONT, 12), fg_color=C.BG_CARD,
            text_color=C.TEXT, border_width=1,
            border_color=C.BORDER, corner_radius=12,
            wrap="word", state="disabled", activate_scrollbars=True,
        )
        self.history_box.pack(fill="both", expand=True, padx=24, pady=(6, 0))

    # ── Footer ────────────────────────────────────────────────

    def _build_footer(self):
        ctk.CTkLabel(
            self, text="Made by Apoorv Sarawgi",
            font=(FONT, 11), text_color=C.TEXT_DIM,
        ).pack(pady=(12, 16))

    # ══════════════════════════════════════════════════════════
    #  STATUS ENGINE
    # ══════════════════════════════════════════════════════════

    def _set_status(self, status: str, hint: str | None = None):
        """Thread-safe status transition."""
        self._current_status = status
        self.after(0, lambda: self._render_status(status, hint))

    def _render_status(self, status: str, hint: str | None = None):
        """Apply visual state (main thread only)."""
        if self._pulse_job:
            self.after_cancel(self._pulse_job)
            self._pulse_job = None

        presets = {
            "ready":        (C.GREEN,  "READY TO DICTATE",  "Hold  [ Right Alt ]  to record"),
            "recording":    (C.RED,    "🔴  RECORDING",     "Release  [ Right Alt ]  to stop"),
            "processing":   (C.AMBER,  "⚡  PROCESSING",    "Transcribing & polishing…"),
            "typing":       (C.ACCENT, "⌨   TYPING",        "Injecting text at cursor…"),
            "initializing": (C.TEXT_DIM, "INITIALIZING…",   "Connecting to Groq cloud…"),
            "error":        (C.RED,    "⚠   ERROR",         ""),
        }
        colour, label, default_hint = presets.get(
            status, (C.TEXT_DIM, status.upper(), "")
        )

        self.status_dot.configure(text_color=colour)
        self.status_label.configure(text=label, text_color=colour)
        self.status_hint.configure(text=hint or default_hint)

        if status == "recording":
            self._pulse_on = True
            self._do_pulse()

    def _do_pulse(self):
        if self._current_status != "recording":
            return
        colour = C.RED if self._pulse_on else C.RED_PULSE
        self.status_dot.configure(text_color=colour)
        self._pulse_on = not self._pulse_on
        self._pulse_job = self.after(500, self._do_pulse)

    # ══════════════════════════════════════════════════════════
    #  SETTINGS
    # ══════════════════════════════════════════════════════════

    def _toggle_settings(self):
        if self._settings_open:
            self.settings_frame.pack_forget()
            self.settings_toggle.configure(text="⚙  Settings  ▸")
        else:
            self.settings_frame.pack(
                fill="x", padx=24, pady=(4, 0),
                after=self.settings_toggle,
            )
            self.settings_toggle.configure(text="⚙  Settings  ▾")
        self._settings_open = not self._settings_open

    def _apply_settings(self):
        # Device index
        try:
            new_device = int(self.device_entry.get().strip())
            self.recorder.device_index = new_device
        except ValueError:
            self.settings_feedback.configure(
                text="⚠  Invalid device index", text_color=C.RED,
            )
            return

        # Groq API Key
        new_key = self.api_key_entry.get().strip()
        if new_key:
            self.brain.set_api_key(new_key)
            self._set_status("ready")
            self.settings_feedback.configure(
                text="✅  Settings applied! API key saved.",
                text_color=C.GREEN,
            )
        else:
            self.settings_feedback.configure(
                text="⚠  Please enter a Groq API Key",
                text_color=C.AMBER,
            )
            return

        self.after(
            4000,
            lambda: self.settings_feedback.configure(text=""),
        )

    # ══════════════════════════════════════════════════════════
    #  HISTORY
    # ══════════════════════════════════════════════════════════

    def _load_history_from_db(self):
        entries = self.vault.get_recent(limit=50)
        if not entries:
            return
        self.history_box.configure(state="normal")
        for ts, txt in entries:
            self.history_box.insert("end", f"{ts}\n", "ts")
            self.history_box.insert("end", f"{txt}\n")
            self.history_box.insert("end", "─" * 52 + "\n\n")
        self.history_box.configure(state="disabled")

    def _push_history_entry(self, ts: str, txt: str):
        """Prepend an entry to the history box (main thread)."""
        block = f"{ts}\n{txt}\n" + "─" * 52 + "\n\n"
        self.history_box.configure(state="normal")
        self.history_box.insert("1.0", block)
        self.history_box.configure(state="disabled")

    def _clear_history(self):
        self.vault.clear()
        self.history_box.configure(state="normal")
        self.history_box.delete("1.0", "end")
        self.history_box.configure(state="disabled")

    # ══════════════════════════════════════════════════════════
    #  SYSTEM TRAY
    # ══════════════════════════════════════════════════════════

    def _setup_tray(self):
        if not HAS_TRAY:
            return
        icon_img = self._make_tray_icon()
        menu = pystray.Menu(
            pystray.MenuItem(
                "Show LocalFlow", self._tray_show, default=True,
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit", self._tray_quit),
        )
        self._tray_icon = pystray.Icon(
            "LocalFlow", icon_img, "LocalFlow — Ready", menu,
        )
        threading.Thread(
            target=self._tray_icon.run, daemon=True,
        ).start()

    @staticmethod
    def _make_tray_icon() -> "Image.Image":
        """Generate a small indigo circle with 'LF' text."""
        size = 64
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.ellipse([4, 4, size - 4, size - 4], fill="#6366f1")
        try:
            font = ImageFont.truetype("segoeui.ttf", 22)
        except Exception:
            font = ImageFont.load_default()
        draw.text(
            (size // 2, size // 2), "LF",
            fill="white", font=font, anchor="mm",
        )
        return img

    def _tray_show(self, _icon=None, _item=None):
        self.after(0, self.deiconify)
        self.after(10, self.lift)
        self.after(20, self.focus_force)

    def _tray_quit(self, _icon=None, _item=None):
        if self._tray_icon:
            self._tray_icon.stop()
        self.after(0, self._quit_app)

    def _on_window_close(self):
        """X button → minimise to tray (or quit if tray unavailable)."""
        if HAS_TRAY and self._tray_icon:
            self.withdraw()
        else:
            self._quit_app()

    def _quit_app(self):
        try:
            keyboard.unhook_all()
        except Exception:
            pass
        if self._tray_icon:
            try:
                self._tray_icon.stop()
            except Exception:
                pass
        self.destroy()

    # ══════════════════════════════════════════════════════════
    #  BACKEND  (runs in background threads)
    # ══════════════════════════════════════════════════════════

    def _initialize_backend(self):
        """Initialize Groq connection and register hotkeys."""
        # Stage 1 — Check API key
        self._set_status("initializing", "Connecting to Groq cloud…")
        self.brain.load_whisper()  # prints status info

        # Stage 2 — System tray
        self.after(0, self._setup_tray)

        # Stage 3 — Register hotkeys
        keyboard.on_press_key(
            "right alt", self._on_key_press, suppress=False,
        )
        keyboard.on_release_key(
            "right alt", self._on_key_release, suppress=False,
        )
        keyboard.add_hotkey(
            "ctrl + shift + a", self._toggle_continuous_recording,
        )

        # Stage 4 — Set status based on API key presence
        if self.brain.is_ready:
            self._set_status("ready")
        else:
            self._set_status(
                "error",
                "Please enter your Groq API Key in Settings",
            )

        # Keep this thread alive so keyboard hooks remain active
        try:
            keyboard.wait()
        except Exception:
            pass

    # ── Hotkey Handlers ───────────────────────────────────────

    def _on_key_press(self, _event):
        if self.is_continuous_mode:
            return
        with self._lock:
            if self.recorder.is_recording or self._is_processing:
                return
        self.recorder.start()
        self._set_status("recording")

    def _on_key_release(self, _event):
        if self.is_continuous_mode:
            return
        if not self.recorder.is_recording:
            return

        audio_path = self.recorder.stop()
        if audio_path is None:
            self._set_status("ready")
            return

        threading.Thread(
            target=self._run_pipeline,
            args=(audio_path,),
            daemon=True,
        ).start()

    # ── Continuous Dictation Toggle ───────────────────────────────

    def _toggle_continuous_recording(self):
        """Toggle hands-free continuous dictation on/off."""
        with self._lock:
            if self._is_processing:
                return

        if self.is_continuous_mode:
            # STOP continuous session
            self.is_continuous_mode = False
            audio_path = self.recorder.stop()
            if audio_path is not None:
                threading.Thread(
                    target=self._run_pipeline,
                    args=(audio_path,),
                    daemon=True,
                ).start()
            else:
                self._set_status("ready")
        else:
            # START continuous session
            if self.recorder.is_recording:
                return
            self.is_continuous_mode = True
            self.recorder.start()
            self._set_status("recording")

    # ── AI Pipeline ───────────────────────────────────────────

    def _run_pipeline(self, audio_path: str):
        with self._lock:
            if self._is_processing:
                return
            self._is_processing = True

        try:
            self._set_status("processing")

            raw_text, polished_text = self.brain.process(audio_path)

            if not polished_text:
                self._set_status("ready", "No speech detected.")
                return

            # Inject at cursor
            self._set_status("typing")
            self.injector.inject(polished_text)

            # Log to vault & update UI
            ts = self.vault.add_entry(polished_text, raw_text)
            self.after(
                0, lambda t=ts, p=polished_text: self._push_history_entry(t, p),
            )

            self._set_status("ready")

        except Exception as e:
            self._set_status("error", f"Pipeline error: {e}")
            self.after(5000, lambda: self._set_status("ready"))

        finally:
            try:
                if audio_path and os.path.exists(audio_path):
                    os.remove(audio_path)
            except OSError:
                pass
            with self._lock:
                self._is_processing = False
