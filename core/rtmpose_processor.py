import os
import cv2
import sys
import numpy as np
import json
from rtmlib import Wholebody, draw_skeleton

class RTMPoseProcessor:
    """RTMPose pose detection processor"""
    
    def __init__(self, exercise_counter, mode='balanced', backend='onnxruntime', device='cpu'):
        self.exercise_counter = exercise_counter
        self.show_skeleton = True
        self.conf_threshold = 0.5
        self.device = device
        self.backend = backend
        self.wholebody = None
        
        # Initialize RTMPose model
        self.init_rtmpose(mode)
        
        self.keypoint_mapping = self.get_keypoint_mapping()
        
        # Load exercise configurations for angle points
        self.exercise_configs = self.load_exercise_configs()
    
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
        self.current_mode = mode
        self.wholebody = None
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
            raise RuntimeError(f"RTMPose initialization failed: {e}") from e

    def get_keypoint_mapping(self):
        """Get keypoint mapping (COCO 17 keypoint format)"""
        # RTMPose and YOLO both use COCO 17 keypoint format, same order
        # 0: nose, 1: left_eye, 2: right_eye, 3: left_ear, 4: right_ear
        # 5: left_shoulder, 6: right_shoulder, 7: left_elbow, 8: right_elbow
        # 9: left_wrist, 10: right_wrist, 11: left_hip, 12: right_hip
        # 13: left_knee, 14: right_knee, 15: left_ankle, 16: right_ankle
        return list(range(17))  # 1:1 mapping
    
    def get_exercises_file_path(self):
        """Get exercises.json file path, compatible with development and packaged environments"""
        if getattr(sys, 'frozen', False):
            # Packaged environment
            # First check for external data folder next to exe (user editable)
            exe_dir = os.path.dirname(sys.executable)
            external_file = os.path.join(exe_dir, 'data', 'exercises.json')
            if os.path.exists(external_file):
                return external_file
            # Fall back to bundled data inside exe
            base_path = sys._MEIPASS
            exercises_file = os.path.join(base_path, 'data', 'exercises.json')
        else:
            # Development environment, data files are in project directory
            exercises_file = os.path.join('data', 'exercises.json')
        
        return exercises_file
    
    def load_exercise_configs(self):
        """Load exercise configurations from JSON file"""
        exercises_file = self.get_exercises_file_path()
        
        try:
            if os.path.exists(exercises_file):
                with open(exercises_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    exercises = data.get('exercises', {})
                    
                    # Extract angle_point for each exercise
                    configs = {}
                    for exercise_type, config in exercises.items():
                        configs[exercise_type] = {
                            'angle_point': config.get('angle_point', [])
                        }
                    
                    return configs
            else:
                print(f"ERROR: Exercises file not found at {exercises_file}")
                print("Please ensure data/exercises.json exists")
                return {}
        except Exception as e:
            print(f"ERROR loading exercises from JSON: {e}")
            return {}
    
    def update_model(self, mode='balanced'):
        """Update model"""
        print(f"Updating RTMPose model to mode: {mode}")
        self.init_rtmpose(mode)
        print(f"RTMPose processor updated to mode: {mode}")

    def update_device(self, device):
        """Update inference device (cpu or cuda)"""
        print(f"Updating RTMPose device: {self.device} -> {device}")
        self.device = device
        self.init_rtmpose(self.current_mode)
        print(f"RTMPose processor updated to device: {device}")
    
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
        
        # Initialize results
        current_angle = None
        angle_point = None
        keypoints = None
        if self.wholebody is None:
            return None, current_angle, angle_point, keypoints
        
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
                
                # Get corresponding angle and joint points based on exercise type
                current_angle, angle_point = self.get_exercise_angle(keypoints, exercise_type)
            
        except Exception as e:
            print(f"RTMPose processing failed: {e}")
        
        # Return None for processed frame, current_angle, angle_point, and keypoints
        return None, current_angle, angle_point, keypoints
    
    def get_exercise_angle(self, keypoints, exercise_type):
        """Get angle based on exercise type"""
        current_angle = None
        angle_point = None
        
        try:
            # Get the counting method based on exercise type
            count_method_map = {
                "squat": self.exercise_counter.count_squat,
                "pushup": self.exercise_counter.count_pushup,
                "situp": self.exercise_counter.count_situp,
                "bicep_curl": self.exercise_counter.count_bicep_curl,
                "lateral_raise": self.exercise_counter.count_lateral_raise,
                "overhead_press": self.exercise_counter.count_overhead_press,
                "leg_raise": self.exercise_counter.count_leg_raise,
                "knee_raise": self.exercise_counter.count_knee_raise,
                "knee_press": self.exercise_counter.count_knee_press,
                "crunch": self.exercise_counter.count_crunch,
                "pullup": self.exercise_counter.count_pullup
            }
            
            # Get counting method
            count_method = count_method_map.get(exercise_type)
            if count_method:
                current_angle = count_method(keypoints)
                
                # Get angle_point from config
                if current_angle is not None and exercise_type in self.exercise_configs:
                    angle_point_indices = self.exercise_configs[exercise_type].get('angle_point', [])
                    if len(angle_point_indices) == 3:
                        angle_point = [
                            keypoints[angle_point_indices[0]],
                            keypoints[angle_point_indices[1]],
                            keypoints[angle_point_indices[2]]
                        ]
        except Exception as e:
            print(f"Error calculating exercise angle: {e}")
            
        return current_angle, angle_point
    
    def set_skeleton_visibility(self, show):
        """Set skeleton display state"""
        self.show_skeleton = show
        print(f"RTMPose skeleton display: {'On' if show else 'Off'}") 
