from PyQt5.QtGui import QColor, QPalette, QFont
from PyQt5.QtCore import Qt

class AppStyles:
    """Application style definitions"""
    
    # Exercise type color mapping
    EXERCISE_COLORS = {
        # Chinese names
        "深蹲": "#3498db",      # Blue
        "俯卧撑": "#e74c3c",    # Red
        "仰卧起坐": "#2ecc71",  # Green
        "二头弯举": "#f39c12", # Yellow
        "三头臂屈伸": "#f39c12", # Yellow
        "侧平举": "#9b59b6",    # Purple
        "颈前推举": "#1abc9c",  # Cyan
        "左右交替抬腿": "#e67e22", # Orange
        "高抬腿": "#16a085",   # Dark cyan
        "提膝下压": "#8e44ad",    # Dark purple
        "左侧提膝下压": "#8e44ad",   # Dark purple
        "右侧提膝下压": "#6c3483",    # Dark purple variant
        
        # English names
        "Squat": "#3498db",      # Blue
        "Push Up": "#e74c3c",    # Red
        "Sit Up": "#2ecc71",  # Green
        "Bicep Curl": "#f39c12", # Yellow
        "Tricep Extension": "#f39c12", # Yellow
        "Lateral Raise": "#9b59b6",    # Purple
        "Overhead Press": "#1abc9c",  # Cyan
        "Leg Raise": "#e67e22", # Orange
        "Knee Raise": "#16a085",   # Dark cyan
        "Knee Press": "#8e44ad",    # Dark purple
        "Left Knee Press": "#8e44ad",   # Dark purple
        "Right Knee Press": "#6c3483"    # Dark purple variant
    }
    
    @staticmethod
    def get_window_palette():
        """Get window palette"""
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(248, 249, 250))
        palette.setColor(QPalette.WindowText, QColor(52, 58, 64))
        return palette
    
    @staticmethod
    def get_global_stylesheet():
        """Get global stylesheet"""
        return """
            QWidget {
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 10pt;
            }
            QComboBox {
                border: 1px solid #bdc3c7;
                border-radius: 3px;
                padding: 5px;
                min-width: 6em;
            }
            QComboBox:hover {
                border: 1px solid #3498db;
            }
            QLabel {
                color: #2c3e50;
            }
            QCheckBox {
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QGroupBox {
                padding-top: 15px;
            }
        """
    
    @staticmethod
    def get_exercise_combo_style():
        """Get exercise selection dropdown style"""
        return """
            QComboBox {
                font-size: 12pt;
                padding: 2px 8px;
                min-height: 28px;
                max-height: 28px;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                background-color: #ffffff;
            }
            QComboBox:hover {
                border-color: #3498db;
            }
            QComboBox::drop-down {
                border: 0px;
                width: 20px;
            }
            QComboBox QAbstractItemView {
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                selection-background-color: #3498db;
                font-size: 12pt;
            }
        """
    
    @staticmethod
    def get_counter_value_style(color="#27ae60"):
        """Get counter style"""
        return f"""
            color: {color}; 
            background-color: #f7f9f9; 
            border-radius: 15px; 
            padding: 10px; 
            border: 3px solid #e8e8e8;
            min-width: 120px;
            text-align: center;
            font-size: 64pt;
        """
    
    @staticmethod
    def get_success_counter_style():
        """Get success counter style"""
        return """
            color: #2ecc71; 
            background-color: #f7f9f9; 
            border-radius: 15px; 
            padding: 10px; 
            border: 3px solid #2ecc71;
            min-width: 120px;
            text-align: center;
            font-size: 64pt;
        """
    
    @staticmethod
    def get_angle_value_style(color="#34495e", highlight=False):
        """Get angle value style"""
        border_color = "#e74c3c" if highlight else "#e8e8e8"
        text_color = "#e74c3c" if highlight else color
        
        return f"""
            color: {text_color}; 
            background-color: #f7f9f9; 
            border-radius: 10px; 
            padding: 5px; 
            border: 2px solid {border_color};
            min-width: 100px;
            text-align: center;
            font-size: 36pt;
        """
    
    @staticmethod
    def get_phase_indicator_style(active=False, color="#3498db"):
        """Get phase indicator style"""
        bg_color = color if active else "#bdc3c7"
        text_color = "white" if active else "#ecf0f1"
        
        return f"""
            font-size: 36pt; 
            color: {text_color}; 
            background-color: {bg_color}; 
            border-radius: 25px; 
            min-width: 50px; 
            min-height: 50px;
            padding: 10px;
            text-align: center;
        """
    
    @staticmethod
    def get_group_box_style():
        """Get group box style"""
        return """
            QGroupBox { 
                font-weight: bold; 
                border: 1px solid #bdc3c7; 
                border-radius: 5px; 
                margin-top: 10px; 
            } 
            QGroupBox::title { 
                subcontrol-origin: margin; 
                left: 10px; 
                padding: 0 5px; 
            }
        """
    
    @staticmethod
    def get_phase_group_style():
        """Get exercise state group style"""
        return """
            QGroupBox { 
                font-weight: bold; 
                border: 1px solid #bdc3c7; 
                border-radius: 5px; 
                margin-top: 10px; 
            } 
            QGroupBox::title { 
                subcontrol-origin: margin; 
                left: 10px; 
                padding: 0 5px;
                font-size: 14pt; 
            }
        """
    
    @staticmethod
    def get_camera_combo_style():
        """Get camera selection dropdown style"""
        return """
            QComboBox {
                font-size: 12pt;
                padding: 2px 8px;
                min-height: 28px;
                max-height: 28px;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                background-color: #ffffff;
            }
            QComboBox:hover {
                border-color: #3498db;
            }
            QComboBox::drop-down {
                border: 0px;
                width: 20px;
            }
            QComboBox QAbstractItemView {
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                selection-background-color: #3498db;
                font-size: 12pt;
            }
        """
        
    @staticmethod
    def get_increase_button_style():
        """Get increase count button style - Green"""
        return """
            QPushButton { 
                background-color: #2ecc71; 
                color: white; 
                border-radius: 5px; 
                padding: 8px; 
                font-weight: bold;
            }
            QPushButton:hover { 
                background-color: #27ae60; 
            }
            QPushButton:pressed { 
                background-color: #1f8a4c; 
            }
        """
    
    @staticmethod
    def get_decrease_button_style():
        """Get decrease count button style - Orange"""
        return """
            QPushButton { 
                background-color: #e67e22; 
                color: white; 
                border-radius: 5px; 
                padding: 8px; 
                font-weight: bold;
            }
            QPushButton:hover { 
                background-color: #d35400; 
            }
            QPushButton:pressed { 
                background-color: #b84700; 
            }
        """
    
    @staticmethod
    def get_reset_button_style():
        """Get reset button style"""
        return """
            QPushButton { 
                background-color: #95a5a6; 
                color: white; 
                border-radius: 5px; 
                padding: 8px; 
                font-weight: bold;
            }
            QPushButton:hover { 
                background-color: #7f8c8d; 
            }
            QPushButton:pressed { 
                background-color: #6a7778; 
            }
        """
    
    @staticmethod
    def get_confirm_button_style():
        """Get confirm record button style - Blue"""
        return """
            QPushButton { 
                background-color: #3498db; 
                color: white; 
                border-radius: 5px; 
                padding: 8px; 
                font-weight: bold;
            }
            QPushButton:hover { 
                background-color: #2980b9; 
            }
            QPushButton:pressed { 
                background-color: #1c6ea4; 
            }
        """
        
    @staticmethod
    def get_success_button_style():
        """Get success button style - Green"""
        return """
            QPushButton { 
                background-color: #27ae60; 
                color: white; 
                border-radius: 5px; 
                padding: 8px; 
                font-weight: bold;
            }
            QPushButton:hover { 
                background-color: #2ecc71; 
            }
            QPushButton:pressed { 
                background-color: #1f8a4c; 
            }
        """
    
    @staticmethod
    def get_toggle_button_style(checked=False):
        """Get toggle button style"""
        # Set different styles for on and off states
        if checked:
            # On state - green background
            return """
                QPushButton {
                    background-color: #2ecc71;
                    border-radius: 15px;
                    color: white;
                    border: none;
                    min-width: 80px;
                    max-width: 80px;
                    min-height: 30px;
                    max-height: 30px;
                    font-weight: bold;
                    font-size: 12pt;
                    padding-right: 25px; /* Leave space for indicator */
                    text-align: center;
                }
                QPushButton:hover {
                    background-color: #27ae60;
                }
            """
        else:
            # Off state - gray background
            return """
                QPushButton {
                    background-color: #bdc3c7;
                    border-radius: 15px;
                    color: white;
                    border: none;
                    min-width: 80px;
                    max-width: 80px;
                    min-height: 30px;
                    max-height: 30px;
                    font-weight: bold;
                    font-size: 12pt;
                    padding-left: 25px; /* Leave space for indicator */
                    text-align: center;
                }
                QPushButton:hover {
                    background-color: #95a5a6;
                }
            """
