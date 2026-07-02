"""
模式管理模块 - 负责不同模式之间的切换
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import QTimer
from core.translations import Translations as T

class ModeManager:
    """模式管理器类"""
    
    def __init__(self, main_window):
        self.main_window = main_window

    def switch_to_workout_mode(self):
        """Switch to the camera training workspace."""
        if self.main_window.video_thread.isRunning():
            self.main_window.video_thread.stop()
            self.main_window.video_thread.wait()

        self.main_window.setup_video_thread()
        self.main_window.video_display.setVisible(True)
        if hasattr(self.main_window, "control_scroll"):
            self.main_window.control_scroll.setVisible(True)
        if hasattr(self.main_window, "control_panel"):
            self.main_window.control_panel.setVisible(True)
        if hasattr(self.main_window, "status_rail"):
            self.main_window.status_rail.setVisible(True)
        self.main_window.workout_view.setVisible(True)
        self.main_window.content_stack.setCurrentWidget(self.main_window.workout_view)

        self.main_window.toggle_skeleton_action.setEnabled(True)
        self.main_window.toggle_rotation_action.setEnabled(True)

        QTimer.singleShot(500, self.main_window.start_video)
        self.main_window.statusBar.showMessage(T.get("switched_to_workout"))

    def switch_to_stats_mode(self):
        """Switch to the statistics workspace."""
        self.main_window.video_thread.stop()

        if hasattr(self.main_window, "stats_panel"):
            self.main_window.content_stack.setCurrentWidget(self.main_window.stats_panel)
            self.main_window.stats_panel.setVisible(True)

        self.main_window.toggle_skeleton_action.setEnabled(False)
        self.main_window.toggle_rotation_action.setEnabled(False)

        self.main_window.update_today_stats()
        self.main_window.update_stats_overview()
        self.main_window.stats_panel.tabs.setCurrentIndex(0)
        self.main_window.statusBar.showMessage(T.get("switched_to_stats"))
    
    def _switch_to_workout_mode_legacy(self):
        """切换到运动模式（显示摄像头和控制面板）"""
        
        # 隐藏统计面板
        if self.main_window.stats_panel.isVisible():
            self.main_window.stats_panel.setVisible(False)
        
        # 等待视频线程完全停止
        if self.main_window.video_thread.isRunning():
            self.main_window.video_thread.stop()
            self.main_window.video_thread.wait()  # 等待线程完全终止
        
        # 重新初始化视频线程
        self.main_window.setup_video_thread()
        
        # 清除主布局
        central_widget = self.main_window.centralWidget()
        main_layout = central_widget.layout()
        
        # 清除所有现有部件
        while main_layout.count():
            item = main_layout.takeAt(0)
            if item.widget():
                widget = item.widget()
                if widget == self.main_window.stats_panel:
                    widget.setVisible(False)
        
        # 创建左侧区域（视频显示）
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # 添加视频显示区域
        self.main_window.video_display.setVisible(True)
        left_layout.addWidget(self.main_window.video_display)
        
        # 将左侧区域和控制面板添加到主布局
        self.main_window.control_panel.setVisible(True)
        main_layout.addWidget(left_widget, 7)  # 为左侧区域分配70%空间
        main_layout.addWidget(self.main_window.control_panel, 3)  # 为控制面板分配30%空间
        
        # 启用相关菜单项
        self.main_window.toggle_skeleton_action.setEnabled(True)
        self.main_window.toggle_rotation_action.setEnabled(True)
        
        # 恢复视频显示高度
        self.main_window.video_display.setMinimumHeight(400)
        
        # 开始视频处理
        QTimer.singleShot(500, self.main_window.start_video)  # 延迟500ms后开始视频
        
        # 更新状态栏
        self.main_window.statusBar.showMessage(T.get("switched_to_workout"))
    
    def _switch_to_stats_mode_legacy(self):
        """切换到统计管理模式（全屏显示统计面板）"""
        
        # 隐藏视频显示区域和控制面板
        self.main_window.video_display.setVisible(False)
        self.main_window.control_panel.setVisible(False)
        
        # 停止视频源以节省资源
        self.main_window.video_thread.stop()
        
        # 查找主界面中心部件
        central_widget = self.main_window.centralWidget()
        main_layout = central_widget.layout()
        
        # 清除现有布局中的左右部分
        while main_layout.count():
            item = main_layout.takeAt(0)
            if item.widget():
                widget = item.widget()
                widget.setVisible(False)
        
        # 将统计面板直接添加到主布局
        main_layout.addWidget(self.main_window.stats_panel)
        
        # 显示运动统计面板
        self.main_window.stats_panel.setVisible(True)
        
        # 禁用相关菜单项
        self.main_window.toggle_skeleton_action.setEnabled(False)
        self.main_window.toggle_rotation_action.setEnabled(False)
        
        # 刷新统计数据
        self.main_window.update_today_stats()
        self.main_window.update_stats_overview()
        
        # 切换到"今日进度"标签页
        self.main_window.stats_panel.tabs.setCurrentIndex(0)  
        
        # 更新状态栏
        self.main_window.statusBar.showMessage(T.get("switched_to_stats"))
    
 
