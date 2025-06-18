import cv2
import numpy as np
import time
import os
from PyQt5.QtCore import Qt, QThread, pyqtSignal

class VideoThread(QThread):
    """Video stream processing thread to avoid UI freezing"""
    change_pixmap_signal = pyqtSignal(np.ndarray, float)  # Add FPS parameter
    
    def __init__(self, camera_id=0, width=640, height=480, rotate=True):
        super().__init__()
        self.camera_id = camera_id
        self.width = width
        self.height = height
        self.rotate = rotate
        self._run_flag = True
        self.buffer_size = 1  # Buffer size, set to 1 to avoid delay
        self.video_file = None  # Local video file path
        self.is_camera = True  # Whether to use camera
        self.fps = 30  # Default frame rate
        self.loop_video = False  # Control whether to loop video playback
        self.video_ended = False  # Mark if video has ended
    
    def set_camera(self, camera_id):
        """Switch camera"""
        if self.isRunning():
            self._run_flag = False
            self.wait()
        self.camera_id = camera_id
        self.video_file = None  # Clear video file path
        self.is_camera = True  # Switch back to camera mode
        self._run_flag = True
        self.start()
    
    def set_rotation(self, rotate):
        """Set whether to rotate video"""
        self.rotate = rotate
        
    def set_resolution(self, width, height):
        """Set resolution"""
        self.width = width
        self.height = height
        
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
            
            # If it's a vertical video (9:16)
            if is_vertical:
                print(f"Detected vertical video (aspect ratio: {aspect_ratio:.2f}, size: {original_width}x{original_height})")
                self.rotate = False  # No rotation
                # Set width to half of original height, maintain professional vertical display
                self.width = max(360, original_width)  # Ensure minimum width
                self.height = int(self.width * original_height / original_width)
            # Otherwise it's a horizontal video (16:9)
            else:
                print(f"Detected horizontal video (aspect ratio: {aspect_ratio:.2f}, size: {original_width}x{original_height})")
                self.rotate = False  # Also no rotation
                # Adjust size to maintain horizontal display
                self.height = 360  # Fixed height
                self.width = int(self.height * aspect_ratio)  # Calculate width based on original aspect ratio
        except Exception as e:
            print(f"Video aspect ratio detection error: {str(e)}")
            # Use default values when error occurs
            self.rotate = False
        except Exception as e:
            print(f"Video aspect ratio detection error: {str(e)}")
            # Keep original settings when error occurs
    
    def run(self):
        """Main thread loop"""
        # Open video source based on mode (camera or file)
        if self.is_camera:
            self.cap = cv2.VideoCapture(self.camera_id)
            if not self.cap.isOpened():
                print(f"Error: Cannot open camera {self.camera_id}")
                return
                
            # Set resolution and buffer (only applicable to camera)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, self.buffer_size)
            
            # Camera mode defaults to rotation (default to portrait mode)
            self.rotate = True
            
            print(f"Camera opened: ID={self.camera_id}, resolution={int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}")
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
        frame_count = 0
        start_time = time.time()
        fps_display = 0
        update_interval = 10  # Update FPS display every 10 frames
        
        # Run flag
        while self._run_flag:
            ret, frame = self.cap.read()
            if ret:
                # Downsample to smaller size for processing
                frame = cv2.resize(frame, (self.width, self.height))
                
                # If rotation is needed (portrait mode)
                if self.rotate:
                    # Rotate 90 degrees to get 9:16 ratio (use INTER_NEAREST to speed up rotation)
                    frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
                
                # Calculate FPS
                frame_count += 1
                if frame_count % update_interval == 0:
                    end_time = time.time()
                    elapsed_time = end_time - start_time
                    fps_display = frame_count / elapsed_time
                    frame_count = 0
                    start_time = time.time()
                
                # Send frame and FPS information
                self.change_pixmap_signal.emit(frame, fps_display)
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
                            self.change_pixmap_signal.emit(frame, fps_display)
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
            
            # Read frames at target frame rate and control playback speed
            time.sleep(1/self.fps)  # Limit to specified frame rate
        
        # Release resources
        self.cap.release()
    
    def stop(self):
        """Stop thread"""
        self._run_flag = False
        self.wait()
