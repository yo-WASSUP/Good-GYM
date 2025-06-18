import os
import json
import datetime
import sys
from collections import defaultdict

class WorkoutTracker:
    """Fitness record tracker, responsible for storing and managing daily exercise data"""
    
    def __init__(self):
        # Determine data storage path
        self.data_dir = self._get_data_directory()
        self.data_file = os.path.join(self.data_dir, "workout_history.json")
        
        # Create data directory (if it doesn't exist)
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize data
        self.workout_history = self.load_history()
        self.workout_goals = self.load_goals()
        
    def _get_data_directory(self):
        """Get data directory path, compatible with development and packaged environments"""
        if getattr(sys, 'frozen', False):
            # Packaged environment
            # First try the data folder in the same directory as the exe file
            exe_dir = os.path.dirname(sys.executable)
            external_data_dir = os.path.join(exe_dir, "data")
            
            if os.path.exists(external_data_dir):
                print(f"Using external data directory: {external_data_dir}")
                return external_data_dir
            else:
                # If external data directory doesn't exist, create it in the same directory as exe
                print(f"Creating external data directory: {external_data_dir}")
                return external_data_dir
        else:
            # Development environment, use data folder under project directory
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            data_dir = os.path.join(base_dir, "data")
            print(f"Using development environment data directory: {data_dir}")
            return data_dir
        
    def load_history(self):
        """Load historical fitness data"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Failed to load historical data: {e}")
                return self._create_default_history()
        else:
            return self._create_default_history()
    
    def _create_default_history(self):
        """Create default historical data structure"""
        return {
            "daily_records": {},
            "last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def load_goals(self):
        """Load fitness goal data"""
        goals_file = os.path.join(self.data_dir, "workout_goals.json")
        if os.path.exists(goals_file):
            try:
                with open(goals_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return self._create_default_goals()
        else:
            return self._create_default_goals()
    
    def _create_default_goals(self):
        """Create default goal data structure"""
        return {
            "daily": {
                "squat": 20,
                "pushup": 30,
                "situp": 30,
                "bicep_curl": 15,
                "lateral_raise": 15,
                "overhead_press": 15,
                "leg_raise": 15,
                "knee_raise": 15,
                "knee_press": 15
            },
            "weekly": {
                "total_workouts": 5  # Planned workout days per week
            }
        }
    
    def save_history(self):
        """Save historical fitness data"""
        self.workout_history["last_updated"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.workout_history, f, ensure_ascii=False, indent=2)
    
    def save_goals(self):
        """Save fitness goal data"""
        goals_file = os.path.join(self.data_dir, "workout_goals.json")
        with open(goals_file, 'w', encoding='utf-8') as f:
            json.dump(self.workout_goals, f, ensure_ascii=False, indent=2)
    
    def add_workout_record(self, exercise_type, count):
        """Add single workout record"""
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        
        # Ensure date record exists
        if today not in self.workout_history["daily_records"]:
            self.workout_history["daily_records"][today] = {}
        
        # Update exercise count
        if exercise_type in self.workout_history["daily_records"][today]:
            self.workout_history["daily_records"][today][exercise_type] += count
        else:
            self.workout_history["daily_records"][today][exercise_type] = count
        
        # Save updated data
        self.save_history()
        
        # Check if goal is reached
        return self.check_goal_reached(exercise_type)
    
    def get_today_stats(self):
        """Get today's fitness statistics"""
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        if today in self.workout_history["daily_records"]:
            return self.workout_history["daily_records"][today]
        return {}
    
    def get_weekly_stats(self):
        """Get this week's fitness statistics (by natural week)"""
        # Get current date
        today = datetime.datetime.now()
        
        # Calculate this week's start (Monday) and end (Sunday)
        # weekday(): Monday is 0, Sunday is 6
        current_weekday = today.weekday()
        week_start = today - datetime.timedelta(days=current_weekday)  # This week's Monday
        week_start = datetime.datetime(week_start.year, week_start.month, week_start.day)  # Reset to start of day
        
        week_end = week_start + datetime.timedelta(days=6)  # This week's Sunday
        week_end = datetime.datetime(week_end.year, week_end.month, week_end.day, 23, 59, 59)  # Set to end of day
        
        # Initialize statistics
        stats = defaultdict(int)
        days_worked_out = 0
        daily_progress = {}
        
        # Iterate through historical records
        for date_str, exercises in self.workout_history["daily_records"].items():
            # Parse date
            record_date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
            
            # Check if within this week (Monday to Sunday)
            if week_start <= record_date <= week_end:

                # Count days with records
                days_worked_out += 1
                
                # Add daily progress data
                daily_progress[date_str] = exercises
                
                # Accumulate count for each exercise type
                for exercise, count in exercises.items():
                    stats[exercise] += count
        
        # Create 7-day structured data, sorted by weekday
        weekday_data = {}
        for i in range(7):  # 0=Monday, 6=Sunday
            day_date = week_start + datetime.timedelta(days=i)
            day_str = day_date.strftime("%Y-%m-%d")
            day_name = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][i]
            
            # Find data for this day
            exercises_data = self.workout_history["daily_records"].get(day_str, {})
            
            weekday_data[i] = {
                "date": day_str,
                "day_name": day_name,
                "exercises": exercises_data
            }
        
        return {
            "exercises": dict(stats),
            "days_worked_out": days_worked_out,
            "daily_progress": daily_progress,  # Original daily progress data
            "weekday_data": weekday_data     # New data sorted by weekday
        }
    
    def get_monthly_stats(self, year=None, month=None):
        """Get fitness statistics for specified month
        
        Args:
            year: Year, defaults to current year
            month: Month, defaults to current month
            
        Returns:
            Dictionary containing monthly statistics
        """
        # If year/month not specified, use current year/month
        if year is None or month is None:
            today = datetime.datetime.now()
            year = today.year
            month = today.month
        
        # Get first day of specified month
        first_day = datetime.datetime(year, month, 1)
        
        # Find first day of next month, then subtract one day to get last day of current month
        if month == 12:
            next_month = datetime.datetime(year+1, 1, 1)
        else:
            next_month = datetime.datetime(year, month+1, 1)
        last_day = next_month - datetime.timedelta(days=1)
        
        # Initialize statistics
        stats = defaultdict(int)
        days_worked_out = 0
        daily_progress = {}
        
        # Iterate through historical records
        for date_str, exercises in self.workout_history["daily_records"].items():
            # Parse date
            try:
                record_date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
                
                # Check if within current month
                if first_day <= record_date <= last_day:
                    # Count days with records
                    days_worked_out += 1
                    
                    # Add daily progress data
                    daily_progress[date_str] = exercises
                    
                    # Accumulate count for each exercise type
                    for exercise, count in exercises.items():
                        stats[exercise] += count
            except ValueError as e:
                print(f"  Date format error: {date_str} - {e}")
        
        return {
            "exercises": dict(stats),
            "days_worked_out": days_worked_out,
            "daily_progress": daily_progress  # Add detailed daily progress data
        }
    
    def update_goal(self, exercise_type, count):
        """Update single exercise goal"""
        self.workout_goals["daily"][exercise_type] = count
        self.save_goals()
    
    def update_weekly_goal(self, count):
        """Update weekly workout days goal"""
        self.workout_goals["weekly"]["total_workouts"] = count
        self.save_goals()
    
    def check_goal_reached(self, exercise_type):
        """Check if goal is reached (returns completion percentage)"""
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        if today not in self.workout_history["daily_records"] or exercise_type not in self.workout_history["daily_records"][today]:
            return 0
        
        current = self.workout_history["daily_records"][today][exercise_type]
        goal = self.workout_goals["daily"].get(exercise_type, 0)
        
        if goal <= 0:
            return 100  # Prevent division by zero error
        
        percentage = min(100, int((current / goal) * 100))
        return percentage
    
    def get_goals(self):
        """Get all set goals"""
        return self.workout_goals
