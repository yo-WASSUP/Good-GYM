from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QFrame, QScrollArea, QSizePolicy, QProgressBar)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

from .base_components import StyledGroupBox
from core.translations import Translations as T

class TodayProgressTab(QWidget):
    """今日进度选项卡"""
    
    def __init__(self, exercise_name_map, exercise_colors, parent=None):
        super().__init__(parent)
        self.exercise_name_map = exercise_name_map
        self.exercise_colors = exercise_colors
        
        # 初始化组件引用字典
        self.progress_bars = {}
        self.count_labels = {}
        self.exercise_frames = {}
        self.exercise_name_labels = {}
        self.exercise_layouts = {}
        
        # 设置布局
        self.setup_ui()
        
        # 默认所有运动项均隐藏，等待设置目标时显示
        self.hide_all_exercises()
        
    def setup_ui(self):
        """设置 UI 组件"""
        layout = QVBoxLayout(self)
        
        # 创建今日进度组件
        self.progress_group = StyledGroupBox(T.get("today_exercise_progress"))
        progress_layout = QVBoxLayout(self.progress_group)
        progress_layout.setContentsMargins(15, 20, 15, 15)  # 增加组框内边距
        
        # 创建没有目标时显示的消息标签
        self.no_goals_label = QLabel(T.get("no_goals_message") if hasattr(T, "get") and callable(getattr(T, "get")) else "未设置任何运动目标")
        self.no_goals_label.setAlignment(Qt.AlignCenter)
        self.no_goals_label.setStyleSheet("color: #7f8c8d; font-size: 16pt; margin: 20px;")
        self.no_goals_label.setVisible(False)  # 默认隐藏，等待检查目标后决定显示
        progress_layout.addWidget(self.no_goals_label)
        
        # 创建滚动区域和内容容器
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
        
        # 创建容器小部件来放置进度项
        container_widget = QWidget()
        container_layout = QVBoxLayout(container_widget)
        container_layout.setSpacing(20)  # 大幅增加项目间间距
        container_layout.setContentsMargins(10, 10, 15, 10)  # 增加全局内边距
        
        # 为每种运动创建进度条
        for i, (exercise_code, exercise_name) in enumerate(self.exercise_name_map.items()):
            # 获取运动的颜色
            color = self.exercise_colors.get(exercise_name, "#3498db")
            
            # 创建与前面有间隔的分隔线（第一项除外）
            if i > 0:
                separator = QFrame()
                separator.setFrameShape(QFrame.HLine)
                separator.setFrameShadow(QFrame.Sunken)
                separator.setStyleSheet("background-color: #e0e0e0; min-height: 1px; margin: 10px 0;")
                container_layout.addWidget(separator)
            
            # 创建运动项容器并记录引用
            exercise_frame = QFrame()
            exercise_frame.setObjectName(f"frame_{exercise_code}")
            exercise_frame.setStyleSheet("background-color: transparent;")
            self.exercise_frames[exercise_code] = exercise_frame
            
            # 创建垂直布局
            item_layout = QVBoxLayout(exercise_frame)
            item_layout.setSpacing(6)  # 紧凑的元素间距
            item_layout.setContentsMargins(5, 5, 5, 10)  # 适当的内边距
            
            # 保存布局引用
            self.exercise_layouts[exercise_code] = item_layout
            
            # 将运动项容器添加到容器布局
            container_layout.addWidget(exercise_frame)
            
            # 标题和当前计数在同一行 - 使用QWidget作为容器
            header_widget = QWidget()
            header_layout = QHBoxLayout(header_widget)
            header_layout.setContentsMargins(0, 0, 0, 0)  # 无边距
            header_layout.setSpacing(10)  # 元素间距
            
            # 运动名称标签
            label = QLabel(exercise_name)
            label.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 18pt;")
            # 保存对标签的引用
            self.exercise_name_labels[exercise_code] = label
            
            # 计数标签
            count_label = QLabel("0 / 0")
            count_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            count_label.setStyleSheet("color: #2c3e50; font-size: 18pt;")
            
            # 将标签和计数添加到布局
            header_layout.addWidget(label)
            header_layout.addStretch(1)
            header_layout.addWidget(count_label)
            
            # 添加标题小部件到项目布局
            item_layout.addWidget(header_widget)
            
            # 进度条
            progress_bar = QProgressBar()
            progress_bar.setRange(0, 100)
            progress_bar.setValue(0)
            progress_bar.setFormat("%p%")  # 显示百分比
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
            
            # 添加进度条到项目布局
            item_layout.addWidget(progress_bar)
            
            # 注意：不需要这里的addLayout，因为exercise_frame已经被addWidget到container_layout
            
            # 记录引用
            self.progress_bars[exercise_code] = progress_bar
            self.count_labels[exercise_code] = count_label
            
        # 添加弹性空间，确保内容向上对齐
        container_layout.addStretch()
        
        # 设置滚动区域的内容
        scroll_area.setWidget(container_widget)
        
        # 设置滚动区域的高度限制，确保不会占用过多空间
        scroll_area.setMinimumHeight(380)  # 增加最小高度以显示更多内容
        scroll_area.setMaximumHeight(500)  # 增加最大高度
        
        # 将滚动区域添加到主布局
        progress_layout.addWidget(scroll_area)
        
        # 今日运动总计 - 使用更醒目的样式
        self.total_group = StyledGroupBox(T.get("today_total"))
        total_layout = QVBoxLayout(self.total_group)
        total_layout.setContentsMargins(15, 20, 15, 15)
        
        # 总计标签
        total_label = QLabel(T.get("total_completion").format(count=0))
        total_label.setAlignment(Qt.AlignCenter)
        total_label.setStyleSheet("color: #2c3e50; margin: 10px 0; padding: 10px; background-color: #f0f7ff; border-radius: 8px; font-size: 18pt;")
        total_layout.addWidget(total_label)
        
        # 记录引用
        self.total_label = total_label
        
        # 添加到主布局
        layout.addWidget(self.progress_group, 4)  # 分配较大的拉伸因子
        layout.addWidget(self.total_group, 1)  # 分配较小的拉伸因子
        
    def update_progress(self, exercise_code, current, goal):
        """更新运动进度"""
        if exercise_code in self.progress_bars:
            # 如果目标为0，则隐藏该运动项
            if goal <= 0:
                if exercise_code in self.exercise_frames:
                    self.exercise_frames[exercise_code].setVisible(False)
                return
                
            # 显示该运动项
            if exercise_code in self.exercise_frames:
                self.exercise_frames[exercise_code].setVisible(True)
            
            # 更新计数标签
            self.count_labels[exercise_code].setText(f"{current} / {goal}")
            
            # 更新进度条
            progress = min(100, int((current / goal) * 100)) if goal > 0 else 0
            self.progress_bars[exercise_code].setValue(progress)
            
            # 设置进度条格式
            color = self.exercise_colors.get(self.exercise_name_map[exercise_code], "#3498db")
            
            # 根据完成情况更新视觉反馈
            if progress >= 100:
                # 完成状态 - 使用成功绿色进度条
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
                # 进行中状态 - 使用原来的颜色
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
        """更新总计"""
        self.total_label.setText(T.get("total_completion").format(count=total_count))
        
    def update_language(self, exercise_name_map=None, exercise_code_map=None):
        """更新界面语言"""
        if exercise_name_map:
            self.exercise_name_map = exercise_name_map
            
            # 更新颜色映射
            new_exercise_colors = {}
            for code, name in self.exercise_name_map.items():
                # 直接使用代码作为键，而不是名称
                if code in self.exercise_colors:
                    new_exercise_colors[name] = self.exercise_colors[code]
                    
            # 更新颜色字典
            self.exercise_colors = new_exercise_colors
        
        # 更新组件标题
        self.progress_group.setTitle(T.get("today_exercise_progress"))
        self.total_group.setTitle(T.get("today_total"))
        
        # 更新总计标签
        total_count = int(self.total_label.text().split(":")[1].strip().split(" ")[0]) if ":" in self.total_label.text() else 0
        self.total_label.setText(T.get("total_completion").format(count=total_count))
        
        # 直接使用保存的标签引用更新运动名称
        for exercise_code, label in self.exercise_name_labels.items():
            if exercise_code in self.exercise_name_map:
                exercise_name = self.exercise_name_map[exercise_code]
                color = self.exercise_colors.get(exercise_name, "#3498db")
                
                # 更新标签文本和样式
                label.setText(exercise_name)
                label.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 18pt;")
    
    def hide_all_exercises(self):
        """隐藏所有运动项"""
        for exercise_code in self.exercise_frames:
            self.exercise_frames[exercise_code].setVisible(False)
        
        # 显示没有目标的提示
        self.no_goals_label.setVisible(True)
    
    def show_exercises_with_goals(self, goals):
        """显示有目标的运动项"""
        has_visible_exercises = False
        
        for exercise_code, exercise_frame in self.exercise_frames.items():
            goal = goals.get(exercise_code, 0)
            if goal > 0:
                exercise_frame.setVisible(True)
                has_visible_exercises = True
                
                # 更新计数标签显示目标值
                if exercise_code in self.count_labels:
                    self.count_labels[exercise_code].setText(f"0 / {goal}")
            else:
                exercise_frame.setVisible(False)
        
        # 根据是否有可见的运动项决定是否显示提示
        self.no_goals_label.setVisible(not has_visible_exercises)
    
    def reset_progress(self):
        """重置所有进度"""
        for exercise_code in self.progress_bars:
            self.progress_bars[exercise_code].setValue(0)
            
            # 获取当前标签的目标值部分
            current_text = self.count_labels[exercise_code].text()
            goal_part = current_text.split("/")[1].strip() if "/" in current_text else "0"
            
            # 重置计数器显示，保留目标值
            self.count_labels[exercise_code].setText(f"0 / {goal_part}")
            
            # 重置进度条样式
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
