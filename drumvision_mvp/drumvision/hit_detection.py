from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Dict, List, Tuple

from .kit import DrumKit, KitPiece
from .tracking import HandState
from .utils import clamp


@dataclass
class HitEvent:
    piece_name: str
    midi_note: int
    velocity: int
    timestamp: float
    hand_id: int
    confidence: float


class HitDetector:
    def __init__(self) -> None:
        self.inside_state: Dict[Tuple[int, str], bool] = {}
        self.armed_state: Dict[Tuple[int, str], bool] = {}

    def _inside_piece(self, piece: KitPiece, point: Tuple[int, int], mode: str) -> bool:
        if mode == "object" and piece.roi:
            x1, y1, x2, y2 = piece.roi
            return x1 <= point[0] <= x2 and y1 <= point[1] <= y2
        dx = point[0] - piece.position[0]
        dy = point[1] - piece.position[1]
        return dx * dx + dy * dy <= piece.radius * piece.radius

    def _velocity_to_midi(self, piece: KitPiece, v_mag: float) -> int:
        min_v = piece.threshold_speed
        max_v = max(piece.velocity_max, min_v + 1)
        v_mag = clamp(v_mag, min_v, max_v)
        vel = int(1 + 126 * (v_mag - min_v) / (max_v - min_v))
        return int(clamp(vel, 1, 127))

    def process(self, hands: List[HandState], kit: DrumKit, mode: str) -> List[HitEvent]:
        events: List[HitEvent] = []
        now = time.time()
        for hand in hands:
            for piece in kit.list_pieces():
                key = (hand.hand_id, piece.name)
                inside = self._inside_piece(piece, hand.strike_point, mode)
                was_inside = self.inside_state.get(key, False)
                armed = self.armed_state.get(key, True)

                if not armed:
                    if not inside or hand.v_y < -0.5 * piece.threshold_speed:
                        self.armed_state[key] = True
                    self.inside_state[key] = inside
                    continue

                cooldown_ok = (now - piece.last_hit_ts) * 1000 >= piece.cooldown_ms
                downstroke_ok = hand.v_y > piece.threshold_speed
                entered = not was_inside and inside

                if entered and cooldown_ok and downstroke_ok:
                    velocity = self._velocity_to_midi(piece, hand.v_mag)
                    events.append(
                        HitEvent(
                            piece_name=piece.name,
                            midi_note=piece.midi_note,
                            velocity=velocity,
                            timestamp=now,
                            hand_id=hand.hand_id,
                            confidence=1.0,
                        )
                    )
                    piece.last_hit_ts = now
                    self.armed_state[key] = False

                self.inside_state[key] = inside
        return events
