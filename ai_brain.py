"""
ai_brain.py — Two-stage cloud AI pipeline for LocalFlow.

Stage 1: Transcribe audio → text via Groq's whisper-large-v3 endpoint.
Stage 2: Polish text via Groq's llama3-70b-8192 endpoint (filler removal,
         grammar fixes, self-correction smoothing).

Requires a Groq API key (https://console.groq.com).
"""

import os
import requests


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
GROQ_TRANSCRIPTION_URL = "https://api.groq.com/openai/v1/audio/transcriptions"
GROQ_CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_WHISPER_MODEL = "whisper-large-v3"
GROQ_LLM_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-70b-versatile",
    "llama3-70b-8192",
    "mixtral-8x7b-32768",
]

# Production-grade universal speech post-processing prompt
EDITOR_SYSTEM_PROMPT = (
    "You are an advanced, context-aware speech post-processor running as the core optimization intelligence of a dictation engine. "
    "Your mandate is to convert raw, chaotic speech-to-text transcripts into pristine, fluid, and natural text that perfectly captures the user's final intended message.\n\n"
    "STRICT GLOBAL RULES:\n"
    "1. RESOLVE SELF-CORRECTIONS & BACKTRACKING: Actively identify spoken editing markers like 'no', 'wait', 'actually', 'not that', 'scratch that', 'instead of', 'mean to say'. Logically collapse the sentence to output ONLY the final corrected intention. Completely eliminate the aborted sentence fragments.\n"
    "2. OBLITERATE FILLER WORDS & STUTTERS: Instantly remove conversational noise, stutters, false starts, and filler phrases (e.g., 'um', 'uh', 'like', 'you know', 'basically', 'so yeah', duplicate accidental word repetitions) unless they are intentionally part of a code snippet or literal quote.\n"
    "3. PRESERVE LONG-FORM PROMPTS & JARGON: When processing massive dictations (250 to 500+ words intended for AI chatbots like ChatGPT or Claude), protect the complete body, specialized technical vocabulary, domain jargon, and explicit line breaks. Do not summarize, truncate, shorten, or compress the core informational content. Only clean the spoken noise.\n"
    "4. ACADEMIC FORMATTING & GRAMMAR: Fix all spelling, structural grammar, missing punctuation, and run-on lines. Intelligently format numbers, dates, and times (e.g., rewrite '12 PM' as '12 p.m.', capitalize brand terms like 'Domino's', 'Python', 'Claude', or 'MongoDB').\n"
    "5. ABSOLUTE ZERO META-COMMENTARY: Output exclusively the clean, final text. Never include introductions, greetings, conversational filler, summaries, explanations, or wrap the final output in outer quotes.\n\n"
    "UNIVERSAL FEW-SHOT PERFORMANCE EXAMPLES:\n\n"
    "Example 1 (Casual Edits & Action Tasks):\n"
    "Input: 'Hi, how are you? See what you have to do is order a pizza for me from Pizza Hut. No, no, no, not Pizza Hut. Order a pizza for me from Domino's at 12 PM. Instead of 1 PM, order'\n"
    "Output: Hi, how are you? See, what you have to do is order a pizza for me from Domino's at 12 p.m.\n\n"
    "Example 2 (Complex Technical Chatbot Prompting):\n"
    "Input: 'Can you build a python script that connects to an SQL database... wait scratch SQL, make it a MongoDB database using pymongo. It should fetch all users who signed up uh like after last Monday... wait, no, let's say signed up within the last 30 days, and basically print their emails... actually make it write to a CSV file instead of printing.'\n"
    "Output: Can you build a python script that connects to a MongoDB database using pymongo. It should fetch all users who signed up within the last 30 days, and write to a CSV file.\n\n"
    "Example 3 (Long-Form Creative / Analytical Dictation):\n"
    "Input: 'Write an analytical essay detailing the causes of the French Revolution... hold on, don't make it an essay, make it a deep, highly detailed prompt for an LLM to generate a breakdown of three specific economic factors, no wait, fiscal factors leading up to the storming of the Bastille. Keep the language formal and structured... yeah, execute that.'\n"
    "Output: Write a deep, highly detailed prompt for an LLM to generate a breakdown of three specific fiscal factors leading up to the storming of the Bastille. Keep the language formal and structured.\n\n"
    "Example 4 (General Professional Correspondence):\n"
    "Input: 'We need to schedule the team alignment meeting for Tuesday afternoon... actually wait, Sarah is out on Tuesday, let's move it to Wednesday morning at 10 AM. Send an invite to the whole marketing group... oh, wait, scratch the design interns, just the core managers.'\n"
    "Output: We need to schedule the team alignment meeting for Wednesday morning at 10 a.m. Send an invite to the core marketing managers."
)

LLM_TEMPERATURE = 0.3
LLM_MAX_TOKENS = 2048


