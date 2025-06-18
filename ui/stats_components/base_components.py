from PyQt5.QtWidgets import (QWidget, QLabel, QProgressBar, QTableWidget, 
                             QHeaderView, QFrame, QGroupBox, QVBoxLayout, QHBoxLayout)
from PyQt5.QtCore import Qt, QSize, QRectF
from PyQt5.QtGui import QFont, QColor, QPainter, QPen, QBrush, QPainterPath
import datetime
from ..styles import AppStyles

class StyledGroupBox(QGroupBox):
    """Styled group box component"""
    
    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.setStyleSheet(AppStyles.get_group_box_style() + """
            QGroupBox { 
                font-family: 'Microsoft YaHei';
                font-size: 18px; 
                font-weight: bold;
                padding-top: 25px;
            }
        """)


class StyledProgressBar(QProgressBar):
    """Styled progress bar component"""
    
    def __init__(self, color="#3498db", parent=None):
        super().__init__(parent)
        self.setRange(0, 100)
        self.setValue(0)
        self.setTextVisible(True)
        self.setFormat("%v / 0")  # Don't know target value during initial loading
        self.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid #bdc3c7;
                border-radius: 10px;
                text-align: center;
                height: 25px;
                font-family: 'Microsoft YaHei';
                font-size: 14px;
                font-weight: bold;
                margin-top: 5px;
                margin-bottom: 10px;
                padding: 0px;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 8px;
            }}
        """)


class DayCircleIndicator(QWidget):
    """Custom component with seven circles representing weekly fitness progress"""
    
    def __init__(self, parent=None, days=7, active_color="#3498db", inactive_color="#ecf0f1", 
                 partial_color="#a6dcff"):
        super().__init__(parent)
        self.days = days  # Total days
        
        # Initialize current state
        # 0=not started, 1=partially completed, 2=fully completed
        self.day_status = [0] * self.days
        
        # Color settings
        self.active_color = active_color      # Completed circle color
        self.inactive_color = inactive_color  # Not started circle color
        self.partial_color = partial_color    # Partially completed circle color
        
        # Different weekday labels
        self.day_labels = ["一", "二", "三", "四", "五", "六", "日"]
        
        # Set layout and size
        self.setMinimumHeight(50)
        self.setMaximumHeight(80)
        
    def setDaysProgress(self, completed, partial=0):
        """This is a backward compatibility method that sets progress using numbers
        
        Args:
            completed: Number of fully completed days
            partial: Number of partially completed days
        """
        # Reset all states
        self.day_status = [0] * self.days
        
        # Set completion states, fill from front to back
        for i in range(min(completed, self.days)):
            self.day_status[i] = 2  # Fully completed
            
        # Set partial completion states
        for i in range(completed, min(completed + partial, self.days)):
            self.day_status[i] = 1  # Partially completed
            
        self.update()  # Refresh drawing
        
    def setDayStatus(self, day_status):
        """Set the status for each day
        
        Args:
            day_status: An array of length 7, corresponding to Monday to Sunday status
                       0=not started, 1=partially completed, 2=fully completed
        """
        if len(day_status) != self.days:
            print(f"Warning: Provided status array length ({len(day_status)}) doesn't match expected days ({self.days})")
            return
            
        self.day_status = day_status[:]
        self.update()  # Refresh drawing
        
    def paintEvent(self, event):
        """Draw circles"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)  # Anti-aliasing
        
        # Calculate circle size and spacing
        width = self.width()
        height = self.height()
        circle_diameter = min(height - 20, (width - 20) / self.days)  # Reserve more vertical space
        
        # Adjust to appropriate size
        circle_diameter = min(circle_diameter, 40)  # Maximum diameter 40px
        
        # Calculate starting position to center circles
        margin = (width - (circle_diameter * self.days + (self.days - 1) * 10)) / 2
        
        # Center circles vertically
        y_center = height / 2 - 5  # Slight upward shift to leave space for text description
        
        # Create font
        font = painter.font()
        font.setPointSize(8)
        painter.setFont(font)
        
        # Draw circles and text
        for i in range(self.days):
            x = margin + i * (circle_diameter + 10)  # Horizontal position, including spacing
            circle_rect = QRectF(x, y_center - circle_diameter/2, circle_diameter, circle_diameter)
            
            # Draw circle based on status
            if self.day_status[i] == 2:  # Fully completed
                # Fill circle
                painter.setPen(QPen(QColor(self.active_color), 2))
                painter.setBrush(QBrush(QColor(self.active_color)))
                painter.drawEllipse(circle_rect)
            elif self.day_status[i] == 1:  # Partially completed
                # Draw outer circle
                painter.setPen(QPen(QColor(self.active_color), 2))
                painter.setBrush(Qt.NoBrush)
                painter.drawEllipse(circle_rect)
                
                # Draw half-fill, show half circle at bottom
                painter.setBrush(QBrush(QColor(self.partial_color)))
                path = QPainterPath()
                path.moveTo(circle_rect.center())
                # Draw bottom half circle: start from 180 degrees (left side), scan 180 degrees to 0 degrees (right side)
                path.arcTo(circle_rect, 180, 180)  # Bottom half circle
                path.lineTo(circle_rect.center())
                painter.drawPath(path)
            else:  # Not started
                # Hollow circle
                painter.setPen(QPen(QColor(self.inactive_color), 2))
                painter.setBrush(Qt.NoBrush)
                painter.drawEllipse(circle_rect)
                
            # Add weekday text below circle
            text_rect = QRectF(x, y_center + circle_diameter/2 + 2, circle_diameter, 15)
            painter.setPen(QPen(QColor("#34495e")))
            painter.drawText(text_rect, Qt.AlignCenter, self.day_labels[i])
                
        painter.end()

