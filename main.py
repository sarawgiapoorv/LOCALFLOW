"""
main.py — Entry point for LocalFlow.

Launches the CustomTkinter desktop GUI.
All coordination, hotkey handling, and backend logic live in gui_app.py.

Usage:
    python main.py          (from an elevated terminal)
    pythonw main.py         (silent, no console window)
    Launch_LocalFlow.bat    (auto-elevates & silent)
"""

import sys

from gui_app import LocalFlowApp


def main():
    app = LocalFlowApp()
    app.mainloop()


if __name__ == "__main__":
    main()
