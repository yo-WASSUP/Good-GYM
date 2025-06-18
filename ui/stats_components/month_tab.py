from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QGridLayout, QTableWidgetItem, QPushButton)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor
import datetime
import calendar

from .base_components import StyledGroupBox, MonthCalendarIndicator, StyledStatsTable
from core.translations import Translations as T

class MonthStatsTab(QWidget):
    """Monthly statistics tab"""
    
    # Define signals
    month_changed = pyqtSignal(int, int)  # Emit signal when month changes (year, month)
    
    def __init__(self, exercise_name_map, exercise_colors, parent=None):
        super().__init__(parent)
        self.exercise_name_map = exercise_name_map
        self.exercise_colors = exercise_colors
        
        # Save last exercise data
        self.last_exercise_data = {}
        
        # Current displayed year and month
        self.current_date = datetime.date.today()
        self.current_year = self.current_date.year
        self.current_month = self.current_date.month
        
        # Maximum allowed year/month range for viewing
        self.min_date = datetime.date(self.current_date.year - 1, 1, 1)  # Can view previous year
        self.max_date = self.current_date  # Can only view up to current month
        
        # Setup layout
        self.setup_ui()
        
    def setup_ui(self):
        """Setup UI components"""
        layout = QVBoxLayout(self)
        
        # Create monthly statistics component
        self.month_group = StyledGroupBox(T.get("monthly_progress"))
        month_layout = QVBoxLayout(self.month_group)
        
        # Get current month days
        days_in_month = self._get_days_in_month()
        
        # Create month navigation component
        month_nav_widget = QWidget()
        month_nav_layout = QHBoxLayout(month_nav_widget)
        
        # Previous month button
        self.prev_month_btn = QPushButton("←")
        self.prev_month_btn.setStyleSheet("""
            QPushButton { 
                font-size: 16px; 
                padding: 5px 10px; 
                background-color: #ecf0f1; 
                border: 1px solid #bdc3c7; 
                border-radius: 4px; 
            }
            QPushButton:hover { background-color: #d6dbdf; }
            QPushButton:pressed { background-color: #bdc3c7; }
        """)
        self.prev_month_btn.setFixedWidth(40)
        self.prev_month_btn.clicked.connect(self.go_to_previous_month)
        month_nav_layout.addWidget(self.prev_month_btn)
        
        # Current month label
        self.month_label = QLabel(self.get_month_display_text())
        self.month_label.setAlignment(Qt.AlignCenter)
        self.month_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2980b9;")
        month_nav_layout.addWidget(self.month_label, 1)
        
        # Next month button
        self.next_month_btn = QPushButton("→")
        self.next_month_btn.setStyleSheet("""
            QPushButton { 
                font-size: 16px; 
                padding: 5px 10px; 
                background-color: #ecf0f1; 
                border: 1px solid #bdc3c7; 
                border-radius: 4px; 
            }
            QPushButton:hover { background-color: #d6dbdf; }
            QPushButton:pressed { background-color: #bdc3c7; }
        """)
        self.next_month_btn.setFixedWidth(40)
        self.next_month_btn.clicked.connect(self.go_to_next_month)
        month_nav_layout.addWidget(self.next_month_btn)
        
        # Add month navigation to layout
        month_layout.addWidget(month_nav_widget)
        
        # Create summary component
        self.summary_group = StyledGroupBox(T.get("monthly_stats"))
        summary_layout = QGridLayout(self.summary_group)
        
        # Add labels
        self.day_label = QLabel(T.get("monthly_stats") + ":")
        self.day_label.setStyleSheet("font-family: 'Microsoft YaHei'; font-size: 16px; font-weight: bold;")
        summary_layout.addWidget(self.day_label, 0, 0)
        
        self.month_days_label = QLabel("0 / 0")
        self.month_days_label.setStyleSheet("color: #27ae60; font-family: 'Microsoft YaHei'; font-size: 16px; font-weight: bold;")  # Use red font
        summary_layout.addWidget(self.month_days_label, 0, 1)
        
        # Add calendar indicator
        self.month_calendar_indicator = MonthCalendarIndicator(
            days_in_month=self._get_days_in_month(),
            active_color="#27ae60",     # Completed dates use green
            inactive_color="#bdc3c7",  # Unstarted dates use gray
            partial_color="#a5ebc8"     # Partially completed dates use light green
        )
        
        # Calculate which weekday the first day of current month is
        today = datetime.date.today()
        first_day_weekday = datetime.date(today.year, today.month, 1).weekday()
        self.month_calendar_indicator.setMonthStart(first_day_weekday)
        
        # Add to layout
        summary_layout.addWidget(self.month_calendar_indicator, 1, 0, 1, 2)
        
        month_layout.addWidget(self.summary_group)
        
        # Monthly exercise statistics table
        self.stats_group = StyledGroupBox(T.get("monthly_stats"))
        stats_layout = QVBoxLayout(self.stats_group)
        
        # Create data table - note we update headers in update_language
        self.table_headers = [T.get("exercise_type"), T.get("count_completed")]
        self.month_stats_table = StyledStatsTable(self.table_headers)
        stats_layout.addWidget(self.month_stats_table)
        
        month_layout.addWidget(self.stats_group)
        
        # Add to main layout
        layout.addWidget(self.month_group)
    
    def _get_days_in_month(self, year=None, month=None):
        """Get number of days in specified year/month. Default gets current selected month days"""
        if year is None:
            year = self.current_year
        if month is None:
            month = self.current_month
            
        return calendar.monthrange(year, month)[1]
        
    def get_month_display_text(self):
        """Get month display text"""
        # Chinese month names
        chinese_months = ["\u4e00\u6708", "\u4e8c\u6708", "\u4e09\u6708", "\u56db\u6708", "\u4e94\u6708", 
                          "\u516d\u6708", "\u4e03\u6708", "\u516b\u6708", "\u4e5d\u6708", "\u5341\u6708", 
                          "\u5341\u4e00\u6708", "\u5341\u4e8c\u6708"]
        
        # English month names
        english_months = ["January", "February", "March", "April", "May", "June",
                         "July", "August", "September", "October", "November", "December"]
                         
        current_lang = T.current_language
        month_name = chinese_months[self.current_month - 1] if current_lang == "zh" else english_months[self.current_month - 1]
        
        return f"{self.current_year} {month_name}"
    
    def go_to_previous_month(self):
        """Switch to previous month"""
        # Calculate previous month date
        if self.current_month == 1:
            new_year = self.current_year - 1
            new_month = 12
        else:
            new_year = self.current_year
            new_month = self.current_month - 1
            
        # Create new date object
        new_date = datetime.date(new_year, new_month, 1)
        
        # Check if exceeds minimum boundary
        if new_date < self.min_date:
            return  # Don't allow viewing too old data
            
        # Update current selected year/month
        self.current_year = new_year
        self.current_month = new_month
        self.current_date = new_date
        
        # Update month display
        self.update_month_display()
        
        # Emit signal - use year and month as two integer parameters
        self.month_changed.emit(self.current_year, self.current_month)
        
    def go_to_next_month(self):
        """Switch to next month"""
        # Calculate next month date
        if self.current_month == 12:
            new_year = self.current_year + 1
            new_month = 1
        else:
            new_year = self.current_year
            new_month = self.current_month + 1
            
        # Create new date object
        new_date = datetime.date(new_year, new_month, 1)
        
        # Check if exceeds maximum boundary
        if new_date > self.max_date:
            return  # Don't allow viewing future data
            
        # Update current selected year/month
        self.current_year = new_year
        self.current_month = new_month
        self.current_date = new_date
        
        # Update month display
        self.update_month_display()
        
        # Emit signal - use year and month as two integer parameters
        self.month_changed.emit(self.current_year, self.current_month)
        
    def update_month_display(self):
        """Update month display information"""
        # Update month label
        self.month_label.setText(self.get_month_display_text())
        
        # Update month days
        days_in_month = self._get_days_in_month()
        
        # Calculate which weekday the first day of selected month is
        first_day_weekday = datetime.date(self.current_year, self.current_month, 1).weekday()
        self.month_calendar_indicator.setDaysInMonth(days_in_month)
        self.month_calendar_indicator.setMonthStart(first_day_weekday)
        
        # Enable/disable navigation buttons
        prev_date = datetime.date(self.current_year, self.current_month, 1)
        if self.current_month == 1:
            prev_date = datetime.date(self.current_year - 1, 12, 1)
        self.prev_month_btn.setEnabled(prev_date >= self.min_date)
        
        next_date = datetime.date(self.current_year, self.current_month, 1)
        if self.current_month == 12:
            next_date = datetime.date(self.current_year + 1, 1, 1)
        self.next_month_btn.setEnabled(next_date <= self.max_date)
        
    def update_language(self, exercise_name_map=None, exercise_code_map=None):
        """Update interface language"""
        if exercise_name_map:
            self.exercise_name_map = exercise_name_map
            
        # Update component titles
        self.month_group.setTitle(T.get("monthly_progress"))
        self.summary_group.setTitle(T.get("monthly_stats"))
        self.stats_group.setTitle(T.get("monthly_stats"))
        
        # Update label text
        self.day_label.setText(T.get("monthly_stats") + ":")
        
        # Update table headers
        self.table_headers = [T.get("exercise_type"), T.get("count_completed")]
        for col, header in enumerate(self.table_headers):
            self.month_stats_table.setHorizontalHeaderItem(col, QTableWidgetItem(header))
        
        # If there's saved data, use it directly to refill the table
        if hasattr(self, 'last_exercise_data') and self.last_exercise_data:
            self.month_stats_table.setRowCount(len(self.last_exercise_data))
            row = 0
            for exercise_code, count in self.last_exercise_data.items():
                if exercise_code in self.exercise_name_map:
                    # Update exercise name
                    exercise_name = self.exercise_name_map[exercise_code]
                    name_item = QTableWidgetItem(exercise_name)
                    color = self.exercise_colors.get(exercise_name, "#3498db")
                    name_item.setBackground(QColor(color).lighter(180))
                    self.month_stats_table.setItem(row, 0, name_item)
                    
                    # Add count
                    count_item = QTableWidgetItem(str(count))
                    count_item.setTextAlignment(Qt.AlignCenter)
                    self.month_stats_table.setItem(row, 1, count_item)
                    
                    row += 1
    
    def update_stats(self, stats, goals):
        """Update monthly statistics data"""
        try:
            # Save original data for language switching recovery
            self.last_stats = stats
            self.last_goals = goals
            
            # Get year/month string prefix for selected month, used for filtering data
            year_month_prefix = f"{self.current_year}-{self.current_month:02d}-"
            
            # Collect selected month data
            filtered_daily_progress = {}
            filtered_exercises = {}
            
            # Daily exercise progress records
            daily_records = stats.get("daily_progress", {})
            # Daily goal data
            daily_goals = goals.get("daily", {})
            
            # Number of days with workout records in current month
            active_days_this_month = 0
            # Collect status for each day
            status_dict = {}
            
            # Filter valid goals (not 0)
            valid_goals = {ex: count for ex, count in daily_goals.items() if count > 0}
            
            # Accumulate exercise data for selected month
            monthly_exercise_data = {}
            
            for date_str, exercises in daily_records.items():
                # Only process data from selected month
                if date_str.startswith(year_month_prefix):
                    # Accumulate all exercise data
                    for exercise_code, count in exercises.items():
                        if exercise_code in monthly_exercise_data:
                            monthly_exercise_data[exercise_code] += count
                        else:
                            monthly_exercise_data[exercise_code] = count
                    
                    # Process daily completion status
                    try:
                        date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")
                        day = date_obj.day  # Get which day of the month
                        
                        # Count as one day regardless of records
                        active_days_this_month += 1
                        
                        # Skip status calculation if no goals set
                        if not valid_goals:
                            continue
                            
                        # Count exercises that meet goals
                        completed_exercises = 0
                        has_partial = False
                        
                        for ex, goal_count in valid_goals.items():
                            actual_count = exercises.get(ex, 0)
                            
                            if actual_count >= goal_count:
                                completed_exercises += 1  # This exercise meets goal
                            elif actual_count > 0:
                                has_partial = True  # Partially completed this exercise
                        
                        # Set status for the day
                        if completed_exercises == len(valid_goals):
                            status_dict[day] = 2  # Fully completed
                        elif completed_exercises > 0 or has_partial:
                            status_dict[day] = 1  # Partially completed
                    except Exception as e:
                        print(f"Error parsing date: {e}")
            
            # Update month days and workout days display
            days_in_month = self._get_days_in_month()
            self.month_days_label.setText(f"{active_days_this_month} / {days_in_month}")
            
            # Update calendar indicator
            self.month_calendar_indicator.setDaysInMonth(days_in_month)
            self.month_calendar_indicator.setMonthStatus(status_dict)
            
            # Update exercise statistics table
            self.month_stats_table.setRowCount(0)  # Clear existing data
            
            # Clear and resave data
            self.last_exercise_data = {}
            
            # If selected month has exercise data
            if monthly_exercise_data:
                self.month_stats_table.setRowCount(len(monthly_exercise_data))
                row = 0
                
                for exercise_code, count in monthly_exercise_data.items():
                    if exercise_code in self.exercise_name_map:
                        # Save data to dictionary for language switching use
                        self.last_exercise_data[exercise_code] = count
                        
                        # Exercise type
                        exercise_name = self.exercise_name_map[exercise_code]
                        name_item = QTableWidgetItem(exercise_name)
                        color = self.exercise_colors.get(exercise_name, "#3498db")
                        name_item.setBackground(QColor(color).lighter(180))
                        self.month_stats_table.setItem(row, 0, name_item)
                        
                        # Completion count
                        count_item = QTableWidgetItem(str(count))
                        count_item.setTextAlignment(Qt.AlignCenter)
                        self.month_stats_table.setItem(row, 1, count_item)
                        
                        row += 1
        except Exception as e:
            print(f"Error updating monthly statistics: {str(e)}")
