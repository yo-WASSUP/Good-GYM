from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTabWidget,
                             QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal
import datetime

from core.translations import Translations as T

from .stats_components.today_tab import TodayProgressTab
from .stats_components.week_tab import WeekStatsTab
from .stats_components.month_tab import MonthStatsTab
from .stats_components.goals_tab import GoalsTab
from .styles import AppStyles

class WorkoutStatsPanel(QWidget):
    """健身统计和计划面板"""
    
    # 定义信号
    goal_updated = pyqtSignal(str, int)  # 运动类型, 目标值
    weekly_goal_updated = pyqtSignal(int)  # 每周健身天数
    month_changed = pyqtSignal(int, int)  # 年份, 月份
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.exercise_colors = AppStyles.EXERCISE_COLORS
        
        # 使用翻译模块生成运动名称映射
        self.update_exercise_mappings()
        
        # 初始化UI
        self.setup_ui()
    
    def update_exercise_mappings(self):
        """更新运动名称映射"""
        self.exercise_name_map = {
            "squat": T.get("squat"),
            "pushup": T.get("pushup"),
            "situp": T.get("situp"),
            "bicep_curl": T.get("bicep_curl"),
            "lateral_raise": T.get("lateral_raise"),
            "overhead_press": T.get("overhead_press"),
            "leg_raise": T.get("leg_raise"),
            "knee_raise": T.get("knee_raise"),
            "left_knee_press": T.get("left_knee_press"),
            "right_knee_press": T.get("right_knee_press")
        }
        self.exercise_code_map = {v: k for k, v in self.exercise_name_map.items()}
    
    def setup_ui(self):
        """设置UI组件"""
        self.layout = QVBoxLayout(self)
        
        # 创建顶部标题
        self.title_label = QLabel(T.get("workout_stats_panel"))
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("color: #2c3e50; font-size: 20pt; font-weight: bold; margin: 15px 0; padding: 10px;")
        self.layout.addWidget(self.title_label)
        
        # 创建选项卡
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.North)
        self.tabs.setTabShape(QTabWidget.Rounded)
        self.tabs.setStyleSheet("""
            QTabWidget::pane { 
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                padding: 15px; 
                background-color: #f8f9fa;
            }
            QTabBar::tab {
                background-color: #ecf0f1; 
                border: 1px solid #bdc3c7;
                border-bottom: none;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
                padding: 10px 20px;
                margin-right: 3px;
                font-family: 'Microsoft YaHei';
                font-size: 16px;
                font-weight: bold;
                min-width: 150px;
            }
            QTabBar::tab:selected {
                background-color: #f8f9fa;
                border-bottom: 2px solid #3498db;
                color: #2980b9;
            }
            QTabBar::tab:hover:!selected {
                background-color: #e0e0e0;
            }
        """)
        
        # 创建统计组件
        self.today_progress_tab = TodayProgressTab(self.exercise_name_map, self.exercise_colors)
        self.week_stats_tab = WeekStatsTab(self.exercise_name_map, self.exercise_colors)
        self.month_stats_tab = MonthStatsTab(self.exercise_name_map, self.exercise_colors)
        self.goals_tab = GoalsTab(self.exercise_name_map, self.exercise_colors)
        
        # 连接目标更新信号
        self.goals_tab.goal_updated.connect(self.goal_updated)
        self.goals_tab.weekly_goal_updated.connect(self.weekly_goal_updated)
        
        # 连接月份变化信号
        self.month_stats_tab.month_changed.connect(self._on_month_changed)
        
        # 添加选项卡
        self.tabs.addTab(self.today_progress_tab, T.get("today_progress"))
        self.tabs.addTab(self.week_stats_tab, T.get("week_stats"))
        self.tabs.addTab(self.month_stats_tab, T.get("month_stats"))
        self.tabs.addTab(self.goals_tab, T.get("fitness_goals"))
        
        # 设置默认显示的tab为"今日进度"
        self.tabs.setCurrentIndex(0)
        
        self.layout.addWidget(self.tabs)
        
    def update_today_stats(self, stats, goals):
        """更新今日统计数据"""
        if "exercises" in stats:
            for exercise_code, data in stats["exercises"].items():
                if exercise_code in self.today_progress_tab.progress_bars:
                    current = data.get("count", 0)
                    goal = goals["daily"].get(exercise_code, 0)
                    self.today_progress_tab.update_progress(exercise_code, current, goal)
            
            # 更新总计
            total_count = sum(data.get("count", 0) for data in stats["exercises"].values())
            self.today_progress_tab.update_total(total_count)
    
    def update_week_stats(self, stats, goals):
        """更新本周统计数据"""
        self.week_stats_tab.update_stats(stats, goals)
    
    def update_month_stats(self, stats, goals):
        """更新本月统计数据"""
        self.month_stats_tab.update_stats(stats, goals)
    
    def set_goals(self, goals):
        """设置目标值"""
        self.goals_tab.set_goals(goals)
        
        # 将日常目标传递给今日进度标签页，显示有目标的运动项
        if hasattr(self.today_progress_tab, 'show_exercises_with_goals') and 'daily' in goals:
            self.today_progress_tab.show_exercises_with_goals(goals['daily'])
    
    def _on_month_changed(self, year, month):
        # 发出信号通知主应用程序需要获取指定月份的数据
        self.month_changed.emit(year, month)
    
    def update_language(self):
        """更新界面语言"""
        # 更新标题
        self.title_label.setText(T.get("workout_stats_panel"))
        
        # 更新运动名称映射
        self.update_exercise_mappings()
        
        # 更新标签页标题
        self.tabs.setTabText(0, T.get("today_progress"))
        self.tabs.setTabText(1, T.get("week_stats"))
        self.tabs.setTabText(2, T.get("month_stats"))
        self.tabs.setTabText(3, T.get("fitness_goals"))
        
        # 如果各标签页有update_language方法，则调用
        if hasattr(self.today_progress_tab, 'update_language'):
            self.today_progress_tab.update_language(self.exercise_name_map, self.exercise_code_map)
            
        if hasattr(self.week_stats_tab, 'update_language'):
            self.week_stats_tab.update_language(self.exercise_name_map)
            
        if hasattr(self.month_stats_tab, 'update_language'):
            self.month_stats_tab.update_language(self.exercise_name_map)
            
        if hasattr(self.goals_tab, 'update_language'):
            self.goals_tab.update_language(self.exercise_name_map)