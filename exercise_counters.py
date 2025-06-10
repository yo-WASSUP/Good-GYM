import numpy as np
from collections import deque
import time
import json

class EnhancedExerciseCounter:
    """Enhanced exercise counter with improved accuracy and robustness"""
    
    def __init__(self, smoothing_window=5, confidence_threshold=0.5):
        # Core counting variables
        self.counter = 0
        self.stage = None
        
        # Enhanced features
        self.smoothing_window = smoothing_window
        self.confidence_threshold = confidence_threshold
        self.angle_history = deque(maxlen=smoothing_window)
        self.last_count_time = 0
        self.min_rep_time = 0.5  # Minimum time between reps (seconds)
        
        # Form quality tracking
        self.form_quality = "Good"
        self.quality_score = 100
        self.form_feedback = []
        
        # Exercise-specific tracking
        self.exercise_stats = {
            'total_reps': 0,
            'session_start': time.time(),
            'calories_burned': 0,
            'form_violations': 0,
            'perfect_reps': 0
        }
        
        # Calibration for different body types
        self.user_profile = {
            'height_ratio': 1.0,  # Will be calibrated
            'limb_ratios': {},
            'flexibility_factor': 1.0
        }
        
        # Exercise configurations
        self.exercise_configs = self.get_exercise_configs()
        
    def get_exercise_configs(self):
        """Exercise-specific angle thresholds and parameters"""
        return {
            'squat': {
                'down_angle': 110,
                'up_angle': 160,
                'form_checks': ['knee_alignment', 'back_straight', 'depth_check'],
                'calories_per_rep': 0.5,
                'muscle_groups': ['quadriceps', 'glutes', 'hamstrings']
            },
            'pushup': {
                'down_angle': 100,
                'up_angle': 160,
                'form_checks': ['elbow_flare', 'body_alignment', 'full_range'],
                'calories_per_rep': 0.4,
                'muscle_groups': ['chest', 'triceps', 'shoulders']
            },
            'situp': {
                'down_angle': 45,
                'up_angle': 80,
                'form_checks': ['neck_position', 'core_engagement', 'full_range'],
                'calories_per_rep': 0.3,
                'muscle_groups': ['abs', 'core']
            },
            'bicep_curl': {
                'down_angle': 160,
                'up_angle': 60,
                'form_checks': ['elbow_stability', 'shoulder_position', 'controlled_motion'],
                'calories_per_rep': 0.2,
                'muscle_groups': ['biceps', 'forearms']
            },
            'lateral_raise': {
                'down_angle': 30,
                'up_angle': 80,
                'form_checks': ['shoulder_height', 'controlled_motion', 'elbow_angle'],
                'calories_per_rep': 0.25,
                'muscle_groups': ['deltoids', 'upper_back']
            }
        }
    
    def reset_counter(self):
        """Reset counter with enhanced tracking"""
        self.counter = 0
        self.stage = None
        self.angle_history.clear()
        self.form_feedback.clear()
        self.quality_score = 100
        self.exercise_stats = {
            'total_reps': 0,
            'session_start': time.time(),
            'calories_burned': 0,
            'form_violations': 0,
            'perfect_reps': 0
        }
    
    def calculate_angle(self, a, b, c):
        """Enhanced angle calculation with validation"""
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
            
            # Calculate angle using dot product
            cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
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
    
    def check_keypoint_confidence(self, keypoints, required_points, confidence_scores=None):
        """Check if required keypoints have sufficient confidence"""
        if confidence_scores is None:
            # If no confidence scores, check for zero coordinates
            for idx in required_points:
                if idx < len(keypoints):
                    point = keypoints[idx]
                    if point[0] == 0 and point[1] == 0:
                        return False
            return True
        
        for idx in required_points:
            if idx < len(confidence_scores):
                if confidence_scores[idx] < self.confidence_threshold:
                    return False
        return True
    
    def check_rep_timing(self):
        """Prevent counting reps too quickly"""
        current_time = time.time()
        if current_time - self.last_count_time < self.min_rep_time:
            return False
        return True
    
    def analyze_form_quality(self, exercise_type, keypoints, angle):
        """Analyze form quality and provide feedback"""
        feedback = []
        quality_deductions = 0
        
        if exercise_type not in self.exercise_configs:
            return feedback, 0
            
        config = self.exercise_configs[exercise_type]
        
        try:
            if exercise_type == 'squat':
                # Check knee alignment
                left_knee = keypoints[13]
                right_knee = keypoints[14]
                left_ankle = keypoints[15]
                right_ankle = keypoints[16]
                
                # Knees should track over toes
                knee_ankle_distance_left = abs(left_knee[0] - left_ankle[0])
                knee_ankle_distance_right = abs(right_knee[0] - right_ankle[0])
                
                if knee_ankle_distance_left > 50 or knee_ankle_distance_right > 50:
                    feedback.append("Keep knees aligned over toes")
                    quality_deductions += 10
                
                # Check depth
                if self.stage == "down" and angle > 120:
                    feedback.append("Go deeper for full squat")
                    quality_deductions += 5
                    
            elif exercise_type == 'pushup':
                # Check body alignment
                shoulder = keypoints[6]
                hip = keypoints[12]
                ankle = keypoints[16]
                
                # Calculate body line angle
                body_angle = self.calculate_angle(shoulder, hip, ankle)
                if body_angle and (body_angle < 160 or body_angle > 200):
                    feedback.append("Keep body in straight line")
                    quality_deductions += 15
                    
            elif exercise_type == 'bicep_curl':
                # Check elbow stability
                left_shoulder = keypoints[5]
                right_shoulder = keypoints[6]
                left_elbow = keypoints[7]
                right_elbow = keypoints[8]
                
                # Elbows should stay close to body
                shoulder_center_x = (left_shoulder[0] + right_shoulder[0]) / 2
                elbow_deviation = abs(left_elbow[0] - shoulder_center_x) + abs(right_elbow[0] - shoulder_center_x)
                
                if elbow_deviation > 100:
                    feedback.append("Keep elbows close to body")
                    quality_deductions += 10
                    
        except Exception as e:
            print(f"Form analysis error: {e}")
        
        return feedback, quality_deductions
    
    def count_squat(self, keypoints, confidence_scores=None):
        """Enhanced squat counting with form analysis"""
        required_points = [11, 12, 13, 14, 15, 16]
        
        if not self.check_keypoint_confidence(keypoints, required_points, confidence_scores):
            return None
            
        try:
            # Get keypoints
            left_hip = keypoints[11]
            left_knee = keypoints[13]
            left_ankle = keypoints[15]
            right_hip = keypoints[12]
            right_knee = keypoints[14]
            right_ankle = keypoints[16]
            
            # Calculate angles
            left_angle = self.calculate_angle(left_hip, left_knee, left_ankle)
            right_angle = self.calculate_angle(right_hip, right_knee, right_ankle)
            
            if left_angle is None or right_angle is None:
                return None
            
            # Use average angle with smoothing
            avg_angle = (left_angle + right_angle) / 2
            smoothed_angle = self.smooth_angle(avg_angle)
            
            if smoothed_angle is None:
                return None
            
            # Get thresholds
            config = self.exercise_configs['squat']
            up_threshold = config['up_angle']
            down_threshold = config['down_angle']
            
            # Form analysis
            feedback, quality_deduction = self.analyze_form_quality('squat', keypoints, smoothed_angle)
            self.form_feedback = feedback
            
            # Counting logic with timing check
            if smoothed_angle > up_threshold and both_legs_confidence(left_angle, right_angle, up_threshold):
                self.stage = "up"
            elif (smoothed_angle < down_threshold and 
                  both_legs_confidence(left_angle, right_angle, down_threshold) and 
                  self.stage == "up" and 
                  self.check_rep_timing()):
                
                self.stage = "down"
                self.counter += 1
                self.last_count_time = time.time()
                
                # Update stats
                self.exercise_stats['total_reps'] += 1
                self.exercise_stats['calories_burned'] += config['calories_per_rep']
                
                if quality_deduction == 0:
                    self.exercise_stats['perfect_reps'] += 1
                else:
                    self.exercise_stats['form_violations'] += 1
                
                # Update quality score
                self.quality_score = max(0, self.quality_score - quality_deduction)
                
            return smoothed_angle
            
        except Exception as e:
            print(f"Squat counting error: {e}")
            return None
    
    def count_pushup(self, keypoints, confidence_scores=None):
        """Enhanced pushup counting"""
        required_points = [5, 6, 7, 8, 9, 10]
        
        if not self.check_keypoint_confidence(keypoints, required_points, confidence_scores):
            return None
            
        try:
            # Calculate elbow angles
            left_shoulder = keypoints[5]
            left_elbow = keypoints[7]
            left_wrist = keypoints[9]
            right_shoulder = keypoints[6]
            right_elbow = keypoints[8]
            right_wrist = keypoints[10]
            
            left_angle = self.calculate_angle(left_shoulder, left_elbow, left_wrist)
            right_angle = self.calculate_angle(right_shoulder, right_elbow, right_wrist)
            
            if left_angle is None or right_angle is None:
                return None
            
            avg_angle = (left_angle + right_angle) / 2
            smoothed_angle = self.smooth_angle(avg_angle)
            
            if smoothed_angle is None:
                return None
            
            config = self.exercise_configs['pushup']
            up_threshold = config['up_angle']
            down_threshold = config['down_angle']
            
            # Form analysis
            feedback, quality_deduction = self.analyze_form_quality('pushup', keypoints, smoothed_angle)
            self.form_feedback = feedback
            
            # Counting logic
            if smoothed_angle > up_threshold and both_arms_confidence(left_angle, right_angle, up_threshold):
                self.stage = "up"
            elif (smoothed_angle < down_threshold and 
                  both_arms_confidence(left_angle, right_angle, down_threshold) and 
                  self.stage == "up" and 
                  self.check_rep_timing()):
                
                self.stage = "down"
                self.counter += 1
                self.last_count_time = time.time()
                
                # Update stats
                self.exercise_stats['total_reps'] += 1
                self.exercise_stats['calories_burned'] += config['calories_per_rep']
                
                if quality_deduction == 0:
                    self.exercise_stats['perfect_reps'] += 1
                else:
                    self.exercise_stats['form_violations'] += 1
                
                self.quality_score = max(0, self.quality_score - quality_deduction)
                
            return smoothed_angle
            
        except Exception as e:
            print(f"Pushup counting error: {e}")
            return None
    
    def get_exercise_stats(self):
        """Get comprehensive exercise statistics"""
        session_duration = time.time() - self.exercise_stats['session_start']
        
        stats = {
            'reps': self.counter,
            'total_reps': self.exercise_stats['total_reps'],
            'calories_burned': round(self.exercise_stats['calories_burned'], 2),
            'session_duration': round(session_duration / 60, 2),  # minutes
            'form_quality': self.form_quality,
            'quality_score': self.quality_score,
            'perfect_reps': self.exercise_stats['perfect_reps'],
            'form_violations': self.exercise_stats['form_violations'],
            'form_feedback': self.form_feedback,
            'reps_per_minute': round(self.counter / (session_duration / 60), 1) if session_duration > 0 else 0
        }
        
        return stats
    
    def save_session_data(self, filename):
        """Save session data to file"""
        stats = self.get_exercise_stats()
        try:
            with open(filename, 'w') as f:
                json.dump(stats, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving session data: {e}")
            return False
    
    def calibrate_user_profile(self, keypoints):
        """Calibrate system for user's body proportions"""
        try:
            # Calculate basic body ratios
            if len(keypoints) >= 17:
                # Shoulder width
                shoulder_width = abs(keypoints[5][0] - keypoints[6][0])
                # Hip width  
                hip_width = abs(keypoints[11][0] - keypoints[12][0])
                # Torso length
                torso_length = abs(keypoints[5][1] - keypoints[11][1])
                
                if shoulder_width > 0 and hip_width > 0 and torso_length > 0:
                    self.user_profile['limb_ratios'] = {
                        'shoulder_hip_ratio': shoulder_width / hip_width,
                        'torso_length': torso_length
                    }
                    print("User profile calibrated successfully")
                    
        except Exception as e:
            print(f"Calibration error: {e}")

# Helper functions
def both_legs_confidence(left_angle, right_angle, threshold):
    """Check if both legs meet the threshold with some tolerance"""
    tolerance = 15
    return (abs(left_angle - threshold) < tolerance or 
            abs(right_angle - threshold) < tolerance)

def both_arms_confidence(left_angle, right_angle, threshold):
    """Check if both arms meet the threshold with some tolerance"""
    tolerance = 20
    return (abs(left_angle - threshold) < tolerance or 
            abs(right_angle - threshold) < tolerance)
