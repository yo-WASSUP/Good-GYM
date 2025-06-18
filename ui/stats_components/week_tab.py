from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QGridLayout, QTableWidgetItem)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

from .base_components import StyledGroupBox, DayCircleIndicator, StyledStatsTable
from core.translations import Translations as T

class WeekStatsTab(QWidget):
    """Weekly statistics tab"""
    
    def __init__(self, exercise_name_map, exercise_colors, parent=None):
        super().__init__(parent)
        self.exercise_name_map = exercise_name_map
        self.exercise_colors = exercise_colors
        
        # Save last exercise data
        self.last_exercise_data = {}
        
        # Setup layout
        self.setup_ui()
        
    def setup_ui(self):
        """Setup UI components"""
        layout = QVBoxLayout(self)
        
        # Create weekly statistics component
        self.week_group = StyledGroupBox(T.get("weekly_progress"))
        week_layout = QVBoxLayout(self.week_group)
        
        # Create workout days and progress bar
        self.summary_group = StyledGroupBox(T.get("weekly_workout_days"))
        summary_layout = QGridLayout(self.summary_group)
        
        # Add labels
        self.day_label = QLabel(T.get("days_per_week") + ":")
        self.day_label.setStyleSheet("font-family: 'Microsoft YaHei'; font-size: 16px; font-weight: bold;")
        summary_layout.addWidget(self.day_label, 0, 0)
        self.week_days_label = QLabel("0 / 7")
        self.week_days_label.setStyleSheet("color: #27ae60; font-family: 'Microsoft YaHei'; font-size: 16px; font-weight: bold;")  # Use green font
        summary_layout.addWidget(self.week_days_label, 0, 1)
        
        self.progress_label = QLabel(T.get("weekly_progress") + ":")
        self.progress_label.setStyleSheet("font-family: 'Microsoft YaHei'; font-size: 16px; font-weight: bold;")
        summary_layout.addWidget(self.progress_label, 1, 0)
        
        # Add 7 circle progress indicators
        self.week_circle_indicator = DayCircleIndicator(
            active_color="#27ae60",    # Completed circles use green
            inactive_color="#bdc3c7", # Unstarted circles use gray
            partial_color="#a5ebc8"    # Partially completed circles use light green
        )
        summary_layout.addWidget(self.week_circle_indicator, 1, 1)
        
        week_layout.addWidget(self.summary_group)
        
        # Weekly exercise statistics table
        self.stats_group = StyledGroupBox(T.get("week_stats"))
        stats_layout = QVBoxLayout(self.stats_group)
        
        # Create data table - note we update headers in update_language
        self.table_headers = [T.get("exercise_type"), T.get("count_completed")]
        self.week_stats_table = StyledStatsTable(self.table_headers)
        stats_layout.addWidget(self.week_stats_table)
        
        week_layout.addWidget(self.stats_group)
        
        # Add to main layout
        layout.addWidget(self.week_group)

    def update_language(self, exercise_name_map=None, exercise_code_map=None):
        """Update interface language"""
        if exercise_name_map:
            self.exercise_name_map = exercise_name_map
            
        # Update component titles
        self.week_group.setTitle(T.get("weekly_progress"))
        self.summary_group.setTitle(T.get("weekly_workout_days"))
        self.stats_group.setTitle(T.get("week_stats"))
        
        # Update label text
        self.day_label.setText(T.get("days_per_week") + ":")
        self.progress_label.setText(T.get("weekly_progress") + ":")
        
        # Update table headers
        self.table_headers = [T.get("exercise_type"), T.get("count_completed")]
        for col, header in enumerate(self.table_headers):
            self.week_stats_table.setHorizontalHeaderItem(col, QTableWidgetItem(header))
        
        # If there's saved data, use it directly to refill the table
        if hasattr(self, 'last_exercise_data') and self.last_exercise_data:
            self.week_stats_table.setRowCount(len(self.last_exercise_data))
            row = 0
            for exercise_code, count in self.last_exercise_data.items():
                if exercise_code in self.exercise_name_map:
                    # Update exercise name
                    exercise_name = self.exercise_name_map[exercise_code]
                    name_item = QTableWidgetItem(exercise_name)
                    color = self.exercise_colors.get(exercise_name, "#3498db")
                    name_item.setBackground(QColor(color).lighter(180))
                    self.week_stats_table.setItem(row, 0, name_item)
                    
                    # Add count
                    count_item = QTableWidgetItem(str(count))
                    count_item.setTextAlignment(Qt.AlignCenter)
                    self.week_stats_table.setItem(row, 1, count_item)
                    
                    row += 1
    
    def update_stats(self, stats, goals):
        """Update weekly statistics data"""
        try:
            # Save original data for language switching recovery
            self.last_stats = stats
            self.last_goals = goals
            
            # Update workout days
            days_worked_out = stats.get("days_worked_out", 0)
            weekly_goal = goals["weekly"]["total_workouts"]
            self.week_days_label.setText(f"{days_worked_out} / {weekly_goal}")
            
            # Get daily goal completion status
            daily_goals = goals.get("daily", {})
            weekday_data = stats.get("weekday_data", {})
            
            if daily_goals and weekday_data:
                # Initialize completion status array for each day, Monday to Sunday
                # 0=not started, 1=partially completed, 2=fully completed
                day_status = [0, 0, 0, 0, 0, 0, 0]
                
                # Iterate through Monday to Sunday
                for weekday, day_info in weekday_data.items():
                    day_exercises = day_info["exercises"]
                    
                    if not day_exercises:  # Skip if no exercise data
                        continue
                    
                    # Filter valid goals (not 0)
                    valid_goals = {ex: count for ex, count in daily_goals.items() if count > 0}
                    total_goal_exercises = len(valid_goals)
                    
                    if total_goal_exercises == 0:
                        continue  # Skip dates without goals
                    
                    # Count exercises that meet goals
                    completed_exercises = 0
                    has_partial = False
                    
                    # Count completion status for different exercises
                    completed = []
                    partial_completed = []
                    
                    for ex, goal_count in valid_goals.items():
                        actual_count = day_exercises.get(ex, 0)  # Actually completed count
                        
                        if actual_count >= goal_count:
                            completed_exercises += 1  # This exercise meets goal
                            completed.append(f"{ex}({actual_count}/{goal_count})")
                        elif actual_count > 0:
                            has_partial = True  # Partially completed this exercise
                            partial_completed.append(f"{ex}({actual_count}/{goal_count})")
                    
                    # Set status for the day
                    if completed_exercises == total_goal_exercises:
                        day_status[int(weekday)] = 2  # Fully completed
                    elif completed_exercises > 0 or has_partial:
                        day_status[int(weekday)] = 1  # Partially completed
                
            # Set circle progress (in weekday order)
            self.week_circle_indicator.setDayStatus(day_status)
            
            # Update exercise statistics table
            exercise_stats = stats.get("exercises", {})
            self.week_stats_table.setRowCount(0)  # Clear existing data
            
            # If there's exercise data
            if exercise_stats:
                row = 0
                self.week_stats_table.setRowCount(len(exercise_stats))
                
                # Clear and resave data
                self.last_exercise_data = {}
                
                for exercise_code, count in exercise_stats.items():
                    if exercise_code in self.exercise_name_map:
                        # Save data to dictionary
                        self.last_exercise_data[exercise_code] = count
                        
                        # Exercise type
                        exercise_name = self.exercise_name_map[exercise_code]
                        name_item = QTableWidgetItem(exercise_name)
                        color = self.exercise_colors.get(exercise_name, "#3498db")
                        name_item.setBackground(QColor(color).lighter(180))
                        self.week_stats_table.setItem(row, 0, name_item)
                        
                        # Completion count
                        count_item = QTableWidgetItem(str(count))
                        count_item.setTextAlignment(Qt.AlignCenter)
                        self.week_stats_table.setItem(row, 1, count_item)
                        
                        row += 1
        except Exception as e:
            print(f"更新周统计时出错: {str(e)}")
