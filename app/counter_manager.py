"""
计数器管理模块 - 负责运动计数和记录功能
"""

from core.translations import Translations as T

class CounterManager:
    """计数器管理器类"""
    
    def __init__(self, main_window):
        self.main_window = main_window
    
    def change_exercise(self, exercise_type):
        """更改运动类型"""
        self.main_window.exercise_type = exercise_type
        self.main_window.exercise_counter.reset_counter()
        self.main_window.current_count = 0
        self.main_window.statusBar.showMessage(f"Switched to {self.main_window.control_panel.exercise_display_map[exercise_type]} exercise")
    
    def reset_counter(self):
        """重置计数器"""
        # 设置重置标志为true以避免触发自动记录
        self.main_window.is_resetting = True
        
        # 重置计数器
        self.main_window.exercise_counter.reset_counter()
        self.main_window.current_count = 0
        self.main_window.manual_count = 0  # 同时重置手动计数
        if hasattr(self.main_window, "status_rail"):
            self.main_window.status_rail.update_counter(0)
            self.main_window.status_rail.update_phase(None)
        self.main_window.control_panel.update_counter(0)
        
        # 重置完成后恢复标志
        self.main_window.is_resetting = False
        
        self.main_window.statusBar.showMessage("Counter has been reset")
    
    def reset_exercise_state(self):
        """重置运动状态，包括计数器和相关变量"""
        # 直接调用现有的重置计数器方法
        self.reset_counter()
    
    def increase_counter(self, new_count):
        """手动增加计数器值"""
        self.main_window.current_count = new_count
        # 直接更新计数器类的内部计数值
        self.main_window.exercise_counter.counter = new_count
        # 增加手动计数
        self.main_window.manual_count += 1
        if hasattr(self.main_window, "status_rail"):
            self.main_window.status_rail.update_counter(new_count)
        self.main_window.control_panel.update_counter(new_count)
        self.main_window.statusBar.showMessage(f"Count increased to {new_count}")
    
    def decrease_counter(self, new_count):
        """手动减少计数器值"""
        self.main_window.current_count = new_count
        # 直接更新计数器类的内部计数值
        self.main_window.exercise_counter.counter = new_count
        # 手动计数不会为负数
        if self.main_window.manual_count > 0:
            self.main_window.manual_count -= 1
        if hasattr(self.main_window, "status_rail"):
            self.main_window.status_rail.update_counter(new_count)
        self.main_window.control_panel.update_counter(new_count)
        self.main_window.statusBar.showMessage(f"Count decreased to {new_count}")
    
    def confirm_record(self, exercise_type):
        """确认记录当前计数结果到历史记录"""
        # 获取当前计数值（现在记录所有计数，不仅仅是手动增加的部分）
        count = self.main_window.current_count
        
        # 记录到历史记录
        if count > 0:
            # 添加记录到运动追踪器
            completion_percentage = self.main_window.workout_tracker.add_workout_record(exercise_type, count)
            
            # 更新统计面板
            self.main_window.update_today_stats()
            self.main_window.update_stats_overview()
            
            # 获取运动类型的中文名称
            exercise_name = ""
            # 尝试从控制面板映射获取
            if exercise_type in self.main_window.control_panel.exercise_display_map:
                exercise_name = self.main_window.control_panel.exercise_display_map[exercise_type]
            
            # 显示成功消息
            self.main_window.statusBar.showMessage(f"Recorded {count} {exercise_name}, {completion_percentage}% of goal completed")
            
            # 重置计数器（也会重置manual_count）
            self.reset_counter()
        else:
            # 如果没有手动增加的计数，显示提示
            self.main_window.statusBar.showMessage("No manually increased count to record") 
