from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from .config import AppConfig


@dataclass
class KitPiece:
    name: str
    midi_note: int
    position: Tuple[int, int]
    radius: int
    cooldown_ms: int
    velocity_min: float
    velocity_max: float
    threshold_speed: float
    last_hit_ts: float = 0.0
    roi: Optional[Tuple[int, int, int, int]] = None


@dataclass
class DrumKit:
    pieces: Dict[str, KitPiece] = field(default_factory=dict)

    @classmethod
    def from_config(cls, config: AppConfig) -> "DrumKit":
        pieces = {}
        for name, piece_cfg in config.pieces.items():
            roi = None
            if piece_cfg.roi:
                roi = tuple(piece_cfg.roi)
            pieces[name] = KitPiece(
                name=name,
                midi_note=piece_cfg.midi_note,
                position=tuple(piece_cfg.position),
                radius=piece_cfg.radius,
                cooldown_ms=piece_cfg.cooldown_ms,
                velocity_min=piece_cfg.velocity_min,
                velocity_max=piece_cfg.velocity_max,
                threshold_speed=piece_cfg.threshold_speed,
                roi=roi,
            )
        return cls(pieces=pieces)

    def list_pieces(self) -> List[KitPiece]:
        return list(self.pieces.values())
