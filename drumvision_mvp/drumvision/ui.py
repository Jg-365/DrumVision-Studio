from __future__ import annotations

import cv2
from typing import Dict, List, Tuple

from .kit import DrumKit
from .tracking import HandState


class UI:
    def __init__(self) -> None:
        self.debug = True
        self.last_hit: Tuple[str, int] | None = None

    def toggle_debug(self) -> None:
        self.debug = not self.debug

    def draw(
        self,
        frame,
        kit: DrumKit,
        hands: List[HandState],
        inside_map: Dict[Tuple[int, str], bool],
        mode: str,
        fps: float,
        midi_enabled: bool,
        audio_enabled: bool,
        message: str,
    ):
        for piece in kit.list_pieces():
            color = (50, 200, 50)
            cv2.circle(frame, piece.position, piece.radius, color, 2)
            cv2.putText(
                frame,
                piece.name,
                (piece.position[0] - 30, piece.position[1] - piece.radius - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color,
                1,
            )
            if piece.roi and mode == "object":
                x1, y1, x2, y2 = piece.roi
                cv2.rectangle(frame, (x1, y1), (x2, y2), (200, 200, 0), 1)

        for hand in hands:
            cv2.circle(frame, hand.strike_point, 8, (255, 0, 0), -1)

        status_text = f"FPS: {fps:.1f} | Mode: {mode.upper()} | MIDI: {'ON' if midi_enabled else 'OFF'} | AUDIO: {'ON' if audio_enabled else 'OFF'}"
        cv2.putText(frame, status_text, (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        if self.last_hit:
            hit_text = f"Hit: {self.last_hit[0]} vel={self.last_hit[1]}"
            cv2.putText(frame, hit_text, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

        if message:
            cv2.putText(frame, message, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 200, 0), 1)

        if self.debug:
            help_text = "Keys: q quit | c calibrate | s save | l load | m MIDI | o mode | d debug"
            cv2.putText(frame, help_text, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

        return frame
