"""
菜单管理模块 - 负责菜单栏的设置和语言切换
"""

from PyQt5.QtWidgets import QAction, QActionGroup, QMenu, QMessageBox
from core.translations import Translations as T

class MenuManager:
    """菜单管理器类"""
    
    def __init__(self, main_window):
        self.main_window = main_window
    
    def setup_menu_bar(self):
        """设置菜单栏"""
        # 创建菜单栏
        menubar = self.main_window.menuBar()
        
        # 工具菜单
        tools_menu = menubar.addMenu(T.get("tools_menu"))
        
        # 骨架显示选项
        self.main_window.toggle_skeleton_action = QAction(T.get("skeleton_display"), self.main_window, checkable=True)
        self.main_window.toggle_skeleton_action.setChecked(False)  
        self.main_window.toggle_skeleton_action.triggered.connect(lambda checked: self.main_window.toggle_skeleton(checked))
        tools_menu.addAction(self.main_window.toggle_skeleton_action)
        
        # 旋转模式选项
        self.main_window.toggle_rotation_action = QAction(T.get("rotation_mode"), self.main_window, checkable=True)
        self.main_window.toggle_rotation_action.setChecked(False)
        self.main_window.toggle_rotation_action.triggered.connect(lambda checked: self.main_window.toggle_rotation(checked))
        
        # 视频文件选项
        open_action = QAction(T.get("video_file"), self.main_window)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.main_window.open_video_file)
        
        # 添加视频文件选项
        tools_menu.addAction(self.main_window.toggle_rotation_action)
        tools_menu.addSeparator()
        tools_menu.addAction(open_action)
        
        # 摄像头模式选项
        camera_mode_action = QAction(T.get("camera_mode"), self.main_window)
        camera_mode_action.triggered.connect(self.main_window.switch_to_camera_mode)
        tools_menu.addAction(camera_mode_action)
        
        # 模式菜单
        mode_menu = menubar.addMenu(T.get("mode_menu"))
        
        # 运动模式选项
        workout_mode_action = QAction(T.get("workout_mode"), self.main_window)
        workout_mode_action.triggered.connect(self.main_window.switch_to_workout_mode)
        mode_menu.addAction(workout_mode_action)
        
        # 统计模式选项
        stats_mode_action = QAction(T.get("stats_mode"), self.main_window)
        stats_mode_action.triggered.connect(self.main_window.switch_to_stats_mode)
        mode_menu.addAction(stats_mode_action)
        
        
        # 语言菜单
        language_menu = menubar.addMenu(T.get("language_menu"))
        
        # 中文选项
        self.main_window.chinese_action = QAction(T.get("chinese"), self.main_window, checkable=True)
        self.main_window.chinese_action.setChecked(T.current_language == "zh")
        self.main_window.chinese_action.triggered.connect(lambda: self.main_window.change_language("zh"))
        language_menu.addAction(self.main_window.chinese_action)
        
        # 英文选项
        self.main_window.english_action = QAction(T.get("english"), self.main_window, checkable=True)
        self.main_window.english_action.setChecked(T.current_language == "en")
        self.main_window.english_action.triggered.connect(lambda: self.main_window.change_language("en"))
        language_menu.addAction(self.main_window.english_action)

        # RUSSIAN
        self.main_window.russian_action = QAction(T.get("russian"), self.main_window, checkable=True)
        self.main_window.russian_action.setChecked(T.current_language == "ru")
        self.main_window.russian_action.triggered.connect(lambda: self.main_window.change_language("ru"))
        language_menu.addAction(self.main_window.russian_action)

        # 帮助菜单
        help_menu = menubar.addMenu(T.get("help_menu"))
        
        # 关于选项
        about_action = QAction(T.get("about"), self.main_window)
        about_action.triggered.connect(self.main_window.show_about)
        help_menu.addAction(about_action)
    
    def show_about(self):
        """显示关于对话框"""
        QMessageBox.about(self.main_window, T.get("about"), T.get("about_text"))
    
    def change_language(self, language):
        """更改界面语言"""
        if T.set_language(language):
            self.main_window.current_language = language
            
            # 更新菜单项选择状态
            self.main_window.chinese_action.setChecked(language == "zh")
            self.main_window.english_action.setChecked(language == "en")
            self.main_window.russian_action.setChecked(language == "ru")

            # 更新窗口标题
            self.main_window.setWindowTitle(T.get("app_title"))
            
            # 更新菜单文本
            self.main_window.menuBar().clear()
            self.setup_menu_bar()
            
            # 更新控制面板文本
            if hasattr(self.main_window, 'control_panel'):
                self.main_window.control_panel.update_language()
            
            # 更新统计面板文本
            if hasattr(self.main_window, 'stats_panel'):
                self.main_window.stats_panel.update_language()
            
            
            # 更新状态栏信息
            self.main_window.statusBar.showMessage(T.get("language_changed")) 