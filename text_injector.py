"""
text_injector.py — OS-level text injection for LocalFlow.

Types text directly at the active Windows cursor position using simulated
keystrokes. Works in any application: browsers, editors, chat apps, terminals.
"""

import time
import keyboard


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
# Delay between keystrokes in seconds.
# A small delay prevents fast-input-rejecting apps from dropping characters.
KEYSTROKE_DELAY = 0.012  # ~12 ms


class TextInjector:
    """Simulates typing at the current cursor position."""

    def __init__(self, delay: float = KEYSTROKE_DELAY):
        self.delay = delay

    def inject(self, text: str) -> None:
        """
        Type the given text at the current cursor position.

        Args:
            text: The polished text to type out.
        """
        if not text:
            return

        # Clean up: strip whitespace, normalize line endings
        cleaned = text.strip().replace("\r\n", "\n")

        if not cleaned:
            return

        # Small pause before typing to let the user's key-release register
        # and to ensure focus is on the target window
        time.sleep(0.15)

        # keyboard.write() handles Unicode and sends OS-level key events
        keyboard.write(cleaned, delay=self.delay)

    def inject_with_newline(self, text: str) -> None:
        """
        Type the text followed by a newline (Enter key).

        Args:
            text: The polished text to type out.
        """
        self.inject(text)
        if text and text.strip():
            time.sleep(0.05)
            keyboard.press_and_release("enter")
