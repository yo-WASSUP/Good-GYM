from PyQt5.QtGui import QColor, QPalette, QFont
from PyQt5.QtCore import Qt

class AppStyles:
    """应用程序样式定义"""
    
    # 运动类型颜色映射
    EXERCISE_COLORS = {
        # 中文名称
        "深蹲": "#3498db",      # 蓝色
        "俯卧撑": "#e74c3c",    # 红色
        "仰卧起坐": "#2ecc71",  # 绿色
        "二头弯举": "#f39c12", # 黄色
        "三头臂屈伸": "#f39c12", # 黄色
        "侧平举": "#9b59b6",    # 紫色
        "颈前推举": "#1abc9c",  # 青色
        "左右交替抬腿": "#e67e22", # 橙色
        "高抬腿": "#16a085",   # 深青色
        "提膝下压": "#8e44ad",    # 深紫色
        "左侧提膝下压": "#8e44ad",   # 深紫色
        "右侧提膝下压": "#6c3483",    # 深紫色变种
        
        # 英文名称
        "Squat": "#3498db",      # 蓝色
        "Push Up": "#e74c3c",    # 红色
        "Sit Up": "#2ecc71",  # 绿色
        "Bicep Curl": "#f39c12", # 黄色
        "Tricep Extension": "#f39c12", # 黄色
        "Lateral Raise": "#9b59b6",    # 紫色
        "Overhead Press": "#1abc9c",  # 青色
        "Leg Raise": "#e67e22", # 橙色
        "Knee Raise": "#16a085",   # 深青色
        "Knee Press": "#8e44ad",    # 深紫色
        "Left Knee Press": "#8e44ad",   # 深紫色
        "Right Knee Press": "#6c3483"    # 深紫色变种
    }
    
    @staticmethod
    def get_window_palette():
        """获取窗口调色板"""
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(248, 249, 250))
        palette.setColor(QPalette.WindowText, QColor(52, 58, 64))
        return palette
    
    @staticmethod
    def get_global_stylesheet():
        """获取全局样式表"""
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
        """获取运动选择下拉框样式"""
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
        """获取计数器样式"""
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
        """获取成功计数器样式"""
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
        """获取角度值样式"""
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
        """获取阶段指示器样式"""
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
        """获取分组框样式"""
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
        """获取运动状态组样式"""
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
        """获取相机选择下拉框样式"""
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
        """获取增加次数按钮样式 - 绿色"""
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
        """获取减少次数按钮样式 - 橙色"""
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
        """获取重置按钮样式"""
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
        """获取确认记录按钮样式 - 蓝色"""
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
        """获取成功按钮样式 - 绿色"""
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
        """获取切换按钮样式"""
        # 为开和关状态设置不同的样式
        if checked:
            # 开启状态 - 绿色背景
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
                    padding-right: 25px; /* 留出空间给指示器 */
                    text-align: center;
                }
                QPushButton:hover {
                    background-color: #27ae60;
                }
            """
        else:
            # 关闭状态 - 灰色背景
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
                    padding-left: 25px; /* 留出空间给指示器 */
                    text-align: center;
                }
                QPushButton:hover {
                    background-color: #95a5a6;
                }
            """
