import numpy as np

class ExerciseCounter:
    """类包含所有运动计数逻辑"""
    
    def __init__(self):
        # 计数变量
        self.counter = 0
        self.stage = None
        
    def reset_counter(self):
        """重置计数器"""
        self.counter = 0
        self.stage = None
        
    def calculate_angle(self, a, b, c):
        """计算三个点之间的角度"""
        a = np.array(a)
        b = np.array(b)
        c = np.array(c)
        
        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
        angle = np.abs(radians * 180.0 / np.pi)
        
        if angle > 180.0:
            angle = 360 - angle
            
        return angle
    
    def count_squat(self, keypoints):
        """计算深蹲次数基于膝盘角度（基于双腿）"""
        # 获取深蹲相关关键点
        # 正确的关键点索引:
        # 11-左髋, 12-右髋, 13-左膝, 14-右膝, 15-左踝, 16-右踝
        try:
            # 左腿关键点
            left_hip = (keypoints[11][0], keypoints[11][1])
            left_knee = (keypoints[13][0], keypoints[13][1])
            left_ankle = (keypoints[15][0], keypoints[15][1])
            
            # 右腿关键点
            right_hip = (keypoints[12][0], keypoints[12][1])
            right_knee = (keypoints[14][0], keypoints[14][1])
            right_ankle = (keypoints[16][0], keypoints[16][1])
            
            # 计算左右腿的膝盘角度
            left_angle = self.calculate_angle(left_hip, left_knee, left_ankle)
            right_angle = self.calculate_angle(right_hip, right_knee, right_ankle)
            
            # 取平均角度作为返回值（用于显示）
            avg_angle = (left_angle + right_angle) / 2
            
            # 计数逻辑 - 只有两条腿都符合条件时才计数
            if left_angle > 160 and right_angle > 160:
                self.stage = "up"
            elif left_angle < 110 and right_angle < 110 and self.stage == "up":
                self.stage = "down"
                self.counter += 1
                
            return avg_angle
        except:
            return None
    
    def count_pushup(self, keypoints):
        """计算俇卧撞次数基于肘部角度（双臂）"""
        # 关键点索引: 
        # 5-左肩, 7-左肘, 9-左腕
        # 6-右肩, 8-右肘, 10-右腕
        try:
            # 左臂关键点
            left_shoulder = (keypoints[5][0], keypoints[5][1])
            left_elbow = (keypoints[7][0], keypoints[7][1])
            left_wrist = (keypoints[9][0], keypoints[9][1])
            
            # 右臂关键点
            right_shoulder = (keypoints[6][0], keypoints[6][1])
            right_elbow = (keypoints[8][0], keypoints[8][1])
            right_wrist = (keypoints[10][0], keypoints[10][1])
            
            # 计算左右臂肘部角度
            left_angle = self.calculate_angle(left_shoulder, left_elbow, left_wrist)
            right_angle = self.calculate_angle(right_shoulder, right_elbow, right_wrist)
            
            # 取平均角度作为返回值（用于显示）
            avg_angle = (left_angle + right_angle) / 2
            
            # 计数逻辑 - 只有两边手臂都符合条件时才计数
            if left_angle > 160 and right_angle > 160:
                self.stage = "up"
            elif left_angle < 100 and right_angle < 100 and self.stage == "up":
                self.stage = "down"
                self.counter += 1
                
            return avg_angle
        except:
            return None
    
    def count_situp(self, keypoints):
        """计算仰卧起坐次数基于躯干角度（基于身体两侧）"""
        # 正确的关键点索引:
        # 5-左肩, 6-右肩, 11-左髋, 12-右髋, 13-左膝, 14-右膝
        try:
            # 左侧躯干关键点
            left_shoulder = (keypoints[5][0], keypoints[5][1])
            left_hip = (keypoints[11][0], keypoints[11][1])
            left_knee = (keypoints[13][0], keypoints[13][1])
            
            # 右侧躯干关键点
            right_shoulder = (keypoints[6][0], keypoints[6][1])
            right_hip = (keypoints[12][0], keypoints[12][1])
            right_knee = (keypoints[14][0], keypoints[14][1])
            
            # 计算左右两侧躯干角度
            left_angle = self.calculate_angle(left_shoulder, left_hip, left_knee)
            right_angle = self.calculate_angle(right_shoulder, right_hip, right_knee)
            
            # 取平均角度作为返回值（用于显示）
            avg_angle = (left_angle + right_angle) / 2
            
            # 计数逻辑 - 左右两侧都身体都要符合条件
            if left_angle < 45 and right_angle < 45:
                self.stage = "up"
            elif left_angle > 80 and right_angle > 80 and self.stage == "up":
                self.stage = "down"
                self.counter += 1
                
            return avg_angle
        except:
            return None
    
    def count_bicep_curl(self, keypoints):
        """计算二头肌弯举次数基于肘部角度（双臂）"""
        try:
            # 正确的关键点索引
            # 左手臂: 5-左肩, 7-左肘, 9-左手腕
            left_shoulder = (keypoints[5][0], keypoints[5][1])
            left_elbow = (keypoints[7][0], keypoints[7][1])
            left_wrist = (keypoints[9][0], keypoints[9][1])
            
            # 右手臂: 6-右肩, 8-右肘, 10-右手腕
            right_shoulder = (keypoints[6][0], keypoints[6][1])
            right_elbow = (keypoints[8][0], keypoints[8][1])
            right_wrist = (keypoints[10][0], keypoints[10][1])
            
            # 计算左右肘部角度
            left_angle = self.calculate_angle(left_shoulder, left_elbow, left_wrist)
            right_angle = self.calculate_angle(right_shoulder, right_elbow, right_wrist)
            
            # 取平均值作为显示角度
            avg_angle = (left_angle + right_angle) / 2
            
            # 判断左右两侧是否都处于同一状态
            left_is_down = left_angle > 160
            right_is_down = right_angle > 160
            left_is_up = left_angle < 60
            right_is_up = right_angle < 60
            
            # 计数逻辑 - 两侧都满足条件才计数
            if left_is_down and right_is_down:
                self.stage = "down"
            elif left_is_up and right_is_up and self.stage == "down":
                self.stage = "up"
                self.counter += 1
                
            return avg_angle
        except:
            return None
    
    def count_lateral_raise(self, keypoints):
        """计算侧平举次数基于肩部角度（双臂）"""
        try:
            # 左侧手臂关键点: 11-left hip, 5-left shoulder, 7-left elbow
            left_hip = (keypoints[11][0], keypoints[11][1])
            left_shoulder = (keypoints[5][0], keypoints[5][1])
            left_elbow = (keypoints[7][0], keypoints[7][1])
            
            # 右侧手臂关键点: 12-right hip, 6-right shoulder, 8-right elbow
            right_hip = (keypoints[12][0], keypoints[12][1])
            right_shoulder = (keypoints[6][0], keypoints[6][1])
            right_elbow = (keypoints[8][0], keypoints[8][1])
            
            # 计算左右两侧肩膀角度
            left_angle = self.calculate_angle(left_hip, left_shoulder, left_elbow)
            right_angle = self.calculate_angle(right_hip, right_shoulder, right_elbow)
            
            # 取左右两侧角度的平均值作为显示
            avg_angle = (left_angle + right_angle) / 2
            
            # 判断左右两侧是否都处于同一状态
            left_is_down = left_angle < 30
            right_is_down = right_angle < 30
            left_is_up = left_angle > 80
            right_is_up = right_angle > 80
            
            # 计数逻辑 - 两侧都满足条件才计数
            if left_is_down and right_is_down:
                self.stage = "down"
            elif left_is_up and right_is_up and self.stage == "down":
                self.stage = "up"
                self.counter += 1
                
            return avg_angle
        except:
            return None
            
    def count_overhead_press(self, keypoints):
        """计算推举次数基于肩部角度（双臂）"""
        try:
            # 左侧手臂关键点: 11-left hip, 5-left shoulder, 7-left elbow
            left_hip = (keypoints[11][0], keypoints[11][1])
            left_shoulder = (keypoints[5][0], keypoints[5][1])
            left_elbow = (keypoints[7][0], keypoints[7][1])
            
            # 右侧手臂关键点: 12-right hip, 6-right shoulder, 8-right elbow
            right_hip = (keypoints[12][0], keypoints[12][1])
            right_shoulder = (keypoints[6][0], keypoints[6][1])
            right_elbow = (keypoints[8][0], keypoints[8][1])
            
            # 计算左右两侧肩膀角度
            left_angle = self.calculate_angle(left_hip, left_shoulder, left_elbow)
            right_angle = self.calculate_angle(right_hip, right_shoulder, right_elbow)
            
            # 取左右两侧角度的平均值作为显示
            avg_angle = (left_angle + right_angle) / 2
            
            # 判断左右两侧是否都处于同一状态
            left_is_down = left_angle < 30
            right_is_down = right_angle < 30
            left_is_up = left_angle > 150
            right_is_up = right_angle > 150
            
            # 计数逻辑 - 两侧都满足条件才计数
            if left_is_down and right_is_down:
                self.stage = "down"
            elif left_is_up and right_is_up and self.stage == "down":
                self.stage = "up"
                self.counter += 1
                
            return avg_angle
        except:
            return None
    
    def count_leg_raise(self, keypoints):
        """计算左右交替抬腿次数"""
        try:
            # 左侧手臂关键点: 5-left shoulder, 7-left elbow, 11-left hip
            left_shoulder = (keypoints[5][0], keypoints[5][1])
            left_hip = (keypoints[11][0], keypoints[11][1])
            left_knee = (keypoints[13][0], keypoints[13][1])
            
            # 右侧手臂关键点: 6-right shoulder, 8-right elbow, 12-right hip
            right_shoulder = (keypoints[6][0], keypoints[6][1])
            right_hip = (keypoints[12][0], keypoints[12][1])
            right_knee = (keypoints[14][0], keypoints[14][1])
            
            # 计算左右腿的髋膝角度
            left_leg_angle = self.calculate_angle(left_shoulder, left_hip, left_knee)
            right_leg_angle = self.calculate_angle(right_shoulder, right_hip, right_knee)
            
            # 判断腿部抬起状态
            left_leg_raised = left_leg_angle < 130  # 左腿抬起
            right_leg_raised = right_leg_angle < 130  # 右腿抬起
            both_legs_down = left_leg_angle > 160 and right_leg_angle > 160  # 两腿都落下
            
            # 取平均角度作为返回值（用于显示）
            current_angle = left_leg_angle if left_leg_raised else right_leg_angle
            
            # 计数逻辑 - 交替抬腿
            # 初始化stage状态
            if not hasattr(self, 'prev_leg'):
                self.prev_leg = 'none'
            
            if both_legs_down:
                self.stage = "down"  # 两腿均落下
            elif left_leg_raised and self.stage == "down" and self.prev_leg != 'left':
                self.stage = "up"
                self.prev_leg = 'left'
                self.counter += 1
            elif right_leg_raised and self.stage == "down" and self.prev_leg != 'right':
                self.stage = "up"
                self.prev_leg = 'right'
                self.counter += 1
            
            return current_angle
        except:
            return None
    
    def count_knee_raise(self, keypoints):
        """计算单侧提膝次数（右腿）"""
        try:
            # 髋部关键点: 12-右髋
            right_hip = (keypoints[12][0], keypoints[12][1])
            
            # 膝盘关键点: 14-右膝
            right_knee = (keypoints[14][0], keypoints[14][1])
            
            # 踝部关键点: 16-右踝
            right_ankle = (keypoints[16][0], keypoints[16][1])
            
            # 计算右腿的髋膝角度
            right_leg_angle = self.calculate_angle(right_hip, right_knee, right_ankle)
            
            # 判断提膝位置
            # 提膝位置的标准：1. 膝盘高于髋部 2. 腿部角度足够大（表示腿部弹性收紧）
            knee_raised = right_leg_angle < 110  # 提膝高度足够且角度足够大
            knee_lowered = right_leg_angle > 160  # 腿部下放
            
            # 计数逻辑
            if knee_lowered:
                self.stage = "down"
            elif knee_raised and self.stage == "down":
                self.stage = "up"
                self.counter += 1
            
            return right_leg_angle
        except:
            return None
            
    def count_left_knee_press(self, keypoints):
        """计算左侧提膝下压次数"""
        try:
            # 左腿关键点
            left_shoulder = (keypoints[5][0], keypoints[5][1])
            left_hip = (keypoints[11][0], keypoints[11][1])
            left_knee = (keypoints[13][0], keypoints[13][1])
            
            # 计算左腿的角度 - 使用肩膛膨和髋关节
            left_leg_angle = self.calculate_angle(left_shoulder, left_hip, left_knee)
            
            # 设置活跃侧为左侧（用于角度显示）
            self.active_side = 'left'
            
            # 设置提膝下压的角度阈值
            down_angle = 110  # 膝盖弯曲时的角度阈值
            up_angle = 150   # 膝盖伸直时的角度阈值
            
            # 初始化阶段变量（如果尚未初始化）
            if not hasattr(self, 'left_stage'):
                self.left_stage = None
            
            # 左腿计数逻辑
            if left_leg_angle < down_angle and self.left_stage != "up":
                self.left_stage = "up"
                self.stage = "up"  # 更新总体阶段状态
            elif left_leg_angle > up_angle and self.left_stage == "up":
                self.counter += 1
                self.left_stage = "down"
                self.stage = "down"  # 更新总体阶段状态
            
            # 直接返回左腿角度值
            return left_leg_angle
        except:
            return None
            
    def count_right_knee_press(self, keypoints):
        """计算右侧提膝下压次数"""
        try:
            # 右腿关键点
            right_shoulder = (keypoints[6][0], keypoints[6][1])
            right_hip = (keypoints[12][0], keypoints[12][1])
            right_knee = (keypoints[14][0], keypoints[14][1])
            
            # 计算右腿的角度 - 使用肩膛膨和髋关节
            right_leg_angle = self.calculate_angle(right_shoulder, right_hip, right_knee)
            
            # 设置活跃侧为右侧（用于角度显示）
            self.active_side = 'right'
            
            # 设置提膝下压的角度阈值
            down_angle = 110  # 膝盖弯曲时的角度阈值
            up_angle = 150   # 膝盖伸直时的角度阈值
            
            # 初始化阶段变量（如果尚未初始化）
            if not hasattr(self, 'right_stage'):
                self.right_stage = None
            
            # 右腿计数逻辑
            if right_leg_angle < down_angle and self.right_stage != "up":
                self.right_stage = "up"
                self.stage = "up"  # 更新总体阶段状态
            elif right_leg_angle > up_angle and self.right_stage == "up":
                self.counter += 1
                self.right_stage = "down"
                self.stage = "down"  # 更新总体阶段状态
            
            # 直接返回右腿角度值
            return right_leg_angle
        except:
            return None
    
    # 获取角度显示位置的辅助函数
    def get_angle_point(self, keypoints, exercise_type):
        """根据运动类型获取角度显示位置"""
        try:
            if exercise_type == "squat":
                # 膝盖关节点 (右膝) - 14
                return (int(keypoints[14][0]), int(keypoints[14][1]))
                
            elif exercise_type == "pushup":
                # 肘部关节点 (右肘) - 8
                return (int(keypoints[8][0]), int(keypoints[8][1]))
                
            elif exercise_type == "situp":
                # 髋部关节点 (右髋) - 12
                return (int(keypoints[12][0]), int(keypoints[12][1]))
                
            elif exercise_type == "bicep_curl":
                # 肘部关节点 (右肘) - 8
                return (int(keypoints[8][0]), int(keypoints[8][1]))
                
            elif exercise_type == "lateral_raise":
                # 肩部关节点 (右肩) - 6
                return (int(keypoints[6][0]), int(keypoints[6][1]))
                
            elif exercise_type == "overhead_press":
                # 肩部关节点 (右肩) - 6
                return (int(keypoints[6][0]), int(keypoints[6][1]))
            
            elif exercise_type == "leg_raise":
                # 显示当前抬起的腿的膝盘关节点
                return (int(keypoints[13][0]), int(keypoints[13][1]))
            
            elif exercise_type == "knee_raise":
                # 单侧提膝的膝盘关节点 (右膝) - 14
                return (int(keypoints[14][0]), int(keypoints[14][1]))
                
            elif exercise_type == "left_knee_press":
                # 左侧提膝下压 - 显示左膝角度
                return (int(keypoints[13][0]), int(keypoints[13][1]))
                
            elif exercise_type == "right_knee_press":
                # 右侧提膝下压 - 显示右膝角度
                return (int(keypoints[14][0]), int(keypoints[14][1]))
                
            return None
        except:
            return None
