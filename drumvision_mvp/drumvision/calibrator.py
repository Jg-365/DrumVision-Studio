from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from .kit import DrumKit
from .tracking import HandState


@dataclass
class CalibrationState:
    active: bool = False
    step: int = 0
    piece_index: int = 0
    radius: int = 60
    messages: List[str] = field(default_factory=list)
    velocity_samples: Dict[str, List[float]] = field(default_factory=dict)
    roi_points: List[Tuple[int, int]] = field(default_factory=list)
    selecting_roi: bool = False


class Calibrator:
    piece_order = ["snare", "kick", "hihat", "tom1", "tom2", "crash", "ride"]

    def __init__(self) -> None:
        self.state = CalibrationState()
        self._inside_state: Dict[str, bool] = {}

    def start(self) -> None:
        self.state = CalibrationState(active=True, step=0, piece_index=0, radius=60)
        self.state.messages = ["Calibration started: Step 1 layout"]
        logging.info("Calibration started")

    def current_piece(self) -> Optional[str]:
        if self.state.piece_index < len(self.piece_order):
            return self.piece_order[self.state.piece_index]
        return None

    def on_mouse(self, event, x, y, flags, params) -> None:
        if not self.state.active or not self.state.selecting_roi:
            return
        if event == 1:  # cv2.EVENT_LBUTTONDOWN
            self.state.roi_points.append((x, y))
            if len(self.state.roi_points) == 2:
                self.state.selecting_roi = False

    def handle_key(self, key: int, kit: DrumKit) -> Optional[str]:
        if not self.state.active:
            return None
        piece_name = self.current_piece()
        if self.state.step == 0:
            if key in (ord("+"), ord("=")):
                self.state.radius += 5
            if key == ord("-"):
                self.state.radius = max(20, self.state.radius - 5)
            if key == ord("r"):
                self.state.selecting_roi = True
                self.state.roi_points = []
            if key == ord("n") and piece_name:
                self.state.piece_index += 1
                return "Next piece"
        return None

    def update_layout(self, hands: List[HandState], kit: DrumKit) -> str:
        piece_name = self.current_piece()
        if not piece_name:
            self.state.step = 1
            self.state.piece_index = 0
            return "Layout done. Step 2: hit each piece 3 times."
        message = f"Point to {piece_name.upper()} and press [1] to set. +/- radius. 'n' skip. 'r' ROI"
        if self.state.selecting_roi:
            message = f"Click two points to set ROI for {piece_name.upper()}"
        for hand in hands:
            if hand.confidence > 0.5:
                if self.state.selecting_roi and len(self.state.roi_points) == 2:
                    p1, p2 = self.state.roi_points
                    x1, y1 = min(p1[0], p2[0]), min(p1[1], p2[1])
                    x2, y2 = max(p1[0], p2[0]), max(p1[1], p2[1])
                    kit.pieces[piece_name].roi = (x1, y1, x2, y2)
                return message
        return message

    def confirm_position(self, hands: List[HandState], kit: DrumKit) -> Optional[str]:
        piece_name = self.current_piece()
        if not piece_name:
            return None
        if not hands:
            return "No hand detected"
        primary = max(hands, key=lambda h: h.confidence)
        kit.pieces[piece_name].position = primary.strike_point
        kit.pieces[piece_name].radius = self.state.radius
        self.state.piece_index += 1
        return f"Set {piece_name} position"

    def update_thresholds(self, hands: List[HandState], kit: DrumKit) -> str:
        piece_name = self.current_piece()
        if not piece_name:
            self.state.active = False
            return "Calibration complete."
        piece = kit.pieces[piece_name]
        samples = self.state.velocity_samples.setdefault(piece_name, [])
        for hand in hands:
            inside = self._inside(piece, hand.strike_point)
            was_inside = self._inside_state.get(piece_name, False)
            if inside and not was_inside and hand.v_y > 0:
                samples.append(hand.v_mag)
            self._inside_state[piece_name] = inside
        remaining = max(0, 3 - len(samples))
        message = f"Hit {piece_name.upper()} {remaining} more times"
        if len(samples) >= 3:
            median = sorted(samples)[1]
            piece.threshold_speed = 0.7 * median
            piece.velocity_max = 1.8 * max(samples)
            self.state.piece_index += 1
            message = f"Threshold set for {piece_name}"
        return message

    @staticmethod
    def _inside(piece, point: Tuple[int, int]) -> bool:
        dx = point[0] - piece.position[0]
        dy = point[1] - piece.position[1]
        return dx * dx + dy * dy <= piece.radius * piece.radius
