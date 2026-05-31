"""
audio_recorder.py — Microphone capture module for LocalFlow.

Uses sounddevice's callback-based streaming to capture audio in real-time.
Records at 16 kHz, mono, 16-bit PCM — the native format faster-whisper expects.
Frames are pushed to a thread-safe queue and stitched into a .wav on stop.
"""

import os
import tempfile
import queue
import threading
import numpy as np
import sounddevice as sd
import wavio


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SAMPLE_RATE = 16_000   # 16 kHz — optimal for Whisper
CHANNELS = 1           # Mono
DTYPE = "int16"        # 16-bit PCM
BLOCK_SIZE = 1024      # Frames per callback (~64 ms at 16 kHz)
DEVICE_INDEX = 3       # Microphone Array (Realtek Audio) — hardcoded per system diagnostics


class AudioRecorder:
    """Hold-to-record microphone capture with a simple start/stop API."""

    def __init__(self, sample_rate: int = SAMPLE_RATE, channels: int = CHANNELS,
                 device_index: int = DEVICE_INDEX):
        self.sample_rate = sample_rate
        self.channels = channels
        self.device_index = device_index
        self._queue: queue.Queue[np.ndarray] = queue.Queue()
        self._stream: sd.InputStream | None = None
        self._is_recording = False
        self._lock = threading.Lock()

        # Confirm the pinned device exists and print its name
        try:
            dev_info = sd.query_devices(self.device_index)
            print(f"  🎤 Input device: [{self.device_index}] {dev_info['name']}")
        except Exception:
            print(f"  ⚠  Device index {self.device_index} not found — "
                  "check sounddevice.query_devices() and update DEVICE_INDEX.")

    # ------------------------------------------------------------------
    # PortAudio callback — runs on the audio thread
    # ------------------------------------------------------------------
    def _audio_callback(self, indata: np.ndarray, frames: int,
                        time_info, status) -> None:
        """Push a copy of each audio block into the queue."""
        if status:
            print(f"  ⚠  Audio status: {status}")
        self._queue.put(indata.copy())

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def start(self) -> None:
        """Begin recording from the selected microphone."""
        with self._lock:
            if self._is_recording:
                return  # Guard against double-start

            # Drain any leftover frames from a previous session
            while not self._queue.empty():
                self._queue.get_nowait()

            self._stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=DTYPE,
                blocksize=BLOCK_SIZE,
                device=self.device_index,
                callback=self._audio_callback,
            )
            self._stream.start()
            self._is_recording = True

    def stop(self) -> str | None:
        """
        Stop recording and save captured audio to a temporary .wav file.

        Returns:
            Path to the .wav file, or None if nothing was recorded.
        """
        with self._lock:
            if not self._is_recording:
                return None
            self._is_recording = False

            if self._stream is not None:
                self._stream.stop()
                self._stream.close()
                self._stream = None

        # Stitch all queued frames into a single NumPy array
        frames: list[np.ndarray] = []
        while not self._queue.empty():
            frames.append(self._queue.get_nowait())

        if not frames:
            return None

        audio_data = np.concatenate(frames, axis=0)

        # Discard recordings shorter than ~0.3 seconds (likely accidental taps)
        min_samples = int(self.sample_rate * 0.3)
        if len(audio_data) < min_samples:
            print("  ⚠  Recording too short — discarded.")
            return None

        # Write to a temp .wav file
        tmp_dir = os.path.join(tempfile.gettempdir(), "localflow")
        os.makedirs(tmp_dir, exist_ok=True)
        filepath = os.path.join(tmp_dir, "recording.wav")

        wavio.write(filepath, audio_data, self.sample_rate, sampwidth=2)
        return filepath

    @property
    def is_recording(self) -> bool:
        return self._is_recording