class MonthCalendarIndicator(QWidget):
    """Calendar-style component displaying monthly fitness progress"""
    
    def __init__(self, parent=None, days_in_month=31, columns=7, 
                 active_color="#27ae60", inactive_color="#ecf0f1", 
                 partial_color="#a5ebc8"):
        super().__init__(parent)
        self.days_in_month = days_in_month  # Days in month
        self.columns = columns  # Calendar columns (usually 7, corresponding to Monday to Sunday)
        
        # Initialize status array (status for each day)
        # 0=not started, 1=partially completed, 2=fully completed
        self.day_status = [0] * (self.days_in_month + 1)  # Index starts from 1, corresponding to date
        
        # Color settings
        self.active_color = active_color      # Completed date color
        self.inactive_color = inactive_color  # Not started date color
        self.partial_color = partial_color    # Partially completed date color
        
        # Set layout and size
        self.setMinimumHeight(180)
        self.setMaximumHeight(250)
        
        # Weekday labels
        self.weekday_labels = ["一", "二", "三", "四", "五", "六", "日"]
        
        # Calculate which weekday the first day of current month is
        today = datetime.date.today()
        self.first_day_weekday = datetime.date(today.year, today.month, 1).weekday()  # 0=Monday, 6=Sunday
    
    def setDaysInMonth(self, days_in_month):
        """Set number of days in month"""
        self.days_in_month = days_in_month
        # Reset status array
        self.day_status = [0] * (days_in_month + 1)  # 0 not used, start from 1
        self.update()  # Trigger redraw
    
    def setMonthStart(self, first_day_weekday):
        """Set which weekday the first day of month is (0=Monday, 6=Sunday)"""
        self.first_day_weekday = first_day_weekday
        self.update()
    
    def setDayStatus(self, day, status):
        """Set status for a specific day
        
        Args:
            day: Which day of the month (1-31)
            status: Status (0=not started, 1=partially completed, 2=fully completed)
        """
        if 1 <= day <= self.days_in_month:
            self.day_status[day] = status
            self.update()
    
    def setMonthStatus(self, status_dict):
        """Set status for entire month
        
        Args:
            status_dict: Dictionary, keys are dates in current month (1-31), values are status (0,1,2)
        """
        # Reset status
        self.day_status = [0] * (self.days_in_month + 1)
        
        # Set status for each day
        for day, status in status_dict.items():
            if 1 <= day <= self.days_in_month:
                self.day_status[day] = status
        
        self.update()
    
    def paintEvent(self, event):
        """Draw calendar-style indicator"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)  # Anti-aliasing
        
        # Calculate size
        width = self.width()
        height = self.height()
        
        # Calculate size of each date cell
        cell_width = width / self.columns
        cell_height = min(cell_width * 0.8, (height - 30) / 6)  # Leave space for weekday labels
        
        # Set fonts
        header_font = painter.font()
        header_font.setPointSize(10)
        header_font.setBold(True)
        
        day_font = painter.font()
        day_font.setPointSize(9)
        
        # Draw weekday labels
        painter.setFont(header_font)
        painter.setPen(QPen(QColor("#34495e")))
        
        for i in range(self.columns):
            x = i * cell_width + cell_width / 2
            text_rect = QRectF(i * cell_width, 0, cell_width, 25)
            painter.drawText(text_rect, Qt.AlignCenter, self.weekday_labels[i])
        
        # Draw dates
        painter.setFont(day_font)
        
        # Calculate number of rows
        rows = (self.days_in_month + self.first_day_weekday - 1) // self.columns + 1
        
        for day in range(1, self.days_in_month + 1):
            # Calculate position of each date in grid
            pos = day + self.first_day_weekday - 1  # Offset
            row = pos // self.columns
            col = pos % self.columns
            
            # Calculate rectangle position
            x = col * cell_width + 2
            y = row * cell_height + 30  # Leave space for weekday labels
            
            # Draw date circle and text
            circle_rect = QRectF(x + 5, y + 2, cell_width - 10, cell_height - 4)
            text_rect = QRectF(x, y, cell_width, cell_height)
            
            # Color based on status
            if self.day_status[day] == 2:  # Fully completed
                # Fill circle
                painter.setPen(QPen(QColor(self.active_color), 1))
                painter.setBrush(QBrush(QColor(self.active_color)))
                painter.drawRoundedRect(circle_rect, 8, 8)  # Rounded rectangle
                
                # Draw date text (white)
                painter.setPen(QPen(QColor("white")))
            elif self.day_status[day] == 1:  # Partially completed
                # Draw outer border
                painter.setPen(QPen(QColor(self.active_color), 1))
                painter.setBrush(Qt.NoBrush)
                painter.drawRoundedRect(circle_rect, 8, 8)  # Rounded rectangle
                
                # Draw half-fill
                half_rect = QRectF(circle_rect.x(), circle_rect.y() + circle_rect.height()/2, 
                                     circle_rect.width(), circle_rect.height()/2)
                painter.setBrush(QBrush(QColor(self.partial_color)))
                painter.drawRoundedRect(half_rect, 0, 0)  # Half-fill rectangle
                
                # Draw date text (dark)
                painter.setPen(QPen(QColor("#333333")))
            else:  # Not started
                # Set light circle
                painter.setPen(QPen(QColor(self.inactive_color), 1))
                painter.setBrush(Qt.NoBrush)
                painter.drawRoundedRect(circle_rect, 8, 8)  # Rounded rectangle
                
                # Draw date text (dark)
                painter.setPen(QPen(QColor("#333333")))
            
            # Draw date text
            painter.drawText(text_rect, Qt.AlignCenter, str(day))
        
        painter.end()


class StyledStatsTable(QTableWidget):
    """Styled statistics table component"""
    
    def __init__(self, columns=None, parent=None):
        super().__init__(parent)
        
        # Set columns
        if columns:
            self.setColumnCount(len(columns))
            self.setHorizontalHeaderLabels(columns)
        
        # Set table behavior
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.setEditTriggers(QTableWidget.NoEditTriggers)
        self.setAlternatingRowColors(True)
        
        # Set style
        self.setStyleSheet("""
            QTableWidget {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                background-color: white;
                font-family: 'Microsoft YaHei';
                font-size: 14px;
            }
            QTableWidget::item {
                padding: 8px;
                min-height: 35px;
            }
            QHeaderView::section {
                background-color: #ecf0f1;
                padding: 10px;
                border: 1px solid #bdc3c7;
                font-weight: bold;
                font-size: 16px;
                min-height: 30px;
            }
        """)
    
    def add_data_row(self, data, exercise_colors=None, row_index=None):
        """Add a row of data to the table"""
        if row_index is None:
            row_index = self.rowCount()
            self.setRowCount(row_index + 1)
        
        # Add data
        for col, value in enumerate(data):
            item = QTableWidget.QTableWidgetItem(str(value))
            
            # Special handling for first column
            if col == 0 and exercise_colors and value in exercise_colors:
                color = exercise_colors.get(value, "#3498db")
                item.setBackground(QColor(color).lighter(180))
            
            # Center alignment
            if col > 0:
                item.setTextAlignment(Qt.AlignCenter)
                
            self.setItem(row_index, col, item)
