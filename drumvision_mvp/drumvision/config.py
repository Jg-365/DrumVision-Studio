from __future__ import annotations

import logging
import os
from typing import Dict, List, Optional, Tuple

from pydantic import BaseModel, Field

from .utils import load_json, save_json

DEFAULT_CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "configs", "default.json")
USER_CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "configs", "user.json")


class PieceConfig(BaseModel):
    midi_note: int
    position: Tuple[int, int]
    radius: int
    cooldown_ms: int = 120
    velocity_min: float = 10.0
    velocity_max: float = 2000.0
    threshold_speed: float = 400.0
    roi: Optional[List[int]] = None


class AppConfig(BaseModel):
    camera_id: int = 0
    mode: str = "air"
    midi_enabled: bool = True
    audio_enabled: bool = True
    pieces: Dict[str, PieceConfig]


class ConfigManager:
    def __init__(self) -> None:
        self.config_path = USER_CONFIG_PATH if os.path.exists(USER_CONFIG_PATH) else DEFAULT_CONFIG_PATH
        self.config = self.load()

    def load(self) -> AppConfig:
        data = load_json(self.config_path)
        logging.info("Loaded config from %s", self.config_path)
        return AppConfig(**data)

    def save(self, path: Optional[str] = None) -> None:
        target = path or USER_CONFIG_PATH
        save_json(target, self.config.model_dump())
        logging.info("Saved config to %s", target)

    def update_piece(self, name: str, position: Tuple[int, int], radius: int) -> None:
        if name in self.config.pieces:
            self.config.pieces[name].position = position
            self.config.pieces[name].radius = radius

    def update_thresholds(self, name: str, threshold_speed: float, velocity_max: float) -> None:
        if name in self.config.pieces:
            self.config.pieces[name].threshold_speed = threshold_speed
            self.config.pieces[name].velocity_max = velocity_max

    def set_mode(self, mode: str) -> None:
        self.config.mode = mode

    def toggle_midi(self) -> None:
        self.config.midi_enabled = not self.config.midi_enabled

    def toggle_audio(self) -> None:
        self.config.audio_enabled = not self.config.audio_enabled
