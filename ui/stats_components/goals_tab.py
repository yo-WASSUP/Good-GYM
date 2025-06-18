from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QFrame, QSpinBox, QScrollArea, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor

from .base_components import StyledGroupBox
from core.translations import Translations as T

class GoalsTab(QWidget):
    """Goal settings tab"""
    
    # Define signals
    goal_updated = pyqtSignal(str, int)  # Exercise type, goal value
    weekly_goal_updated = pyqtSignal(int)  # Weekly workout days
    
    def __init__(self, exercise_name_map, exercise_colors, parent=None):
        super().__init__(parent)
        self.exercise_name_map = exercise_name_map
        self.exercise_colors = exercise_colors
        self.exercise_code_map = {v: k for k, v in exercise_name_map.items()}
        
        # Initialize component reference dictionary
        self.goal_spinboxes = {}
        self.exercise_name_labels = {}
        self.target_labels = {}
        
        # Setup layout
        self.setup_ui()
        
    def setup_ui(self):
        """Setup UI components"""
        layout = QVBoxLayout(self)
        
        # Daily exercise goals
        self.daily_group = StyledGroupBox(T.get("daily_goals"))
        daily_layout = QVBoxLayout(self.daily_group)
        daily_layout.setContentsMargins(15, 20, 15, 15)  # Increase padding
        
        # Create scroll area
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
        
        # Create container to place goal items
        container_widget = QWidget()
        container_layout = QVBoxLayout(container_widget)
        container_layout.setSpacing(20)  # Increase spacing between items
        container_layout.setContentsMargins(10, 10, 15, 10)  # Appropriate padding
        
        # Create goal settings for each exercise type
        for i, (exercise_code, exercise_name) in enumerate(self.exercise_name_map.items()):
            color = self.exercise_colors.get(exercise_name, "#3498db")
            
            # Create separator line with spacing from previous item (except first item)
            if i > 0:
                separator = QFrame()
                separator.setFrameShape(QFrame.HLine)
                separator.setFrameShadow(QFrame.Sunken)
                separator.setStyleSheet("background-color: #e0e0e0; min-height: 1px; margin: 10px 0;")
                container_layout.addWidget(separator)
            
            # Create container widget to place horizontal layout
            goal_widget = QWidget()
            goal_layout = QHBoxLayout(goal_widget)
            goal_layout.setContentsMargins(5, 5, 5, 5)
            goal_layout.setSpacing(15)  # Increase element spacing
            
            # Exercise type label
            exercise_label = QLabel(exercise_name)
            exercise_label.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 18pt;")
            # Save reference to label
            self.exercise_name_labels[exercise_code] = exercise_label
            goal_layout.addWidget(exercise_label)
            
            # Goal definition label
            self.target_labels[exercise_code] = QLabel(T.get("daily_goals") + ":")
            self.target_labels[exercise_code].setStyleSheet("font-size: 16pt;")
            self.target_labels[exercise_code].setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            goal_layout.addStretch(1)  # Add stretch space
            goal_layout.addWidget(self.target_labels[exercise_code])
            
            # Goal value input
            spinbox = QSpinBox()
            spinbox.setRange(0, 500)
            spinbox.setSingleStep(5)
            spinbox.setFixedWidth(120)
            spinbox.setFixedHeight(40)
            spinbox.setButtonSymbols(QSpinBox.PlusMinus)
            spinbox.valueChanged.connect(lambda value, code=exercise_code: self.goal_updated.emit(code, value))
            
            # Improved style
            spinbox.setStyleSheet("""
                QSpinBox {
                    border: 2px solid #bdc3c7;
                    border-radius: 10px;
                    padding: 5px;
                    font-size: 16pt;
                    font-weight: bold;
                }
                QSpinBox:hover {
                    border-color: #3498db;
                }
                QSpinBox::up-button, QSpinBox::down-button {
                    width: 25px;
                    height: 18px;
                    border-radius: 5px;
                    background-color: #ecf0f1;
                }
                QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                    background-color: #d5dbdb;
                }
            """)
            
            goal_layout.addWidget(spinbox)
            
            # Save reference
            self.goal_spinboxes[exercise_code] = spinbox
            
            # Add container widget with horizontal layout to container layout
            container_layout.addWidget(goal_widget)
        
        # Add stretch space to ensure content aligns to top
        container_layout.addStretch()
        
        # Set scroll area content
        scroll_area.setWidget(container_widget)
        
        # Set scroll area height limits
        scroll_area.setMinimumHeight(380)  # Minimum height
        scroll_area.setMaximumHeight(500)  # Maximum height
        
        # Add scroll area to main layout
        daily_layout.addWidget(scroll_area)
        
        # Weekly goals
        self.weekly_group = StyledGroupBox(T.get("weekly_goals"))
        weekly_layout = QHBoxLayout(self.weekly_group)
        weekly_layout.setContentsMargins(15, 20, 15, 15)  # Increase padding
        
        self.weekly_label = QLabel(T.get("days_per_week") + ":")
        self.weekly_label.setStyleSheet("font-size: 18pt; font-weight: bold;")
        
        self.weekly_spinbox = QSpinBox()
        self.weekly_spinbox.setRange(1, 7)
        self.weekly_spinbox.setValue(3)
        self.weekly_spinbox.setFixedWidth(120)
        self.weekly_spinbox.setFixedHeight(40)
        self.weekly_spinbox.valueChanged.connect(self.weekly_goal_updated.emit)
        self.weekly_spinbox.setStyleSheet("""
            QSpinBox {
                border: 2px solid #bdc3c7;
                border-radius: 10px;
                padding: 5px;
                font-size: 16pt;
                font-weight: bold;
            }
            QSpinBox:hover {
                border-color: #3498db;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 25px;
                height: 18px;
                border-radius: 5px;
                background-color: #ecf0f1;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background-color: #d5dbdb;
            }
        """)
        
        weekly_layout.addWidget(self.weekly_label)
        weekly_layout.addStretch(1)  # Add stretch space
        weekly_layout.addWidget(self.weekly_spinbox)
        
        # Add to main layout
        layout.addWidget(self.daily_group, 4)  # Allocate larger space
        layout.addWidget(self.weekly_group, 1)  # Allocate smaller space
    
    def update_language(self, exercise_name_map=None, exercise_code_map=None):
        """Update interface language"""
        if exercise_name_map:
            self.exercise_name_map = exercise_name_map
            self.exercise_code_map = {v: k for k, v in exercise_name_map.items()}
            
            # Update color mapping
            new_exercise_colors = {}
            for code, name in self.exercise_name_map.items():
                # Use code directly as key, not name
                if code in self.exercise_colors:
                    new_exercise_colors[name] = self.exercise_colors[code]
                    
            # Update color dictionary
            self.exercise_colors = new_exercise_colors
            
        # Update component titles
        self.daily_group.setTitle(T.get("daily_goals"))
        self.weekly_group.setTitle(T.get("weekly_goals"))
        
        # Update goal definition labels
        for exercise_code in self.target_labels.keys():
            self.target_labels[exercise_code].setText(T.get("daily_goals") + ":")
        
        # Update weekly goal label
        self.weekly_label.setText(T.get("days_per_week") + ":")
        
        # Directly use saved label references to update exercise names
        for exercise_code, label in self.exercise_name_labels.items():
            if exercise_code in self.exercise_name_map:
                exercise_name = self.exercise_name_map[exercise_code]
                color = self.exercise_colors.get(exercise_name, "#3498db")
                
                # Update label text and style
                label.setText(exercise_name)
                label.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 18pt;")
    
    def set_goals(self, goals):
        """Set goal values"""
        # Set daily goals
        for exercise_code, spinbox in self.goal_spinboxes.items():
            spinbox.setValue(goals["daily"].get(exercise_code, 0))
        
        # Set weekly goals
        self.weekly_spinbox.setValue(goals["weekly"]["total_workouts"])
