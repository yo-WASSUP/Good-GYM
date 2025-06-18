from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QComboBox, QGroupBox)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont
from .styles import AppStyles
from .custom_widgets import SwitchControl
from core.translations import Translations as T

class ControlPanel(QWidget):
    """Control panel component"""
    
    # Define signals
    exercise_changed = pyqtSignal(str)
    counter_reset = pyqtSignal()
    camera_changed = pyqtSignal(int)
    rotation_toggled = pyqtSignal(bool)
    skeleton_toggled = pyqtSignal(bool)
    counter_increase = pyqtSignal(int)
    counter_decrease = pyqtSignal(int)
    record_confirmed = pyqtSignal(str)
    model_changed = pyqtSignal(str)  # Add model switching signal
    mirror_toggled = pyqtSignal(bool)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.exercise_colors = AppStyles.EXERCISE_COLORS
        
        # Initialize exercise type mappings
        self.exercise_display_map = {
            "overhead_press": T.get("overhead_press"),
            "bicep_curl": T.get("bicep_curl"),
            "squat": T.get("squat"),
            "pushup": T.get("pushup"),
            "situp": T.get("situp"),
            "lateral_raise": T.get("lateral_raise"),
            "leg_raise": T.get("leg_raise"),
            "knee_raise": T.get("knee_raise"),
            "knee_press": T.get("knee_press")
        }
        
        # Initialize model type mappings - only keep RTMPose options
        self.model_display_map = {
            "lightweight": T.get("lightweight"),
            "balanced": T.get("balanced"),
            "performance": T.get("performance")
        }
        
        # Initialize reverse mappings
        self.exercise_code_map = {v: k for k, v in self.exercise_display_map.items()}
        self.current_exercise = "overhead_press"
        
        # Setup layout
        self.layout = QVBoxLayout(self)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup control panel UI"""
        # Application title
        self.title_label = QLabel(T.get("app_title"))
        self.title_label.setFont(QFont("Arial", 20, QFont.Bold))
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 25pt; font-weight: bold; color: #2c3e50; margin-bottom: 15px;")
        self.layout.addWidget(self.title_label)
        
        # Add info group
        self.setup_info_group()
        
        # Add control options group
        self.setup_controls_group()
        
        # Add phase display group
        self.setup_phase_group()
        
        # Add stretch space
        self.layout.addStretch()
    
    def setup_info_group(self):
        """Setup exercise info group"""
        self.info_group = QGroupBox(T.get("exercise_data"))
        self.info_group.setStyleSheet(AppStyles.get_group_box_style())
        info_layout = QVBoxLayout(self.info_group)
        
        # Create counter display
        counter_layout = QHBoxLayout()
        self.counter_label = QLabel(T.get("count_completed"))
        self.counter_label.setStyleSheet("color: #2c3e50; font-size: 20pt; font-weight: bold;")
        self.counter_label.setMinimumHeight(40)
        
        self.counter_value = QLabel("0")
        self.counter_value.setStyleSheet(AppStyles.get_counter_value_style())
        self.counter_value.setAlignment(Qt.AlignCenter)
        self.counter_value.setFixedSize(180, 120)
        
        counter_layout.addWidget(self.counter_label)
        counter_layout.addWidget(self.counter_value, 1, Qt.AlignCenter)
        info_layout.addLayout(counter_layout)
        
        # Add spacing
        spacer = QWidget()
        spacer.setMinimumHeight(10)
        info_layout.addWidget(spacer)
        
        # Angle display - comment out this code section
        # angle_layout = QHBoxLayout()
        # self.angle_label = QLabel(T.get("current_angle"))
        # self.angle_label.setStyleSheet("color: #2c3e50; font-size: 20pt; font-weight: bold;")
        # self.angle_label.setMinimumHeight(40)
        # 
        # self.angle_value = QLabel("0°")
        # self.angle_value.setStyleSheet(AppStyles.get_angle_value_style())
        # self.angle_value.setAlignment(Qt.AlignCenter)
        # self.angle_value.setFixedSize(180, 70)
        # 
        # angle_layout.addWidget(self.angle_label)
        # angle_layout.addWidget(self.angle_value, 1, Qt.AlignCenter)
        # info_layout.addLayout(angle_layout)
        
        self.layout.addWidget(self.info_group)
    
    def setup_controls_group(self):
        """Setup control options group"""
        self.controls_group = QGroupBox(T.get("control_options"))
        self.controls_group.setStyleSheet(AppStyles.get_group_box_style())
        controls_layout = QVBoxLayout(self.controls_group)
        controls_layout.setSpacing(12)  # Increase overall layout spacing
        
        # Exercise type selection
        exercise_layout = QHBoxLayout()
        self.exercise_label = QLabel(T.get("exercise_type"))
        self.exercise_label.setStyleSheet("color: #2c3e50; font-size: 16pt; font-weight: bold;")  # Reduce font size
        self.exercise_combo = QComboBox()
        
        # Set dropdown menu style
        self.exercise_combo.setStyleSheet(AppStyles.get_exercise_combo_style())
        
        # Use our predefined exercise type mappings
        for code, display in self.exercise_display_map.items():
            self.exercise_combo.addItem(display)
        
        # Set default selected item
        overhead_press_text = self.exercise_display_map.get("overhead_press", "")
        if overhead_press_text:
            self.exercise_combo.setCurrentText(overhead_press_text)
            
        self.exercise_combo.currentTextChanged.connect(self._on_exercise_changed)
        
        exercise_layout.addWidget(self.exercise_label)
        exercise_layout.addWidget(self.exercise_combo, 1)
        controls_layout.addLayout(exercise_layout)
        
        # Model selection
        model_layout = QHBoxLayout()
        self.model_label = QLabel(T.get("model_type"))
        self.model_label.setStyleSheet("color: #2c3e50; font-size: 16pt; font-weight: bold;")  # Reduce font size
        
        self.model_combo = QComboBox()
        self.model_combo.setStyleSheet(AppStyles.get_exercise_combo_style())
        
        # Add model options
        for model_code, model_display in self.model_display_map.items():
            self.model_combo.addItem(model_display, model_code)
            
        # Set default model to RTMPose balanced mode
        rtmpose_balanced_index = list(self.model_display_map.keys()).index("balanced")
        self.model_combo.setCurrentIndex(rtmpose_balanced_index)
        self.model_combo.currentIndexChanged.connect(self._on_model_changed)
        
        model_layout.addWidget(self.model_label)
        model_layout.addWidget(self.model_combo, 1)
        controls_layout.addLayout(model_layout)
        
        # Camera selection
        camera_layout = QHBoxLayout()
        self.camera_label = QLabel(T.get("camera"))
        self.camera_label.setStyleSheet("color: #2c3e50; font-size: 16pt; font-weight: bold;")  # Reduce font size
        
        self.camera_combo = QComboBox()
        self.camera_combo.addItems(["0", "1"])
        self.camera_combo.currentIndexChanged.connect(self._on_camera_changed)
        self.camera_combo.setStyleSheet(AppStyles.get_camera_combo_style())
        
        camera_layout.addWidget(self.camera_label)
        camera_layout.addWidget(self.camera_combo, 1)
        
        # Add spacing
        spacer = QWidget()
        spacer.setMinimumHeight(5)
        controls_layout.addWidget(spacer)
        
        controls_layout.addLayout(camera_layout)
        
        # Portrait mode toggle
        self.rotation_switch = SwitchControl(T.get("rotation_mode"))
        self.rotation_switch.switched.connect(self._on_rotation_toggled)
        controls_layout.addWidget(self.rotation_switch)
        
        # Skeleton display toggle
        self.skeleton_switch = SwitchControl(T.get("skeleton_display"))
        self.skeleton_switch.switched.connect(self._on_skeleton_toggled)
        controls_layout.addWidget(self.skeleton_switch)
        
        # Mirror mode toggle
        self.mirror_switch = SwitchControl(T.get("mirror_mode"))
        self.mirror_switch.switched.connect(self._on_mirror_toggled)
        controls_layout.addWidget(self.mirror_switch)
        
        # Add spacing
        spacer = QWidget()
        spacer.setMinimumHeight(5)
        controls_layout.addWidget(spacer)
        
        # Counter operation button row
        counter_buttons_layout = QHBoxLayout()
        # Decrease count button - orange-red
        self.decrease_button = QPushButton(T.get("decrease"))
        self.decrease_button.setFixedSize(80, 32)
        self.decrease_button.setStyleSheet(AppStyles.get_decrease_button_style())
        self.decrease_button.clicked.connect(self._on_decrease_counter)
        counter_buttons_layout.addWidget(self.decrease_button)

        # Increase count button - green
        self.increase_button = QPushButton(T.get("increase"))
        self.increase_button.setFixedSize(80, 32)
        self.increase_button.setStyleSheet(AppStyles.get_increase_button_style())
        self.increase_button.clicked.connect(self._on_increase_counter)
        counter_buttons_layout.addWidget(self.increase_button)
        
        # Reset counter button - gray
        self.reset_button = QPushButton(T.get("reset"))
        self.reset_button.setFixedSize(80, 32)
        self.reset_button.setStyleSheet(AppStyles.get_reset_button_style())
        self.reset_button.clicked.connect(self._on_reset_counter)
        counter_buttons_layout.addWidget(self.reset_button)

        # Confirm record button - blue system
        self.confirm_button = QPushButton(T.get("confirm"))
        self.confirm_button.setFixedSize(80, 32)
        self.confirm_button.setStyleSheet(AppStyles.get_confirm_button_style())
        self.confirm_button.clicked.connect(self._on_confirm_record)
        counter_buttons_layout.addWidget(self.confirm_button)

        controls_layout.addLayout(counter_buttons_layout)
        
        self.layout.addWidget(self.controls_group)
    
    def _on_increase_counter(self):
        """Manually increase counter value"""
        try:
            # Get current count value
            current_count = int(self.counter_value.text())
            
            # Increase by 1 each time
            new_count = current_count + 1
            
            # Update display
            self.counter_value.setText(str(new_count))
            
            # Send signal
            self.counter_increase.emit(new_count)
            
            # Show success animation
            self.show_success_animation()
            
        except ValueError:
            # If count value is not a valid number, reset to 1
            self.counter_value.setText("1")
            self.counter_increase.emit(1)

    def _on_decrease_counter(self):
        """Manually decrease counter value"""
        try:
            # Get current count value
            current_count = int(self.counter_value.text())
            
            # Ensure count doesn't go negative
            new_count = max(0, current_count - 1)
            
            # Update display
            self.counter_value.setText(str(new_count))
            
            # Send signal
            self.counter_decrease.emit(new_count)
            
            # Update style
            self.update_counter_style()
            
        except ValueError:
            # If count value is not a valid number, reset to 0
            self.counter_value.setText("0")
            self.counter_decrease.emit(0)

    def _on_confirm_record(self):
        """Confirm record current exercise result"""
        try:
            # Get current count value
            current_count = int(self.counter_value.text())
            
            # Only record if count is greater than 0
            if current_count > 0:
                # Send confirm record signal with current exercise type
                self.record_confirmed.emit(self.current_exercise)
                
                # Show success style - change background to green
                self.confirm_button.setStyleSheet(
                    AppStyles.get_success_button_style()
                )
                
                # Return to normal style after 1.5 seconds
                QTimer.singleShot(1500, lambda: self.confirm_button.setStyleSheet(
                    AppStyles.get_confirm_button_style()
                ))
                
        except ValueError:
            # If count value is not a valid number, ignore directly
            pass
    
    def setup_phase_group(self):
        """Setup phase display group"""
        self.phase_group = QGroupBox(T.get("phase_display"))
        self.phase_group.setStyleSheet(AppStyles.get_group_box_style())
        phase_layout = QVBoxLayout(self.phase_group)
        
        # Current phase label
        phase_label_layout = QHBoxLayout()
        self.phase_title = QLabel(T.get("current_phase"))
        self.phase_title.setStyleSheet("color: #2c3e50; font-size: 20pt; font-weight: bold;")
        
        phase_label_layout.addWidget(self.phase_title)
        phase_layout.addLayout(phase_label_layout)
        
        # Create outline indicator
        phase_indicator = QHBoxLayout()
        
        # Current phase indicator
        self.up_indicator = QLabel("↑")
        self.up_indicator.setStyleSheet(AppStyles.get_phase_indicator_style(False))
        self.up_indicator.setAlignment(Qt.AlignCenter)
        
        self.down_indicator = QLabel("↓")
        self.down_indicator.setStyleSheet(AppStyles.get_phase_indicator_style(False))
        self.down_indicator.setAlignment(Qt.AlignCenter)
        
        # Add to layout
        phase_indicator.addWidget(self.up_indicator)
        phase_indicator.addWidget(self.down_indicator)
        
        # Add to layout
        phase_layout.addLayout(phase_indicator)
        
        # Phase value display
        self.stage_value = QLabel(T.get("prepare"))
        self.stage_value.setStyleSheet("color: #3498db; font-size: 24pt; font-weight: bold;")
        self.stage_value.setAlignment(Qt.AlignCenter)
        self.stage_value.setFixedSize(180, 60)
        
        # Add current phase label
        phase_text_layout = QHBoxLayout()
        phase_text_layout.addWidget(self.stage_value, 0, Qt.AlignCenter)
        
        phase_layout.addLayout(phase_text_layout)
        
        # Leave some extra space for phase situation
        spacer = QWidget()
        spacer.setMinimumHeight(20)
        phase_layout.addWidget(spacer)
        
        self.layout.addWidget(self.phase_group)
    
    def _on_exercise_changed(self, exercise_display):
        """Exercise type change handler"""
        # Check if exercise_display is empty or not in mapping
        if not exercise_display or exercise_display not in self.exercise_code_map:
            return
            
        exercise_code = self.exercise_code_map[exercise_display]
        self.current_exercise = exercise_code
        self.exercise_changed.emit(exercise_code)
        self.update_counter_style()
    
    def _on_reset_counter(self):
        """Reset counter handler"""
        self.counter_reset.emit()
    
    def _on_camera_changed(self, index):
        """Camera change handler"""
        self.camera_changed.emit(index)
    
    def _on_rotation_toggled(self, checked):
        """Rotation mode toggle handler"""
        # Send signal
        self.rotation_toggled.emit(checked)
    
    def _on_skeleton_toggled(self, checked):
        """Skeleton display toggle handler"""
        # Send signal
        self.skeleton_toggled.emit(checked)
    
    def _on_model_changed(self, index):
        """RTMPose mode change handler"""
        # Get currently selected mode
        model_mode = self.model_combo.currentData()
        # Emit signal to notify main application
        self.model_changed.emit(model_mode)
    
    def _on_mirror_toggled(self, checked):
        """Mirror mode toggle handler"""
        self.mirror_toggled.emit(checked)
    
    def update_counter(self, value):
        """Update counter value"""
        old_count = int(self.counter_value.text() or "0")
        new_count = int(value)
        
        # Update counter display
        self.counter_value.setText(str(value))
        
        # If increased, show animation
        if new_count > old_count:
            self.show_success_animation()
    
    def update_angle(self, angle_text, exercise_type=None):
        """Update angle display"""
        if exercise_type:
            # Set angle text
            self.angle_value.setText(f"{angle_text}°")
            
            # Update color based on angle value and exercise type
            try:
                current_exercise = self.exercise_display_map.get(exercise_type, "bicep_curl")
                current_color = self.exercise_colors.get(current_exercise, "#3498db")
                
                # Determine if highlighting is needed
                highlight = False
                angle_value = float(angle_text)
                
                if exercise_type == "squat" and angle_value < 120:  # Squat lower limit point
                    highlight = True
                elif exercise_type == "pushup" and angle_value < 100:  # Pushup lower limit point
                    highlight = True
                elif exercise_type == "leg_raise" and angle_value > 90:  # Leg raise upper limit point
                    highlight = True
                elif exercise_type == "knee_raise" and angle_value > 100:  # Knee raise upper limit point
                    highlight = True
                elif exercise_type == "knee_press" and (angle_value < 100 or angle_value > 160):  # Knee press key points
                    highlight = True
                
                # Set style
                self.angle_value.setStyleSheet(AppStyles.get_angle_value_style(current_color, highlight))
            except Exception as e:
                print(f"Error updating angle style: {e}")
    
    def update_phase(self, stage):
        """Update phase display"""
        if stage == "up":
            self.stage_value.setText(T.get("up"))
            self.up_indicator.setStyleSheet(AppStyles.get_phase_indicator_style(True))
            self.down_indicator.setStyleSheet(AppStyles.get_phase_indicator_style(False))
        elif stage == "down":
            self.stage_value.setText(T.get("down"))
            self.up_indicator.setStyleSheet(AppStyles.get_phase_indicator_style(False))
            self.down_indicator.setStyleSheet(AppStyles.get_phase_indicator_style(True))
        else:
            self.stage_value.setText(T.get("prepare"))
            self.up_indicator.setStyleSheet(AppStyles.get_phase_indicator_style(False))
            self.down_indicator.setStyleSheet(AppStyles.get_phase_indicator_style(False))
    
    def update_stage(self, stage, exercise_type):
        """Update exercise stage"""
        if not stage:
            return
            
        self.stage_value.setText(stage)
        
        try:
            # Update stage indicator
            current_exercise = self.exercise_display_map.get(exercise_type, "")
            
            # If preset color not found, use default color
            if current_exercise in AppStyles.EXERCISE_COLORS:
                current_color = AppStyles.EXERCISE_COLORS[current_exercise]
            else:
                current_color = "#3498db"  # Default use blue
            
            if stage == "up":
                self.up_indicator.setStyleSheet(AppStyles.get_phase_indicator_style(True, current_color))
                self.down_indicator.setStyleSheet(AppStyles.get_phase_indicator_style(False))
            elif stage == "down":
                self.down_indicator.setStyleSheet(AppStyles.get_phase_indicator_style(True, current_color))
                self.up_indicator.setStyleSheet(AppStyles.get_phase_indicator_style(False))
        except Exception as e:
            print(f"Error in update_stage: {e}")
            # Use default color on error
            current_color = "#3498db"
    
    def show_success_animation(self):
        """Show success animation for counter increase"""
        self.counter_value.setStyleSheet(AppStyles.get_success_counter_style())
    
    def update_counter_style(self):
        """Update counter style to current exercise color"""
        try:
            # Get current exercise type display name
            current_exercise = self.exercise_display_map.get(self.current_exercise, "")
            
            # If preset color not found, use default color
            if current_exercise in AppStyles.EXERCISE_COLORS:
                current_color = AppStyles.EXERCISE_COLORS[current_exercise]
            else:
                current_color = "#3498db"  # Default use blue
                
            self.counter_value.setStyleSheet(AppStyles.get_counter_value_style(current_color))
        except Exception as e:
            print(f"Error in update_counter_style: {e}")
            # Use default color on error
            self.counter_value.setStyleSheet(AppStyles.get_counter_value_style("#3498db"))
    
    def reset_counter_style(self):
        """Reset counter style"""
        try:
            # Get current exercise type display name
            current_exercise = self.exercise_display_map.get(self.current_exercise, "")
            
            # If preset color not found, use default color
            if current_exercise in AppStyles.EXERCISE_COLORS:
                current_color = AppStyles.EXERCISE_COLORS[current_exercise]
            else:
                current_color = "#3498db"  # Default use blue
                
            self.counter_value.setStyleSheet(AppStyles.get_counter_value_style(current_color))
        except Exception as e:
            print(f"Error in reset_counter_style: {e}")
            # Use default color on error
            self.counter_value.setStyleSheet(AppStyles.get_counter_value_style("#3498db"))
        
    def update_language(self):
        """Update interface language"""
        # Update exercise type mappings
        self.exercise_display_map = {
            "overhead_press": T.get("overhead_press"),
            "bicep_curl": T.get("bicep_curl"),
            "squat": T.get("squat"),
            "pushup": T.get("pushup"),
            "situp": T.get("situp"),
            "lateral_raise": T.get("lateral_raise"),
            "leg_raise": T.get("leg_raise"),
            "knee_raise": T.get("knee_raise"),
            "knee_press": T.get("knee_press")
        }
        
        # Update model type mappings
        self.model_display_map = {
            "lightweight": T.get("lightweight"),
            "balanced": T.get("balanced"),
            "performance": T.get("performance")
        }
        
        # Update reverse mappings
        self.exercise_code_map = {v: k for k, v in self.exercise_display_map.items()}
        
        # Update UI text
        self.title_label.setText(T.get("app_title"))
        self.controls_group.setTitle(T.get("control_options"))
        self.info_group.setTitle(T.get("exercise_data"))
        self.phase_group.setTitle(T.get("motion_detection"))
        
        self.counter_label.setText(T.get("count_completed"))
        self.exercise_label.setText(T.get("exercise_type"))
        self.model_label.setText(T.get("model_type"))  
        self.camera_label.setText(T.get("camera"))
        
        # Update switch text
        self.rotation_switch.label.setText(T.get("rotation_mode"))
        self.skeleton_switch.label.setText(T.get("skeleton_display"))
        self.mirror_switch.label.setText(T.get("mirror_mode"))
        
        # Update button text
        self.increase_button.setText(T.get("increase"))
        self.decrease_button.setText(T.get("decrease"))
        self.reset_button.setText(T.get("reset"))
        self.confirm_button.setText(T.get("confirm"))
        
        # Update phase label
        self.phase_title.setText(T.get(self.current_phase) if hasattr(self, "current_phase") else "")
        
        # Update combo boxes
        self._update_combo_items(self.exercise_combo, self.exercise_display_map)
        self._update_combo_items(self.model_combo, self.model_display_map)  # Update model selection box

    def _update_combo_items(self, combo_box, item_map):
        """Update combo box content"""
        # Save current selected data
        current_data = combo_box.currentData()
        current_text = combo_box.currentText()
        
        # Clear combo box
        combo_box.clear()
        
        # Refill options
        for code, display in item_map.items():
            combo_box.addItem(display, code)
        
        # Try to restore previously selected item
        if current_data:
            # If there's data, restore based on data
            for i in range(combo_box.count()):
                if combo_box.itemData(i) == current_data:
                    combo_box.setCurrentIndex(i)
                    break
        elif current_text:
            # Otherwise try to restore based on text
            for i in range(combo_box.count()):
                if combo_box.itemText(i) == current_text:
                    combo_box.setCurrentIndex(i)
                    break
