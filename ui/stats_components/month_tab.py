from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QGridLayout, QTableWidgetItem, QPushButton)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor
import datetime
import calendar

from .base_components import StyledGroupBox, MonthCalendarIndicator, StyledStatsTable
from core.translations import Translations as T

class MonthStatsTab(QWidget):
    """本月统计选项卡"""
    
    # 定义信号
    month_changed = pyqtSignal(int, int)  # 月份变化时发出信号(year, month)
    
    def __init__(self, exercise_name_map, exercise_colors, parent=None):
        super().__init__(parent)
        self.exercise_name_map = exercise_name_map
        self.exercise_colors = exercise_colors
        
        # 保存最后一次的运动数据
        self.last_exercise_data = {}
        
        # 当前显示的年月
        self.current_date = datetime.date.today()
        self.current_year = self.current_date.year
        self.current_month = self.current_date.month
        
        # 最大允许查看的年月范围
        self.min_date = datetime.date(self.current_date.year - 1, 1, 1)  # 可以看前一年
        self.max_date = self.current_date  # 最多只能看到当前月份
        
        # 设置布局
        self.setup_ui()
        
    def setup_ui(self):
        """设置UI组件"""
        layout = QVBoxLayout(self)
        
        # 创建月度统计组件
        self.month_group = StyledGroupBox(T.get("monthly_progress"))
        month_layout = QVBoxLayout(self.month_group)
        
        # 获取当月天数
        days_in_month = self._get_days_in_month()
        
        # 创建月份导航组件
        month_nav_widget = QWidget()
        month_nav_layout = QHBoxLayout(month_nav_widget)
        
        # 上个月按钮
        self.prev_month_btn = QPushButton("←")
        self.prev_month_btn.setStyleSheet("""
            QPushButton { 
                font-size: 16px; 
                padding: 5px 10px; 
                background-color: #ecf0f1; 
                border: 1px solid #bdc3c7; 
                border-radius: 4px; 
            }
            QPushButton:hover { background-color: #d6dbdf; }
            QPushButton:pressed { background-color: #bdc3c7; }
        """)
        self.prev_month_btn.setFixedWidth(40)
        self.prev_month_btn.clicked.connect(self.go_to_previous_month)
        month_nav_layout.addWidget(self.prev_month_btn)
        
        # 当前月份标签
        self.month_label = QLabel(self.get_month_display_text())
        self.month_label.setAlignment(Qt.AlignCenter)
        self.month_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2980b9;")
        month_nav_layout.addWidget(self.month_label, 1)
        
        # 下个月按钮
        self.next_month_btn = QPushButton("→")
        self.next_month_btn.setStyleSheet("""
            QPushButton { 
                font-size: 16px; 
                padding: 5px 10px; 
                background-color: #ecf0f1; 
                border: 1px solid #bdc3c7; 
                border-radius: 4px; 
            }
            QPushButton:hover { background-color: #d6dbdf; }
            QPushButton:pressed { background-color: #bdc3c7; }
        """)
        self.next_month_btn.setFixedWidth(40)
        self.next_month_btn.clicked.connect(self.go_to_next_month)
        month_nav_layout.addWidget(self.next_month_btn)
        
        # 添加月份导航到布局
        month_layout.addWidget(month_nav_widget)
        
        # 创建汇总组件
        self.summary_group = StyledGroupBox(T.get("monthly_stats"))
        summary_layout = QGridLayout(self.summary_group)
        
        # 添加标签
        self.day_label = QLabel(T.get("monthly_stats") + ":")
        self.day_label.setStyleSheet("font-family: 'Microsoft YaHei'; font-size: 16px; font-weight: bold;")
        summary_layout.addWidget(self.day_label, 0, 0)
        
        self.month_days_label = QLabel("0 / 0")
        self.month_days_label.setStyleSheet("color: #27ae60; font-family: 'Microsoft YaHei'; font-size: 16px; font-weight: bold;")  # 使用红色字体
        summary_layout.addWidget(self.month_days_label, 0, 1)
        
        # 添加日历指示器
        self.month_calendar_indicator = MonthCalendarIndicator(
            days_in_month=self._get_days_in_month(),
            active_color="#27ae60",     # 完成的日期使用绿色
            inactive_color="#bdc3c7",  # 未开始的日期使用灰色
            partial_color="#a5ebc8"     # 部分完成的日期使用浅绿色
        )
        
        # 计算当前月的第一天是周几
        today = datetime.date.today()
        first_day_weekday = datetime.date(today.year, today.month, 1).weekday()
        self.month_calendar_indicator.setMonthStart(first_day_weekday)
        
        # 添加到布局
        summary_layout.addWidget(self.month_calendar_indicator, 1, 0, 1, 2)
        
        month_layout.addWidget(self.summary_group)
        
        # 本月运动统计表格
        self.stats_group = StyledGroupBox(T.get("monthly_stats"))
        stats_layout = QVBoxLayout(self.stats_group)
        
        # 创建数据表格 - 注意我们在update_language中更新表头
        self.table_headers = [T.get("exercise_type"), T.get("count_completed")]
        self.month_stats_table = StyledStatsTable(self.table_headers)
        stats_layout.addWidget(self.month_stats_table)
        
        month_layout.addWidget(self.stats_group)
        
        # 添加到主布局
        layout.addWidget(self.month_group)
    
    def _get_days_in_month(self, year=None, month=None):
        """获取指定年月的天数。默认获取当前选中的月份天数"""
        if year is None:
            year = self.current_year
        if month is None:
            month = self.current_month
            
        return calendar.monthrange(year, month)[1]
        
    def get_month_display_text(self):
        """获取月份显示文本"""
        # 中文月份名称
        chinese_months = ["\u4e00\u6708", "\u4e8c\u6708", "\u4e09\u6708", "\u56db\u6708", "\u4e94\u6708", 
                          "\u516d\u6708", "\u4e03\u6708", "\u516b\u6708", "\u4e5d\u6708", "\u5341\u6708", 
                          "\u5341\u4e00\u6708", "\u5341\u4e8c\u6708"]
        
        # 英文月份名称
        english_months = ["January", "February", "March", "April", "May", "June",
                         "July", "August", "September", "October", "November", "December"]
                         
        current_lang = T.current_language
        month_name = chinese_months[self.current_month - 1] if current_lang == "zh" else english_months[self.current_month - 1]
        
        return f"{self.current_year} {month_name}"
    
    def go_to_previous_month(self):
        """切换到上个月"""
        # 计算上个月的日期
        if self.current_month == 1:
            new_year = self.current_year - 1
            new_month = 12
        else:
            new_year = self.current_year
            new_month = self.current_month - 1
            
        # 创建新的日期对象
        new_date = datetime.date(new_year, new_month, 1)
        
        # 检查是否超出最小边界
        if new_date < self.min_date:
            return  # 不允许查看过老的数据
            
        # 更新当前选中的年月
        self.current_year = new_year
        self.current_month = new_month
        self.current_date = new_date
        
        # 更新月份显示
        self.update_month_display()
        
        # 发出信号 - 使用年和月两个整数参数
        self.month_changed.emit(self.current_year, self.current_month)
        
    def go_to_next_month(self):
        """切换到下个月"""
        # 计算下个月的日期
        if self.current_month == 12:
            new_year = self.current_year + 1
            new_month = 1
        else:
            new_year = self.current_year
            new_month = self.current_month + 1
            
        # 创建新的日期对象
        new_date = datetime.date(new_year, new_month, 1)
        
        # 检查是否超出最大边界
        if new_date > self.max_date:
            return  # 不允许查看未来的数据
            
        # 更新当前选中的年月
        self.current_year = new_year
        self.current_month = new_month
        self.current_date = new_date
        
        # 更新月份显示
        self.update_month_display()
        
        # 发出信号 - 使用年和月两个整数参数
        self.month_changed.emit(self.current_year, self.current_month)
        
    def update_month_display(self):
        """更新月份显示信息"""
        # 更新月份标签
        self.month_label.setText(self.get_month_display_text())
        
        # 更新月份天数
        days_in_month = self._get_days_in_month()
        
        # 计算选中月份的第一天是周几
        first_day_weekday = datetime.date(self.current_year, self.current_month, 1).weekday()
        self.month_calendar_indicator.setDaysInMonth(days_in_month)
        self.month_calendar_indicator.setMonthStart(first_day_weekday)
        
        # 禁用/启用导航按钮
        prev_date = datetime.date(self.current_year, self.current_month, 1)
        if self.current_month == 1:
            prev_date = datetime.date(self.current_year - 1, 12, 1)
        self.prev_month_btn.setEnabled(prev_date >= self.min_date)
        
        next_date = datetime.date(self.current_year, self.current_month, 1)
        if self.current_month == 12:
            next_date = datetime.date(self.current_year + 1, 1, 1)
        self.next_month_btn.setEnabled(next_date <= self.max_date)
        
    def update_language(self, exercise_name_map=None, exercise_code_map=None):
        """更新界面语言"""
        if exercise_name_map:
            self.exercise_name_map = exercise_name_map
            
        # 更新组件标题
        self.month_group.setTitle(T.get("monthly_progress"))
        self.summary_group.setTitle(T.get("monthly_stats"))
        self.stats_group.setTitle(T.get("monthly_stats"))
        
        # 更新标签文本
        self.day_label.setText(T.get("monthly_stats") + ":")
        
        # 更新表格标题
        self.table_headers = [T.get("exercise_type"), T.get("count_completed")]
        for col, header in enumerate(self.table_headers):
            self.month_stats_table.setHorizontalHeaderItem(col, QTableWidgetItem(header))
        
        # 如果有保存的数据，直接使用它来重新填充表格
        if hasattr(self, 'last_exercise_data') and self.last_exercise_data:
            self.month_stats_table.setRowCount(len(self.last_exercise_data))
            row = 0
            for exercise_code, count in self.last_exercise_data.items():
                if exercise_code in self.exercise_name_map:
                    # 更新运动名称
                    exercise_name = self.exercise_name_map[exercise_code]
                    name_item = QTableWidgetItem(exercise_name)
                    color = self.exercise_colors.get(exercise_name, "#3498db")
                    name_item.setBackground(QColor(color).lighter(180))
                    self.month_stats_table.setItem(row, 0, name_item)
                    
                    # 添加计数
                    count_item = QTableWidgetItem(str(count))
                    count_item.setTextAlignment(Qt.AlignCenter)
                    self.month_stats_table.setItem(row, 1, count_item)
                    
                    row += 1
    
    def update_stats(self, stats, goals):
        """更新月度统计数据"""
        try:
            # 保存原始数据，以便语言切换时恢复
            self.last_stats = stats
            self.last_goals = goals
            
            # 获取选中月份的年月字符串前缀，用于过滤数据
            year_month_prefix = f"{self.current_year}-{self.current_month:02d}-"
            
            # 采集选中月份的数据
            filtered_daily_progress = {}
            filtered_exercises = {}
            
            # 日运动进度记录
            daily_records = stats.get("daily_progress", {})
            # 日目标数据
            daily_goals = goals.get("daily", {})
            
            # 当前月有健身记录的天数
            active_days_this_month = 0
            # 收集各天状态
            status_dict = {}
            
            # 筛选有效的目标（不为0）
            valid_goals = {ex: count for ex, count in daily_goals.items() if count > 0}
            
            # 选中月份的运动数据累计
            monthly_exercise_data = {}
            
            for date_str, exercises in daily_records.items():
                # 只处理选中月份的数据
                if date_str.startswith(year_month_prefix):
                    # 累计所有运动的数据
                    for exercise_code, count in exercises.items():
                        if exercise_code in monthly_exercise_data:
                            monthly_exercise_data[exercise_code] += count
                        else:
                            monthly_exercise_data[exercise_code] = count
                    
                    # 处理当天完成状态
                    try:
                        date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")
                        day = date_obj.day  # 获取当月的第几天
                        
                        # 无论如何，有记录就算一天
                        active_days_this_month += 1
                        
                        # 如果没有设置目标，则跳过状态计算
                        if not valid_goals:
                            continue
                            
                        # 统计达成目标的运动数量
                        completed_exercises = 0
                        has_partial = False
                        
                        for ex, goal_count in valid_goals.items():
                            actual_count = exercises.get(ex, 0)
                            
                            if actual_count >= goal_count:
                                completed_exercises += 1  # 该运动达到目标
                            elif actual_count > 0:
                                has_partial = True  # 部分完成该运动
                        
                        # 设置当天的状态
                        if completed_exercises == len(valid_goals):
                            status_dict[day] = 2  # 完全完成
                        elif completed_exercises > 0 or has_partial:
                            status_dict[day] = 1  # 部分完成
                    except Exception as e:
                        print(f"解析日期时出错: {e}")
            
            # 更新月份天数和运动天数显示
            days_in_month = self._get_days_in_month()
            self.month_days_label.setText(f"{active_days_this_month} / {days_in_month}")
            
            # 更新日历指示器
            self.month_calendar_indicator.setDaysInMonth(days_in_month)
            self.month_calendar_indicator.setMonthStatus(status_dict)
            
            # 更新运动统计表格
            self.month_stats_table.setRowCount(0)  # 清除现有数据
            
            # 清空并重新保存数据
            self.last_exercise_data = {}
            
            # 如果选中月有运动数据
            if monthly_exercise_data:
                self.month_stats_table.setRowCount(len(monthly_exercise_data))
                row = 0
                
                for exercise_code, count in monthly_exercise_data.items():
                    if exercise_code in self.exercise_name_map:
                        # 保存数据到字典供语言切换时使用
                        self.last_exercise_data[exercise_code] = count
                        
                        # 运动类型
                        exercise_name = self.exercise_name_map[exercise_code]
                        name_item = QTableWidgetItem(exercise_name)
                        color = self.exercise_colors.get(exercise_name, "#3498db")
                        name_item.setBackground(QColor(color).lighter(180))
                        self.month_stats_table.setItem(row, 0, name_item)
                        
                        # 完成次数
                        count_item = QTableWidgetItem(str(count))
                        count_item.setTextAlignment(Qt.AlignCenter)
                        self.month_stats_table.setItem(row, 1, count_item)
                        
                        row += 1
        except Exception as e:
            print(f"更新月统计时出错: {str(e)}")
