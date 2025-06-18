from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QFrame, QScrollArea, QSizePolicy, QProgressBar)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

from .base_components import StyledGroupBox
from core.translations import Translations as T

class TodayProgressTab(QWidget):
    """Today's progress tab"""
    
    def __init__(self, exercise_name_map, exercise_colors, parent=None):
        super().__init__(parent)
        self.exercise_name_map = exercise_name_map
        self.exercise_colors = exercise_colors
        
        # Initialize component reference dictionary
        self.progress_bars = {}
        self.count_labels = {}
        self.exercise_frames = {}
        self.exercise_name_labels = {}
        self.exercise_layouts = {}
        
        # Setup layout
        self.setup_ui()
        
        # Hide all exercise items by default, wait for goal setting to display
        self.hide_all_exercises()
        
    def setup_ui(self):
        """Setup UI components"""
        layout = QVBoxLayout(self)
        
        # Create today's progress component
        self.progress_group = StyledGroupBox(T.get("today_exercise_progress"))
        progress_layout = QVBoxLayout(self.progress_group)
        progress_layout.setContentsMargins(15, 20, 15, 15)  # Increase group box padding
        
        # Create message label to display when no goals are set
        self.no_goals_label = QLabel(T.get("no_goals_message") if hasattr(T, "get") and callable(getattr(T, "get")) else "No exercise goals set")
        self.no_goals_label.setAlignment(Qt.AlignCenter)
        self.no_goals_label.setStyleSheet("color: #7f8c8d; font-size: 16pt; margin: 20px;")
        self.no_goals_label.setVisible(False)  # Hidden by default, wait for goal check to decide display
        progress_layout.addWidget(self.no_goals_label)
        
        # Create scroll area and content container
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                width: 14px;
                background: #f0f0f0;
                margin: 2px;
                border-radius: 7px;
            }
            QScrollBar::handle:vertical {
                background: #bdc3c7;
                min-height: 40px;
                border-radius: 7px;
            }
            QScrollBar::handle:vertical:hover {
                background: #a0a0a0;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        
        # Create container widget to place progress items
        container_widget = QWidget()
        container_layout = QVBoxLayout(container_widget)
        container_layout.setSpacing(20)  # Significantly increase spacing between items
        container_layout.setContentsMargins(10, 10, 15, 10)  # Increase global padding
        
        # Create progress bar for each exercise type
        for i, (exercise_code, exercise_name) in enumerate(self.exercise_name_map.items()):
            # Get exercise color
            color = self.exercise_colors.get(exercise_name, "#3498db")
            
            # Create separator line with spacing from previous item (except first item)
            if i > 0:
                separator = QFrame()
                separator.setFrameShape(QFrame.HLine)
                separator.setFrameShadow(QFrame.Sunken)
                separator.setStyleSheet("background-color: #e0e0e0; min-height: 1px; margin: 10px 0;")
                container_layout.addWidget(separator)
            
            # Create exercise item container and record reference
            exercise_frame = QFrame()
            exercise_frame.setObjectName(f"frame_{exercise_code}")
            exercise_frame.setStyleSheet("background-color: transparent;")
            self.exercise_frames[exercise_code] = exercise_frame
            
            # Create vertical layout
            item_layout = QVBoxLayout(exercise_frame)
            item_layout.setSpacing(6)  # Compact element spacing
            item_layout.setContentsMargins(5, 5, 5, 10)  # Appropriate padding
            
            # Save layout reference
            self.exercise_layouts[exercise_code] = item_layout
            
            # Add exercise item container to container layout
            container_layout.addWidget(exercise_frame)
            
            # Title and current count on same line - use QWidget as container
            header_widget = QWidget()
            header_layout = QHBoxLayout(header_widget)
            header_layout.setContentsMargins(0, 0, 0, 0)  # No margins
            header_layout.setSpacing(10)  # Element spacing
            
            # Exercise name label
            label = QLabel(exercise_name)
            label.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 18pt;")
            # Save reference to label
            self.exercise_name_labels[exercise_code] = label
            
            # Count label
            count_label = QLabel("0 / 0")
            count_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            count_label.setStyleSheet("color: #2c3e50; font-size: 18pt;")
            
            # Add label and count to layout
            header_layout.addWidget(label)
            header_layout.addStretch(1)
            header_layout.addWidget(count_label)
            
            # Add header widget to item layout
            item_layout.addWidget(header_widget)
            
            # Progress bar
            progress_bar = QProgressBar()
            progress_bar.setRange(0, 100)
            progress_bar.setValue(0)
            progress_bar.setFormat("%p%")  # Show percentage
            progress_bar.setTextVisible(True)
            progress_bar.setMinimumHeight(22)
            progress_bar.setStyleSheet(f"""
                QProgressBar {{
                    border: 1px solid #bdc3c7;
                    border-radius: 10px;
                    text-align: center;
                    height: 25px;
                    font-family: 'Microsoft YaHei';
                    font-size: 14px;
                    font-weight: bold;
                    color: #2c3e50;
                    background-color: #f5f5f5;
                }}
                QProgressBar::chunk {{
                    background-color: {color};
                    border-radius: 8px;
                }}
            """)
            
            # Add progress bar to item layout
            item_layout.addWidget(progress_bar)
            
            # Note: No need for addLayout here since exercise_frame has already been addWidget to container_layout
            
            # Record references
            self.progress_bars[exercise_code] = progress_bar
            self.count_labels[exercise_code] = count_label
            
        # Add stretch space to ensure content aligns to top
        container_layout.addStretch()
        
        # Set scroll area content
        scroll_area.setWidget(container_widget)
        
        # Set scroll area height limits to ensure it doesn't take up too much space
        scroll_area.setMinimumHeight(380)  # Increase minimum height to show more content
        scroll_area.setMaximumHeight(500)  # Increase maximum height
        
        # Add scroll area to main layout
        progress_layout.addWidget(scroll_area)
        
        # Today's exercise total - use more prominent style
        self.total_group = StyledGroupBox(T.get("today_total"))
        total_layout = QVBoxLayout(self.total_group)
        total_layout.setContentsMargins(15, 20, 15, 15)
        
        # Total label
        total_label = QLabel(T.get("total_completion").format(count=0))
        total_label.setAlignment(Qt.AlignCenter)
        total_label.setStyleSheet("color: #2c3e50; margin: 10px 0; padding: 10px; background-color: #f0f7ff; border-radius: 8px; font-size: 18pt;")
        total_layout.addWidget(total_label)
        
        # Record reference
        self.total_label = total_label
        
        # Add to main layout
        layout.addWidget(self.progress_group, 4)  # Allocate larger stretch factor
        layout.addWidget(self.total_group, 1)  # Allocate smaller stretch factor
        
    def update_progress(self, exercise_code, current, goal):
        """Update exercise progress"""
        if exercise_code in self.progress_bars:
            # If goal is 0, hide this exercise item
            if goal <= 0:
                if exercise_code in self.exercise_frames:
                    self.exercise_frames[exercise_code].setVisible(False)
                return
                
            # Show this exercise item
            if exercise_code in self.exercise_frames:
                self.exercise_frames[exercise_code].setVisible(True)
            
            # Update count label
            self.count_labels[exercise_code].setText(f"{current} / {goal}")
            
            # Update progress bar
            progress = min(100, int((current / goal) * 100)) if goal > 0 else 0
            self.progress_bars[exercise_code].setValue(progress)
            
            # Set progress bar format
            color = self.exercise_colors.get(self.exercise_name_map[exercise_code], "#3498db")
            
            # Update visual feedback based on completion status
            if progress >= 100:
                # Completed state - use success green progress bar
                self.progress_bars[exercise_code].setStyleSheet(f"""
                    QProgressBar {{
                        border: 1px solid #bdc3c7;
                        border-radius: 10px;
                        text-align: center;
                        font-family: 'Microsoft YaHei';
                        font-size: 13px;
                        font-weight: bold;
                        color: #2c3e50;
                        background-color: #f5f5f5;
                    }}
                    QProgressBar::chunk {{
                        background-color: #2ecc71;
                        border-radius: 8px;
                    }}
                """)
            else:
                # In progress state - use original color
                self.progress_bars[exercise_code].setStyleSheet(f"""
                    QProgressBar {{
                        border: 1px solid #bdc3c7;
                        border-radius: 10px;
                        text-align: center;
                        font-family: 'Microsoft YaHei';
                        font-size: 13px;
                        font-weight: bold;
                        color: #2c3e50;
                        background-color: #f5f5f5;
                    }}
                    QProgressBar::chunk {{
                        background-color: {color};
                        border-radius: 8px;
                    }}
                """)
            
    def update_total(self, total_count):
        """Update total"""
        self.total_label.setText(T.get("total_completion").format(count=total_count))
        
    def update_language(self, exercise_name_map=None, exercise_code_map=None):
        """Update interface language"""
        if exercise_name_map:
            self.exercise_name_map = exercise_name_map
            
            # Update color mapping
            new_exercise_colors = {}
            for code, name in self.exercise_name_map.items():
                # Use code directly as key, not name
                if code in self.exercise_colors:
                    new_exercise_colors[name] = self.exercise_colors[code]
                    
            # Update color dictionary
            self.exercise_colors = new_exercise_colors
        
        # Update component titles
        self.progress_group.setTitle(T.get("today_exercise_progress"))
        self.total_group.setTitle(T.get("today_total"))
        
        # Update total label
        total_count = int(self.total_label.text().split(":")[1].strip().split(" ")[0]) if ":" in self.total_label.text() else 0
        self.total_label.setText(T.get("total_completion").format(count=total_count))
        
        # Directly use saved label references to update exercise names
        for exercise_code, label in self.exercise_name_labels.items():
            if exercise_code in self.exercise_name_map:
                exercise_name = self.exercise_name_map[exercise_code]
                color = self.exercise_colors.get(exercise_name, "#3498db")
                
                # Update label text and style
                label.setText(exercise_name)
                label.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 18pt;")
    
    def hide_all_exercises(self):
        """Hide all exercise items"""
        for exercise_code in self.exercise_frames:
            self.exercise_frames[exercise_code].setVisible(False)
        
        # Show no goals prompt
        self.no_goals_label.setVisible(True)
    
    def show_exercises_with_goals(self, goals):
        """Show exercise items with goals"""
        has_visible_exercises = False
        
        for exercise_code, exercise_frame in self.exercise_frames.items():
            goal = goals.get(exercise_code, 0)
            if goal > 0:
                exercise_frame.setVisible(True)
                has_visible_exercises = True
                
                # Update count label to show goal value
                if exercise_code in self.count_labels:
                    self.count_labels[exercise_code].setText(f"0 / {goal}")
            else:
                exercise_frame.setVisible(False)
        
        # Decide whether to show prompt based on whether there are visible exercise items
        self.no_goals_label.setVisible(not has_visible_exercises)
    
    def reset_progress(self):
        """Reset all progress"""
        for exercise_code in self.progress_bars:
            self.progress_bars[exercise_code].setValue(0)
            
            # Get current label's goal value part
            current_text = self.count_labels[exercise_code].text()
            goal_part = current_text.split("/")[1].strip() if "/" in current_text else "0"
            
            # Reset counter display, keep goal value
            self.count_labels[exercise_code].setText(f"0 / {goal_part}")
            
            # Reset progress bar style
            color = self.exercise_colors.get(self.exercise_name_map[exercise_code], "#3498db")
            self.progress_bars[exercise_code].setStyleSheet(f"""
                QProgressBar {{
                    border: 1px solid #bdc3c7;
                    border-radius: 10px;
                    text-align: center;
                    font-family: 'Microsoft YaHei';
                    font-size: 13px;
                    font-weight: bold;
                    color: #2c3e50;
                    background-color: #f5f5f5;
                }}
                QProgressBar::chunk {{
                    background-color: {color};
                    border-radius: 8px;
                }}
            """)
        
        self.total_label.setText(T.get("total_completion").format(count=0))
