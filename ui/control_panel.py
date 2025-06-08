from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QComboBox, QGroupBox)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont
from .styles import AppStyles
from .custom_widgets import SwitchControl
from core.translations import Translations as T

class ControlPanel(QWidget):
    """控制面板组件"""
    
    # 定义信号
    exercise_changed = pyqtSignal(str)
    counter_reset = pyqtSignal()
    camera_changed = pyqtSignal(int)
    rotation_toggled = pyqtSignal(bool)
    skeleton_toggled = pyqtSignal(bool)
    counter_increase = pyqtSignal(int)
    counter_decrease = pyqtSignal(int)
    record_confirmed = pyqtSignal(str)
    model_changed = pyqtSignal(str)  # 添加模型切换信号
    mirror_toggled = pyqtSignal(bool)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.exercise_colors = AppStyles.EXERCISE_COLORS
        
        # 初始化运动类型映射
        self.exercise_display_map = {
            "overhead_press": T.get("overhead_press"),
            "bicep_curl": T.get("bicep_curl"),
            "squat": T.get("squat"),
            "pushup": T.get("pushup"),
            "situp": T.get("situp"),
            "lateral_raise": T.get("lateral_raise"),
            "leg_raise": T.get("leg_raise"),
            "knee_raise": T.get("knee_raise"),
            "left_knee_press": T.get("left_knee_press"),
            "right_knee_press": T.get("right_knee_press")
        }
        
        # 初始化模型类型映射 - 只保留RTMPose选项
        self.model_display_map = {
            "lightweight": T.get("lightweight"),
            "balanced": T.get("balanced"),
            "performance": T.get("performance")
        }
        
        # 初始化反向映射
        self.exercise_code_map = {v: k for k, v in self.exercise_display_map.items()}
        self.current_exercise = "overhead_press"
        
        # 设置布局
        self.layout = QVBoxLayout(self)
        self.setup_ui()
    
    def setup_ui(self):
        """设置控制面板UI"""
        # 应用标题
        self.title_label = QLabel(T.get("app_title"))
        self.title_label.setFont(QFont("Arial", 20, QFont.Bold))
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 25pt; font-weight: bold; color: #2c3e50; margin-bottom: 15px;")
        self.layout.addWidget(self.title_label)
        
        # 添加信息组
        self.setup_info_group()
        
        # 添加控制选项组
        self.setup_controls_group()
        
        # 添加阶段显示组
        self.setup_phase_group()
        
        # 添加弹性空间
        self.layout.addStretch()
    
    def setup_info_group(self):
        """设置运动信息组"""
        self.info_group = QGroupBox(T.get("exercise_data"))
        self.info_group.setStyleSheet(AppStyles.get_group_box_style())
        info_layout = QVBoxLayout(self.info_group)
        
        # 创建计数器显示
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
        
        # 添加间隔
        spacer = QWidget()
        spacer.setMinimumHeight(10)
        info_layout.addWidget(spacer)
        
        # 角度显示 - 注释掉这部分代码
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
        """设置控制选项组"""
        self.controls_group = QGroupBox(T.get("control_options"))
        self.controls_group.setStyleSheet(AppStyles.get_group_box_style())
        controls_layout = QVBoxLayout(self.controls_group)
        controls_layout.setSpacing(12)  # 增加整体布局间距
        
        # 运动类型选择
        exercise_layout = QHBoxLayout()
        self.exercise_label = QLabel(T.get("exercise_type"))
        self.exercise_label.setStyleSheet("color: #2c3e50; font-size: 16pt; font-weight: bold;")  # 减小字体大小
        self.exercise_combo = QComboBox()
        
        # 设置下拉菜单的样式
        self.exercise_combo.setStyleSheet(AppStyles.get_exercise_combo_style())
        
        # 使用我们已经定义好的运动类型映射
        for code, display in self.exercise_display_map.items():
            self.exercise_combo.addItem(display)
        
        # 设置默认选中项
        overhead_press_text = self.exercise_display_map.get("overhead_press", "")
        if overhead_press_text:
            self.exercise_combo.setCurrentText(overhead_press_text)
            
        self.exercise_combo.currentTextChanged.connect(self._on_exercise_changed)
        
        exercise_layout.addWidget(self.exercise_label)
        exercise_layout.addWidget(self.exercise_combo, 1)
        controls_layout.addLayout(exercise_layout)
        
        # 模型选择
        model_layout = QHBoxLayout()
        self.model_label = QLabel(T.get("model_type"))
        self.model_label.setStyleSheet("color: #2c3e50; font-size: 16pt; font-weight: bold;")  # 减小字体大小
        
        self.model_combo = QComboBox()
        self.model_combo.setStyleSheet(AppStyles.get_exercise_combo_style())
        
        # 添加模型选项
        for model_code, model_display in self.model_display_map.items():
            self.model_combo.addItem(model_display, model_code)
            
        # 设置默认模型为RTMPose平衡模式
        rtmpose_balanced_index = list(self.model_display_map.keys()).index("balanced")
        self.model_combo.setCurrentIndex(rtmpose_balanced_index)
        self.model_combo.currentIndexChanged.connect(self._on_model_changed)
        
        model_layout.addWidget(self.model_label)
        model_layout.addWidget(self.model_combo, 1)
        controls_layout.addLayout(model_layout)
        
        # 摄像头选择
        camera_layout = QHBoxLayout()
        self.camera_label = QLabel(T.get("camera"))
        self.camera_label.setStyleSheet("color: #2c3e50; font-size: 16pt; font-weight: bold;")  # 减小字体大小
        
        self.camera_combo = QComboBox()
        self.camera_combo.addItems(["0", "1"])
        self.camera_combo.currentIndexChanged.connect(self._on_camera_changed)
        self.camera_combo.setStyleSheet(AppStyles.get_camera_combo_style())
        
        camera_layout.addWidget(self.camera_label)
        camera_layout.addWidget(self.camera_combo, 1)
        
        # 添加间隔
        spacer = QWidget()
        spacer.setMinimumHeight(5)
        controls_layout.addWidget(spacer)
        
        controls_layout.addLayout(camera_layout)
        
        # 竖屏模式切换
        self.rotation_switch = SwitchControl(T.get("rotation_mode"))
        self.rotation_switch.switched.connect(self._on_rotation_toggled)
        controls_layout.addWidget(self.rotation_switch)
        
        # 骨架显示切换
        self.skeleton_switch = SwitchControl(T.get("skeleton_display"))
        self.skeleton_switch.switched.connect(self._on_skeleton_toggled)
        controls_layout.addWidget(self.skeleton_switch)
        
        # 镜像模式切换
        self.mirror_switch = SwitchControl(T.get("mirror_mode"))
        self.mirror_switch.switched.connect(self._on_mirror_toggled)
        controls_layout.addWidget(self.mirror_switch)
        
        # 添加间隔
        spacer = QWidget()
        spacer.setMinimumHeight(5)
        controls_layout.addWidget(spacer)
        
        # 计数操作按钮行
        counter_buttons_layout = QHBoxLayout()
        # 减少次数按钮 - 橙红色
        self.decrease_button = QPushButton(T.get("decrease"))
        self.decrease_button.setFixedSize(80, 32)
        self.decrease_button.setStyleSheet(AppStyles.get_decrease_button_style())
        self.decrease_button.clicked.connect(self._on_decrease_counter)
        counter_buttons_layout.addWidget(self.decrease_button)

        # 增加次数按钮 - 绿色
        self.increase_button = QPushButton(T.get("increase"))
        self.increase_button.setFixedSize(80, 32)
        self.increase_button.setStyleSheet(AppStyles.get_increase_button_style())
        self.increase_button.clicked.connect(self._on_increase_counter)
        counter_buttons_layout.addWidget(self.increase_button)
        
        # 计数归零按钮 - 灰色
        self.reset_button = QPushButton(T.get("reset"))
        self.reset_button.setFixedSize(80, 32)
        self.reset_button.setStyleSheet(AppStyles.get_reset_button_style())
        self.reset_button.clicked.connect(self._on_reset_counter)
        counter_buttons_layout.addWidget(self.reset_button)

        # 确认记录按钮 - 蓝色系
        self.confirm_button = QPushButton(T.get("confirm"))
        self.confirm_button.setFixedSize(80, 32)
        self.confirm_button.setStyleSheet(AppStyles.get_confirm_button_style())
        self.confirm_button.clicked.connect(self._on_confirm_record)
        counter_buttons_layout.addWidget(self.confirm_button)

        controls_layout.addLayout(counter_buttons_layout)
        
        self.layout.addWidget(self.controls_group)
    
    def _on_increase_counter(self):
        """手动增加计数器值"""
        try:
            # 获取当前计数值
            current_count = int(self.counter_value.text())
            
            # 每次增加 1 次
            new_count = current_count + 1
            
            # 更新显示
            self.counter_value.setText(str(new_count))
            
            # 发送信号
            self.counter_increase.emit(new_count)
            
            # 显示成功动画
            self.show_success_animation()
            
        except ValueError:
            # 如果计数值不是有效数字，重置为 1
            self.counter_value.setText("1")
            self.counter_increase.emit(1)

    def _on_decrease_counter(self):
        """手动减少计数器值"""
        try:
            # 获取当前计数值
            current_count = int(self.counter_value.text())
            
            # 确保计数不会为负
            new_count = max(0, current_count - 1)
            
            # 更新显示
            self.counter_value.setText(str(new_count))
            
            # 发送信号
            self.counter_decrease.emit(new_count)
            
            # 更新样式
            self.update_counter_style()
            
        except ValueError:
            # 如果计数值不是有效数字，重置为 0
            self.counter_value.setText("0")
            self.counter_decrease.emit(0)

    def _on_confirm_record(self):
        """确认记录当前运动结果"""
        try:
            # 获取当前计数值
            current_count = int(self.counter_value.text())
            
            # 只有当计数大于 0 时才记录
            if current_count > 0:
                # 发送确认记录信号，带上当前运动类型
                self.record_confirmed.emit(self.current_exercise)
                
                # 显示成功样式 - 将背景修改为绿色
                self.confirm_button.setStyleSheet(
                    AppStyles.get_success_button_style()
                )
                
                # 1.5秒后恢复正常样式
                QTimer.singleShot(1500, lambda: self.confirm_button.setStyleSheet(
                    AppStyles.get_confirm_button_style()
                ))
                
        except ValueError:
            # 如果计数值不是有效数字，直接忽略
            pass
    
    def setup_phase_group(self):
        """设置阶段显示组"""
        self.phase_group = QGroupBox(T.get("phase_display"))
        self.phase_group.setStyleSheet(AppStyles.get_group_box_style())
        phase_layout = QVBoxLayout(self.phase_group)
        
        # 当前阶段标签
        phase_label_layout = QHBoxLayout()
        self.phase_title = QLabel(T.get("current_phase"))
        self.phase_title.setStyleSheet("color: #2c3e50; font-size: 20pt; font-weight: bold;")
        
        phase_label_layout.addWidget(self.phase_title)
        phase_layout.addLayout(phase_label_layout)
        
        # 创建轮廓图示器
        phase_indicator = QHBoxLayout()
        
        # 当前阶段图示
        self.up_indicator = QLabel("↑")
        self.up_indicator.setStyleSheet(AppStyles.get_phase_indicator_style(False))
        self.up_indicator.setAlignment(Qt.AlignCenter)
        
        self.down_indicator = QLabel("↓")
        self.down_indicator.setStyleSheet(AppStyles.get_phase_indicator_style(False))
        self.down_indicator.setAlignment(Qt.AlignCenter)
        
        # 添加到布局
        phase_indicator.addWidget(self.up_indicator)
        phase_indicator.addWidget(self.down_indicator)
        
        # 添加到布局
        phase_layout.addLayout(phase_indicator)
        
        # 阶段值显示
        self.stage_value = QLabel(T.get("prepare"))
        self.stage_value.setStyleSheet("color: #3498db; font-size: 24pt; font-weight: bold;")
        self.stage_value.setAlignment(Qt.AlignCenter)
        self.stage_value.setFixedSize(180, 60)
        
        # 添加当前阶段标签
        phase_text_layout = QHBoxLayout()
        phase_text_layout.addWidget(self.stage_value, 0, Qt.AlignCenter)
        
        phase_layout.addLayout(phase_text_layout)
        
        # 给相位情况留出一些额外空间
        spacer = QWidget()
        spacer.setMinimumHeight(20)
        phase_layout.addWidget(spacer)
        
        self.layout.addWidget(self.phase_group)
    
    def _on_exercise_changed(self, exercise_display):
        """运动类型更改处理"""
        # 检查exercise_display是否为空或不在映射中
        if not exercise_display or exercise_display not in self.exercise_code_map:
            return
            
        exercise_code = self.exercise_code_map[exercise_display]
        self.current_exercise = exercise_code
        self.exercise_changed.emit(exercise_code)
        self.update_counter_style()
    
    def _on_reset_counter(self):
        """重置计数器处理"""
        self.counter_reset.emit()
    
    def _on_camera_changed(self, index):
        """摄像头更改处理"""
        self.camera_changed.emit(index)
    
    def _on_rotation_toggled(self, checked):
        """旋转模式切换处理"""
        # 发送信号
        self.rotation_toggled.emit(checked)
    
    def _on_skeleton_toggled(self, checked):
        """骨架显示切换处理"""
        # 发送信号
        self.skeleton_toggled.emit(checked)
    
    def _on_model_changed(self, index):
        """RTMPose模式改变处理"""
        # 获取当前选中的模式
        model_mode = self.model_combo.currentData()
        # 发出信号通知主应用程序
        self.model_changed.emit(model_mode)
    
    def _on_mirror_toggled(self, checked):
        """镜像模式切换处理"""
        self.mirror_toggled.emit(checked)
    
    def update_counter(self, value):
        """更新计数值"""
        old_count = int(self.counter_value.text() or "0")
        new_count = int(value)
        
        # 更新计数器显示
        self.counter_value.setText(str(value))
        
        # 如果是增加，显示动画
        if new_count > old_count:
            self.show_success_animation()
    
    def update_angle(self, angle_text, exercise_type=None):
        """更新角度显示"""
        if exercise_type:
            # 设置角度文本
            self.angle_value.setText(f"{angle_text}°")
            
            # 根据角度值和运动类型更新颜色
            try:
                current_exercise = self.exercise_display_map.get(exercise_type, "bicep_curl")
                current_color = self.exercise_colors.get(current_exercise, "#3498db")
                
                # 确定是否需要高亮显示
                highlight = False
                angle_value = float(angle_text)
                
                if exercise_type == "squat" and angle_value < 120:  # 深蹲下限点
                    highlight = True
                elif exercise_type == "pushup" and angle_value < 100:  # 俱卧撞下限点
                    highlight = True
                elif exercise_type == "leg_raise" and angle_value > 90:  # 抬腿上限点
                    highlight = True
                elif exercise_type == "knee_raise" and angle_value > 100:  # 提膝上限点
                    highlight = True
                elif exercise_type == "knee_press" and (angle_value < 100 or angle_value > 160):  # 提膝下压的关键点
                    highlight = True
                
                # 设置样式
                self.angle_value.setStyleSheet(AppStyles.get_angle_value_style(current_color, highlight))
            except Exception as e:
                print(f"更新角度样式时出错: {e}")
    
    def update_phase(self, stage):
        """更新阶段显示"""
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
        """更新运动阶段"""
        if not stage:
            return
            
        self.stage_value.setText(stage)
        
        try:
            # 更新阶段指示器
            current_exercise = self.exercise_display_map.get(exercise_type, "")
            
            # 如果找不到对应的预设颜色，使用默认颜色
            if current_exercise in AppStyles.EXERCISE_COLORS:
                current_color = AppStyles.EXERCISE_COLORS[current_exercise]
            else:
                current_color = "#3498db"  # 默认使用蓝色
            
            if stage == "up":
                self.up_indicator.setStyleSheet(AppStyles.get_phase_indicator_style(True, current_color))
                self.down_indicator.setStyleSheet(AppStyles.get_phase_indicator_style(False))
            elif stage == "down":
                self.down_indicator.setStyleSheet(AppStyles.get_phase_indicator_style(True, current_color))
                self.up_indicator.setStyleSheet(AppStyles.get_phase_indicator_style(False))
        except Exception as e:
            print(f"Error in update_stage: {e}")
            # 出错时使用默认颜色
            current_color = "#3498db"
    
    def show_success_animation(self):
        """显示计数增加的成功动画"""
        self.counter_value.setStyleSheet(AppStyles.get_success_counter_style())
    
    def update_counter_style(self):
        """更新计数器样式为当前运动的颜色"""
        try:
            # 获取当前运动类型的显示名称
            current_exercise = self.exercise_display_map.get(self.current_exercise, "")
            
            # 如果找不到对应的预设颜色，使用默认颜色
            if current_exercise in AppStyles.EXERCISE_COLORS:
                current_color = AppStyles.EXERCISE_COLORS[current_exercise]
            else:
                current_color = "#3498db"  # 默认使用蓝色
                
            self.counter_value.setStyleSheet(AppStyles.get_counter_value_style(current_color))
        except Exception as e:
            print(f"Error in update_counter_style: {e}")
            # 出错时使用默认颜色
            self.counter_value.setStyleSheet(AppStyles.get_counter_value_style("#3498db"))
    
    def reset_counter_style(self):
        """重置计数器样式"""
        try:
            # 获取当前运动类型的显示名称
            current_exercise = self.exercise_display_map.get(self.current_exercise, "")
            
            # 如果找不到对应的预设颜色，使用默认颜色
            if current_exercise in AppStyles.EXERCISE_COLORS:
                current_color = AppStyles.EXERCISE_COLORS[current_exercise]
            else:
                current_color = "#3498db"  # 默认使用蓝色
                
            self.counter_value.setStyleSheet(AppStyles.get_counter_value_style(current_color))
        except Exception as e:
            print(f"Error in reset_counter_style: {e}")
            # 出错时使用默认颜色
            self.counter_value.setStyleSheet(AppStyles.get_counter_value_style("#3498db"))
        
    def update_language(self):
        """更新界面语言"""
        # 更新运动类型映射
        self.exercise_display_map = {
            "overhead_press": T.get("overhead_press"),
            "bicep_curl": T.get("bicep_curl"),
            "squat": T.get("squat"),
            "pushup": T.get("pushup"),
            "situp": T.get("situp"),
            "lateral_raise": T.get("lateral_raise"),
            "leg_raise": T.get("leg_raise"),
            "knee_raise": T.get("knee_raise"),
            "left_knee_press": T.get("left_knee_press"),
            "right_knee_press": T.get("right_knee_press")
        }
        
        # 更新模型类型映射
        self.model_display_map = {
            "lightweight": T.get("lightweight"),
            "balanced": T.get("balanced"),
            "performance": T.get("performance")
        }
        
        # 更新反向映射
        self.exercise_code_map = {v: k for k, v in self.exercise_display_map.items()}
        
        # 更新UI文本
        self.title_label.setText(T.get("app_title"))
        self.controls_group.setTitle(T.get("control_options"))
        self.info_group.setTitle(T.get("exercise_data"))
        self.phase_group.setTitle(T.get("motion_detection"))
        
        self.counter_label.setText(T.get("count_completed"))
        self.exercise_label.setText(T.get("exercise_type"))
        self.model_label.setText(T.get("model_type"))  
        self.camera_label.setText(T.get("camera"))
        
        # 更新开关文本
        self.rotation_switch.label.setText(T.get("rotation_mode"))
        self.skeleton_switch.label.setText(T.get("skeleton_display"))
        self.mirror_switch.label.setText(T.get("mirror_mode"))
        
        # 更新按钮文本
        self.increase_button.setText(T.get("increase"))
        self.decrease_button.setText(T.get("decrease"))
        self.reset_button.setText(T.get("reset"))
        self.confirm_button.setText(T.get("confirm"))
        
        # 更新阶段标签
        self.phase_title.setText(T.get(self.current_phase) if hasattr(self, "current_phase") else "")
        
        # 更新组合框
        self._update_combo_items(self.exercise_combo, self.exercise_display_map)
        self._update_combo_items(self.model_combo, self.model_display_map)  # 更新模型选择框

    def _update_combo_items(self, combo_box, item_map):
        """更新组合框内容"""
        # 保存当前选择的数据
        current_data = combo_box.currentData()
        current_text = combo_box.currentText()
        
        # 清空组合框
        combo_box.clear()
        
        # 重新填充选项
        for code, display in item_map.items():
            combo_box.addItem(display, code)
        
        # 尝试恢复先前选中的项
        if current_data:
            # 如果有数据，根据数据恢复
            for i in range(combo_box.count()):
                if combo_box.itemData(i) == current_data:
                    combo_box.setCurrentIndex(i)
                    break
        elif current_text:
            # 否则尝试根据文本恢复
            for i in range(combo_box.count()):
                if combo_box.itemText(i) == current_text:
                    combo_box.setCurrentIndex(i)
                    break
