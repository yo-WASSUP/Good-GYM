from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QComboBox, QGroupBox, QFrame, QGridLayout, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont
import json
import os
import sys
from .styles import AppStyles
from .custom_widgets import SwitchControl
from core.translations import Translations as T


class ClickOnlyComboBox(QComboBox):
    """Combo box selection changes only through clicks/keyboard, not mouse wheel."""

    def wheelEvent(self, event):
        event.ignore()


class WorkoutStatusRail(QFrame):
    """Compact live metrics shown beside the camera feed."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("StatusRail")
        self.setMinimumWidth(210)
        self.setMaximumWidth(280)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(8)

        self.rail_title = QLabel(T.get("live_session"))
        self.rail_title.setObjectName("RailTitle")
        layout.addWidget(self.rail_title)

        count_tile = QFrame()
        count_tile.setObjectName("RailCountTile")
        count_layout = QVBoxLayout(count_tile)
        count_layout.setContentsMargins(14, 14, 14, 14)
        count_layout.setSpacing(8)

        self.count_label = QLabel(T.get("count_completed"))
        self.count_label.setObjectName("RailLabel")
        self.count_value = QLabel("0")
        self.count_value.setObjectName("RailCount")
        self.count_value.setAlignment(Qt.AlignCenter)

        count_layout.addWidget(self.count_label)
        count_layout.addWidget(self.count_value, 1)
        layout.addWidget(count_tile)

        self.phase_label, self.phase_value = self._add_metric(layout, T.get("current_phase"), T.get("prepare"))
        self.fps_label, self.fps_value = self._add_metric(layout, T.get("camera_fps"), "0")
        self.ai_label, self.ai_value = self._add_metric(layout, T.get("ai_fps"), "--")

        layout.addStretch(1)

    def _add_metric(self, layout, label_text, value_text):
        tile = QFrame()
        tile.setObjectName("StatusTile")
        tile_layout = QVBoxLayout(tile)
        tile_layout.setContentsMargins(12, 10, 12, 10)
        tile_layout.setSpacing(5)

        label = QLabel(label_text)
        label.setObjectName("RailLabel")
        value = QLabel(value_text)
        value.setObjectName("RailValue")
        value.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        tile_layout.addWidget(label)
        tile_layout.addWidget(value)
        layout.addWidget(tile)
        return label, value

    def update_counter(self, value):
        text = str(value)
        if self.count_value.text() == text:
            return
        self.count_value.setText(text)

    def update_phase(self, stage):
        if stage == "up":
            text = T.get("up")
        elif stage == "down":
            text = T.get("down")
        else:
            text = T.get("prepare")
        if self.phase_value.text() == text:
            return
        self.phase_value.setText(text)

    def update_fps(self, fps):
        try:
            value = f"{float(fps):.1f}"
        except (TypeError, ValueError):
            value = "0"
        if self.fps_value.text() == value:
            return
        self.fps_value.setText(value)

    def update_inference(self, elapsed_ms):
        try:
            ms = max(float(elapsed_ms), 0.001)
            ai_fps = 1000.0 / ms
            value = f"{ai_fps:.1f}"
        except (TypeError, ValueError):
            value = "--"
        if self.ai_value.text() == value:
            return
        self.ai_value.setText(value)

    def update_camera(self, camera_index):
        return

    def update_language(self):
        self.rail_title.setText(T.get("live_session"))
        self.count_label.setText(T.get("count_completed"))
        self.phase_label.setText(T.get("current_phase"))
        self.fps_label.setText(T.get("camera_fps"))
        self.ai_label.setText(T.get("ai_fps"))
        self.phase_value.setText(T.get("prepare"))


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
    device_changed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.exercise_colors = AppStyles.EXERCISE_COLORS
        
        # Initialize exercise type mappings from JSON file
        self.exercise_display_map = self.load_exercise_display_map()
        
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
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
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
    
    def load_exercise_display_map(self):
        """Load exercise display map from JSON file"""
        exercises_file = self.get_exercises_file_path()
        
        try:
            if os.path.exists(exercises_file):
                with open(exercises_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    exercises = data.get('exercises', {})
                    
                    # Build exercise_display_map from JSON file
                    exercise_map = {}
                    current_lang = T.get_language()  # Get current language setting
                    
                    for exercise_type, config in exercises.items():
                        # Get display name from JSON file based on current language
                        if current_lang == 'zh':
                            display_name = config.get('name_zh', '')
                        elif current_lang == 'en':
                            display_name = config.get('name_en', '')
                        else:
                            # Fallback to English if language not supported
                            display_name = config.get('name_en', '')
                        
                        # If name not found in JSON, try translation module as fallback
                        if not display_name:
                            display_name = T.get(exercise_type)
                        
                        if display_name:
                            exercise_map[exercise_type] = display_name
                    
                    if exercise_map:
                        print(f"Loaded {len(exercise_map)} exercises from {exercises_file}")
                        return exercise_map
                    else:
                        print(f"WARNING: No exercises found in {exercises_file}")
                        return {}
            else:
                print(f"ERROR: Exercises file not found at {exercises_file}")
                print("Please ensure data/exercises.json exists")
                return {}
        except Exception as e:
            print(f"ERROR loading exercises from JSON: {e}")
            return {}
    
    def _setup_ui_legacy(self):
        """Setup control panel UI"""
        # Application title
        self.title_label = QLabel("Good-GYM")
        self.title_label.setFont(QFont("Segoe UI", 20, QFont.Bold))
        self.title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.title_label.setStyleSheet(AppStyles.get_panel_title_style())
        self.layout.addWidget(self.title_label)
        
        # Add info group
        self.setup_info_group()
        
        # Add control options group
        self.setup_controls_group()
        
        # Add phase display group
        self.setup_phase_group()
        
        # Add stretch space
        self.layout.addStretch()
    
    def _setup_info_group_legacy(self):
        """Setup exercise info group"""
        self.info_group = QGroupBox(T.get("exercise_data"))
        self.info_group.setStyleSheet(AppStyles.get_group_box_style())
        info_layout = QVBoxLayout(self.info_group)
        info_layout.setContentsMargins(10, 12, 10, 10)
        info_layout.setSpacing(8)
        
        # Create counter display
        counter_layout = QHBoxLayout()
        self.counter_label = QLabel(T.get("count_completed"))
        self.counter_label.setStyleSheet(AppStyles.get_section_label_style())
        self.counter_label.setMinimumHeight(28)
        
        self.counter_value = QLabel("0", self)
        self.counter_value.setStyleSheet(AppStyles.get_counter_value_style())
        self.counter_value.setAlignment(Qt.AlignCenter)
        self.counter_value.setFixedSize(150, 88)
        
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
    
    def _setup_controls_group_legacy(self):
        """Setup control options group"""
        self.controls_group = QGroupBox(T.get("control_options"))
        self.controls_group.setStyleSheet(AppStyles.get_group_box_style())
        controls_layout = QVBoxLayout(self.controls_group)
        controls_layout.setContentsMargins(10, 12, 10, 10)
        controls_layout.setSpacing(8)  # Increase overall layout spacing
        
        # Exercise type selection
        exercise_layout = QHBoxLayout()
        self.exercise_label = QLabel(T.get("exercise_type"))
        self.exercise_label.setStyleSheet(AppStyles.get_field_label_style())
        self.exercise_label.setFixedWidth(120)
        self.exercise_combo = ClickOnlyComboBox()
        self.exercise_combo.setFixedHeight(36)
        
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
        self.model_label.setStyleSheet(AppStyles.get_field_label_style())
        self.model_label.setFixedWidth(120)
        
        self.model_combo = ClickOnlyComboBox()
        self.model_combo.setFixedHeight(36)
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
        self.camera_label.setStyleSheet(AppStyles.get_field_label_style())
        self.camera_label.setFixedWidth(120)
        
        self.camera_combo = ClickOnlyComboBox()
        self.camera_combo.setFixedHeight(36)
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

        # GPU acceleration toggle
        self.gpu_switch = SwitchControl(T.get("gpu_acceleration"))
        self.gpu_switch.setChecked(False)  # Default off until GPU detected
        self.gpu_switch.setEnabled(False)  # Disabled until GPU detected
        self.gpu_switch.switched.connect(self._on_device_toggled)
        controls_layout.addWidget(self.gpu_switch)

        # Add spacing
        spacer = QWidget()
        spacer.setMinimumHeight(5)
        controls_layout.addWidget(spacer)

        # Counter operation button row
        counter_buttons_layout = QHBoxLayout()
        counter_buttons_layout.setSpacing(8)
        # Decrease count button - orange-red
        self.decrease_button = QPushButton(T.get("decrease"))
        self.decrease_button.setFixedSize(76, 34)
        self.decrease_button.setStyleSheet(AppStyles.get_decrease_button_style())
        self.decrease_button.clicked.connect(self._on_decrease_counter)
        counter_buttons_layout.addWidget(self.decrease_button)

        # Increase count button - green
        self.increase_button = QPushButton(T.get("increase"))
        self.increase_button.setFixedSize(76, 34)
        self.increase_button.setStyleSheet(AppStyles.get_increase_button_style())
        self.increase_button.clicked.connect(self._on_increase_counter)
        counter_buttons_layout.addWidget(self.increase_button)
        
        # Reset counter button - gray
        self.reset_button = QPushButton(T.get("reset"))
        self.reset_button.setFixedSize(76, 34)
        self.reset_button.setStyleSheet(AppStyles.get_reset_button_style())
        self.reset_button.clicked.connect(self._on_reset_counter)
        counter_buttons_layout.addWidget(self.reset_button)

        # Confirm record button - blue system
        self.confirm_button = QPushButton(T.get("confirm"))
        self.confirm_button.setFixedSize(76, 34)
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
    
    def _setup_phase_group_legacy(self):
        """Setup phase display group"""
        self.phase_group = QGroupBox(T.get("phase_display"))
        self.phase_group.setStyleSheet(AppStyles.get_group_box_style())
        phase_layout = QVBoxLayout(self.phase_group)
        phase_layout.setContentsMargins(10, 12, 10, 10)
        phase_layout.setSpacing(8)
        
        # Current phase label
        phase_label_layout = QHBoxLayout()
        self.phase_title = QLabel(T.get("current_phase"))
        self.phase_title.setStyleSheet(AppStyles.get_section_label_style())
        
        phase_label_layout.addWidget(self.phase_title)
        phase_layout.addLayout(phase_label_layout)
        
        # Create outline indicator
        phase_indicator = QHBoxLayout()
        
        # Current phase indicator
        self.up_indicator = QLabel("↑")
        self.up_indicator.setStyleSheet(AppStyles.get_phase_indicator_style(False))
        self.up_indicator.setAlignment(Qt.AlignCenter)
        self.up_indicator.setFixedSize(46, 46)
        
        self.down_indicator = QLabel("↓")
        self.down_indicator.setStyleSheet(AppStyles.get_phase_indicator_style(False))
        self.down_indicator.setAlignment(Qt.AlignCenter)
        self.down_indicator.setFixedSize(46, 46)
        
        # Add to layout
        phase_indicator.addWidget(self.up_indicator)
        phase_indicator.addWidget(self.down_indicator)
        
        # Add to layout
        phase_layout.addLayout(phase_indicator)
        
        # Phase value display
        self.stage_value = QLabel(T.get("prepare"))
        self.stage_value.setStyleSheet(AppStyles.get_stage_value_style())
        self.stage_value.setAlignment(Qt.AlignCenter)
        self.stage_value.setFixedSize(150, 44)
        
        # Add current phase label
        phase_text_layout = QHBoxLayout()
        phase_text_layout.addWidget(self.stage_value, 0, Qt.AlignCenter)
        
        phase_layout.addLayout(phase_text_layout)
        
        # Leave some extra space for phase situation
        spacer = QWidget()
        spacer.setMinimumHeight(4)
        phase_layout.addWidget(spacer)
        
        self.layout.addWidget(self.phase_group)
    
    def setup_ui(self):
        """Setup the desktop bottom control dock."""
        self.setObjectName("ControlPanel")
        self.setMinimumHeight(104)
        self.setMaximumHeight(128)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.counter_value = QLabel("0")
        self.counter_value.hide()

        dock = QFrame()
        dock.setObjectName("ControlDock")
        dock_layout = QHBoxLayout(dock)
        dock_layout.setContentsMargins(14, 12, 14, 12)
        dock_layout.setSpacing(12)

        self.exercise_combo = ClickOnlyComboBox()
        self.exercise_combo.setStyleSheet(AppStyles.get_exercise_combo_style())
        for code, display in self.exercise_display_map.items():
            self.exercise_combo.addItem(display)

        overhead_press_text = self.exercise_display_map.get("overhead_press", "")
        if overhead_press_text:
            self.exercise_combo.setCurrentText(overhead_press_text)
        self.exercise_combo.currentTextChanged.connect(self._on_exercise_changed)
        exercise_field, self.exercise_label = self._create_dock_field(T.get("exercise_type"), self.exercise_combo, 190)
        dock_layout.addWidget(exercise_field, 2)

        self.model_combo = ClickOnlyComboBox()
        self.model_combo.setStyleSheet(AppStyles.get_exercise_combo_style())
        for model_code, model_display in self.model_display_map.items():
            self.model_combo.addItem(model_display, model_code)
        self.model_combo.setCurrentIndex(list(self.model_display_map.keys()).index("balanced"))
        self.model_combo.currentIndexChanged.connect(self._on_model_changed)
        model_field, self.model_label = self._create_dock_field(T.get("model_type"), self.model_combo, 150)
        dock_layout.addWidget(model_field, 1)

        self.camera_combo = ClickOnlyComboBox()
        self.camera_combo.addItems(["0", "1"])
        self.camera_combo.currentIndexChanged.connect(self._on_camera_changed)
        self.camera_combo.setStyleSheet(AppStyles.get_camera_combo_style())
        camera_field, self.camera_label = self._create_dock_field(T.get("camera"), self.camera_combo, 82, 112)
        dock_layout.addWidget(camera_field, 0)

        switches = QFrame()
        switches.setObjectName("DockSwitches")
        switches_layout = QVBoxLayout(switches)
        switches_layout.setContentsMargins(0, 0, 0, 0)
        switches_layout.setSpacing(7)

        self.rotation_switch = SwitchControl(T.get("rotation_mode"))
        self.rotation_switch.switched.connect(self._on_rotation_toggled)
        switches_layout.addWidget(self.rotation_switch)

        self.gpu_switch = SwitchControl(T.get("gpu_acceleration"))
        self.gpu_switch.setChecked(False)
        self.gpu_switch.setEnabled(False)
        self.gpu_switch.switched.connect(self._on_device_toggled)
        switches_layout.addWidget(self.gpu_switch)
        dock_layout.addWidget(switches, 1)

        buttons = QFrame()
        buttons.setObjectName("DockButtons")
        buttons_layout = QHBoxLayout(buttons)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(7)

        self.decrease_button = QPushButton("-")
        self.decrease_button.setObjectName("CounterButton")
        self.decrease_button.setStyleSheet(AppStyles.get_decrease_button_style())
        self.decrease_button.clicked.connect(self._on_decrease_counter)
        buttons_layout.addWidget(self.decrease_button)

        self.increase_button = QPushButton("+")
        self.increase_button.setObjectName("CounterButton")
        self.increase_button.setStyleSheet(AppStyles.get_increase_button_style())
        self.increase_button.clicked.connect(self._on_increase_counter)
        buttons_layout.addWidget(self.increase_button)

        self.reset_button = QPushButton(T.get("reset"))
        self.reset_button.setObjectName("ActionButton")
        self.reset_button.setStyleSheet(AppStyles.get_reset_button_style())
        self.reset_button.clicked.connect(self._on_reset_counter)
        buttons_layout.addWidget(self.reset_button)

        self.confirm_button = QPushButton(T.get("confirm"))
        self.confirm_button.setObjectName("ActionButton")
        self.confirm_button.setStyleSheet(AppStyles.get_confirm_button_style())
        self.confirm_button.clicked.connect(self._on_confirm_record)
        buttons_layout.addWidget(self.confirm_button)

        self.decrease_button.setFixedSize(38, 34)
        self.increase_button.setFixedSize(38, 34)
        self.reset_button.setFixedSize(68, 34)
        self.confirm_button.setFixedSize(86, 34)
        dock_layout.addWidget(buttons, 0)

        self.layout.addWidget(dock)

    def _create_dock_field(self, label_text, field_widget, min_width=120, max_width=None):
        field = QFrame()
        field.setObjectName("DockField")
        field.setMinimumWidth(min_width)
        if max_width:
            field.setMaximumWidth(max_width)

        field_layout = QVBoxLayout(field)
        field_layout.setContentsMargins(0, 0, 0, 0)
        field_layout.setSpacing(6)

        label = QLabel(label_text)
        label.setObjectName("DockLabel")
        field_widget.setMinimumHeight(34)
        field_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        field_layout.addWidget(label)
        field_layout.addWidget(field_widget)
        return field, label

    def _create_card(self):
        card = QFrame()
        card.setObjectName("PanelCard")
        card.setStyleSheet(AppStyles.get_card_style())
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 14, 16, 16)
        layout.setSpacing(12)
        return card, layout

    def _add_section_header(self, layout, title):
        label = QLabel(title)
        label.setObjectName("CardTitle")
        label.setStyleSheet(AppStyles.get_section_label_style())
        layout.addWidget(label)
        return label

    def _create_form_row(self, label_text, field_widget):
        row = QVBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(6)

        label = QLabel(label_text)
        label.setStyleSheet(AppStyles.get_field_label_style())
        label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        field_widget.setMinimumHeight(38)
        field_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        row.addWidget(label)
        row.addWidget(field_widget)
        return row, label

    def setup_info_group(self):
        """Setup exercise data card."""
        self.info_group, info_layout = self._create_card()
        self.info_title = self._add_section_header(info_layout, T.get("exercise_data"))

        metric = QFrame()
        metric.setObjectName("CounterMetric")
        metric_layout = QHBoxLayout(metric)
        metric_layout.setContentsMargins(14, 12, 14, 12)
        metric_layout.setSpacing(12)

        self.counter_label = QLabel(T.get("count_completed"))
        self.counter_label.setObjectName("MetricLabel")
        self.counter_label.setStyleSheet(AppStyles.get_field_label_style())

        self.counter_value = QLabel("0")
        self.counter_value.setStyleSheet(AppStyles.get_counter_value_style())
        self.counter_value.setAlignment(Qt.AlignCenter)
        self.counter_value.setMinimumSize(118, 82)
        self.counter_value.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        metric_layout.addWidget(self.counter_label, 0, Qt.AlignVCenter)
        metric_layout.addWidget(self.counter_value, 1)
        info_layout.addWidget(metric)

        self.layout.addWidget(self.info_group)

    def setup_controls_group(self):
        """Setup controls card."""
        self.controls_group, controls_layout = self._create_card()
        self.controls_title = self._add_section_header(controls_layout, T.get("control_options"))

        self.exercise_combo = ClickOnlyComboBox()
        self.exercise_combo.setStyleSheet(AppStyles.get_exercise_combo_style())
        for code, display in self.exercise_display_map.items():
            self.exercise_combo.addItem(display)

        overhead_press_text = self.exercise_display_map.get("overhead_press", "")
        if overhead_press_text:
            self.exercise_combo.setCurrentText(overhead_press_text)
        self.exercise_combo.currentTextChanged.connect(self._on_exercise_changed)
        row, self.exercise_label = self._create_form_row(T.get("exercise_type"), self.exercise_combo)
        controls_layout.addLayout(row)

        self.model_combo = ClickOnlyComboBox()
        self.model_combo.setStyleSheet(AppStyles.get_exercise_combo_style())
        for model_code, model_display in self.model_display_map.items():
            self.model_combo.addItem(model_display, model_code)

        rtmpose_balanced_index = list(self.model_display_map.keys()).index("balanced")
        self.model_combo.setCurrentIndex(rtmpose_balanced_index)
        self.model_combo.currentIndexChanged.connect(self._on_model_changed)
        row, self.model_label = self._create_form_row(T.get("model_type"), self.model_combo)
        controls_layout.addLayout(row)

        self.camera_combo = ClickOnlyComboBox()
        self.camera_combo.addItems(["0", "1"])
        self.camera_combo.currentIndexChanged.connect(self._on_camera_changed)
        self.camera_combo.setStyleSheet(AppStyles.get_camera_combo_style())
        row, self.camera_label = self._create_form_row(T.get("camera"), self.camera_combo)
        controls_layout.addLayout(row)

        switches = QFrame()
        switches.setObjectName("SwitchList")
        switch_layout = QVBoxLayout(switches)
        switch_layout.setContentsMargins(0, 2, 0, 0)
        switch_layout.setSpacing(8)

        self.rotation_switch = SwitchControl(T.get("rotation_mode"))
        self.rotation_switch.switched.connect(self._on_rotation_toggled)
        switch_layout.addWidget(self.rotation_switch)

        self.gpu_switch = SwitchControl(T.get("gpu_acceleration"))
        self.gpu_switch.setChecked(False)
        self.gpu_switch.setEnabled(False)
        self.gpu_switch.switched.connect(self._on_device_toggled)
        switch_layout.addWidget(self.gpu_switch)
        controls_layout.addWidget(switches)

        buttons_grid = QGridLayout()
        buttons_grid.setContentsMargins(0, 4, 0, 0)
        buttons_grid.setHorizontalSpacing(8)
        buttons_grid.setVerticalSpacing(8)

        self.decrease_button = QPushButton(T.get("decrease"))
        self.decrease_button.setStyleSheet(AppStyles.get_decrease_button_style())
        self.decrease_button.clicked.connect(self._on_decrease_counter)
        buttons_grid.addWidget(self.decrease_button, 0, 0)

        self.increase_button = QPushButton(T.get("increase"))
        self.increase_button.setStyleSheet(AppStyles.get_increase_button_style())
        self.increase_button.clicked.connect(self._on_increase_counter)
        buttons_grid.addWidget(self.increase_button, 0, 1)

        self.reset_button = QPushButton(T.get("reset"))
        self.reset_button.setStyleSheet(AppStyles.get_reset_button_style())
        self.reset_button.clicked.connect(self._on_reset_counter)
        buttons_grid.addWidget(self.reset_button, 1, 0)

        self.confirm_button = QPushButton(T.get("confirm"))
        self.confirm_button.setStyleSheet(AppStyles.get_confirm_button_style())
        self.confirm_button.clicked.connect(self._on_confirm_record)
        buttons_grid.addWidget(self.confirm_button, 1, 1)

        for button in (self.decrease_button, self.increase_button, self.reset_button, self.confirm_button):
            button.setMinimumHeight(40)
            button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        controls_layout.addLayout(buttons_grid)
        self.layout.addWidget(self.controls_group)

    def setup_phase_group(self):
        """Setup motion phase card."""
        self.phase_group, phase_layout = self._create_card()
        self.phase_group_title = self._add_section_header(phase_layout, T.get("phase_display"))

        self.phase_title = QLabel(T.get("current_phase"))
        self.phase_title.setStyleSheet(AppStyles.get_field_label_style())
        phase_layout.addWidget(self.phase_title)

        phase_indicator = QHBoxLayout()
        phase_indicator.setContentsMargins(0, 0, 0, 0)
        phase_indicator.setSpacing(10)

        self.up_indicator = QLabel("UP")
        self.up_indicator.setStyleSheet(AppStyles.get_phase_indicator_style(False))
        self.up_indicator.setAlignment(Qt.AlignCenter)
        self.up_indicator.setMinimumSize(72, 44)
        self.up_indicator.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.down_indicator = QLabel("DOWN")
        self.down_indicator.setStyleSheet(AppStyles.get_phase_indicator_style(False))
        self.down_indicator.setAlignment(Qt.AlignCenter)
        self.down_indicator.setMinimumSize(72, 44)
        self.down_indicator.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        phase_indicator.addWidget(self.up_indicator)
        phase_indicator.addWidget(self.down_indicator)
        phase_layout.addLayout(phase_indicator)

        self.stage_value = QLabel(T.get("prepare"))
        self.stage_value.setStyleSheet(AppStyles.get_stage_value_style())
        self.stage_value.setAlignment(Qt.AlignCenter)
        self.stage_value.setMinimumHeight(44)
        self.stage_value.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        phase_layout.addWidget(self.stage_value)

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

    def _on_device_toggled(self, checked):
        """GPU acceleration toggle handler"""
        self.device_changed.emit('cuda' if checked else 'cpu')

    def set_gpu_available(self, available):
        """Set GPU toggle state based on detection result"""
        self.gpu_switch.setEnabled(available)
        self.gpu_switch.setChecked(False)
    
    def update_counter(self, value):
        """Update counter value"""
        if not hasattr(self, "counter_value"):
            return
        new_text = str(value)
        old_text = self.counter_value.text() or "0"
        if old_text == new_text:
            return
        old_count = int(old_text)
        new_count = int(new_text)
        
        # Update counter display
        self.counter_value.setText(new_text)
        
        # If increased, show animation
        if new_count > old_count:
            self.show_success_animation()
    
    def update_angle(self, angle_text, exercise_type=None):
        """Update angle display"""
        if not hasattr(self, "angle_value"):
            return
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
        if not all(hasattr(self, name) for name in ("stage_value", "up_indicator", "down_indicator")):
            return
        if getattr(self, "_last_phase_stage", None) == stage:
            return
        self._last_phase_stage = stage
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
        if not all(hasattr(self, name) for name in ("stage_value", "up_indicator", "down_indicator")):
            return
        if not stage:
            return
            
        self.stage_value.setText(stage)
        
        try:
            current_exercise = self.exercise_display_map.get(exercise_type, "")
            current_color = AppStyles.EXERCISE_COLORS.get(
                exercise_type,
                AppStyles.EXERCISE_COLORS.get(current_exercise, "#38D6B2")
            )
            
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
        if not hasattr(self, "counter_value"):
            return
        self.counter_value.setStyleSheet(AppStyles.get_success_counter_style())
    
    def update_counter_style(self):
        """Update counter style to current exercise color"""
        if not hasattr(self, "counter_value"):
            return
        try:
            current_exercise = self.exercise_display_map.get(self.current_exercise, "")
            current_color = AppStyles.EXERCISE_COLORS.get(
                self.current_exercise,
                AppStyles.EXERCISE_COLORS.get(current_exercise, "#38D6B2")
            )
                
            self.counter_value.setStyleSheet(AppStyles.get_counter_value_style(current_color))
        except Exception as e:
            print(f"Error in update_counter_style: {e}")
            # Use default color on error
            self.counter_value.setStyleSheet(AppStyles.get_counter_value_style("#3498db"))
    
    def reset_counter_style(self):
        """Reset counter style"""
        if not hasattr(self, "counter_value"):
            return
        try:
            current_exercise = self.exercise_display_map.get(self.current_exercise, "")
            current_color = AppStyles.EXERCISE_COLORS.get(
                self.current_exercise,
                AppStyles.EXERCISE_COLORS.get(current_exercise, "#38D6B2")
            )
                
            self.counter_value.setStyleSheet(AppStyles.get_counter_value_style(current_color))
        except Exception as e:
            print(f"Error in reset_counter_style: {e}")
            # Use default color on error
            self.counter_value.setStyleSheet(AppStyles.get_counter_value_style("#3498db"))
        
    def update_language(self):
        """Update interface language"""
        self._last_phase_stage = None
        # Reload exercise type mappings from JSON file (with updated translations)
        self.exercise_display_map = self.load_exercise_display_map()
        
        # Update model type mappings
        self.model_display_map = {
            "lightweight": T.get("lightweight"),
            "balanced": T.get("balanced"),
            "performance": T.get("performance")
        }
        
        # Update reverse mappings
        self.exercise_code_map = {v: k for k, v in self.exercise_display_map.items()}
        
        if hasattr(self, "title_label"):
            self.title_label.setText("Good-GYM")
        if hasattr(self, "controls_title"):
            self.controls_title.setText(T.get("control_options"))
        if hasattr(self, "info_title"):
            self.info_title.setText(T.get("exercise_data"))
        if hasattr(self, "phase_group_title"):
            self.phase_group_title.setText(T.get("phase_display"))

        if hasattr(self, "counter_label"):
            self.counter_label.setText(T.get("count_completed"))
        self.exercise_label.setText(T.get("exercise_type"))
        self.model_label.setText(T.get("model_type"))
        self.camera_label.setText(T.get("camera"))
        
        # Update switch text
        self.rotation_switch.label.setText(T.get("rotation_mode"))
        if hasattr(self, "skeleton_switch"):
            self.skeleton_switch.label.setText(T.get("skeleton_display"))
        if hasattr(self, "mirror_switch"):
            self.mirror_switch.label.setText(T.get("mirror_mode"))
        self.gpu_switch.label.setText(T.get("gpu_acceleration"))
        
        # Update button text
        self.increase_button.setText("+")
        self.decrease_button.setText("-")
        self.reset_button.setText(T.get("reset"))
        self.confirm_button.setText(T.get("confirm"))
        
        # Update phase label
        if hasattr(self, "phase_title"):
            self.phase_title.setText(T.get("current_phase"))
        
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
