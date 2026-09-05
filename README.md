# LocalFlow v9.5 🎙️

**The Ultimate Speech-to-Mind Voice Dictation Engine for Windows.**

LocalFlow is a state-of-the-art, context-aware dictation copilot engineered to match and exceed Wispr Flow. Built natively for Windows, it marries ultra-low-latency local ASR (`faster-whisper`) with Gemini cloud intelligence (`gemini-2.5-flash`) and a zero-touch local LLM fallback (`llama3.2:3b` via Ollama) to deliver real-time, speech-to-mind transcription that automatically repairs speech slips, self-corrections, and hesitations with zero friction.

---

## 🌟 Key Features

### 🧠 Speech-to-Mind Intelligence & Verbal Self-Correction
- **Intelligent Mid-Speech Self-Correction**: When you change your mind mid-sentence (e.g., *"order me a pizza from dominos no order me a pizza from pizza hut"*), LocalFlow discards the canceled thought and outputs only the final intended text (*"Order me a pizza from Pizza Hut."*).
- **Direct Polished Injection (Zero Raw Typing)**: LocalFlow eliminates buggy "optimistic raw typing" and clipboard swapping loops. Speech is transcribed and copyedited first, then typed cleanly into your active window in a single shot.
- **Pristine Polish & Grammar**: Automatic punctuation, capitalization, filler-word pruning (`um`, `uh`, `like`), and phonetic brand correction (Pizza Hut, Domino's, GitHub, Python, VS Code).
- **Tone Profiles**: Switch effortlessly between **Normal**, **Formal**, **Casual**, and **Developer** modes.
- **Generative Drafting Mode**: Speak *"draft an email..."* or *"write a PR description..."* to dynamically instruct the AI to draft high-quality content directly into your active window.

### ⚡ Automatic Local LLM Fallback (`llama3.2:3b`)
- **Zero Configuration & Headless Lifecycle**: LocalFlow auto-discovers `ollama.exe` and starts the Ollama server silently in the background (`CREATE_NO_WINDOW`) without console popups or manual URL copying.
- **RAM Pre-Warming**: Pre-loads `llama3.2:3b` weights into memory on application startup to eliminate cold-start latency.
- **Sticky Session Circuit Breaker**: If the Gemini API hits a rate limit (HTTP 429), quota exhaustion, or network outage, LocalFlow immediately trips into Local Mode. The current sentence is instantly rescued, and subsequent dictations remain local for zero-delay continuity.
- **Header Engine Indicator & Manual Toggle**: The UI header displays `● Cloud Polish` (Sky Blue) or `⚡ Local LLM (llama3.2:3b)` (Amber) with a 1-click `↺ Reset` button to restore cloud polish whenever you desire.
- **Passive Transcriber Framework**: Built with turn-based few-shots and strict anti-assistant refusal guards. The model will never reply conversationally or answer questions—it transcribes verbatim what was spoken.

### 📊 API Telemetry & Call Analytics Dashboard
- **SQLite-Backed Telemetry**: Every API call is logged with provider slot, model, response status (`SUCCESS`, `RATE_LIMIT_429`, `TIMEOUT`, `ERROR`), and roundtrip latency in milliseconds.
- **Live In-App Analytics**: Open the Settings drawer to view:
  - Total API calls made & overall success rate %.
  - Per-key breakdown for all Gemini slots and local LLM fallbacks.
  - One-click stats clearing.

### 🎨 Minimalist Editorial Cream & Pure White UI
- **Refined Minimalist Aesthetic**: Clean warm alabaster/cream (`#fbfbf8`) background with pristine white cards and deep charcoal typography.
- **Floating Translucent Widget Mode**: Double-click the status card to toggle into a borderless, translucent floating widget that stays atop your windows with real-time waveform animations.
- **System Tray Integration**: Minimize to tray on close, with hotkey indicators and status tooltips.

### 🖥️ Native Desktop & OS Integration
- **1-Click Desktop App**: Launch with `LocalFlow.lnk` or run silently in the background with `Launch_LocalFlow.vbs` (`pythonw.exe`).
- **Autonomous Bootstrapper (`Launch_LocalFlow.bat`)**: Automated dependency verification and graceful compile failover.
- **DSP Noise Gating & Audio Ducking**: Real-time spectral gating (`noisereduce`) to strip fan hum and ambient noise, with per-session media ducking (`pycaw`) during recording.
- **Enterprise Security**: Gemini API keys are securely vaulted in the native **Windows Credential Manager** via `keyring` (no plaintext configuration files).

---

## 🛠️ Setup & Installation

### 1. Prerequisites
- **Windows 10 / 11 (64-bit)**
- **Python 3.10+**
- *(Optional, Recommended for Offline Polish)*: [Ollama](https://ollama.com/) with `ollama pull llama3.2:3b`. LocalFlow will detect and launch it headlessly automatically.

### 2. Zero-Touch Launch
Double-click `Launch_LocalFlow.bat`. 

The launcher will:
1. Verify your Python environment.
2. Install or upgrade dependencies from `requirements.txt`.
3. Handle compiler dependencies gracefully.
4. Launch the application.

### 3. API Key Setup
When prompted, enter your Google Gemini API key. You can add multiple comma-separated keys for automatic multi-key rotation. Keys are encrypted inside the Windows Credential Manager.

---

## 🚀 Launch Options

1. **Standard Dashboard:** 
   ```bash
   python main.py
   ```
2. **Silent System Tray Mode:**
   ```bash
   python main.py --silent
   ```
3. **Windows Startup:**
   Toggle **"Start LocalFlow with Windows Boot"** in Settings to run silently on boot without UAC prompts.

---

## 🎙️ Hotkeys & Voice Commands

### Hotkeys
- **Push-to-Talk:** Hold `Right Alt`, speak, and release to inject.
- **Continuous Mode:** Press `Ctrl + Shift + A` to toggle continuous voice-activity-detected dictation.

### Voice Commands
- **"scratch that"** / **"undo that"**: Natively deletes the last dictation.
- **"make that a bulleted list"**: Formats incoming speech as a markdown list.
- **"rewrite clipboard"**: Polishes and formats current clipboard contents.
- **"add [word] to my dictionary"**: Trains custom vocabulary into `dictionary.json`.
- **"draft an email..."**: Triggers Generative AI drafting mode.

---

## 🧪 Automated Test Suite

LocalFlow comes equipped with a comprehensive 14-test automated suite verifying all core subsystems:
```bash
python test_suite.py
```

Tests include:
- Vocabulary & contextual app dictionary hints
- Snippet text expansions
- Tone style profile mapping
- Fast-path suffix diffing & injection normalization
- Connection pre-warming
- Speech-to-mind verbal self-correction
- Multi-key API rotation
- Swap guard & clipboard race condition defenses
- Local LLM inference & anti-assistant prompts (`llama3.2:3b`)
- Sticky session circuit breaker failover
- Persistent API telemetry & analytics reporting

---

*LocalFlow v9.5 — Fast, Private, and Autonomous Speech-to-Mind Dictation.*
