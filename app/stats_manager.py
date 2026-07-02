"""
统计管理模块 - 负责运动统计和面板管理
"""

from ui.workout_stats_panel import WorkoutStatsPanel
from core.translations import Translations as T

class StatsManager:
    """统计管理器类"""
    
    def __init__(self, main_window):
        self.main_window = main_window
    
    def init_workout_stats(self):
        """初始化运动统计面板"""
        # 创建运动统计面板
        self.main_window.stats_panel = WorkoutStatsPanel()
        if hasattr(self.main_window, "content_stack"):
            self.main_window.content_stack.addWidget(self.main_window.stats_panel)
        self.main_window.stats_panel.setVisible(False)  # 初始不可见
        
        # 设置目标
        self.main_window.stats_panel.set_goals(self.main_window.workout_tracker.get_goals())
        
        # 连接统计面板信号 - 在面板创建后连接
        self.main_window.stats_panel.goal_updated.connect(self.main_window.update_goal)
        self.main_window.stats_panel.weekly_goal_updated.connect(self.main_window.update_weekly_goal)
        self.main_window.stats_panel.month_changed.connect(self.main_window.load_month_stats)
    
    def update_today_stats(self):
        """更新今日运动统计"""
        # 获取原始数据
        today_stats_raw = self.main_window.workout_tracker.get_today_stats()
        goals = self.main_window.workout_tracker.get_goals()
        
        # 转换数据结构为UI组件期望的格式
        today_stats = {
            "exercises": {}
        }
        
        for exercise, count in today_stats_raw.items():
            today_stats["exercises"][exercise] = {"count": count}
        
        # 更新UI
        self.main_window.stats_panel.update_today_stats(today_stats, goals)
    
    def update_stats_overview(self):
        """更新所有统计概览"""
        # 获取数据
        weekly_stats = self.main_window.workout_tracker.get_weekly_stats()
        monthly_stats = self.main_window.workout_tracker.get_monthly_stats()
        goals = self.main_window.workout_tracker.get_goals()
        
        # 更新到UI
        self.main_window.stats_panel.update_week_stats(weekly_stats, goals)
        self.main_window.stats_panel.update_month_stats(monthly_stats, goals)
    
    def load_month_stats(self, year, month):
        """加载指定月份的统计数据
        
        Args:
            year: 年份
            month: 月份
        """
        try:
            # 获取指定月份的数据
            monthly_stats = self.main_window.workout_tracker.get_monthly_stats(year, month)
            goals = self.main_window.workout_tracker.get_goals()
            
            # 更新月度统计面板
            self.main_window.stats_panel.update_month_stats(monthly_stats, goals)
        except Exception as e:
            print(f"Error loading monthly data: {e}")
            self.main_window.statusBar.showMessage(f"Failed to load monthly data: {str(e)}")
    
    def update_goal(self, exercise_type, count):
        """更新运动目标"""
        self.main_window.workout_tracker.update_goal(exercise_type, count)
        self.main_window.update_today_stats()
        self.main_window.statusBar.showMessage(f"Updated {self.main_window.control_panel.exercise_display_map.get(exercise_type, exercise_type)} goal to {count}")
    
    def update_weekly_goal(self, count):
        """更新周目标"""
        self.main_window.workout_tracker.update_weekly_goal(count)
        self.main_window.update_stats_overview()
        self.main_window.statusBar.showMessage(f"Updated weekly fitness goal to {count} days") 
