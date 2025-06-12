import numpy as np
from collections import deque
import time

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
        
        # Independent counting for leg exercises
        self.leg_exercises = ['leg_raise', 'knee_raise', 'knee_press']
        self.leg_stages = {'left': None, 'right': None}  # Track each leg's stage
    
    def get_exercise_configs(self):
        """Exercise-specific angle thresholds"""
        return {
            'squat': {
                'down_angle': 110,
                'up_angle': 160,
                'keypoints': {
                    'left': [11, 13, 15],  # hip, knee, ankle
                    'right': [12, 14, 16]  # hip, knee, ankle
                }
            },
            'pushup': {
                'down_angle': 110,
                'up_angle': 160,
                'keypoints': {
                    'left': [5, 7, 9],    # shoulder, elbow, wrist
                    'right': [6, 8, 10]   # shoulder, elbow, wrist
                }
            },
            'situp': {
                'down_angle': 145,
                'up_angle': 170,
                'keypoints': {
                    'left': [5, 11, 15],  # shoulder, hip, ankle
                    'right': [6, 12, 16]  # shoulder, hip, ankle
                }
            },
            'bicep_curl': {
                'down_angle': 160,
                'up_angle': 60,
                'keypoints': {
                    'left': [5, 7, 9],    # shoulder, elbow, wrist
                    'right': [6, 8, 10]   # shoulder, elbow, wrist
                }
            },
            'lateral_raise': {
                'down_angle': 30,
                'up_angle': 80,
                'keypoints': {
                    'left': [11, 5, 7],    # hip, shoulder, elbow
                    'right': [12, 6, 8]   # hip, shoulder, elbow
                }
            },
            'overhead_press': {
                'down_angle': 30,
                'up_angle': 150,
                'keypoints': {
                    'left': [11, 5, 7],    # hip, shoulder, elbow
                    'right': [12, 6, 8]   # hip, shoulder, elbow
                }
            },
            'leg_raise': {
                'down_angle': 130,
                'up_angle': 160,
                'keypoints': {
                    'left': [5, 11, 13],  # shoulder, hip, knee
                    'right': [6, 12, 14]  # shoulder, hip, knee
                }
            },
            'knee_raise': {
                'down_angle': 110,
                'up_angle': 160,
                'keypoints': {
                    'left': [11, 13, 15],  # hip, knee, ankle
                    'right': [12, 14, 16]  # hip, knee, ankle
                }
            },
            'knee_press': {
                'down_angle': 110,
                'up_angle': 160,
                'keypoints': {
                    'left': [11, 13, 15],  # hip, knee, ankle
                    'right': [12, 14, 16]  # hip, knee, ankle
                }
            }
        }
    
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
            
            # Counting logic with timing check
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
        
        # Check if either leg meets the criteria
        if self.check_rep_timing():
            # Left leg
            if left_angle > up_threshold:
                self.leg_stages['left'] = "up"
            elif (left_angle < down_threshold and 
                  self.leg_stages['left'] == "up"):
                self.counter += 1
                self.last_count_time = time.time()
                self.leg_stages['left'] = "down"
            
            # Right leg
            if right_angle > up_threshold:
                self.leg_stages['right'] = "up"
            elif (right_angle < down_threshold and 
                  self.leg_stages['right'] == "up"):
                self.counter += 1
                self.last_count_time = time.time()
                self.leg_stages['right'] = "down"
        
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
