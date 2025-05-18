from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QGridLayout, QTableWidgetItem)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

from .base_components import StyledGroupBox, DayCircleIndicator, StyledStatsTable
from core.translations import Translations as T

class WeekStatsTab(QWidget):
    """本周统计选项卡"""
    
    def __init__(self, exercise_name_map, exercise_colors, parent=None):
        super().__init__(parent)
        self.exercise_name_map = exercise_name_map
        self.exercise_colors = exercise_colors
        
        # 保存最后一次的运动数据
        self.last_exercise_data = {}
        
        # 设置布局
        self.setup_ui()
        
    def setup_ui(self):
        """设置UI组件"""
        layout = QVBoxLayout(self)
        
        # 创建周统计组件
        self.week_group = StyledGroupBox(T.get("weekly_progress"))
        week_layout = QVBoxLayout(self.week_group)
        
        # 创建健身天数和进度条
        self.summary_group = StyledGroupBox(T.get("weekly_workout_days"))
        summary_layout = QGridLayout(self.summary_group)
        
        # 添加标签
        self.day_label = QLabel(T.get("days_per_week") + ":")
        self.day_label.setStyleSheet("font-family: 'Microsoft YaHei'; font-size: 16px; font-weight: bold;")
        summary_layout.addWidget(self.day_label, 0, 0)
        self.week_days_label = QLabel("0 / 7")
        self.week_days_label.setStyleSheet("color: #27ae60; font-family: 'Microsoft YaHei'; font-size: 16px; font-weight: bold;")  # 使用绿色字体
        summary_layout.addWidget(self.week_days_label, 0, 1)
        
        self.progress_label = QLabel(T.get("weekly_progress") + ":")
        self.progress_label.setStyleSheet("font-family: 'Microsoft YaHei'; font-size: 16px; font-weight: bold;")
        summary_layout.addWidget(self.progress_label, 1, 0)
        
        # 添加7个圆圈进度指示器
        self.week_circle_indicator = DayCircleIndicator(
            active_color="#27ae60",    # 完成的圆圈使用绿色
            inactive_color="#bdc3c7", # 未开始的圆圈使用灰色
            partial_color="#a5ebc8"    # 部分完成的圆圈使用浅绿色
        )
        summary_layout.addWidget(self.week_circle_indicator, 1, 1)
        
        week_layout.addWidget(self.summary_group)
        
        # 本周运动统计表格
        self.stats_group = StyledGroupBox(T.get("week_stats"))
        stats_layout = QVBoxLayout(self.stats_group)
        
        # 创建数据表格 - 注意我们在update_language中更新表头
        self.table_headers = [T.get("exercise_type"), T.get("count_completed")]
        self.week_stats_table = StyledStatsTable(self.table_headers)
        stats_layout.addWidget(self.week_stats_table)
        
        week_layout.addWidget(self.stats_group)
        
        # 添加到主布局
        layout.addWidget(self.week_group)

    def update_language(self, exercise_name_map=None, exercise_code_map=None):
        """更新界面语言"""
        if exercise_name_map:
            self.exercise_name_map = exercise_name_map
            
        # 更新组件标题
        self.week_group.setTitle(T.get("weekly_progress"))
        self.summary_group.setTitle(T.get("weekly_workout_days"))
        self.stats_group.setTitle(T.get("week_stats"))
        
        # 更新标签文本
        self.day_label.setText(T.get("days_per_week") + ":")
        self.progress_label.setText(T.get("weekly_progress") + ":")
        
        # 更新表格标题
        self.table_headers = [T.get("exercise_type"), T.get("count_completed")]
        for col, header in enumerate(self.table_headers):
            self.week_stats_table.setHorizontalHeaderItem(col, QTableWidgetItem(header))
        
        # 如果有保存的数据，直接使用它来重新填充表格
        if hasattr(self, 'last_exercise_data') and self.last_exercise_data:
            self.week_stats_table.setRowCount(len(self.last_exercise_data))
            row = 0
            for exercise_code, count in self.last_exercise_data.items():
                if exercise_code in self.exercise_name_map:
                    # 更新运动名称
                    exercise_name = self.exercise_name_map[exercise_code]
                    name_item = QTableWidgetItem(exercise_name)
                    color = self.exercise_colors.get(exercise_name, "#3498db")
                    name_item.setBackground(QColor(color).lighter(180))
                    self.week_stats_table.setItem(row, 0, name_item)
                    
                    # 添加计数
                    count_item = QTableWidgetItem(str(count))
                    count_item.setTextAlignment(Qt.AlignCenter)
                    self.week_stats_table.setItem(row, 1, count_item)
                    
                    row += 1
    
    def update_stats(self, stats, goals):
        """更新本周统计数据"""
        try:
            # 保存原始数据，以便语言切换时恢复
            self.last_stats = stats
            self.last_goals = goals
            
            # 更新健身天数
            days_worked_out = stats.get("days_worked_out", 0)
            weekly_goal = goals["weekly"]["total_workouts"]
            self.week_days_label.setText(f"{days_worked_out} / {weekly_goal}")
            
            # 获取每日目标完成情况
            daily_goals = goals.get("daily", {})
            weekday_data = stats.get("weekday_data", {})
            
            if daily_goals and weekday_data:
                # 初始化每天的完成状态数组，周一到周日
                # 0=未开始，1=部分完成，2=完全完成
                day_status = [0, 0, 0, 0, 0, 0, 0]
                
                # 遍历星期一到星期日
                for weekday, day_info in weekday_data.items():
                    day_exercises = day_info["exercises"]
                    
                    if not day_exercises:  # 如果没有运动数据，跳过
                        continue
                    
                    # 筛选有效的目标（不为0）
                    valid_goals = {ex: count for ex, count in daily_goals.items() if count > 0}
                    total_goal_exercises = len(valid_goals)
                    
                    if total_goal_exercises == 0:
                        continue  # 跳过没有目标的日期
                    
                    # 统计达成目标的运动数量
                    completed_exercises = 0
                    has_partial = False
                    
                    # 统计不同运动的完成情况
                    completed = []
                    partial_completed = []
                    
                    for ex, goal_count in valid_goals.items():
                        actual_count = day_exercises.get(ex, 0)  # 实际完成的次数
                        
                        if actual_count >= goal_count:
                            completed_exercises += 1  # 该运动达到目标
                            completed.append(f"{ex}({actual_count}/{goal_count})")
                        elif actual_count > 0:
                            has_partial = True  # 部分完成该运动
                            partial_completed.append(f"{ex}({actual_count}/{goal_count})")
                    
                    # 设置当天的状态
                    if completed_exercises == total_goal_exercises:
                        day_status[int(weekday)] = 2  # 完全完成
                    elif completed_exercises > 0 or has_partial:
                        day_status[int(weekday)] = 1  # 部分完成
                
            # 设置圆圈进度（按周几顺序）
            self.week_circle_indicator.setDayStatus(day_status)
            
            # 更新运动统计表格
            exercise_stats = stats.get("exercises", {})
            self.week_stats_table.setRowCount(0)  # 清除现有数据
            
            # 如果有运动数据
            if exercise_stats:
                row = 0
                self.week_stats_table.setRowCount(len(exercise_stats))
                
                # 清空并重新保存数据
                self.last_exercise_data = {}
                
                for exercise_code, count in exercise_stats.items():
                    if exercise_code in self.exercise_name_map:
                        # 保存数据到字典
                        self.last_exercise_data[exercise_code] = count
                        
                        # 运动类型
                        exercise_name = self.exercise_name_map[exercise_code]
                        name_item = QTableWidgetItem(exercise_name)
                        color = self.exercise_colors.get(exercise_name, "#3498db")
                        name_item.setBackground(QColor(color).lighter(180))
                        self.week_stats_table.setItem(row, 0, name_item)
                        
                        # 完成次数
                        count_item = QTableWidgetItem(str(count))
                        count_item.setTextAlignment(Qt.AlignCenter)
                        self.week_stats_table.setItem(row, 1, count_item)
                        
                        row += 1
        except Exception as e:
            print(f"更新周统计时出错: {str(e)}")
