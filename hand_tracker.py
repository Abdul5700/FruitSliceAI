"""Webcam index-fingertip tracking for legacy and current MediaPipe builds."""
from __future__ import annotations

from pathlib import Path
from urllib.request import urlretrieve

import cv2
import mediapipe as mp
import numpy as np

MODEL_URL = ("https://storage.googleapis.com/mediapipe-models/hand_landmarker/"
             "hand_landmarker/float16/latest/hand_landmarker.task")
MODEL_PATH = Path(__file__).resolve().parent / "assets" / "models" / "hand_landmarker.task"


class HandTracker:
    """Returns a smoothed screen-space index fingertip and camera preview.

    MediaPipe's current Python 3.13 wheels use the Tasks API, while older
    wheels expose ``mp.solutions``. Both variants are supported.
    """
    def __init__(self, camera_index: int = 0) -> None:
        self.capture = cv2.VideoCapture(camera_index)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.available = self.capture.isOpened()
        self.error = "Webcam unavailable. Connect a camera and restart." if not self.available else ""
        self.point: tuple[float, float] | None = None
        self.preview: np.ndarray | None = None
        self.landmarks: list[tuple[float, float]] = []
        self.timestamp_ms = 0
        self.mode = "legacy"
        self.hands = None

        if not self.available:
            return
        try:
            if hasattr(mp, "solutions"):
                self.hands = mp.solutions.hands.Hands(
                    static_image_mode=False, max_num_hands=1, model_complexity=0,
                    min_detection_confidence=.58, min_tracking_confidence=.55,
                )
            else:
                self._create_task_landmarker()
                self.mode = "tasks"
        except Exception as exc:  # Let the game open with a clear on-screen message.
            self.available = False
            self.error = f"Hand tracker could not start: {exc}"

    def _create_task_landmarker(self) -> None:
        """Create the current MediaPipe Tasks tracker and obtain its small model once."""
        from mediapipe.tasks import python
        from mediapipe.tasks.python import vision

        if not MODEL_PATH.exists():
            MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
            urlretrieve(MODEL_URL, MODEL_PATH)
        options = vision.HandLandmarkerOptions(
            base_options=python.BaseOptions(model_asset_path=str(MODEL_PATH)),
            running_mode=vision.RunningMode.VIDEO,
            num_hands=1,
            min_hand_detection_confidence=.58,
            min_hand_presence_confidence=.55,
            min_tracking_confidence=.55,
        )
        self.hands = vision.HandLandmarker.create_from_options(options)

    def update(self, screen_size: tuple[int, int]) -> tuple[float, float] | None:
        if not self.available or not self.hands:
            return None
        ok, frame = self.capture.read()
        if not ok:
            self.error, self.available = "Camera frame could not be read.", False
            return None
        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.preview = rgb
        try:
            if self.mode == "legacy":
                result = self.hands.process(rgb)
                landmarks = result.multi_hand_landmarks[0].landmark if result.multi_hand_landmarks else None
            else:
                self.timestamp_ms += 33
                image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
                result = self.hands.detect_for_video(image, self.timestamp_ms)
                landmarks = result.hand_landmarks[0] if result.hand_landmarks else None
        except Exception as exc:
            self.error, self.available = f"Hand tracking stopped: {exc}", False
            return None
        if not landmarks:
            self.point = None
            self.landmarks = []
            return None
        self.landmarks = [(landmark.x, landmark.y) for landmark in landmarks]
        tip = landmarks[8]
        target = (tip.x * screen_size[0], tip.y * screen_size[1])
        self.point = target if self.point is None else (
            self.point[0] * .38 + target[0] * .62,
            self.point[1] * .38 + target[1] * .62,
        )
        return self.point

    def close(self) -> None:
        if self.capture:
            self.capture.release()
        if self.hands and hasattr(self.hands, "close"):
            self.hands.close()
