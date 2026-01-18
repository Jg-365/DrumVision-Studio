from __future__ import annotations

import logging
import os
from typing import Dict

import pygame


class AudioOut:
    def __init__(self, enabled: bool = True) -> None:
        self.enabled = enabled
        self.samples: Dict[str, pygame.mixer.Sound] = {}
        if not enabled:
            return
        try:
            pygame.mixer.init()
            logging.info("Pygame mixer initialized")
        except Exception as exc:
            logging.warning("Failed to init pygame mixer: %s", exc)
            self.enabled = False
            return
        self._load_samples()

    def _load_samples(self) -> None:
        base = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "samples")
        if not os.path.isdir(base):
            logging.warning("Samples directory missing: %s", base)
            return
        for name in ["snare", "kick", "hihat", "tom1", "tom2", "crash", "ride"]:
            path = os.path.join(base, f"{name}.wav")
            if not os.path.exists(path):
                logging.warning("Sample missing: %s", path)
                continue
            try:
                self.samples[name] = pygame.mixer.Sound(path)
            except Exception as exc:
                logging.warning("Failed to load sample %s: %s", path, exc)

    def play_hit(self, piece_name: str, velocity: int) -> None:
        if not self.enabled:
            return
        sample = self.samples.get(piece_name)
        if not sample:
            return
        volume = max(0.1, min(1.0, velocity / 127))
        sample.set_volume(volume)
        sample.play()

    def close(self) -> None:
        if self.enabled:
            pygame.mixer.quit()
            logging.info("Pygame mixer closed")
