from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTabWidget,
                             QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal
import datetime
import json
import os
import sys

from core.translations import Translations as T

from .stats_components.today_tab import TodayProgressTab
from .stats_components.week_tab import WeekStatsTab
from .stats_components.month_tab import MonthStatsTab
from .stats_components.goals_tab import GoalsTab
from .styles import AppStyles

class WorkoutStatsPanel(QWidget):
    """Fitness statistics and planning panel"""
    
    # Define signals
    goal_updated = pyqtSignal(str, int)  # Exercise type, goal value
    weekly_goal_updated = pyqtSignal(int)  # Weekly workout days
    month_changed = pyqtSignal(int, int)  # Year, month
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.exercise_colors = AppStyles.EXERCISE_COLORS
        
        # Use translation module to generate exercise name mappings from JSON file
        self.update_exercise_mappings()
        
        # Initialize UI
        self.setup_ui()
    
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
    
    def update_exercise_mappings(self):
        """Update exercise name mappings from JSON file"""
        exercises_file = self.get_exercises_file_path()
        
        try:
            if os.path.exists(exercises_file):
                with open(exercises_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    exercises = data.get('exercises', {})
                    
                    # Build exercise_name_map from JSON file
                    exercise_map = {}
                    current_lang = T.get_language()  # Get current language setting
                    
                    for exercise_type, config in exercises.items():
                        # Get display name from JSON file based on current language
                        if current_lang == 'zh':
                            display_name = config.get('name_zh', '')
                        elif current_lang == 'en':
                            display_name = config.get('name_en', '')
                        elif current_lang == 'ru':
                            display_name = config.get('name_ru', '')
                        else:
                            # Fallback to English if language not supported
                            display_name = config.get('name_en', '')
                        
                        # If name not found in JSON, try translation module as fallback
                        if not display_name:
                            display_name = T.get(exercise_type)
                        
                        if display_name:
                            exercise_map[exercise_type] = display_name
                    
                    if exercise_map:
                        self.exercise_name_map = exercise_map
                        self.exercise_code_map = {v: k for k, v in self.exercise_name_map.items()}
                        return
                    else:
                        print(f"WARNING: No exercises found in {exercises_file}")
                        self.exercise_name_map = {}
                        self.exercise_code_map = {}
                        return
            
            # File not found
            print(f"ERROR: Exercises file not found at {exercises_file}")
            print("Please ensure data/exercises.json exists")
            self.exercise_name_map = {}
            self.exercise_code_map = {}
        except Exception as e:
            print(f"ERROR loading exercises from JSON: {e}")
            self.exercise_name_map = {}
            self.exercise_code_map = {}
    
    def setup_ui(self):
        """Setup UI components"""
        self.layout = QVBoxLayout(self)
        
        # Create top title
        self.title_label = QLabel(T.get("fitness_statistics"))
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("color: #2c3e50; font-size: 20pt; font-weight: bold; margin: 15px 0; padding: 10px;")
        self.layout.addWidget(self.title_label)
        
        # Create tabs
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.North)
        self.tabs.setTabShape(QTabWidget.Rounded)
        self.tabs.setStyleSheet("""
            QTabWidget::pane { 
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                padding: 15px; 
                background-color: #f8f9fa;
            }
            QTabBar::tab {
                background-color: #ecf0f1; 
                border: 1px solid #bdc3c7;
                border-bottom: none;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
                padding: 10px 20px;
                margin-right: 3px;
                font-family: 'Microsoft YaHei';
                font-size: 16px;
                font-weight: bold;
                min-width: 150px;
            }
            QTabBar::tab:selected {
                background-color: #f8f9fa;
                border-bottom: 2px solid #3498db;
                color: #2980b9;
            }
            QTabBar::tab:hover:!selected {
                background-color: #e0e0e0;
            }
        """)
        
        # Create statistics components
        self.today_progress_tab = TodayProgressTab(self.exercise_name_map, self.exercise_colors)
        self.week_stats_tab = WeekStatsTab(self.exercise_name_map, self.exercise_colors)
        self.month_stats_tab = MonthStatsTab(self.exercise_name_map, self.exercise_colors)
        self.goals_tab = GoalsTab(self.exercise_name_map, self.exercise_colors)
        
        # Connect goal update signals
        self.goals_tab.goal_updated.connect(self.goal_updated)
        self.goals_tab.weekly_goal_updated.connect(self.weekly_goal_updated)
        
        # Connect month change signal
        self.month_stats_tab.month_changed.connect(self._on_month_changed)
        
        # Add tabs
        self.tabs.addTab(self.today_progress_tab, T.get("today_tab"))
        self.tabs.addTab(self.week_stats_tab, T.get("week_tab"))
        self.tabs.addTab(self.month_stats_tab, T.get("month_tab"))
        self.tabs.addTab(self.goals_tab, T.get("goals_tab"))
        
        # Set default tab to "Today's Progress"
        self.tabs.setCurrentIndex(0)
        
        self.layout.addWidget(self.tabs)
        
    def update_today_stats(self, stats, goals):
        """Update today's statistics data"""
        if "exercises" in stats:
            for exercise_code, data in stats["exercises"].items():
                if exercise_code in self.today_progress_tab.progress_bars:
                    current = data.get("count", 0)
                    goal = goals["daily"].get(exercise_code, 0)
                    self.today_progress_tab.update_progress(exercise_code, current, goal)
            
            # Update total
            total_count = sum(data.get("count", 0) for data in stats["exercises"].values())
            self.today_progress_tab.update_total(total_count)
    
    def update_week_stats(self, stats, goals):
        """Update weekly statistics data"""
        self.week_stats_tab.update_stats(stats, goals)
    
    def update_month_stats(self, stats, goals):
        """Update monthly statistics data"""
        self.month_stats_tab.update_stats(stats, goals)
    
    def set_goals(self, goals):
        """Set goal values"""
        self.goals_tab.set_goals(goals)
        
        # Pass daily goals to today's progress tab to show exercise items with goals
        if hasattr(self.today_progress_tab, 'show_exercises_with_goals') and 'daily' in goals:
            self.today_progress_tab.show_exercises_with_goals(goals['daily'])
    
    def _on_month_changed(self, year, month):
        # Emit signal to notify main application that data for specified month is needed
        self.month_changed.emit(year, month)
    
    def update_language(self):
        """Update interface language"""
        # Update title
        self.title_label.setText(T.get("workout_stats_panel"))
        
        # Update exercise name mappings
        self.update_exercise_mappings()
        
        # Update tab titles
        self.tabs.setTabText(0, T.get("today_progress"))
        self.tabs.setTabText(1, T.get("week_stats"))
        self.tabs.setTabText(2, T.get("month_stats"))
        self.tabs.setTabText(3, T.get("fitness_goals"))
        
        # If each tab has update_language method, call it
        if hasattr(self.today_progress_tab, 'update_language'):
            self.today_progress_tab.update_language(self.exercise_name_map, self.exercise_code_map)
            
        if hasattr(self.week_stats_tab, 'update_language'):
            self.week_stats_tab.update_language(self.exercise_name_map)
            
        if hasattr(self.month_stats_tab, 'update_language'):
            self.month_stats_tab.update_language(self.exercise_name_map)
            
        if hasattr(self.goals_tab, 'update_language'):
            self.goals_tab.update_language(self.exercise_name_map)