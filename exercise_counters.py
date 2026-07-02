import numpy as np
from collections import deque
import time
import json
import os
import sys

class ExerciseCounter:
    """Basic exercise counter with angle-based detection"""
    
    def __init__(self, smoothing_window=5):
        # Core counting variables
        self.counter = 0
        self.stage = None
        
        # Basic features
        self.smoothing_window = smoothing_window
        self.angle_history = deque(maxlen=smoothing_window)
        self.last_count_time = 0
        self.min_rep_time = 0.5  # Minimum time between reps (seconds)
        
        # Exercise configurations
        self.exercise_configs = self.get_exercise_configs()
        
        # Independent counting for leg exercises - load from config
        self.leg_exercises = [
            exercise_type for exercise_type, config in self.exercise_configs.items()
            if config.get('is_leg_exercise', False)
        ]
        self.leg_stages = {'left': None, 'right': None}  # Track each leg's stage
    
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
    
    def get_exercise_configs(self):
        """Load exercise-specific angle thresholds from JSON file"""
        exercises_file = self.get_exercises_file_path()
        
        try:
            if os.path.exists(exercises_file):
                with open(exercises_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    exercises = data.get('exercises', {})
                    
                    # Convert to the format expected by the rest of the code
                    configs = {}
                    for exercise_type, config in exercises.items():
                        configs[exercise_type] = {
                            'down_angle': config.get('down_angle'),
                            'up_angle': config.get('up_angle'),
                            'keypoints': config.get('keypoints', {}),
                            'is_leg_exercise': config.get('is_leg_exercise', False),
                            'angle_direction': config.get('angle_direction')
                        }
                    
                    print(f"Loaded {len(configs)} exercises from {exercises_file}")
                    return configs
            else:
                print(f"ERROR: Exercises file not found at {exercises_file}")
                print("Please ensure data/exercises.json exists")
                return {}
        except Exception as e:
            print(f"ERROR loading exercises from JSON: {e}")
            return {}
    
    def reset_counter(self):
        """Reset counter to initial state"""
        self.counter = 0
        self.stage = None
        self.angle_history.clear()
        self.leg_stages = {'left': None, 'right': None}
    
    def calculate_angle(self, a, b, c):
        """Calculate angle between three points"""
        try:
            a = np.array(a, dtype=np.float64)
            b = np.array(b, dtype=np.float64)
            c = np.array(c, dtype=np.float64)
            
            # Check for invalid points
            if np.any(np.isnan([a, b, c])) or np.any([a, b, c] == [0, 0]):
                return None
            
            # Calculate vectors
            ba = a - b
            bc = c - b
            
            # Check for zero vectors
            ba_norm = np.linalg.norm(ba)
            bc_norm = np.linalg.norm(bc)
            
            if ba_norm == 0 or bc_norm == 0:
                return None
            
            # Calculate angle using dot product
            cosine_angle = np.dot(ba, bc) / (ba_norm * bc_norm)
            cosine_angle = np.clip(cosine_angle, -1.0, 1.0)  # Prevent numerical errors
            angle = np.arccos(cosine_angle)
            
            return np.degrees(angle)
            
        except Exception as e:
            print(f"Angle calculation error: {e}")
            return None
    
    def smooth_angle(self, angle):
        """Apply smoothing to reduce noise"""
        if angle is None:
            return None
            
        self.angle_history.append(angle)
        
        if len(self.angle_history) < 3:
            return angle
            
        # Use median filter to remove outliers, then average
        angles_array = np.array(list(self.angle_history))
        median_angle = np.median(angles_array)
        
        # Remove outliers (angles > 2 std devs from median)
        std_dev = np.std(angles_array)
        filtered_angles = angles_array[np.abs(angles_array - median_angle) <= 2 * std_dev]
        
        return np.mean(filtered_angles) if len(filtered_angles) > 0 else angle
    
    def check_rep_timing(self):
        """Prevent counting reps too quickly"""
        current_time = time.time()
        if current_time - self.last_count_time < self.min_rep_time:
            return False
        return True
    
    def get_angle_direction(self, config):
        """Infer movement direction when old exercise configs do not specify it."""
        direction = config.get('angle_direction')
        if direction in ('increasing', 'decreasing'):
            return direction
        return 'decreasing' if config['up_angle'] < config['down_angle'] else 'increasing'
    
    def count_exercise(self, keypoints, exercise_type):
        """Generic exercise counting function"""
        try:
            if exercise_type not in self.exercise_configs:
                print(f"Unknown exercise type: {exercise_type}")
                return None
                
            config = self.exercise_configs[exercise_type]
            kp = config['keypoints']
            
            # Calculate angles for both sides
            left_angle = self.calculate_angle(
                keypoints[kp['left'][0]],  # first point
                keypoints[kp['left'][1]],  # middle point
                keypoints[kp['left'][2]]   # last point
            )
            
            right_angle = self.calculate_angle(
                keypoints[kp['right'][0]],  # first point
                keypoints[kp['right'][1]],  # middle point
                keypoints[kp['right'][2]]   # last point
            )
            
            if left_angle is None or right_angle is None:
                return None
            
            # Handle leg exercises differently
            if exercise_type in self.leg_exercises:
                return self.count_leg_exercise(left_angle, right_angle, config)
            
            # For other exercises, use average angle
            avg_angle = (left_angle + right_angle) / 2
            smoothed_angle = self.smooth_angle(avg_angle)
            
            if smoothed_angle is None:
                return None
            
            # Get thresholds
            up_threshold = config['up_angle']
            down_threshold = config['down_angle']
            direction = self.get_angle_direction(config)
            
            # Counting logic with timing check
            if direction == 'decreasing':
                if smoothed_angle > down_threshold:
                    self.stage = "down"
                elif (smoothed_angle < up_threshold and 
                      self.stage == "down" and 
                      self.check_rep_timing()):
                    
                    self.stage = "up"
                    self.counter += 1
                    self.last_count_time = time.time()
            else:
                if smoothed_angle > up_threshold:
                    self.stage = "up"
                elif (smoothed_angle < down_threshold and 
                      self.stage == "up" and 
                      self.check_rep_timing()):
                    
                    self.stage = "down"
                    self.counter += 1
                    self.last_count_time = time.time()
                
            return smoothed_angle
            
        except Exception as e:
            print(f"Exercise counting error: {e}")
            return None
    
    def count_leg_exercise(self, left_angle, right_angle, config):
        """Count leg exercises with complete up-down cycles"""
        up_threshold = config['up_angle']
        down_threshold = config['down_angle']
        direction = self.get_angle_direction(config)
        
        # Check if either leg meets the criteria
        if self.check_rep_timing():
            # Left leg
            if direction == 'decreasing':
                left_ready = left_angle > down_threshold
                left_counted = left_angle < up_threshold and self.leg_stages['left'] == "down"
            else:
                left_ready = left_angle > up_threshold
                left_counted = left_angle < down_threshold and self.leg_stages['left'] == "up"
            
            if left_ready:
                self.leg_stages['left'] = "down" if direction == 'decreasing' else "up"
            elif left_counted:
                self.counter += 1
                self.last_count_time = time.time()
                self.leg_stages['left'] = "up" if direction == 'decreasing' else "down"
            
            # Right leg
            if direction == 'decreasing':
                right_ready = right_angle > down_threshold
                right_counted = right_angle < up_threshold and self.leg_stages['right'] == "down"
            else:
                right_ready = right_angle > up_threshold
                right_counted = right_angle < down_threshold and self.leg_stages['right'] == "up"
            
            if right_ready:
                self.leg_stages['right'] = "down" if direction == 'decreasing' else "up"
            elif right_counted:
                self.counter += 1
                self.last_count_time = time.time()
                self.leg_stages['right'] = "up" if direction == 'decreasing' else "down"
        
        # Return average angle for display purposes
        return (left_angle + right_angle) / 2
    
    # Wrapper functions for different exercises
    def count_squat(self, keypoints):
        """Count squat repetitions"""
        return self.count_exercise(keypoints, 'squat')
    
    def count_pushup(self, keypoints):
        """Count pushup repetitions"""
        return self.count_exercise(keypoints, 'pushup')
    
    def count_situp(self, keypoints):
        """Count situp repetitions"""
        return self.count_exercise(keypoints, 'situp')
    
    def count_bicep_curl(self, keypoints):
        """Count bicep curl repetitions"""
        return self.count_exercise(keypoints, 'bicep_curl')
    
    def count_lateral_raise(self, keypoints):
        """Count lateral raise repetitions"""
        return self.count_exercise(keypoints, 'lateral_raise')
    
    def count_overhead_press(self, keypoints):
        """Count overhead press repetitions"""
        return self.count_exercise(keypoints, 'overhead_press')
    
    def count_leg_raise(self, keypoints):
        """Count leg raise repetitions"""
        return self.count_exercise(keypoints, 'leg_raise')
    
    def count_knee_raise(self, keypoints):
        """Count knee raise repetitions"""
        return self.count_exercise(keypoints, 'knee_raise')
    
    def count_knee_press(self, keypoints):
        """Count knee press repetitions"""
        return self.count_exercise(keypoints, 'knee_press')
    
    def count_crunch(self, keypoints):
        """Count crunch repetitions"""
        return self.count_exercise(keypoints, 'crunch')
    
    def count_pullup(self, keypoints):
        """Count pullup repetitions"""
        return self.count_exercise(keypoints, 'pullup')
