import os
import json
import datetime
import sys
from collections import defaultdict

class WorkoutTracker:
    """健身记录追踪器，负责存储和管理每日运动数据"""
    
    def __init__(self):
        # 确定数据存储路径
        self.data_dir = self._get_data_directory()
        self.data_file = os.path.join(self.data_dir, "workout_history.json")
        
        # 创建数据目录（如果不存在）
        os.makedirs(self.data_dir, exist_ok=True)
        
        # 初始化数据
        self.workout_history = self.load_history()
        self.workout_goals = self.load_goals()
        
    def _get_data_directory(self):
        """获取数据目录路径，兼容开发环境和打包环境"""
        if getattr(sys, 'frozen', False):
            # 打包后的环境
            # 首先尝试exe文件同级目录的data文件夹
            exe_dir = os.path.dirname(sys.executable)
            external_data_dir = os.path.join(exe_dir, "data")
            
            if os.path.exists(external_data_dir):
                print(f"使用外部data目录: {external_data_dir}")
                return external_data_dir
            else:
                # 如果外部data目录不存在，使用exe同级目录创建
                print(f"创建外部data目录: {external_data_dir}")
                return external_data_dir
        else:
            # 开发环境，使用项目目录下的data文件夹
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            data_dir = os.path.join(base_dir, "data")
            print(f"使用开发环境data目录: {data_dir}")
            return data_dir
        
    def load_history(self):
        """加载历史健身数据"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"加载历史数据失败: {e}")
                return self._create_default_history()
        else:
            return self._create_default_history()
    
    def _create_default_history(self):
        """创建默认的历史数据结构"""
        return {
            "daily_records": {},
            "last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def load_goals(self):
        """加载健身目标数据"""
        goals_file = os.path.join(self.data_dir, "workout_goals.json")
        if os.path.exists(goals_file):
            try:
                with open(goals_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return self._create_default_goals()
        else:
            return self._create_default_goals()
    
    def _create_default_goals(self):
        """创建默认的目标数据结构"""
        return {
            "daily": {
                "squat": 20,
                "pushup": 30,
                "situp": 30,
                "bicep_curl": 15,
                "lateral_raise": 15,
                "overhead_press": 15,
                "leg_raise": 15,
                "knee_raise": 15,
                "left_knee_press": 15,
                "right_knee_press": 15
            },
            "weekly": {
                "total_workouts": 5  # 每周计划健身天数
            }
        }
    
    def save_history(self):
        """保存历史健身数据"""
        self.workout_history["last_updated"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.workout_history, f, ensure_ascii=False, indent=2)
    
    def save_goals(self):
        """保存健身目标数据"""
        goals_file = os.path.join(self.data_dir, "workout_goals.json")
        with open(goals_file, 'w', encoding='utf-8') as f:
            json.dump(self.workout_goals, f, ensure_ascii=False, indent=2)
    
    def add_workout_record(self, exercise_type, count):
        """添加单次健身记录"""
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        
        # 确保日期记录存在
        if today not in self.workout_history["daily_records"]:
            self.workout_history["daily_records"][today] = {}
        
        # 更新该运动的计数
        if exercise_type in self.workout_history["daily_records"][today]:
            self.workout_history["daily_records"][today][exercise_type] += count
        else:
            self.workout_history["daily_records"][today][exercise_type] = count
        
        # 保存更新后的数据
        self.save_history()
        
        # 检查是否达成目标
        return self.check_goal_reached(exercise_type)
    
    def get_today_stats(self):
        """获取今日健身统计数据"""
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        if today in self.workout_history["daily_records"]:
            return self.workout_history["daily_records"][today]
        return {}
    
    def get_weekly_stats(self):
        """获取本周健身统计数据（按自然周）"""
        # 获取当前日期
        today = datetime.datetime.now()
        
        # 计算本周的开始（周一）和结束（周日）
        # weekday(): 周一是0，周日是6
        current_weekday = today.weekday()
        week_start = today - datetime.timedelta(days=current_weekday)  # 本周周一
        week_start = datetime.datetime(week_start.year, week_start.month, week_start.day)  # 重置为当天凌晨
        
        week_end = week_start + datetime.timedelta(days=6)  # 本周周日
        week_end = datetime.datetime(week_end.year, week_end.month, week_end.day, 23, 59, 59)  # 设置为当天最后一秒
        
        # 初始化统计数据
        stats = defaultdict(int)
        days_worked_out = 0
        daily_progress = {}
        
        # 遍历历史记录
        for date_str, exercises in self.workout_history["daily_records"].items():
            # 解析日期
            record_date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
            
            # 检查是否在本周内（周一到周日）
            if week_start <= record_date <= week_end:

                # 有记录的天数计数
                days_worked_out += 1
                
                # 添加每日进度数据
                daily_progress[date_str] = exercises
                
                # 累计每种运动的次数
                for exercise, count in exercises.items():
                    stats[exercise] += count
        
        # 创建7天的结构化数据，按周几排序
        weekday_data = {}
        for i in range(7):  # 0=周一, 6=周日
            day_date = week_start + datetime.timedelta(days=i)
            day_str = day_date.strftime("%Y-%m-%d")
            day_name = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][i]
            
            # 查找该天的数据
            exercises_data = self.workout_history["daily_records"].get(day_str, {})
            
            weekday_data[i] = {
                "date": day_str,
                "day_name": day_name,
                "exercises": exercises_data
            }
        
        return {
            "exercises": dict(stats),
            "days_worked_out": days_worked_out,
            "daily_progress": daily_progress,  # 原始每日进度数据
            "weekday_data": weekday_data     # 新增按周几排序的数据
        }
    
    def get_monthly_stats(self, year=None, month=None):
        """获取指定月份的健身统计数据
        
        Args:
            year: 年份，默认为当前年
            month: 月份，默认为当前月
            
        Returns:
            包含该月统计信息的字典
        """
        # 如果未指定年月，使用当前年月
        if year is None or month is None:
            today = datetime.datetime.now()
            year = today.year
            month = today.month
        
        # 获取指定月份的第一天
        first_day = datetime.datetime(year, month, 1)
        
        # 查找下个月的第一天，然后回退一天得到本月的最后一天
        if month == 12:
            next_month = datetime.datetime(year+1, 1, 1)
        else:
            next_month = datetime.datetime(year, month+1, 1)
        last_day = next_month - datetime.timedelta(days=1)
        
        # 初始化统计数据
        stats = defaultdict(int)
        days_worked_out = 0
        daily_progress = {}
        
        # 遍历历史记录
        for date_str, exercises in self.workout_history["daily_records"].items():
            # 解析日期
            try:
                record_date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
                
                # 检查是否在本月内
                if first_day <= record_date <= last_day:
                    # 有记录的天数计数
                    days_worked_out += 1
                    
                    # 添加每日进度数据
                    daily_progress[date_str] = exercises
                    
                    # 累计每种运动的次数
                    for exercise, count in exercises.items():
                        stats[exercise] += count
            except ValueError as e:
                print(f"  日期格式错误: {date_str} - {e}")
        
        return {
            "exercises": dict(stats),
            "days_worked_out": days_worked_out,
            "daily_progress": daily_progress  # 添加每日进度详细数据
        }
    
    def update_goal(self, exercise_type, count):
        """更新单个运动目标"""
        self.workout_goals["daily"][exercise_type] = count
        self.save_goals()
    
    def update_weekly_goal(self, count):
        """更新每周健身天数目标"""
        self.workout_goals["weekly"]["total_workouts"] = count
        self.save_goals()
    
    def check_goal_reached(self, exercise_type):
        """检查是否达到目标（返回完成百分比）"""
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        if today not in self.workout_history["daily_records"] or exercise_type not in self.workout_history["daily_records"][today]:
            return 0
        
        current = self.workout_history["daily_records"][today][exercise_type]
        goal = self.workout_goals["daily"].get(exercise_type, 0)
        
        if goal <= 0:
            return 100  # 防止除零错误
        
        percentage = min(100, int((current / goal) * 100))
        return percentage
    
    def get_goals(self):
        """获取所有设定的目标"""
        return self.workout_goals
