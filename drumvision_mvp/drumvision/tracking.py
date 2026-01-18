from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import cv2
import mediapipe as mp
import numpy as np


@dataclass
class HandState:
    hand_id: int
    strike_point: Tuple[int, int]
    v_y: float
    v_mag: float
    timestamp: float
    confidence: float


@dataclass
class HandHistory:
    points: List[Tuple[float, Tuple[int, int], float]] = field(default_factory=list)

    def add(self, timestamp: float, point: Tuple[int, int], confidence: float) -> None:
        self.points.append((timestamp, point, confidence))
        if len(self.points) > 8:
            self.points.pop(0)

    def velocity(self) -> Tuple[float, float]:
        if len(self.points) < 2:
            return 0.0, 0.0
        (t1, p1, _), (t2, p2, _) = self.points[-2], self.points[-1]
        dt = max(t2 - t1, 1e-6)
        dx = (p2[0] - p1[0]) / dt
        dy = (p2[1] - p1[1]) / dt
        v_mag = float(np.hypot(dx, dy))
        return dy, v_mag


class HandTracker:
    def __init__(self) -> None:
        self.hands = mp.solutions.hands.Hands(
            max_num_hands=2,
            model_complexity=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        self.histories: Dict[int, HandHistory] = {}
        self.smooth_points: Dict[int, Tuple[int, int]] = {}
        self.alpha = 0.6
        logging.info("MediaPipe Hands initialized")

    def _smooth(self, hand_id: int, point: Tuple[int, int]) -> Tuple[int, int]:
        if hand_id not in self.smooth_points:
            self.smooth_points[hand_id] = point
            return point
        prev = self.smooth_points[hand_id]
        smoothed = (
            int(self.alpha * point[0] + (1 - self.alpha) * prev[0]),
            int(self.alpha * point[1] + (1 - self.alpha) * prev[1]),
        )
        self.smooth_points[hand_id] = smoothed
        return smoothed

    @staticmethod
    def _strike_point(landmarks, image_shape: Tuple[int, int]) -> Tuple[int, int]:
        h, w = image_shape
        idx_tip = landmarks[mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP]
        if idx_tip:
            return int(idx_tip.x * w), int(idx_tip.y * h)
        wrist = landmarks[mp.solutions.hands.HandLandmark.WRIST]
        palm = [
            wrist,
            landmarks[mp.solutions.hands.HandLandmark.INDEX_FINGER_MCP],
            landmarks[mp.solutions.hands.HandLandmark.MIDDLE_FINGER_MCP],
            landmarks[mp.solutions.hands.HandLandmark.RING_FINGER_MCP],
            landmarks[mp.solutions.hands.HandLandmark.PINKY_MCP],
        ]
        x = int(sum(p.x for p in palm) / len(palm) * w)
        y = int(sum(p.y for p in palm) / len(palm) * h)
        return x, y

    def process(self, frame: np.ndarray) -> List[HandState]:
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.hands.process(image_rgb)
        states: List[HandState] = []
        now = time.time()
        if not result.multi_hand_landmarks:
            return states
        for idx, hand_landmarks in enumerate(result.multi_hand_landmarks):
            point = self._strike_point(hand_landmarks.landmark, frame.shape[:2])
            point = self._smooth(idx, point)
            history = self.histories.setdefault(idx, HandHistory())
            history.add(now, point, 1.0)
            v_y, v_mag = history.velocity()
            states.append(
                HandState(
                    hand_id=idx,
                    strike_point=point,
                    v_y=v_y,
                    v_mag=v_mag,
                    timestamp=now,
                    confidence=1.0,
                )
            )
        return states

    def close(self) -> None:
        self.hands.close()
        logging.info("MediaPipe Hands closed")
