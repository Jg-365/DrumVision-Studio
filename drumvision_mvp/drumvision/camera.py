from __future__ import annotations

import cv2
import logging
from typing import Optional, Tuple


class CameraManager:
    def __init__(self, camera_id: int = 0, frame_size: Optional[Tuple[int, int]] = None) -> None:
        self.capture = cv2.VideoCapture(camera_id)
        if frame_size:
            self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, frame_size[0])
            self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_size[1])
        if not self.capture.isOpened():
            raise RuntimeError("Could not open camera")
        logging.info("Camera initialized with id=%s", camera_id)

    def read(self):
        return self.capture.read()

    def release(self) -> None:
        self.capture.release()
        logging.info("Camera released")
