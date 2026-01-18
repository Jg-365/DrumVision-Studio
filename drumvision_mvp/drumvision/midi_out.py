from __future__ import annotations

import logging
import queue
import threading
import time
from typing import Optional

import mido


class MidiOut:
    def __init__(self, enabled: bool = True) -> None:
        self.enabled = enabled
        self.port: Optional[mido.ports.BaseOutput] = None
        self._queue: "queue.Queue[tuple[float, int, int]]" = queue.Queue()
        self._thread = threading.Thread(target=self._worker, daemon=True)
        self._thread.start()
        if enabled:
            self._open_port()

    def _open_port(self) -> None:
        try:
            self.port = mido.open_output("DrumVision MIDI", virtual=True)
            logging.info("Opened virtual MIDI port: DrumVision MIDI")
            return
        except Exception as exc:  # pragma: no cover - system dependent
            logging.warning("Virtual MIDI port not available: %s", exc)
        try:
            outputs = mido.get_output_names()
            if outputs:
                self.port = mido.open_output(outputs[0])
                logging.info("Opened MIDI output: %s", outputs[0])
            else:
                logging.warning("No MIDI outputs found, MIDI disabled")
                self.enabled = False
        except Exception as exc:  # pragma: no cover - system dependent
            logging.error("Failed to open MIDI output: %s", exc)
            self.enabled = False

    def send_hit(self, midi_note: int, velocity: int) -> None:
        if not self.enabled or not self.port:
            return
        now = time.time()
        self.port.send(mido.Message("note_on", note=midi_note, velocity=velocity))
        self._queue.put((now + 0.05, midi_note, 0))

    def _worker(self) -> None:
        while True:
            try:
                due, note, velocity = self._queue.get(timeout=0.05)
            except queue.Empty:
                continue
            delay = max(0.0, due - time.time())
            if delay:
                time.sleep(delay)
            if self.port:
                self.port.send(mido.Message("note_off", note=note, velocity=velocity))

    def close(self) -> None:
        if self.port:
            self.port.close()
            logging.info("MIDI port closed")
