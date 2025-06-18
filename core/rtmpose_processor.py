import os
import cv2
import sys
from rtmlib import Wholebody, draw_skeleton

class RTMPoseProcessor:
    """RTMPose pose detection processor"""
    
    def __init__(self, exercise_counter, mode='balanced', backend='onnxruntime', device='cpu'):
        self.exercise_counter = exercise_counter
        self.show_skeleton = True
        self.conf_threshold = 0.5
        self.device = device
        self.backend = backend
        
        # Initialize RTMPose model
        self.init_rtmpose(mode)
        
        self.keypoint_mapping = self.get_keypoint_mapping()
    
    def get_models_dir(self):
        """Get model file directory, compatible with development and packaged environments"""
        if getattr(sys, 'frozen', False):
            # Packaged environment, model files are in temp directory
            base_path = sys._MEIPASS
            models_dir = os.path.join(base_path, 'models')
        else:
            # Development environment, model files are in project directory
            models_dir = './models'
        
        return models_dir
    
    def init_rtmpose(self, mode='balanced'):
        """Initialize RTMPose model"""
        try:
            print(f"Initializing RTMPose model (mode: {mode}, backend: {self.backend}, device: {self.device})")
            
            # Check if local model files exist
            models_dir = self.get_models_dir()
            if os.path.exists(models_dir):
                # Try to use local models
                det_model = os.path.join(models_dir, 'yolox_nano_8xb8-300e_humanart-40f6f0d0.onnx')
                
                # Select different pose detection models based on mode
                if mode == 'lightweight':
                    pose_model = os.path.join(models_dir, 'rtmpose-t_simcc-body7_pt-body7_420e-256x192-026a1439_20230504.onnx')
                    pose_input_size = (192, 256)
                elif mode == 'performance':
                    pose_model = os.path.join(models_dir, 'rtmpose-m_simcc-body7_pt-body7_420e-256x192-e48f03d0_20230504.onnx')
                    pose_input_size = (192, 256)
                else:  # balanced
                    pose_model = os.path.join(models_dir, 'rtmpose-s_simcc-body7_pt-body7_420e-256x192-acd4a1ef_20230504.onnx')
                    pose_input_size = (192, 256)
                
                if os.path.exists(det_model) and os.path.exists(pose_model):
                    print(f"Using local model files ({mode} mode)")
                    self.wholebody = Wholebody(
                        det=det_model,
                        det_input_size=(416, 416),
                        pose=pose_model,
                        pose_input_size=pose_input_size,
                        backend=self.backend,
                        device=self.device
                    )
                    print("RTMPose local model initialization successful")
                    return
                else:
                    print("Local model files incomplete, using online download")
            else:
                print("models directory doesn't exist, using online download")
                self.wholebody = Wholebody(
                    mode=mode,
                    backend=self.backend,
                    device=self.device
                )
                print("RTMPose online model initialization successful")
            
        except Exception as e:
            print(f"RTMPose initialization failed: {e}")

    def get_keypoint_mapping(self):
        """Get keypoint mapping (COCO 17 keypoint format)"""
        # RTMPose and YOLO both use COCO 17 keypoint format, same order
        # 0: nose, 1: left_eye, 2: right_eye, 3: left_ear, 4: right_ear
        # 5: left_shoulder, 6: right_shoulder, 7: left_elbow, 8: right_elbow
        # 9: left_wrist, 10: right_wrist, 11: left_hip, 12: right_hip
        # 13: left_knee, 14: right_knee, 15: left_ankle, 16: right_ankle
        return list(range(17))  # 1:1 mapping
    
    def update_model(self, mode='balanced'):
        """Update model"""
        print(f"Updating RTMPose model to mode: {mode}")
        self.init_rtmpose(mode)
        print(f"RTMPose processor updated to mode: {mode}")
    
    def process_frame(self, frame, exercise_type):
        """Process single frame for pose detection and exercise counting"""
        # Size check, resize if frame is too large
        h, w = frame.shape[:2]
        original_size = (w, h)
        
        # RTMPose is suitable for higher resolution, but limit for performance
        if w > 640 or h > 640:
            scale = min(640/w, 640/h)
            frame = cv2.resize(frame, (int(w*scale), int(h*scale)))
            scale_factor = scale
        else:
            scale_factor = 1.0
        
        # Copy frame to draw on it
        output_frame = frame.copy()
        
        # Initialize results
        current_angle = None
        angle_point = None
        keypoints = None
        
        try:
            # Use RTMPose for pose detection
            detected_keypoints, scores = self.wholebody(frame)
            
            # Process results
            if detected_keypoints is not None and len(detected_keypoints) > 0:
                # Get first person's keypoints (highest confidence)
                keypoints = detected_keypoints[0]  # shape: (17, 2)
                confidence_scores = scores[0] if scores is not None else None
                
                # Filter low confidence keypoints
                if confidence_scores is not None:
                    valid_mask = confidence_scores > self.conf_threshold
                    keypoints[~valid_mask] = [0, 0]  # Set low confidence points to (0,0)
                
                # If need to scale back to original size
                if scale_factor != 1.0:
                    keypoints = keypoints / scale_factor
                    # Also adjust output frame size
                    output_frame = cv2.resize(output_frame, original_size)
                
                # Get corresponding angle and joint points based on exercise type
                current_angle, angle_point = self.get_exercise_angle(keypoints, exercise_type)
                
                # Draw skeleton on image (if enabled)
                if self.show_skeleton:
                    output_frame = self.draw_rtmpose_skeleton(output_frame, keypoints, confidence_scores)
            
        except Exception as e:
            print(f"RTMPose processing failed: {e}")
            # Return original frame when error occurs
            pass
        
        # BGR to RGB (PyQt needs RGB format)
        output_frame = cv2.cvtColor(output_frame, cv2.COLOR_BGR2RGB)
        
        return output_frame, current_angle, keypoints
    
    def get_exercise_angle(self, keypoints, exercise_type):
        """Get angle based on exercise type"""
        current_angle = None
        angle_point = None
        
        try:
            if exercise_type == "squat":
                current_angle = self.exercise_counter.count_squat(keypoints)
                if current_angle is not None:
                    angle_point = [keypoints[12], keypoints[14], keypoints[16]]
            elif exercise_type == "pushup":
                current_angle = self.exercise_counter.count_pushup(keypoints)
                if current_angle is not None:
                    angle_point = [keypoints[6], keypoints[8], keypoints[10]]
            elif exercise_type == "situp":
                current_angle = self.exercise_counter.count_situp(keypoints)
                if current_angle is not None:
                    angle_point = [keypoints[5], keypoints[11], keypoints[12]]
            elif exercise_type == "bicep_curl":
                current_angle = self.exercise_counter.count_bicep_curl(keypoints)
                if current_angle is not None:
                    angle_point = [keypoints[6], keypoints[8], keypoints[10]]
            elif exercise_type == "lateral_raise":
                current_angle = self.exercise_counter.count_lateral_raise(keypoints)
                if current_angle is not None:
                    angle_point = [keypoints[12], keypoints[6], keypoints[8]]
            elif exercise_type == "overhead_press":
                current_angle = self.exercise_counter.count_overhead_press(keypoints)
                if current_angle is not None:
                    angle_point = [keypoints[12], keypoints[6], keypoints[8]]
            elif exercise_type == "leg_raise":
                current_angle = self.exercise_counter.count_leg_raise(keypoints)
                if current_angle is not None:
                    angle_point = [keypoints[12], keypoints[14], keypoints[16]]
            elif exercise_type == "knee_raise":
                current_angle = self.exercise_counter.count_knee_raise(keypoints)
                if current_angle is not None:
                    angle_point = [keypoints[12], keypoints[14], keypoints[16]]
            elif exercise_type == "knee_press":
                current_angle = self.exercise_counter.count_knee_press(keypoints)
                if current_angle is not None:
                    angle_point = [keypoints[11], keypoints[13], keypoints[15]]
        except Exception as e:
            print(f"Error calculating exercise angle: {e}")
            
        return current_angle, angle_point
    
    def draw_rtmpose_skeleton(self, img, keypoints, confidence_scores=None):
        """Draw RTMPose skeleton on image"""
        if keypoints is None or len(keypoints) == 0:
            return img
        
        annotated_frame = img.copy()
        
        # Define connections (COCO 17 keypoint format)
        connections = [
            # Head and face
            [0, 1], [0, 2], [1, 3], [2, 4],  # nose-eyes-ears
            # Torso
            [5, 6],   # left_shoulder-right_shoulder
            [5, 11],  # left_shoulder-left_hip
            [6, 12],  # right_shoulder-right_hip
            [11, 12], # left_hip-right_hip
            # Arms
            [5, 7], [7, 9],    # left_shoulder-left_elbow-left_wrist
            [6, 8], [8, 10],   # right_shoulder-right_elbow-right_wrist
            # Legs
            [11, 13], [13, 15], # left_hip-left_knee-left_ankle
            [12, 14], [14, 16]  # right_hip-right_knee-right_ankle
        ]
        
        # Define colors (BGR format)
        colors = {
            'head': (51, 153, 255),    # Blue
            'torso': (255, 153, 51),   # Orange
            'arms': (153, 255, 51),    # Green
            'legs': (255, 51, 153)     # Pink
        }
        
        # Draw connection lines
        for connection in connections:
            pt1_idx, pt2_idx = connection
            if pt1_idx < len(keypoints) and pt2_idx < len(keypoints):
                pt1 = keypoints[pt1_idx]
                pt2 = keypoints[pt2_idx]
                
                # Skip invalid points
                if (pt1[0] == 0 and pt1[1] == 0) or (pt2[0] == 0 and pt2[1] == 0):
                    continue
                
                # Select color
                if pt1_idx in [0, 1, 2, 3, 4]:  # Head
                    color = colors['head']
                elif pt1_idx in [5, 6, 11, 12]:  # Torso
                    color = colors['torso']
                elif pt1_idx in [7, 8, 9, 10]:  # Arms
                    color = colors['arms']
                else:  # Legs
                    color = colors['legs']
                
                # Draw connection line
                cv2.line(annotated_frame, 
                        (int(pt1[0]), int(pt1[1])), 
                        (int(pt2[0]), int(pt2[1])), 
                        color, 3)
        
        # Draw keypoints
        for i, point in enumerate(keypoints):
            if point[0] == 0 and point[1] == 0:  # Skip invalid points
                continue
                
            # Adjust transparency based on confidence
            alpha = 1.0
            if confidence_scores is not None and i < len(confidence_scores):
                alpha = min(1.0, confidence_scores[i] / self.conf_threshold)
            
            # Select color
            if i in [0, 1, 2, 3, 4]:  # Head
                color = colors['head']
            elif i in [5, 6, 11, 12]:  # Torso
                color = colors['torso']
            elif i in [7, 8, 9, 10]:  # Arms
                color = colors['arms']
            else:  # Legs
                color = colors['legs']
            
            # Apply transparency
            color = tuple(int(c * alpha) for c in color)
            
            # Draw keypoint
            cv2.circle(annotated_frame, (int(point[0]), int(point[1])), 5, color, -1)
            cv2.circle(annotated_frame, (int(point[0]), int(point[1])), 7, color, 2)
        
        return annotated_frame
    
    def set_skeleton_visibility(self, show):
        """Set skeleton display state"""
        self.show_skeleton = show
        print(f"RTMPose skeleton display: {'On' if show else 'Off'}") 