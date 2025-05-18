from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QFrame, QSpinBox, QScrollArea, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor

from .base_components import StyledGroupBox
from core.translations import Translations as T

class GoalsTab(QWidget):
    """目标设置选项卡"""
    
    # 定义信号
    goal_updated = pyqtSignal(str, int)  # 运动类型, 目标值
    weekly_goal_updated = pyqtSignal(int)  # 每周健身天数
    
    def __init__(self, exercise_name_map, exercise_colors, parent=None):
        super().__init__(parent)
        self.exercise_name_map = exercise_name_map
        self.exercise_colors = exercise_colors
        self.exercise_code_map = {v: k for k, v in exercise_name_map.items()}
        
        # 初始化组件引用字典
        self.goal_spinboxes = {}
        self.exercise_name_labels = {}
        self.target_labels = {}
        
        # 设置布局
        self.setup_ui()
        
    def setup_ui(self):
        """设置 UI 组件"""
        layout = QVBoxLayout(self)
        
        # 每日运动目标
        self.daily_group = StyledGroupBox(T.get("daily_goals"))
        daily_layout = QVBoxLayout(self.daily_group)
        daily_layout.setContentsMargins(15, 20, 15, 15)  # 增加内边距
        
        # 创建滚动区域
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
        
        # 创建容器来放置目标项
        container_widget = QWidget()
        container_layout = QVBoxLayout(container_widget)
        container_layout.setSpacing(20)  # 增加项目间间距
        container_layout.setContentsMargins(10, 10, 15, 10)  # 适当的内边距
        
        # 创建每种运动的目标设置
        for i, (exercise_code, exercise_name) in enumerate(self.exercise_name_map.items()):
            color = self.exercise_colors.get(exercise_name, "#3498db")
            
            # 创建与前面有间隔的分隔线（第一项除外）
            if i > 0:
                separator = QFrame()
                separator.setFrameShape(QFrame.HLine)
                separator.setFrameShadow(QFrame.Sunken)
                separator.setStyleSheet("background-color: #e0e0e0; min-height: 1px; margin: 10px 0;")
                container_layout.addWidget(separator)
            
            # 创建容器小部件来放置水平布局
            goal_widget = QWidget()
            goal_layout = QHBoxLayout(goal_widget)
            goal_layout.setContentsMargins(5, 5, 5, 5)
            goal_layout.setSpacing(15)  # 增加元素间距
            
            # 运动类型标签
            exercise_label = QLabel(exercise_name)
            exercise_label.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 18pt;")
            # 保存对标签的引用
            self.exercise_name_labels[exercise_code] = exercise_label
            goal_layout.addWidget(exercise_label)
            
            # 目标定义标签
            self.target_labels[exercise_code] = QLabel(T.get("daily_goals") + ":")
            self.target_labels[exercise_code].setStyleSheet("font-size: 16pt;")
            self.target_labels[exercise_code].setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            goal_layout.addStretch(1)  # 添加弹性空间
            goal_layout.addWidget(self.target_labels[exercise_code])
            
            # 目标值输入
            spinbox = QSpinBox()
            spinbox.setRange(0, 500)
            spinbox.setSingleStep(5)
            spinbox.setFixedWidth(120)
            spinbox.setFixedHeight(40)
            spinbox.setButtonSymbols(QSpinBox.PlusMinus)
            spinbox.valueChanged.connect(lambda value, code=exercise_code: self.goal_updated.emit(code, value))
            
            # 改进样式
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
            
            # 保存引用
            self.goal_spinboxes[exercise_code] = spinbox
            
            # 将包含水平布局的容器小部件添加到容器布局
            container_layout.addWidget(goal_widget)
        
        # 添加弹性空间，确保内容向上对齐
        container_layout.addStretch()
        
        # 设置滚动区域的内容
        scroll_area.setWidget(container_widget)
        
        # 设置滚动区域的高度限制
        scroll_area.setMinimumHeight(380)  # 最小高度
        scroll_area.setMaximumHeight(500)  # 最大高度
        
        # 将滚动区域添加到主布局
        daily_layout.addWidget(scroll_area)
        
        # 每周目标
        self.weekly_group = StyledGroupBox(T.get("weekly_goals"))
        weekly_layout = QHBoxLayout(self.weekly_group)
        weekly_layout.setContentsMargins(15, 20, 15, 15)  # 增加内边距
        
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
        weekly_layout.addStretch(1)  # 添加弹性空间
        weekly_layout.addWidget(self.weekly_spinbox)
        
        # 添加到主布局
        layout.addWidget(self.daily_group, 4)  # 分配较大的空间
        layout.addWidget(self.weekly_group, 1)  # 分配较小的空间
    
    def update_language(self, exercise_name_map=None, exercise_code_map=None):
        """更新界面语言"""
        if exercise_name_map:
            self.exercise_name_map = exercise_name_map
            self.exercise_code_map = {v: k for k, v in exercise_name_map.items()}
            
            # 更新颜色映射
            new_exercise_colors = {}
            for code, name in self.exercise_name_map.items():
                # 直接使用代码作为键，而不是名称
                if code in self.exercise_colors:
                    new_exercise_colors[name] = self.exercise_colors[code]
                    
            # 更新颜色字典
            self.exercise_colors = new_exercise_colors
            
        # 更新组件标题
        self.daily_group.setTitle(T.get("daily_goals"))
        self.weekly_group.setTitle(T.get("weekly_goals"))
        
        # 更新目标定义标签
        for exercise_code in self.target_labels.keys():
            self.target_labels[exercise_code].setText(T.get("daily_goals") + ":")
        
        # 更新每周目标标签
        self.weekly_label.setText(T.get("days_per_week") + ":")
        
        # 直接使用保存的标签引用更新运动名称
        for exercise_code, label in self.exercise_name_labels.items():
            if exercise_code in self.exercise_name_map:
                exercise_name = self.exercise_name_map[exercise_code]
                color = self.exercise_colors.get(exercise_name, "#3498db")
                
                # 更新标签文本和样式
                label.setText(exercise_name)
                label.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 18pt;")
    
    def set_goals(self, goals):
        """设置目标值"""
        # 设置每日目标
        for exercise_code, spinbox in self.goal_spinboxes.items():
            spinbox.setValue(goals["daily"].get(exercise_code, 0))
        
        # 设置每周目标
        self.weekly_spinbox.setValue(goals["weekly"]["total_workouts"])
