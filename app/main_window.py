"""
主窗口类 - 负责基本的UI设置和信号连接
"""

import sys
import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
                             QStatusBar, QMessageBox, QAction, QActionGroup, QMenu, QFileDialog,
                             QLabel, QFrame, QScrollArea, QSplitter, QStackedLayout, QSizePolicy)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap

from core.video_thread import VideoThread
from core.rtmpose_processor import RTMPoseProcessor
from core.sound_manager import SoundManager
from core.workout_tracker import WorkoutTracker
from core.translations import Translations as T
from exercise_counters import ExerciseCounter
from ui.video_display import VideoDisplay
from ui.control_panel import ControlPanel, WorkoutStatusRail
from ui.workout_stats_panel import WorkoutStatsPanel
from ui.styles import AppStyles

from .mode_manager import ModeManager
from .menu_manager import MenuManager
from .stats_manager import StatsManager
from .video_processor import VideoProcessor
from .counter_manager import CounterManager

class WorkoutTrackerApp(QMainWindow):
    """AI Fitness Assistant Main Window Class"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle(T.get("app_title"))
        self.setMinimumSize(980, 660)
        self.resize(1260, 820)
        
        # 初始化核心组件
        self._init_core_components()
        self._init_video_preferences()
        
        # 初始化管理器
        self._init_managers()
        
        # 创建UI
        self.setup_ui()
        
        # 初始化视频线程
        self.setup_video_thread()
        
        # 创建动画定时器
        self.setup_animation_timer()
        
        # 初始化面板
        self._init_panels()
        
        # 开始视频处理
        self.start_video()
        
        # 初始化状态变量
        self._init_state_variables()
        
        # 显示欢迎消息
        self.statusBar.showMessage(f"{T.get('welcome')} - RTMPose ({self.model_mode}) on {self.device}")
    
    @staticmethod
    def _register_nvidia_dll_dirs():
        """Add pip-installed NVIDIA package DLL directories to PATH so onnxruntime can find CUDA libs"""
        try:
            import nvidia
            nvidia_root = os.path.dirname(nvidia.__file__)
            paths_to_add = []
            for pkg in os.listdir(nvidia_root):
                bin_dir = os.path.join(nvidia_root, pkg, 'bin')
                if os.path.isdir(bin_dir):
                    paths_to_add.append(bin_dir)
            if paths_to_add:
                os.environ['PATH'] = ';'.join(paths_to_add) + ';' + os.environ.get('PATH', '')
                print(f"Added {len(paths_to_add)} NVIDIA DLL directories to PATH")
        except ImportError:
            pass  # No pip-installed nvidia packages
        except Exception as e:
            print(f"Warning: Failed to register NVIDIA DLL dirs: {e}")

    def _asset_path(self, filename):
        """Return an asset path that works in development and PyInstaller builds."""
        if getattr(sys, "frozen", False):
            base_dir = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_dir, "assets", filename)

    def _detect_device(self):
        """Detect available inference device by testing CUDA session creation"""
        self._register_nvidia_dll_dirs()
        try:
            import onnxruntime as ort
            if 'CUDAExecutionProvider' not in ort.get_available_providers():
                print("CUDAExecutionProvider not listed, using CPU")
                return 'cpu'
            # get_available_providers() lists CUDA even when CUDA toolkit is missing.
            # Actually try to create a session with CUDA to verify it works.
            det_model = os.path.join('./models', 'yolox_nano_8xb8-300e_humanart-40f6f0d0.onnx')
            if not os.path.exists(det_model):
                print("No local model for CUDA test, using CPU")
                return 'cpu'
            sess_options = ort.SessionOptions()
            sess_options.log_severity_level = 4  # FATAL only
            # Suppress onnxruntime's C++ stderr output during the CUDA probe
            # sys.stderr redirect doesn't work because onnxruntime writes at C level
            devnull_fd = os.open(os.devnull, os.O_WRONLY)
            old_stderr_fd = os.dup(2)
            os.dup2(devnull_fd, 2)
            try:
                sess = ort.InferenceSession(
                    det_model, sess_options,
                    providers=['CUDAExecutionProvider']
                )
                active_providers = sess.get_providers()
                del sess
            finally:
                os.dup2(old_stderr_fd, 2)
                os.close(old_stderr_fd)
                os.close(devnull_fd)
            if 'CUDAExecutionProvider' in active_providers:
                print("CUDA GPU verified, defaulting to CPU inference")
                self.gpu_available = True
                return 'cpu'
            else:
                print("CUDA runtime not available, using CPU")
                self.gpu_available = False
                return 'cpu'
        except Exception as e:
            print(f"CUDA detection failed: {e}")
            self.gpu_available = False
        print("Using CPU inference")
        return 'cpu'

    def _init_core_components(self):
        """初始化核心组件"""
        # 设备设置 - 自动检测GPU
        self.gpu_available = False
        self.device = self._detect_device()
        self.model_mode = 'balanced'
        
        # 创建运动计数器
        self.exercise_counter = ExerciseCounter()
        
        # 初始化RTMPose姿态处理器
        print(f"Initializing RTMPose processor (mode: {self.model_mode}, device: {self.device})")
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
        
        # 创建运动追踪器
        self.workout_tracker = WorkoutTracker()

    def _init_video_preferences(self):
        """Keep camera state stable across model/device reloads."""
        self.current_camera_id = 0
        self.rotation_mode = True
        self.mirror_mode = True
        self.current_video_file = None
        self.is_camera_source = True
        
    
    def _init_managers(self):
        """初始化管理器"""
        # 模式管理器
        self.mode_manager = ModeManager(self)
        
        # 菜单管理器
        self.menu_manager = MenuManager(self)
        
        
        # 统计管理器
        self.stats_manager = StatsManager(self)
        
        # 视频处理器
        self.video_processor = VideoProcessor(self)
        
        # 计数器管理器
        self.counter_manager = CounterManager(self)
    
    def _init_panels(self):
        """初始化面板"""
        # 初始化运动统计面板
        self.stats_manager.init_workout_stats()

        # 设置GPU开关初始状态
        gpu_available = getattr(self, "gpu_available", False)
        self.control_panel.set_gpu_available(gpu_available)
        
    
    def _init_state_variables(self):
        """初始化状态变量"""
        # 当前计数值
        if getattr(self, '_state_initialized', False):
            return
        self._state_initialized = True
        self.current_count = 0
        
        # 手动计数追踪
        self.manual_count = 0
        
        # 重置操作标志
        self.is_resetting = False
        
        # 默认不显示运动统计面板
        self.stats_panel.setVisible(False)
        
        # 镜像模式相关属性
        self.mirror_mode = True
    
    def _setup_legacy_ui(self):
        """设置用户界面"""
        # 应用样式
        self.setPalette(AppStyles.get_window_palette())
        self.setStyleSheet(AppStyles.get_global_stylesheet())
        
        # 创建主窗口布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(18, 18, 18, 14)
        main_layout.setSpacing(18)
        
        # 创建左侧区域（视频和运动统计）
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # 添加视频显示区域
        self.video_display = VideoDisplay()
        left_layout.addWidget(self.video_display)
        
        # 创建右侧区域（仅控制面板）
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # 添加控制面板
        self.control_panel = ControlPanel()
        right_layout.addWidget(self.control_panel)
        
        # 添加拉伸以将控制面板推到顶部
        right_layout.addStretch()
        
        # 将左侧区域和右侧部件添加到主布局
        main_layout.addWidget(left_widget, 7)  # 为左侧区域分配70%空间
        main_layout.addWidget(right_widget, 3)  # 为右侧区域分配30%空间
        
        # 添加状态栏
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage(T.get("ready"))
        
        # 设置菜单栏
        self.menu_manager.setup_menu_bar()
        
        # 连接控制面板信号
        self.connect_signals()
    
    def setup_ui(self):
        """Build the desktop training workbench."""
        self.setPalette(AppStyles.get_window_palette())
        self.setStyleSheet(AppStyles.get_global_stylesheet())

        central_widget = QWidget()
        central_widget.setObjectName("RootSurface")
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(16, 14, 16, 12)
        main_layout.setSpacing(12)

        self.top_bar = QFrame()
        self.top_bar.setObjectName("TopBar")
        top_layout = QHBoxLayout(self.top_bar)
        top_layout.setContentsMargins(14, 8, 14, 8)
        top_layout.setSpacing(12)

        self.logo_label = QLabel()
        self.logo_label.setObjectName("BrandLogo")
        self.logo_label.setFixedSize(44, 44)
        self.logo_label.setAlignment(Qt.AlignCenter)
        logo_pixmap = QPixmap(self._asset_path("Logo.png"))
        if not logo_pixmap.isNull():
            self.logo_label.setPixmap(
                logo_pixmap.scaled(34, 34, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
        else:
            self.logo_label.setText("G")

        brand_layout = QVBoxLayout()
        brand_layout.setContentsMargins(0, 0, 0, 0)
        brand_layout.setSpacing(1)

        self.brand_label = QLabel("Good-GYM")
        self.brand_label.setObjectName("BrandLabel")
        self.brand_subtitle = QLabel(T.get("app_subtitle"))
        self.brand_subtitle.setObjectName("MutedLabel")
        brand_layout.addWidget(self.brand_label)
        brand_layout.addWidget(self.brand_subtitle)

        top_layout.addWidget(self.logo_label)
        top_layout.addLayout(brand_layout)
        top_layout.addStretch()
        main_layout.addWidget(self.top_bar)

        self.content_stack = QStackedLayout()
        self.content_stack.setContentsMargins(0, 0, 0, 0)
        main_layout.addLayout(self.content_stack, 1)

        self.workout_view = QWidget()
        self.workout_view.setObjectName("WorkoutView")
        workout_layout = QVBoxLayout(self.workout_view)
        workout_layout.setContentsMargins(0, 0, 0, 0)
        workout_layout.setSpacing(10)

        self.workout_body = QSplitter(Qt.Horizontal)
        self.workout_body.setObjectName("WorkoutSplitter")
        self.workout_body.setChildrenCollapsible(False)
        self.workout_body.setHandleWidth(8)

        self.video_shell = QFrame()
        self.video_shell.setObjectName("VideoShell")
        self.video_shell.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        video_layout = QVBoxLayout(self.video_shell)
        video_layout.setContentsMargins(12, 12, 12, 12)
        video_layout.setSpacing(10)

        video_header = QFrame()
        video_header.setObjectName("VideoHeader")
        video_header_layout = QHBoxLayout(video_header)
        video_header_layout.setContentsMargins(4, 0, 4, 0)

        self.video_title_label = QLabel(T.get("camera_feed"))
        self.video_title_label.setObjectName("SectionTitle")
        self.video_hint_label = QLabel(T.get("tracking_status"))
        self.video_hint_label.setObjectName("MutedLabel")

        video_header_layout.addWidget(self.video_title_label)
        video_header_layout.addStretch()
        video_header_layout.addWidget(self.video_hint_label)
        video_layout.addWidget(video_header)

        self.video_display = VideoDisplay()
        video_layout.addWidget(self.video_display, 1)

        self.status_rail = WorkoutStatusRail()
        self.control_panel = ControlPanel()

        self.workout_body.addWidget(self.video_shell)
        self.workout_body.addWidget(self.status_rail)
        self.workout_body.setStretchFactor(0, 1)
        self.workout_body.setStretchFactor(1, 0)
        self.workout_body.setSizes([980, 230])

        workout_layout.addWidget(self.workout_body, 1)
        workout_layout.addWidget(self.control_panel, 0)
        self.content_stack.addWidget(self.workout_view)

        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage(T.get("ready"))

        self.menu_manager.setup_menu_bar()
        self.connect_signals()

    def connect_signals(self):
        """连接信号和槽"""
        # 连接控制面板信号
        self.control_panel.exercise_changed.connect(self.change_exercise)
        self.control_panel.counter_reset.connect(self.reset_counter)
        self.control_panel.camera_changed.connect(self.change_camera)
        self.control_panel.rotation_toggled.connect(self.toggle_rotation)
        self.control_panel.skeleton_toggled.connect(self.toggle_skeleton)
        self.control_panel.model_changed.connect(self.change_model)
        self.control_panel.mirror_toggled.connect(self.toggle_mirror)
        self.control_panel.device_changed.connect(self.change_device)

        # 连接新按钮信号
        self.control_panel.counter_increase.connect(self.increase_counter)
        self.control_panel.counter_decrease.connect(self.decrease_counter)
        self.control_panel.record_confirmed.connect(self.confirm_record)
        
        # 连接统计面板信号
        if hasattr(self, 'stats_panel'):
            self.stats_panel.goal_updated.connect(self.update_goal)
            self.stats_panel.weekly_goal_updated.connect(self.update_weekly_goal)
            self.stats_panel.month_changed.connect(self.load_month_stats)
    
    def setup_video_thread(self):
        """设置视频处理线程"""
        # 设置双分辨率：UI显示高分辨率，模型推理低分辨率
        camera_id = getattr(self, "current_camera_id", 0)
        rotate = getattr(self, "rotation_mode", True)
        self.video_thread = VideoThread(
            camera_id=camera_id,
            rotate=rotate,
            display_width=1280,
            display_height=720,
            inference_width=640,
            inference_height=360
        )
        
        # 设置主窗口引用，用于存储推理帧
        self.video_thread.main_window = self
        self.video_thread.set_mirror(getattr(self, "mirror_mode", True))
        if hasattr(self, "video_display"):
            self.video_display.set_orientation(portrait_mode=rotate)
        
        self.video_thread.change_pixmap_signal.connect(self.update_image)
        
        # 初始化FPS值和推理帧
        self.current_fps = 0
        self.current_inference_frame = None

    def update_runtime_badge(self):
        """Runtime badges were removed from the header."""
        return

    def update_language(self):
        """Refresh static shell labels after switching language."""
        if hasattr(self, "brand_subtitle"):
            self.brand_subtitle.setText(T.get("app_subtitle"))
        if hasattr(self, "video_title_label"):
            self.video_title_label.setText(T.get("camera_feed"))
        if hasattr(self, "video_hint_label"):
            self.video_hint_label.setText(T.get("tracking_status"))
    
    def setup_animation_timer(self):
        """设置动画定时器"""
        self.count_animation_timer = QTimer()
        self.count_animation_timer.setSingleShot(True)
        self.count_animation_timer.timeout.connect(self.control_panel.reset_counter_style)
    
    def start_video(self):
        """开始视频处理"""
        if not hasattr(self, 'current_count'):
            self._init_state_variables()
        self.video_thread.set_rotation(getattr(self, "rotation_mode", True))
        self.video_thread.set_mirror(self.mirror_mode)
        if not self.video_thread.isRunning():
            self.video_thread.start()
    
    def update_image(self, frame, inference_frame=None, fps=0):
        """更新图像显示并处理姿态检测"""
        try:
            self.video_processor.update_image(frame, inference_frame, fps)
        finally:
            if hasattr(self.video_thread, "mark_frame_processed"):
                self.video_thread.mark_frame_processed()
    
    def change_exercise(self, exercise_type):
        """更改运动类型"""
        self.counter_manager.change_exercise(exercise_type)
    
    def reset_counter(self):
        """重置计数器"""
        self.counter_manager.reset_counter()
    
    def reset_exercise_state(self):
        """重置运动状态"""
        self.counter_manager.reset_exercise_state()
    
    def increase_counter(self, new_count):
        """手动增加计数器值"""
        self.counter_manager.increase_counter(new_count)
    
    def decrease_counter(self, new_count):
        """手动减少计数器值"""
        self.counter_manager.decrease_counter(new_count)
    
    def confirm_record(self, exercise_type):
        """确认记录当前计数结果到历史记录"""
        self.counter_manager.confirm_record(exercise_type)
    
    def change_camera(self, index):
        """切换摄像头"""
        self.video_processor.change_camera(index)
    
    def toggle_rotation(self, rotate):
        """切换视频旋转模式"""
        self.video_processor.toggle_rotation(rotate)
    
    def toggle_skeleton(self, show):
        """切换骨架显示"""
        self.video_processor.toggle_skeleton(show)
    
    def toggle_mirror(self, mirror):
        """切换镜像模式"""
        self.video_processor.toggle_mirror(mirror)
    
    def open_video_file(self):
        """打开视频文件"""
        self.video_processor.open_video_file()
    
    def switch_to_camera_mode(self):
        """切换回摄像头模式"""
        self.video_processor.switch_to_camera_mode()
    
    def change_device(self, device):
        """切换推理设备 (cpu/cuda)"""
        self.video_processor.change_device(device)

    def change_model(self, model_mode):
        """切换RTMPose模型模式"""
        self.video_processor.change_model(model_mode)
    
    def switch_to_workout_mode(self):
        """切换到运动模式"""
        self.mode_manager.switch_to_workout_mode()
    
    def switch_to_stats_mode(self):
        """切换到统计管理模式"""
        self.mode_manager.switch_to_stats_mode()
    
    def switch_to_voice_control_mode(self):
        """切换到语音控制模式"""
        self.mode_manager.switch_to_voice_control_mode()
    
    def show_about(self):
        """显示关于对话框"""
        self.menu_manager.show_about()
    
    def change_language(self, language):
        """更改界面语言"""
        self.menu_manager.change_language(language)
    
    def update_today_stats(self):
        """更新今日运动统计"""
        self.stats_manager.update_today_stats()
    
    def update_stats_overview(self):
        """更新所有统计概览"""
        self.stats_manager.update_stats_overview()
    
    def load_month_stats(self, year, month):
        """加载指定月份的统计数据"""
        self.stats_manager.load_month_stats(year, month)
    
    def update_goal(self, exercise_type, count):
        """更新运动目标"""
        self.stats_manager.update_goal(exercise_type, count)
    
    def update_weekly_goal(self, count):
        """更新周目标"""
        self.stats_manager.update_weekly_goal(count)
    
    def closeEvent(self, event):
        """关闭窗口时清理资源"""
        if self.video_thread.isRunning():
            self.video_thread.stop()
        
        
        event.accept() 
