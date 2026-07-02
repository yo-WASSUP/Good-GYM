import cv2
import numpy as np
import time
import os
from threading import Lock
from PyQt5.QtCore import Qt, QThread, pyqtSignal

class VideoThread(QThread):
    """Video stream processing thread to avoid UI freezing"""
    change_pixmap_signal = pyqtSignal(np.ndarray, object, float)
    
    def __init__(self, camera_id=0, rotate=True, display_width=1280, display_height=720, inference_width=640, inference_height=360):
        super().__init__()
        self.camera_id = camera_id
        self.rotate = rotate
        self._run_flag = True
        self.buffer_size = 1  # Buffer size, set to 1 to avoid delay
        self.video_file = None  # Local video file path
        self.is_camera = True  # Whether to use camera
        self.fps = 30  # Default frame rate
        self.loop_video = False  # Control whether to loop video playback
        self.video_ended = False  # Mark if video has ended
        self.mirror = False  # Added for mirror mode
        self.display_width = display_width
        self.display_height = display_height
        self.inference_width = inference_width
        self.inference_height = inference_height
        self._logged_frame_shape = False
        self.max_emit_fps = 30
        self.debug_camera_stats = os.environ.get("GOOD_GYM_CAMERA_DEBUG") == "1"
        self._pending_lock = Lock()
        self._ui_frame_pending = False

    def set_camera(self, camera_id):
        """Switch camera"""
        if self.isRunning():
            self._run_flag = False
            self.wait()
        self.camera_id = camera_id
        self.video_file = None  # Clear video file path
        self.is_camera = True  # Switch back to camera mode
        self._logged_frame_shape = False
        self.mark_frame_processed()
        self._run_flag = True
        self.start()
    
    def set_rotation(self, rotate):
        """Set whether to rotate video"""
        self.rotate = rotate
        
    def set_mirror(self, mirror):
        """Set whether to mirror video"""
        self.mirror = mirror

    def _try_mark_frame_pending(self):
        with self._pending_lock:
            if self._ui_frame_pending:
                return False
            self._ui_frame_pending = True
            return True

    def mark_frame_processed(self):
        with self._pending_lock:
            self._ui_frame_pending = False

    def _resize_for_inference(self, frame):
        """Resize while preserving the displayed aspect ratio."""
        height, width = frame.shape[:2]
        if width <= 0 or height <= 0:
            return frame

        if width >= height:
            target_width = self.inference_width
            target_height = max(1, int(target_width * height / width))
        else:
            target_height = self.inference_width
            target_width = max(1, int(target_height * width / height))

        return cv2.resize(frame, (target_width, target_height))

    def _open_camera_with_backend(self, backend):
        if backend:
            return cv2.VideoCapture(self.camera_id, backend)
        return cv2.VideoCapture(self.camera_id)

    def _apply_camera_mode(self, capture, fourcc, width, height):
        capture.set(cv2.CAP_PROP_BUFFERSIZE, self.buffer_size)
        capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*fourcc))
        capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        capture.set(cv2.CAP_PROP_FPS, self.fps)

    def _open_best_camera_capture(self):
        if os.name == "nt":
            preferred_modes = [
                ("MSMF", cv2.CAP_MSMF, "MJPG", 800, 600),
                ("DEFAULT", 0, "MJPG", 800, 600),
                ("MSMF", cv2.CAP_MSMF, "MJPG", 640, 480),
                ("DEFAULT", 0, "MJPG", 640, 480),
                ("MSMF", cv2.CAP_MSMF, "YUY2", 640, 480),
                ("DSHOW", cv2.CAP_DSHOW, "MJPG", 640, 480),
            ]
        else:
            preferred_modes = [("DEFAULT", 0, "MJPG", 800, 600)]

        for backend_name, backend, fourcc, request_width, request_height in preferred_modes:
            capture = self._open_camera_with_backend(backend)
            if not capture.isOpened():
                capture.release()
                print(f"Camera backend unavailable: backend={backend_name}")
                continue

            self._apply_camera_mode(capture, fourcc, request_width, request_height)
            actual_width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
            if actual_width <= 0 or actual_height <= 0:
                capture.release()
                continue

            self.cap = capture
            print(
                f"Camera mode selected: backend={backend_name}, fourcc={fourcc}, "
                f"request={request_width}x{request_height}, "
                f"actual={actual_width}x{actual_height}"
            )
            return True

        self.cap = self._open_camera_with_backend(0)
        return self.cap.isOpened()
        
    def set_video_file(self, file_path, loop=False):
        """Set video file path
        
        Args:
            file_path (str): Video file path
            loop (bool): Whether to loop video playback, default is False
        """
        if self.isRunning():
            self._run_flag = False
            self.wait()
        self.video_file = file_path
        self.is_camera = False  # Switch to video file mode
        self.loop_video = loop  # Set whether to loop playback
        self.video_ended = False  # Reset video end flag
        
        # Pre-detect video aspect ratio to decide which rotation mode to apply
        self.auto_detect_orientation(file_path)
        
        self._run_flag = True
        self.start()
        
    def auto_detect_orientation(self, file_path):
        """Automatically detect video file aspect ratio and set appropriate rotation mode"""
        try:
            if not os.path.exists(file_path):
                print(f"Error: Video file does not exist {file_path}")
                return
                
            temp_cap = cv2.VideoCapture(file_path)
            if not temp_cap.isOpened():
                print(f"Error: Cannot open video file for aspect ratio detection {file_path}")
                return
                
            # Get original video size information (not dependent on frame reading)
            original_width = int(temp_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            original_height = int(temp_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            # If first frame can be obtained, use first frame size information to confirm
            ret, first_frame = temp_cap.read()
            if ret:
                height, width = first_frame.shape[:2]
                # Check if frame size matches video size
                if height != original_height or width != original_width:
                    # If there's a difference, use frame size
                    original_width = width
                    original_height = height
                    print("Frame size differs from video size, using frame size information")
            
            # Release temporary camera
            temp_cap.release()
            
            # Calculate aspect ratio
            aspect_ratio = original_width / original_height
            
            # Determine video orientation
            # Vertical ratio less than 0.8, horizontal ratio greater than 1.3, middle value is square
            is_vertical = aspect_ratio < 0.8
            
            # If it's a vertical video
            if is_vertical:
                print(f"Detected vertical video (aspect ratio: {aspect_ratio:.2f}, size: {original_width}x{original_height})")
                self.rotate = False  # No rotation
                # Set display resolution
                self.display_width = max(720, original_width)
                self.display_height = int(self.display_width * original_height / original_width)
                # Set inference resolution
                self.inference_width = max(360, original_width)
                self.inference_height = int(self.inference_width * original_height / original_width)
            # Otherwise it's a horizontal video
            else:
                print(f"Detected horizontal video (aspect ratio: {aspect_ratio:.2f}, size: {original_width}x{original_height})")
                self.rotate = False  # Also no rotation
                # Set display resolution
                self.display_height = 720
                self.display_width = int(self.display_height * aspect_ratio)
                # Set inference resolution
                self.inference_height = 480
                self.inference_width = int(self.inference_height * aspect_ratio)
        except Exception as e:
            print(f"Video aspect ratio detection error: {str(e)}")
            # Use default values when error occurs
            self.rotate = False
    
    def run(self):
        """Main thread loop"""
        # Open video source based on mode (camera or file)
        if self.is_camera:
            if not self._open_best_camera_capture():
                print(f"Error: Cannot open camera {self.camera_id}")
                return
            
            actual_fps = self.cap.get(cv2.CAP_PROP_FPS)
            print(
                f"Camera opened: ID={self.camera_id}, "
                f"display_resolution={int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}, "
                f"reported_fps={actual_fps:.1f}"
            )
        else:
            # Open video file
            if not os.path.exists(self.video_file):
                print(f"Error: Video file does not exist {self.video_file}")
                return
                
            self.cap = cv2.VideoCapture(self.video_file)
            if not self.cap.isOpened():
                print(f"Error: Cannot open video file {self.video_file}")
                return
                
            video_name = os.path.basename(self.video_file)
            print(f"Video file opened: {video_name}, resolution={int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}")
            
            # Get actual frame rate (may differ from requested)
            real_fps = int(self.cap.get(cv2.CAP_PROP_FPS))
            if real_fps == 0:
                real_fps = 30  # Default value
            
            # Limit maximum frame rate to 30fps
            self.fps = min(real_fps, 30)
            print(f"Frame rate: original {real_fps}fps, current display {self.fps}fps")
        
        # Initialize FPS calculation
        read_frame_count = 0
        emitted_frame_count = 0
        stats_start = time.perf_counter()
        fps_display = 0
        last_emit_time = 0
        last_stats_log_time = 0
        emit_interval = 1 / max(self.max_emit_fps, 1)
        
        # Run flag
        while self._run_flag:
            ret, frame = self.cap.read()
            if ret:
                now = time.perf_counter()
                read_frame_count += 1
                stats_elapsed = now - stats_start
                if stats_elapsed >= 1.0:
                    read_fps = read_frame_count / stats_elapsed
                    fps_display = emitted_frame_count / stats_elapsed
                    if self.is_camera and self.debug_camera_stats and now - last_stats_log_time >= 5.0:
                        print(f"Camera stats: read_fps={read_fps:.1f}, emit_fps={fps_display:.1f}")
                        last_stats_log_time = now
                    read_frame_count = 0
                    emitted_frame_count = 0
                    stats_start = now

                if self.is_camera:
                    if now - last_emit_time < emit_interval:
                        continue
                    if not self._try_mark_frame_pending():
                        continue
                # 创建两个版本的帧：高分辨率用于显示，低分辨率用于推理
                if self.is_camera:
                    display_frame = frame.copy()
                    if not self._logged_frame_shape:
                        raw_h, raw_w = frame.shape[:2]
                        print(f"Camera frame: raw={raw_w}x{raw_h}, using full frame")
                        self._logged_frame_shape = True
                else:
                    display_frame = frame.copy()
                
                # 对显示帧应用旋转（如果需要）
                if self.rotate:
                    display_frame = cv2.rotate(display_frame, cv2.ROTATE_90_CLOCKWISE)
                
                # 对显示帧应用镜像（如果需要）
                if self.mirror:
                    display_frame = cv2.flip(display_frame, 1)
                inference_frame = self._resize_for_inference(display_frame)
                
                # 将推理帧存储在主窗口中，供模型使用
                # Send display frame and FPS information
                emitted_frame_count += 1
                last_emit_time = now
                self.change_pixmap_signal.emit(display_frame, inference_frame, fps_display)
            else:
                # When reading video file fails, if in video file mode
                if not self.is_camera and self.video_file:
                    # Check if loop playback is needed
                    if self.loop_video:
                        # Loop mode: reset to beginning and continue playback
                        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        ret, frame = self.cap.read()
                        if ret:
                            # Send frame and FPS information
                            inference_frame = self._resize_for_inference(frame)
                            self.change_pixmap_signal.emit(frame, inference_frame, fps_display)
                        else:
                            # If reset still cannot read, output warning
                            print("Warning: Video file playback ended and cannot loop again")
                            self.video_ended = True
                    else:
                        # Non-loop mode: mark video as ended
                        if not self.video_ended:
                            print("Video playback completed, stopped at last frame")
                            self.video_ended = True
                else:
                    print("Warning: Cannot read video frame")
            
            # Camera reads are already paced by hardware/driver. Extra sleeping
            # here can cut live camera FPS far below the requested value.
            if not self.is_camera:
                time.sleep(1 / self.fps)
        
        # Release resources
        self.cap.release()
    
    def stop(self):
        """Stop thread"""
        self._run_flag = False
        self.wait()
