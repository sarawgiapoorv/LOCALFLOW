# ⚡ LocalFlow

An advanced, privacy-first desktop voice dictation engine built to provide a powerful, open-source replacement for tools like **Flow** and **Whisper**. LocalFlow captures raw microphone streams, executes real-time cloud transcriptions, and passes them through a resilient multi-model LLM pool to strip filler words, fix grammar, and process spoken self-corrections instantly before injecting the text directly at your cursor.

---

## ✨ Core Features

* **Two-Stage Core AI Pipeline:**
    * **Stage 1 (Transcription):** Blazing fast audio-to-text decoding via Groq's `whisper-large-v3` cloud endpoint.
    * **Stage 2 (Polishing):** Context-aware text refinement utilizing deep LLM instructions to eliminate conversational stutter, remove filler phrases (`um`, `uh`, `basically`), and resolve complex verbal backtracking on-the-fly.
* **Resilient Model Failover Pool:** Implements a multi-model fallback safety system. If the default `llama-3.3-70b-versatile` endpoint fails or times out, the application sequentially hot-swaps to `llama-3.1-70b-versatile`, `llama3-70b-8192`, or `mixtral-8x7b-32768` to guarantee zero dictation dropouts.
* **Dual-Mode Recording Controls:**
    * **Hold-to-Record:** Hold down the `Right Alt` key to capture audio, and release it to instantly process and type your text.
    * **Hands-Free Continuous Mode:** Press `Ctrl + Shift + A` to toggle a long-form session. Speak completely hands-free and press the shortcut again to process blocks of narrative dictation.
* **Seamless Cursor Injection:** Automatically pushes finalized, polished prose into whatever text editor, IDE, or browser field you are currently focused on.
* **Persistent SQLite History Vault:** Locally logs every text generation with accurate timestamps into `localflow_history.db` so you never lose an optimized thought.
* **Production-Grade UI/UX:** Built on a sleek, Tailwind-inspired custom dark theme featuring live color-pulsing record animations and minimized close-to-tray system integration via `pystray`.

---

## 🏗️ Architecture & Technical Stack

```text
[Microphone] ──> SoundDevice Stream (16kHz Mono PCM)
                     └──> Stage 1: Groq Whisper API (Raw Text)
                              └──> Stage 2: Resilient LLM Pool (Pristine Text)
                                       ├──> Auto-Inject at Active Cursor
                                       └──> Local SQLite History Logging