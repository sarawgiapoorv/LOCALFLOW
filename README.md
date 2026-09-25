# LocalFlow 🎙️

**The Passive Speech-to-Mind Dictation Engine for Windows.**

LocalFlow is an AI-powered voice dictation copilot engineered to match and exceed Wispr Flow on Windows. Built natively for desktop productivity, it combines ultra-low-latency local ASR (`faster-whisper`) with a multi-tiered LLM copyediting pipeline to deliver real-time, speech-to-mind transcription that automatically repairs speech slips, self-corrections, and hesitations with zero conversational interference.

---

## 🌟 How LocalFlow Works: The Honest Architecture

Unlike chatbots, autonomous agents, or voice assistants that attempt to execute commands or reply conversationally, LocalFlow is strictly a **passive speech-to-text dictation engine**. Whatever you speak is transcribed, polished, and typed directly at your active cursor position.

```
[Spoken Audio]
       │
       ▼
[Stage 1: Local Whisper ASR]  ──>  Ultra-fast raw transcription (faster-whisper)
       │
       ▼
[Stage 2: 4-Tier Polish Pipeline]
  ├── Tier 1: FreeLLMAPI (Local proxy, headless, 250+ free upstream models)
  ├── Tier 2: Google Gemini (Direct Cloud, gemini-2.5-flash with key-rotation)
  ├── Tier 3: Local LLM (Ollama llama3.2:3b, 100% offline & private)
  └── Tier 0: Sticky Circuit Breaker (Auto-failover + self-healing TCP probe)
       │
       ▼
[Stage 3: Reasoning & CoT Sanitizer]  ──> Strips <think> tags & reasoning narration
       │
       ▼
[Stage 4: Text Injector]  ──> Unicode-safe typing directly at active cursor
```

---

## 🛡️ Anti-Agent & Strict Passive Dictation Guarantees

1. **Zero Execution of Spoken Words**: If you dictate *"order a pizza from Domino's"*, *"turn off the lights"*, or *"build a website"*, LocalFlow transcribes those exact words cleanly. It will **never** execute, fulfill, or automate the request.
2. **Never Answers Questions**: If you dictate *"what is the capital of France?"*, it outputs *"What is the capital of France?"* with a question mark. It will never output *"Paris"*.
3. **Zero Conversational Filler**: No *"Sure!"*, *"Here is your text:"*, *"As an AI..."*, or apology preambles. Only the polished text reaches your screen.
4. **Speech-to-Mind Self-Correction**: When you repair your speech mid-sentence (*"order from Domino's no wait make it Pizza Hut"*), LocalFlow outputs only the intended thought (*"Make it Pizza Hut."*).
5. **Reasoning & CoT Leakage Guard**: Reasoning models can sometimes dump their internal deliberations (*"The user wants me to..."*). LocalFlow automatically strips `<think>` / `<reasoning>` blocks, detects unlabeled monologue leaks, recovers the clean final thought, or falls back to raw speech so deliberation walls are never typed.
6. **Terminal / Console Safety**: When focused on command prompts (`Windows Terminal`, `PowerShell`, `cmd`, `bash`), unprompted newlines are stripped so dictated speech never accidentally submits or runs shell commands.

---

## ⚡ 4-Tier Intelligent Polish Pipeline

### Tier 1: FreeLLMAPI Gateway (Default Cloud Tier)
- **Headless Server Management**: `freellm_manager.py` automatically discovers, boots (`CREATE_NO_WINDOW`), health-checks, and shuts down your local FreeLLMAPI instance.
- **Automated Vault Sync**: Automatically reads the master `unified_api_key` from FreeLLMAPI's internal SQLite database (`freeapi.db`) on first launch and vaults it into the **Windows Credential Manager** (`LocalFlow_FreeLLM`).
- **Instruct Model Routing**: Targets fast, non-reasoning instruct models (default: `groq/llama-3.3-70b-versatile` with fallbacks to `sambanova/Meta-Llama-3.1-8B-Instruct`, `openrouter/...`, and `auto`).
- **Strict 8-Second Timeout**: Prevents hanging on slow or overloaded upstream endpoints.

### Tier 2: Direct Google Gemini Cloud
- Direct API calls to `gemini-2.5-flash`.
- Supports multi-key rotation (comma-separated keys in Settings).
- Keys securely vaulted in Windows Credential Manager under `LocalFlow / api_key`.

### Tier 3: Local Offline LLM (`llama3.2:3b` via Ollama)
- Zero-touch headless auto-discovery and startup of `ollama serve`.
- RAM pre-warming on application boot to eliminate token generation latency.
- Completely offline, private, and free.

### Tier 0: Sticky Circuit Breaker with Self-Healing Recovery
- If cloud tiers fail or time out, LocalFlow instantly falls back to Tier 3 for zero-delay continuity.
- Background TCP probes periodically check if the cloud gateway has recovered, automatically restoring Tier 1 without requiring manual UI intervention.

---

## 🎨 Minimalist Alabaster & Cream UI

- **Alabaster Palette**: Refined warm cream (`#fbfbf8`) background with deep charcoal typography and crisp white cards.
- **Engine Status Pill**: Live visual status (`● Cloud Polish` in Sky Blue, `⚡ Local LLM` in Amber) with a 1-click `↺ Reset` button.
- **Floating Waveform Widget**: Double-click the main card to toggle a borderless, translucent floating widget that stays on top of your workspace with live recording feedback.
- **System Tray Mode**: Close to tray, with global hotkeys active in the background.

---

## 🛠️ Setup & Installation

### 1. Prerequisites
- **Windows 10 / 11 (64-bit)**
- **Python 3.10+**
- *(Optional, for Tier 1)*: [FreeLLMAPI](https://github.com/freellmapi/freellmapi) installed in your user directory.
- *(Optional, for Tier 3)*: [Ollama](https://ollama.com/) with `ollama pull llama3.2:3b`.

### 2. Launching LocalFlow
```powershell
# Standard GUI launch
python main.py

# Launch minimized to system tray
python main.py --silent
```
Or double-click `Launch_LocalFlow.bat` / `LocalFlow.lnk`.

### 3. Built-in Diagnostics
To verify your FreeLLMAPI connection and API authentication:
```powershell
python diagnose_freellmapi.py
```

---

## 🎙️ Global Hotkeys & Vocabulary

- **Push-to-Talk (Default)**: Hold `Right Alt`, speak, and release to transcribe and type.
- **Continuous Mode**: Press `Ctrl + Shift + A` to toggle hands-free VAD dictation.
- **Dynamic Vocabulary Training**: Say *"add [word] to my dictionary"* (e.g. *"add Kubernetes to my dictionary"*) to instantly add specialized jargon to `dictionary.json`.

---

## 🧪 Automated Verification Suite

Run the full reasoning-leak and anti-execution verification suite:
```powershell
python -m unittest discover -s .
# Or run the reasoning-guard regression suite
python run_verification_tests.py
```

---

*LocalFlow — Fast, Private, and Autonomous Speech-to-Mind Dictation.*
