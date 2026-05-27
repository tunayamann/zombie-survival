"""
Programmatic sound generation – no external audio files required.
Tones are synthesised as 16-bit mono PCM and wrapped in an in-memory WAV,
so pygame.mixer can load them directly from a BytesIO buffer.
"""

import io
import math
import struct

import pygame


class SoundManager:
    def __init__(self):
        self.sounds: dict[str, pygame.mixer.Sound] = {}
        self.enabled = False
        self._init()

    # ── Initialisation ────────────────────────────────────────────────────────

    def _init(self):
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)
            self._load_all()
            self.enabled = True
        except Exception as exc:
            print(f"[SoundManager] Audio disabled: {exc}")

    def _load_all(self):
        self.sounds["shoot"]      = self._make_tone(800,  0.08, 0.15)
        self.sounds["zombie_die"] = self._make_tone(180,  0.30, 0.30)
        self.sounds["player_hit"] = self._make_tone(380,  0.18, 0.40)
        self.sounds["wave_start"] = self._make_tone(550,  0.45, 0.25)
        self.sounds["game_over"]  = self._make_tone(100,  0.90, 0.35)
        self.sounds["win"]        = self._make_tone(740,  0.70, 0.28)

    # ── Tone synthesis ────────────────────────────────────────────────────────

    def _make_tone(self, freq: float, duration: float,
                   volume: float, sample_rate: int = 44100) -> pygame.mixer.Sound:
        """Return a pygame Sound of a decaying sine wave at *freq* Hz."""
        n = int(sample_rate * duration)
        raw = bytearray(n * 2)
        for i in range(n):
            t   = i / sample_rate
            env = 1.0 - i / n                         # linear decay envelope
            val = int(volume * env * 32767 * math.sin(2 * math.pi * freq * t))
            val = max(-32768, min(32767, val))
            struct.pack_into("<h", raw, i * 2, val)

        buf = io.BytesIO()
        data_len = len(raw)
        # RIFF/WAVE header
        buf.write(b"RIFF")
        buf.write(struct.pack("<I", 36 + data_len))
        buf.write(b"WAVE")
        # fmt  chunk
        buf.write(b"fmt ")
        buf.write(struct.pack("<I",  16))             # chunk size
        buf.write(struct.pack("<HH", 1, 1))           # PCM, mono
        buf.write(struct.pack("<I",  sample_rate))
        buf.write(struct.pack("<I",  sample_rate * 2))# byte rate
        buf.write(struct.pack("<HH", 2, 16))          # block align, bits/sample
        # data chunk
        buf.write(b"data")
        buf.write(struct.pack("<I", data_len))
        buf.write(raw)
        buf.seek(0)
        return pygame.mixer.Sound(file=buf)

    # ── Public API ────────────────────────────────────────────────────────────

    def play(self, name: str):
        if self.enabled and name in self.sounds:
            try:
                self.sounds[name].play()
            except Exception:
                pass
