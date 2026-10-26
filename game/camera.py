import time
import threading
from typing import Optional, Tuple
import cv2
import numpy as np
import pygame
from game import config

class HSVHandTracker:
    def __init__(self,
                 webcam_index: int = config.WEBCAM_INDEX,
                 lower_blue: np.ndarray = config.LOWER_BLUE,
                 upper_blue: np.ndarray = config.UPPER_BLUE,
                 min_contour_area: float = config.MIN_CONTOUR_AREA):
        self.webcam_index = webcam_index
        self.lower_blue = np.array(lower_blue, dtype=np.uint8)
        self.upper_blue = np.array(upper_blue, dtype=np.uint8)
        self.min_contour_area = min_contour_area

        # Thread synchronization
        self._lock = threading.Lock()
        self._running = False
        self._thread: Optional[threading.Thread] = None

        # Camera state
        self.is_camera_available = False
        self.error_message = ""

        # Tracking telemetry
        self.is_detected = False
        self.centroid: Optional[Tuple[int, int]] = None
        self.contour_area: float = 0.0

        # Motion & Gesture tracking
        self.baseline_x: Optional[float] = None
        self.smoothed_cx: Optional[float] = None
        self.current_dx: float = 0.0
        self.last_gesture_time: float = 0.0
        self.pending_gesture: Optional[str] = None

        # Pygame surface for HUD preview
        self.latest_preview_surf: Optional[pygame.Surface] = None

        # Morphological kernel
        self.kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))

    def start(self):
        if self._running:
            return

        self._running = True
        self._thread = threading.Thread(target=self._worker_loop, name="WebcamHSVThread", daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.5)
        self._thread = None

    def process_motion(self, cx: float, now: float) -> Optional[str]:
        if self.baseline_x is None:
            self.baseline_x = float(cx)
            self.smoothed_cx = float(cx)
            return None

        # Smooth coordinate for telemetry
        self.smoothed_cx += (cx - self.smoothed_cx) * 0.6
        dx = float(cx) - self.baseline_x
        self.current_dx = dx

        can_trigger = (now - self.last_gesture_time) >= config.GESTURE_COOLDOWN

        if can_trigger:
            # Check move to RIGHT
            if dx >= config.SWIPE_THRESHOLD_PX:
                self.baseline_x = float(cx)
                self.last_gesture_time = now
                return "RIGHT"

            # Check move to LEFT
            elif dx <= -config.SWIPE_THRESHOLD_PX:
                self.baseline_x = float(cx)
                self.last_gesture_time = now
                return "LEFT"
            else:
                # Gentle baseline drift so hand doesn't trigger on slow ambient drift
                self.baseline_x += (cx - self.baseline_x) * config.BASELINE_DRIFT_FACTOR
        else:
            # During cooldown, adapt baseline to follow hand
            self.baseline_x += (cx - self.baseline_x) * 0.25

        return None

    def _worker_loop(self):
        cap = None
        try:
            cap = cv2.VideoCapture(self.webcam_index)
            if not cap.isOpened():
                cap.release()
                cap = cv2.VideoCapture(1)

            if not cap or not cap.isOpened():
                self.is_camera_available = False
                self.error_message = f"Webcam index {self.webcam_index} not accessible. Using keyboard fallback."
                print(f"[HSVHandTracker] {self.error_message}")
                return

            self.is_camera_available = True
            self.error_message = ""
            print(f"[HSVHandTracker] Webcam opened successfully on index {self.webcam_index}.")

            target_w = config.WEBCAM_FRAME_WIDTH
            target_h = config.WEBCAM_FRAME_HEIGHT

            while self._running:
                ret, frame = cap.read()
                if not ret or frame is None:
                    time.sleep(0.02)
                    continue

                # 1. Resize frame to standard dimensions
                frame = cv2.resize(frame, (target_w, target_h), interpolation=cv2.INTER_LINEAR)

                # 2. Mirror frame horizontally
                frame = cv2.flip(frame, 1)

                # 3. Convert BGR to HSV
                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

                # 4. Color segmentation: inRange binary mask
                with self._lock:
                    lower = self.lower_blue.copy()
                    upper = self.upper_blue.copy()

                mask = cv2.inRange(hsv, lower, upper)

                # 5. Morphological operations
                mask_clean = cv2.morphologyEx(mask, cv2.MORPH_OPEN, self.kernel, iterations=2)
                mask_clean = cv2.morphologyEx(mask_clean, cv2.MORPH_CLOSE, self.kernel, iterations=2)

                # 6. Find contours
                contours, _ = cv2.findContours(mask_clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                detected = False
                detected_cx = None
                detected_cy = None
                max_area = 0.0
                best_cnt = None

                if contours:
                    best_cnt = max(contours, key=cv2.contourArea)
                    max_area = cv2.contourArea(best_cnt)

                    if max_area >= self.min_contour_area:
                        M = cv2.moments(best_cnt)
                        if M["m00"] > 0:
                            detected_cx = int(M["m10"] / M["m00"])
                            detected_cy = int(M["m01"] / M["m00"])
                            detected = True

                # 7. Process directional motion (MOVE LEFT / MOVE RIGHT)
                now = time.time()
                gesture_detected = None

                if detected and detected_cx is not None:
                    gesture_detected = self.process_motion(detected_cx, now)
                else:
                    self.baseline_x = None
                    self.smoothed_cx = None
                    self.current_dx = 0.0

                # 8. Clean visual display (no text or banners, blue object blocked out cleanly)
                overlay = frame.copy()

                if detected and best_cnt is not None:
                    block_layer = overlay.copy()
                    cv2.drawContours(block_layer, [best_cnt], -1, (0, 235, 255), thickness=-1)
                    cv2.addWeighted(block_layer, 0.85, overlay, 0.15, 0, overlay)

                # 9. Convert OpenCV BGR to Pygame RGB surface
                rgb_preview = cv2.cvtColor(overlay, cv2.COLOR_BGR2RGB)
                preview_surf = pygame.image.frombuffer(rgb_preview.tobytes(), (target_w, target_h), "RGB")

                # Thread-safe update
                with self._lock:
                    self.is_detected = detected
                    self.centroid = (detected_cx, detected_cy) if detected else None
                    self.contour_area = max_area
                    self.latest_preview_surf = preview_surf
                    if gesture_detected:
                        self.pending_gesture = gesture_detected

                time.sleep(1.0 / config.WEBCAM_FPS)

        except Exception as e:
            self.is_camera_available = False
            self.error_message = f"Webcam error: {e}"
            print(f"[HSVHandTracker] Exception in worker: {e}")
        finally:
            if cap and cap.isOpened():
                cap.release()
            print("[HSVHandTracker] Webcam released and thread terminated.")

    def get_state(self):
        with self._lock:
            gesture = self.pending_gesture
            self.pending_gesture = None

            return {
                "is_detected": self.is_detected,
                "gesture": gesture,
                "preview_surface": self.latest_preview_surf,
                "is_camera_available": self.is_camera_available,
                "error_message": self.error_message
            }
