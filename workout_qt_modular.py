import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
                             QSplitter, QStatusBar, QMessageBox, QAction, QActionGroup, QMenu, QTableWidgetItem, QFileDialog)
from PyQt5.QtCore import Qt, QTimer

# 导入自定义模块
from core.video_thread import VideoThread
from core.rtmpose_processor import RTMPoseProcessor
from core.sound_manager import SoundManager
from core.workout_tracker import WorkoutTracker
from core.translations import Translations as T
from exercise_counters import ExerciseCounter
from ui.video_display import VideoDisplay
from ui.control_panel import ControlPanel
from ui.workout_stats_panel import WorkoutStatsPanel
from ui.styles import AppStyles

class WorkoutTrackerApp(QMainWindow):
    """AI健身助手主窗口类"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle(T.get("app_title"))
        self.setMinimumSize(900, 900)
        
        # 只使用CPU设备
        self.device = 'cpu'
        
        # 设置默认模型模式
        self.model_mode = 'balanced'
        
        # 创建运动计数器实例
        self.exercise_counter = ExerciseCounter()
        
        # 初始化RTMPose姿态处理器
        print(f"初始化RTMPose处理器 (模式: {self.model_mode}, 设备: {self.device})")
        self.pose_processor = RTMPoseProcessor(
            exercise_counter=self.exercise_counter,
            mode=self.model_mode,
            backend='onnxruntime',
            device=self.device
        )
        
        # 设置默认运动类型
        self.exercise_type = "overhead_press"
        
        # 创建声音管理器
        self.sound_manager = SoundManager()
        
        # 创建运动跟踪器
        self.workout_tracker = WorkoutTracker()
        
        # 创建UI
        self.setup_ui()
        
        # 初始化视频线程
        self.setup_video_thread()
        
        # 创建计时器用于动画效果
        self.setup_animation_timer()
        
        # 初始化健身统计面板
        self.init_workout_stats()
        
        # 启动视频处理
        self.start_video()
        
        # 计数器当前值
        self.current_count = 0
        
        # 手动计数跟踪
        self.manual_count = 0
        
        # 重置操作标志，用于避免重置操作触发自动记录
        self.is_resetting = False
        
        # 默认不显示健身统计面板
        self.stats_panel.setVisible(False)
        
        # 首次启动显示欢迎信息
        self.statusBar.showMessage(f"{T.get('welcome')} - RTMPose ({self.model_mode}) on {self.device}")
        
        # 添加镜像模式相关属性
        self.mirror_mode = True
    
    def setup_ui(self):
        """设置用户界面"""
        # 应用样式
        self.setPalette(AppStyles.get_window_palette())
        self.setStyleSheet(AppStyles.get_global_stylesheet())
        
        # 创建主窗口布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # 创建左侧区域（视频和健身统计）
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # 添加视频显示部分
        self.video_display = VideoDisplay()
        left_layout.addWidget(self.video_display)
        
        # 将左侧区域添加到主布局
        main_layout.addWidget(left_widget, 7)  # 分配70%的空间给左侧区域
        
        # 添加控制面板
        self.control_panel = ControlPanel()
        main_layout.addWidget(self.control_panel, 3)  # 分配30%的空间给控制面板
        
        # 添加状态栏
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage(T.get("ready"))
        
        # 设置菜单栏
        self.setup_menu_bar()
        
        # 当前语言
        self.current_language = "zh"
        
        # 连接控制面板信号
        self.connect_signals()
    
    def connect_signals(self):
        """连接信号与槽"""
        # 连接控制面板信号
        self.control_panel.exercise_changed.connect(self.change_exercise)
        self.control_panel.counter_reset.connect(self.reset_counter)
        self.control_panel.camera_changed.connect(self.change_camera)
        self.control_panel.rotation_toggled.connect(self.toggle_rotation)
        self.control_panel.skeleton_toggled.connect(self.toggle_skeleton)
        self.control_panel.model_changed.connect(self.change_model)  # 连接模型切换信号
        self.control_panel.mirror_toggled.connect(self.toggle_mirror)
        
        # 连接新增的按钮信号
        self.control_panel.counter_increase.connect(self.increase_counter)
        self.control_panel.counter_decrease.connect(self.decrease_counter)
        self.control_panel.record_confirmed.connect(self.confirm_record)
        
        # 连接统计面板信号
        # 注意：这些需要在self.stats_panel已初始化后调用
        if hasattr(self, 'stats_panel'):
            self.stats_panel.goal_updated.connect(self.update_goal)
            self.stats_panel.weekly_goal_updated.connect(self.update_weekly_goal)
            self.stats_panel.month_changed.connect(self.load_month_stats)
    
    def setup_video_thread(self):
        """设置视频处理线程"""
        # 使用更低的分辨率以提高性能
        self.video_thread = VideoThread(
            camera_id=0,
            width=640,  # 降低分辨率到640x480
            height=360,
            rotate=True
        )
        self.video_thread.change_pixmap_signal.connect(self.update_image)
        
        # 初始化FPS值
        self.current_fps = 0
    
    def setup_animation_timer(self):
        """设置动画计时器"""
        self.count_animation_timer = QTimer()
        self.count_animation_timer.setSingleShot(True)
        self.count_animation_timer.timeout.connect(self.control_panel.reset_counter_style)
    
    def start_video(self):
        """启动视频处理"""
        self.video_thread.start()
    
    def update_image(self, frame, fps=0):
        """更新图像显示并处理姿态检测"""
        try:
            # 更新FPS值
            self.current_fps = fps
            
            # 姿态处理器处理当前帧 (每帧都处理，无跳帧)
            processed_frame, current_angle, keypoints = self.pose_processor.process_frame(
                frame, self.exercise_type
            )
            
            # 如果启用镜像模式，应用镜像处理
            if self.mirror_mode:
                import cv2
                processed_frame = cv2.flip(processed_frame, 1)
            
            # 更新视频显示
            self.video_display.update_image(processed_frame)
            
            # 更新UI组件
            self.update_ui_components(current_angle, keypoints)
            
        except Exception as e:
            print(f"更新图像时出错: {e}")
    
    def update_ui_components(self, current_angle, keypoints):
        """更新UI组件显示"""
        try:
            # 更新角度显示 - 注释掉这部分代码
            # if current_angle is not None:
            #     self.control_panel.update_angle(str(int(current_angle)), self.exercise_type)
            
            # 更新阶段显示 (上升/下降)
            if hasattr(self.exercise_counter, 'stage'):
                self.control_panel.update_phase(self.exercise_counter.stage)
            
            # 获取当前计数 - 直接使用counter属性
            current_count = self.exercise_counter.counter
            
            # 如果计数增加且不是重置操作，播放声音（但不自动记录）
            if current_count > self.current_count and not self.is_resetting:
                # 为每次计数增加播放计数声音
                self.sound_manager.play_count_sound()
                
                # 每计数10次播放成功声音
                if current_count % 10 == 0:
                    self.sound_manager.play_milestone_sound(current_count)
                    self.statusBar.showMessage(f"恭喜完成 {current_count} 次 {self.control_panel.exercise_display_map[self.exercise_type]}!")
                
                # 更新缓存的当前计数
                self.current_count = current_count
            
            # 更新计数器显示
            self.control_panel.update_counter(str(current_count))
            
            # 关键点信息已得到处理，不需要单独更新显示
        except Exception as e:
            print(f"更新图像时出错: {str(e)}")
    
    def change_exercise(self, exercise_type):
        """改变运动类型"""
        self.exercise_type = exercise_type
        self.exercise_counter.reset_counter()
        self.current_count = 0
        self.statusBar.showMessage(f"切换到{self.control_panel.exercise_display_map[exercise_type]}运动")
    
    def reset_counter(self):
        """重置计数器"""
        # 设置重置标志为真，避免触发自动记录
        self.is_resetting = True
        
        # 重置计数器
        self.exercise_counter.reset_counter()
        self.current_count = 0
        self.manual_count = 0  # 同时重置手动计数
        self.control_panel.update_counter(0)
        
        # 重置完成后恢复标志
        self.is_resetting = False
        
        self.statusBar.showMessage("已重置计数器")
    
    def reset_exercise_state(self):
        """重置运动状态，包括计数器和相关变量"""
        # 直接调用现有的重置计数器方法
        self.reset_counter()
    
    def increase_counter(self, new_count):
        """手动增加计数器值"""
        self.current_count = new_count
        # 直接更新计数器类的内部计数值
        self.exercise_counter.counter = new_count
        # 增加手动计数
        self.manual_count += 1
        self.statusBar.showMessage(f"计数增加至 {new_count} 次")
    
    def decrease_counter(self, new_count):
        """手动减少计数器值"""
        self.current_count = new_count
        # 直接更新计数器类的内部计数值
        self.exercise_counter.counter = new_count
        # 手动计数不会为负数
        if self.manual_count > 0:
            self.manual_count -= 1
        self.statusBar.showMessage(f"计数减少至 {new_count} 次")
    
    def confirm_record(self, exercise_type):
        """确认记录当前计数结果到历史记录中"""
        # 获取当前计数值（现在记录全部计数，而不仅仅是手动增加的部分）
        count = self.current_count
        
        # 记录到历史记录中
        if count > 0:
            # 添加记录到运动跟踪器
            completion_percentage = self.workout_tracker.add_workout_record(exercise_type, count)
            
            # 更新统计面板
            self.update_today_stats()
            self.update_stats_overview()
            
            # 获取运动类型的中文名称
            exercise_name = ""
            # 尝试从控制面板的映射中获取
            if exercise_type in self.control_panel.exercise_display_map:
                exercise_name = self.control_panel.exercise_display_map[exercise_type]
            
            # 显示成功消息
            self.statusBar.showMessage(f"已记录 {count} 次{exercise_name}，完成目标的 {completion_percentage}%")
            
            # 重置计数器（会同时重置 manual_count）
            self.reset_counter()
        else:
            # 如果没有手动增加的计数，显示提示信息
            self.statusBar.showMessage("没有手动增加的计数需要记录")
    
    def change_camera(self, index):
        """切换摄像头"""
        self.video_thread.set_camera(index)
        self.statusBar.showMessage(f"切换到摄像头 {index}")
    
    def toggle_rotation(self, rotate):
        """切换视频旋转模式"""
        # 更新视频线程的旋转设置
        self.video_thread.set_rotation(rotate)
        
        # 更新视频显示的方向设置
        # rotate为True表示竖屏，False表示横屏
        self.video_display.set_orientation(portrait_mode=rotate)
        
        if rotate:
            self.toggle_rotation_action.setText("关闭旋转模式")
            self.statusBar.showMessage("切换到竖屏模式 (9:16)")
        else:
            self.toggle_rotation_action.setText("开启旋转模式")
            self.statusBar.showMessage("切换到横屏模式 (16:9)")
            
    def toggle_skeleton(self, show):
        """切换骨架显示"""
        self.pose_processor.set_skeleton_visibility(show)
        if show:
            self.statusBar.showMessage("显示骨架线条")
        else:
            self.statusBar.showMessage("隐藏骨架线条")
            
    def open_video_file(self):
        """打开视频文件"""
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            T.get("open_video"),
            "",
            T.get("video_files"),
            options=options
        )
        
        if file_name:
            try:
                # 清空当前的计数状态
                self.reset_exercise_state()
                
                # 切换到运动模式（如果当前不是）
                if hasattr(self, 'stacked_layout') and hasattr(self, 'exercise_container'):
                    if not self.stacked_layout.currentWidget() == self.exercise_container:
                        self.switch_to_workout_mode()
                
                # 设置状态栏信息
                video_name = os.path.basename(file_name)
                self.statusBar.showMessage(f"当前视频: {video_name}")
                
                # 将文件路径传递给视频线程，设置为非循环播放模式
                self.video_thread.set_video_file(file_name, loop=False)
            except Exception as e:
                print(f"打开视频文件时出错: {e}")
                self.statusBar.showMessage(f"打开视频文件失败: {str(e)}")
    
    def switch_to_camera_mode(self):
        """切换回摄像头模式"""
        try:
            # 清空当前的计数状态
            self.reset_exercise_state()
            
            # 切换到运动模式（如果当前不是）
            if hasattr(self, 'stacked_layout') and hasattr(self, 'exercise_container'):
                if not self.stacked_layout.currentWidget() == self.exercise_container:
                    self.switch_to_workout_mode()
                
            # 设置状态栏信息
            self.statusBar.showMessage("当前模式: 摄像头")
            
            # 返回摄像头模式
            self.video_thread.set_camera(0)  # 使用默认摄像头
        except Exception as e:
            print(f"切换到摄像头模式时出错: {e}")
            self.statusBar.showMessage(f"切换摄像头模式失败: {str(e)}")
    
    def show_about(self):
        """显示关于信息"""
        about_text = """
        <h1>AI健身助手-GoodGYM</h1>
        <p>版本 1.1</p>
        <p>基于PyQt5和rtmpose开发的健身运动计数器应用，支持多种运动姿态识别和自动计数。</p>
        <p>特点：</p>
        <ul>
            <li>实时姿态检测和角度计算</li>
            <li>健身统计 - 跟踪您的健身进度</li>
            <li>实时帧显示和状态反馈</li>
            <li>支持多种运动类型</li>
            <li>美观的用户界面和多语言支持</li>
        </ul>
        <p>作者：Spike Don</p>
        <p>GitHub：<a href="https://github.com/yo-WASSUP/Good-GYM">Good-GYM</a></p>
        <p>小红书：<a href="https://www.xiaohongshu.com/user/profile/5fdf34b50000000001008057?xsec_token=&xsec_source=pc_note">想吃好果汁</a></p>
        """
        
        QMessageBox.about(self, T.get("about_title"), about_text)
    
    def setup_menu_bar(self):
        """设置菜单栏"""
        # 创建菜单栏
        menubar = self.menuBar()
        
        # 工具菜单
        tools_menu = menubar.addMenu(T.get("tools_menu"))
        
        # 骨架显示选项
        self.toggle_skeleton_action = QAction(T.get("skeleton_display"), self, checkable=True)
        self.toggle_skeleton_action.setChecked(False)  
        self.toggle_skeleton_action.triggered.connect(lambda checked: self.toggle_skeleton(checked))
        tools_menu.addAction(self.toggle_skeleton_action)
        
        # 旋转模式选项
        self.toggle_rotation_action = QAction(T.get("rotation_mode"), self, checkable=True)
        self.toggle_rotation_action.setChecked(False)
        self.toggle_rotation_action.triggered.connect(lambda checked: self.toggle_rotation(checked))
        
        # 视频文件选项
        open_action = QAction(T.get("video_file"), self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_video_file)
        
        # 添加视频文件选项
        tools_menu.addAction(self.toggle_rotation_action)
        tools_menu.addSeparator()
        tools_menu.addAction(open_action)
        
        # 摄像头模式选项
        camera_mode_action = QAction(T.get("camera_mode"), self)
        camera_mode_action.triggered.connect(self.switch_to_camera_mode)
        tools_menu.addAction(camera_mode_action)
        
        # 模式菜单
        mode_menu = menubar.addMenu(T.get("mode_menu"))
        
        # 健身模式选项
        workout_mode_action = QAction(T.get("workout_mode"), self)
        workout_mode_action.triggered.connect(self.switch_to_workout_mode)
        mode_menu.addAction(workout_mode_action)
        
        # 统计模式选项
        stats_mode_action = QAction(T.get("stats_mode"), self)
        stats_mode_action.triggered.connect(self.switch_to_stats_mode)
        mode_menu.addAction(stats_mode_action)
        
        # 语言菜单
        language_menu = menubar.addMenu(T.get("language_menu"))
        
        # 中文选项
        self.chinese_action = QAction(T.get("chinese"), self, checkable=True)
        self.chinese_action.setChecked(T.current_language == "zh")
        self.chinese_action.triggered.connect(lambda: self.change_language("zh"))
        language_menu.addAction(self.chinese_action)
        
        # 英文选项
        self.english_action = QAction(T.get("english"), self, checkable=True)
        self.english_action.setChecked(T.current_language == "en")
        self.english_action.triggered.connect(lambda: self.change_language("en"))
        language_menu.addAction(self.english_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu(T.get("help_menu"))
        
        # 关于选项
        about_action = QAction(T.get("about"), self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def init_workout_stats(self):
        """初始化健身统计面板"""
        # 创建健身统计面板
        self.stats_panel = WorkoutStatsPanel()
        self.stats_panel.setVisible(False)  # 初始时不显示
        
        # 设置目标
        self.stats_panel.set_goals(self.workout_tracker.get_goals())
        
        # 连接统计面板信号 - 在面板创建后连接
        self.stats_panel.goal_updated.connect(self.update_goal)
        self.stats_panel.weekly_goal_updated.connect(self.update_weekly_goal)
        self.stats_panel.month_changed.connect(self.load_month_stats)
        
        # 更新今日统计
    def update_today_stats(self):
        """更新今日健身统计"""
        # 获取原始数据
        today_stats_raw = self.workout_tracker.get_today_stats()
        goals = self.workout_tracker.get_goals()
        
        # 转换数据结构为UI组件期望的格式
        # 从 {"exercise": count} 转换为 {"exercises": {"exercise": {"count": count}}}
        today_stats = {
            "exercises": {}
        }
        
        for exercise, count in today_stats_raw.items():
            today_stats["exercises"][exercise] = {"count": count}
        
        # 更新UI
        self.stats_panel.update_today_stats(today_stats, goals)
    
    def update_stats_overview(self):
        """更新所有统计概览"""
        # 获取数据
        weekly_stats = self.workout_tracker.get_weekly_stats()
        monthly_stats = self.workout_tracker.get_monthly_stats()
        goals = self.workout_tracker.get_goals()
        
        # 更新到UI
        self.stats_panel.update_week_stats(weekly_stats, goals)
        self.stats_panel.update_month_stats(monthly_stats, goals)
    
    def load_month_stats(self, year, month):
        """加载指定月份的统计数据
        
        Args:
            year: 年份
            month: 月份
        """
        try:
            # 获取指定月份的数据
            monthly_stats = self.workout_tracker.get_monthly_stats(year, month)
            goals = self.workout_tracker.get_goals()
            
            # 更新月度统计面板
            self.stats_panel.update_month_stats(monthly_stats, goals)
        except Exception as e:
            print(f"加载月度数据时出错: {e}")
            self.statusBar.showMessage(f"加载月度数据失败: {str(e)}")
    
    def update_goal(self, exercise_type, count):
        """更新运动目标"""
        self.workout_tracker.update_goal(exercise_type, count)
        self.update_today_stats()
        self.statusBar.showMessage(f"已更新{self.control_panel.exercise_display_map.get(exercise_type, exercise_type)}的目标为 {count} 次")
    
    def update_weekly_goal(self, count):
        """更新每周目标"""
        self.workout_tracker.update_weekly_goal(count)
        self.update_stats_overview()
        self.statusBar.showMessage(f"已更新每周健身目标为 {count} 天")
    
    def switch_to_workout_mode(self):
        """切换到健身运动模式（显示摄像头和控制面板）"""
        # 隐藏统计面板
        if self.stats_panel.isVisible():
            self.stats_panel.setVisible(False)
        
        # 等待视频线程完全停止
        if self.video_thread.isRunning():
            self.video_thread.stop()
            self.video_thread.wait()  # 等待线程完全终止
        
        # 重新初始化视频线程
        self.setup_video_thread()
        
        # 清除主布局
        central_widget = self.centralWidget()
        main_layout = central_widget.layout()
        
        # 清除所有已有部件
        while main_layout.count():
            item = main_layout.takeAt(0)
            if item.widget():
                widget = item.widget()
                if widget == self.stats_panel:
                    widget.setVisible(False)
        
        # 创建左侧区域（视频显示）
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # 添加视频显示部分
        self.video_display.setVisible(True)
        left_layout.addWidget(self.video_display)
        
        # 将左侧区域和控制面板添加到主布局
        self.control_panel.setVisible(True)
        main_layout.addWidget(left_widget, 7)  # 分配70%的空间给左侧区域
        main_layout.addWidget(self.control_panel, 3)  # 分配30%的空间给控制面板
        
        # 启用相关菜单项
        self.toggle_skeleton_action.setEnabled(True)
        self.toggle_rotation_action.setEnabled(True)
        
        # 恢复视频显示高度
        self.video_display.setMinimumHeight(400)
        
        # 启动视频处理
        QTimer.singleShot(500, self.start_video)  # 延迟500毫秒再启动视频
        
        # 更新状态栏
        self.statusBar.showMessage(T.get("switched_to_workout"))
    
    def switch_to_stats_mode(self):
        """切换到统计管理模式（全屏显示统计面板）"""
        # 隐藏视频显示区域和控制面板
        self.video_display.setVisible(False)
        self.control_panel.setVisible(False)
        
        # 停止视频源以节省资源
        self.video_thread.stop()
        
        # 找到主界面的中心小部件
        central_widget = self.centralWidget()
        main_layout = central_widget.layout()
        
        # 清除现有布局中的左右部分
        while main_layout.count():
            item = main_layout.takeAt(0)
            if item.widget():
                widget = item.widget()
                widget.setVisible(False)
        
        # 将统计面板直接添加到主布局
        main_layout.addWidget(self.stats_panel)
        
        # 显示健身统计面板
        self.stats_panel.setVisible(True)
        
        # 禁用相关菜单项
        self.toggle_skeleton_action.setEnabled(False)
        self.toggle_rotation_action.setEnabled(False)
        
        # 刷新统计数据
        self.update_today_stats()
        self.update_stats_overview()
        
        # 切换到"今日进度"标签
        self.stats_panel.tabs.setCurrentIndex(0)  
        
        # 更新状态栏
        self.statusBar.showMessage(T.get("switched_to_stats"))
    
    def closeEvent(self, event):
        """关闭窗口时清理资源"""
        if self.video_thread.isRunning():
            self.video_thread.stop()
        event.accept()


    def change_language(self, language):
        """更改界面语言"""
        if T.set_language(language):
            self.current_language = language
            
            # 更新菜单项选中状态
            self.chinese_action.setChecked(language == "zh")
            self.english_action.setChecked(language == "en")
            
            # 更新窗口标题
            self.setWindowTitle(T.get("app_title"))
            
            # 更新菜单文本
            self.menuBar().clear()
            self.setup_menu_bar()
            
            # 更新控制面板文本
            if hasattr(self, 'control_panel'):
                self.control_panel.update_language()
            
            # 更新统计面板文本
            if hasattr(self, 'stats_panel'):
                self.stats_panel.update_language()
            
            # 更新状态栏信息
            self.statusBar.showMessage(T.get("language_changed"))

    def change_model(self, model_mode):
        """切换RTMPose模型模式"""
        try:
            if model_mode == self.model_mode:
                # 如果是同一个模式，不需要重新加载
                return
                
            # 停止视频处理
            self.video_thread.stop()
            
            # 显示状态信息
            self.statusBar.showMessage(f"正在切换RTMPose模式到: {model_mode}...")
            
            # 更新模型模式
            old_model_mode = self.model_mode
            self.model_mode = model_mode
            
            print(f"切换RTMPose模式: {old_model_mode} -> {model_mode}")
            
            # 更新RTMPose处理器模式
            self.pose_processor.update_model(model_mode)
            
            # 重新初始化视频线程
            self.setup_video_thread()
            
            # 重新开始视频处理
            QTimer.singleShot(500, self.start_video)  # 延迟500毫秒再启动视频
            
            # 更新状态栏
            self.statusBar.showMessage(f"已切换到RTMPose {model_mode}模式")
            
        except Exception as e:
            # 如果切换失败，显示错误信息
            error_msg = f"RTMPose模式切换失败: {str(e)}"
            self.statusBar.showMessage(error_msg)
            print(error_msg)
            
            # 尝试回退到原来的模式
            try:
                self.model_mode = old_model_mode
                self.pose_processor.update_model(old_model_mode)
                self.setup_video_thread()
                QTimer.singleShot(500, self.start_video)
                self.statusBar.showMessage(f"已回退到RTMPose {old_model_mode}模式")
                
            except:
                # 如果回退也失败，显示严重错误
                self.statusBar.showMessage("RTMPose模式切换出现严重错误")

    def toggle_mirror(self, mirror):
        """切换镜像模式"""
        self.mirror_mode = mirror


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WorkoutTrackerApp()
    window.show()
    sys.exit(app.exec_())
