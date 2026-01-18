from __future__ import annotations

import logging
import os
import sys
import time
from typing import List

import cv2

from drumvision.audio_out import AudioOut
from drumvision.calibrator import Calibrator
from drumvision.camera import CameraManager
from drumvision.config import AppConfig, ConfigManager
from drumvision.hit_detection import HitDetector
from drumvision.kit import DrumKit
from drumvision.midi_out import MidiOut
from drumvision.tracking import HandTracker
from drumvision.ui import UI
from drumvision.utils import FPSCounter, setup_logging


def update_config_from_kit(config: AppConfig, kit: DrumKit) -> None:
    for name, piece in kit.pieces.items():
        config.pieces[name].position = piece.position
        config.pieces[name].radius = piece.radius
        config.pieces[name].threshold_speed = piece.threshold_speed
        config.pieces[name].velocity_max = piece.velocity_max
        if piece.roi:
            config.pieces[name].roi = list(piece.roi)


def main() -> None:
    setup_logging()
    logging.info("Starting DrumVision MVP")

    config_manager = ConfigManager()
    config = config_manager.config

    try:
        camera = CameraManager(config.camera_id)
    except RuntimeError as exc:
        logging.error("Camera error: %s", exc)
        sys.exit(1)

    try:
        tracker = HandTracker()
    except Exception as exc:
        logging.error("MediaPipe init failed: %s", exc)
        sys.exit(1)

    kit = DrumKit.from_config(config)
    detector = HitDetector()
    midi_out = MidiOut(enabled=config.midi_enabled)
    audio_out = AudioOut(enabled=config.audio_enabled)
    ui = UI()
    calibrator = Calibrator()
    fps_counter = FPSCounter()

    cv2.namedWindow("DrumVision MVP")

    def mouse_callback(event, x, y, flags, params):
        calibrator.on_mouse(event, x, y, flags, params)

    cv2.setMouseCallback("DrumVision MVP", mouse_callback)

    message = ""
    while True:
        ret, frame = camera.read()
        if not ret:
            logging.warning("Failed to read camera frame")
            continue

        hands = tracker.process(frame)
        events = detector.process(hands, kit, config.mode)
        for event in events:
            logging.info(
                "Hit %s vel=%s hand=%s", event.piece_name, event.velocity, event.hand_id
            )
            if config.midi_enabled:
                midi_out.send_hit(event.midi_note, event.velocity)
            if config.audio_enabled:
                audio_out.play_hit(event.piece_name, event.velocity)
            ui.last_hit = (event.piece_name, event.velocity)

        if calibrator.state.active:
            if calibrator.state.step == 0:
                message = calibrator.update_layout(hands, kit)
            else:
                message = calibrator.update_thresholds(hands, kit)

        fps = fps_counter.tick()
        frame = ui.draw(
            frame,
            kit,
            hands,
            detector.inside_state,
            config.mode,
            fps,
            config.midi_enabled,
            config.audio_enabled,
            message,
        )

        cv2.imshow("DrumVision MVP", frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break
        if key == ord("d"):
            ui.toggle_debug()
        if key == ord("m"):
            config_manager.toggle_midi()
            config = config_manager.config
            midi_out.enabled = config.midi_enabled
        if key == ord("o"):
            config.mode = "object" if config.mode == "air" else "air"
        if key == ord("c"):
            calibrator.start()
            message = "Calibration started"
        if key == ord("s"):
            update_config_from_kit(config, kit)
            config_manager.save()
            message = "Config saved"
        if key == ord("l"):
            config_manager = ConfigManager()
            config = config_manager.config
            kit = DrumKit.from_config(config)
            message = "Config loaded"
        if key == ord("1") and calibrator.state.active and calibrator.state.step == 0:
            message = calibrator.confirm_position(hands, kit) or message
        if calibrator.state.active:
            msg = calibrator.handle_key(key, kit)
            if msg:
                message = msg

    camera.release()
    tracker.close()
    midi_out.close()
    audio_out.close()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