class AIBrain:
    """Manages Groq cloud transcription and LLM polishing."""

    def __init__(self):
        self.api_key: str = self._load_api_key()

    @staticmethod
    def _load_api_key() -> str:
        """Read the Groq API key from config.txt if it exists."""
        config_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "config.txt"
        )
        if os.path.isfile(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                key = f.readline().strip()
            if key:
                return key
        return ""

    # ------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------
    def set_api_key(self, key: str) -> None:
        """Set the Groq API key (called from GUI settings)."""
        self.api_key = key.strip()

    @property
    def is_ready(self) -> bool:
        """True if the API key has been provided."""
        return bool(self.api_key)

    def _auth_headers(self) -> dict:
        """Return authorization headers for Groq API calls."""
        return {
            "Authorization": f"Bearer {self.api_key}",
        }

    # ------------------------------------------------------------------
    # Initialization (instant — no local model to load)
    # ------------------------------------------------------------------
    def load_whisper(self) -> None:
        """No-op: Whisper runs on Groq's cloud. Kept for API compat."""
        if not self.api_key:
            print("  ⚠  No Groq API key set — enter one in Settings.")
            return
        print(f"  ☁️  Groq cloud pipeline active (transcription: {GROQ_WHISPER_MODEL})")
        print(f"  ☁️  LLM polishing model: {GROQ_LLM_MODELS[0]}")
        print("  ✅ Ready — no local model loading needed.")

    def detect_lm_studio_model(self) -> bool:
        """No-op: kept for API compat with gui_app. Always returns True."""
        return True

    # ------------------------------------------------------------------
    # Stage 1: Cloud Transcription (Groq whisper-large-v3)
    # ------------------------------------------------------------------
    def transcribe(self, audio_path: str) -> str:
        """
        Transcribe an audio file via Groq's Whisper API.

        Args:
            audio_path: Path to a .wav file.

        Returns:
            Raw transcribed text.
        """
        if not self.api_key:
            raise RuntimeError("Groq API key not set. Enter it in Settings.")

        with open(audio_path, "rb") as audio_file:
            resp = requests.post(
                GROQ_TRANSCRIPTION_URL,
                headers=self._auth_headers(),
                files={"file": (audio_path, audio_file, "audio/wav")},
                data={
                    "model": GROQ_WHISPER_MODEL,
                    "language": "en",
                    "response_format": "json",
                },
                timeout=30,
            )

        resp.raise_for_status()
        data = resp.json()
        return data.get("text", "").strip()

    # ------------------------------------------------------------------
    # Stage 2: LLM Polishing (Groq llama3-70b-8192)
    # ------------------------------------------------------------------
    def polish(self, raw_text: str) -> str:
        """
        Send raw transcription to Groq for speech editing.

        Falls back to raw text if Groq is unavailable.

        Args:
            raw_text: Unedited transcription from Whisper.

        Returns:
            Polished text (or raw text on failure).
        """
        if not raw_text:
            return ""

        if not self.api_key:
            return raw_text

        print("  ⚡ Groq LLM polishing (cloud)...")

        for model_name in GROQ_LLM_MODELS:
            payload = {
                "model": model_name,
                "messages": [
                    {"role": "system", "content": EDITOR_SYSTEM_PROMPT},
                    {"role": "user", "content": raw_text},
                ],
                "temperature": LLM_TEMPERATURE,
                "max_tokens": LLM_MAX_TOKENS,
                "stream": False,
            }

            try:
                print(f"  🔄 Trying model: {model_name}")
                resp = requests.post(
                    GROQ_CHAT_URL,
                    headers={
                        **self._auth_headers(),
                        "Content-Type": "application/json",
                    },
                    json=payload,
                    timeout=30,
                )
                resp.raise_for_status()
                data = resp.json()

                polished = (
                    data.get("choices", [{}])[0]
                    .get("message", {})
                    .get("content", "")
                    .strip()
                )

                if polished:
                    print(f"  ✅ Success with model: {model_name}")
                    return polished
                else:
                    print(f"  ⚠  Model {model_name} returned empty — trying next.")

            except requests.ConnectionError:
                print(f"  ⚠  Connection failed on model {model_name} — trying next.")
            except requests.Timeout:
                print(f"  ⚠  Timeout on model {model_name} — trying next.")
            except Exception as e:
                print(f"  ⚠  Model {model_name} failed: {e} — trying next.")

        print("  🚨 CRITICAL: All premium LLM models in the resiliency pool failed or timed out.")
        return raw_text

    # ------------------------------------------------------------------
    # Combined pipeline
    # ------------------------------------------------------------------
    def process(self, audio_path: str) -> tuple[str, str]:
        """
        Full pipeline: transcribe → polish → return both texts.

        Args:
            audio_path: Path to recorded .wav file.

        Returns:
            (raw_text, polished_text) tuple.  Both may be empty if
            no speech was detected.
        """
        print("  🧠 Transcribing audio via Groq...")
        raw_text = self.transcribe(audio_path)

        if not raw_text:
            print("  ⚠  No speech detected in recording.")
            return "", ""

        print(f"  📝 Raw:      \"{raw_text}\"")

        if self.api_key:
            print("  ✨ Polishing with LLM...")
            final_text = self.polish(raw_text)
            print(f"  ✅ Polished:  \"{final_text}\"")
        else:
            final_text = raw_text
            print("  ℹ  No API key — using raw transcription.")

        return raw_text, final_text
