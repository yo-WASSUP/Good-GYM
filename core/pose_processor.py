import cv2
import numpy as np

class PoseProcessor:
    """处理姿态检测结果和图像绘制"""
    
    def __init__(self, model, exercise_counter):
        self.model = model
        self.exercise_counter = exercise_counter
        self.show_skeleton = True
        self.conf_threshold = 0.5
        # 获取设备信息，用于模型推理
        self.device = model.device
    
    def update_model(self, new_model):
        """更新模型"""
        self.model = new_model
        self.device = new_model.device
        print(f"Pose processor updated with new model on device: {self.device}")
    
    def process_frame(self, frame, exercise_type):
        """处理单帧图像进行姿态检测和运动计数"""
        # 尺寸检查，如果帧太大则缩小
        h, w = frame.shape[:2]
        if w > 640 or h > 640:  # 如果帧过大，先进行缩小以加快处理
            scale = min(640/w, 640/h)
            frame = cv2.resize(frame, (int(w*scale), int(h*scale)))
        
        # 复制帧以在其上绘制（使用浅复制加快）
        output_frame = frame
        
        # BGR转RGB（PyQt需要RGB格式）
        output_frame = cv2.cvtColor(output_frame, cv2.COLOR_BGR2RGB)
        
        # 运行YOLO11-pose姿态估计，使用优化的设置
        results = self.model(frame, conf=self.conf_threshold, verbose=False, imgsz=640)
        
        # 初始化结果
        current_angle = None
        angle_point = None
        keypoints = None
        
        # 处理结果
        if len(results) > 0 and len(results[0].keypoints.xy) > 0:
            # 获取检测到的第一个人（最高置信度）
            keypoints = results[0].keypoints.xy[0].cpu().numpy()
            
            # 根据运动类型获取相应的角度和关节点
            if exercise_type == "squat":
                current_angle = self.exercise_counter.count_squat(keypoints)
                if current_angle is not None:
                    # 膝关节点 - 髋、膝、踝
                    angle_point = [keypoints[12], keypoints[14], keypoints[16]]
            elif exercise_type == "pushup":
                current_angle = self.exercise_counter.count_pushup(keypoints)
                if current_angle is not None:
                    # 肘部关节点 - 肩、肘、腕
                    angle_point = [keypoints[6], keypoints[8], keypoints[10]]
            elif exercise_type == "situp":
                current_angle = self.exercise_counter.count_situp(keypoints)
                if current_angle is not None:
                    # 腰部关节点
                    angle_point = [keypoints[5], keypoints[11], keypoints[12]]
            elif exercise_type == "bicep_curl":
                current_angle = self.exercise_counter.count_bicep_curl(keypoints)
                if current_angle is not None:
                    # 肘部关节点 - 肩、肘、腕
                    # 显示在右肘处
                    angle_point = [keypoints[6], keypoints[8], keypoints[10]]
            elif exercise_type == "lateral_raise":
                current_angle = self.exercise_counter.count_lateral_raise(keypoints)
                if current_angle is not None:
                    # 肩部关节点
                    angle_point = [keypoints[12], keypoints[6], keypoints[8]]
            elif exercise_type == "overhead_press":
                current_angle = self.exercise_counter.count_overhead_press(keypoints)
                if current_angle is not None:
                    # 肩部关节点
                    angle_point = [keypoints[12], keypoints[6], keypoints[8]]
            elif exercise_type == "leg_raise":
                current_angle = self.exercise_counter.count_leg_raise(keypoints)
                if current_angle is not None:
                    # 当前抬起的腿的髋、膝、踝角度
                    # 由于左右交替抬腿，角度点会根据当前抬起的腿而变化
                    if hasattr(self.exercise_counter, 'prev_leg') and self.exercise_counter.prev_leg == 'left':
                        # 左腿: 左髋、左膝、左踝
                        angle_point = [keypoints[11], keypoints[13], keypoints[15]]
                    else:
                        # 右腿: 右髋、右膝、右踝
                        angle_point = [keypoints[12], keypoints[14], keypoints[16]]
            elif exercise_type == "knee_raise":
                current_angle = self.exercise_counter.count_knee_raise(keypoints)
                if current_angle is not None:
                    # 膝盘关节点
                    angle_point = [keypoints[12], keypoints[14], keypoints[16]]
            elif exercise_type == "left_knee_press":
                current_angle = self.exercise_counter.count_left_knee_press(keypoints)
                if current_angle is not None:
                    # 左侧提膝下压
                    angle_point = [keypoints[11], keypoints[13], keypoints[15]]
            elif exercise_type == "right_knee_press":
                current_angle = self.exercise_counter.count_right_knee_press(keypoints)
                if current_angle is not None:
                    # 右侧提膝下压
                    angle_point = [keypoints[12], keypoints[14], keypoints[16]]
            
            # 在图像上绘制骨架如果启用
            if self.show_skeleton:
                output_frame = self.draw_skeleton(output_frame, results)
        
            # 在特定关节处显示角度 - 注释掉这部分代码
            # if current_angle is not None and angle_point is not None:
            #     output_frame = self.draw_angle(output_frame, angle_point, current_angle, exercise_type)
        
        return output_frame, current_angle, keypoints
    
    def draw_skeleton(self, img, results):
        """在图像上绘制骨架，不显示边界框"""
        annotated_frame = img.copy()
        
        # 获取关键点
        if len(results) > 0 and len(results[0].keypoints.xy) > 0:
            keypoints = results[0].keypoints.xy[0].cpu().numpy()
            n_keypoints = len(keypoints)
            
            # 头部和颈部连接 (紫色)
            head_connections = [
                [0, 1], [0, 2], [1, 3], [2, 4],  # 鼻子到眼睛，眼睛到耳朵
            ]
            
            # 身体躯干 (蓝色)
            torso_connections = [
                [5, 6],   # 左肩到右肩
                [5, 11],  # 左肩到左臂
                [6, 12],  # 右肩到右臂
                [11, 12], # 左臂到右臂
            ]
            
            # 手臂 (绿色)
            arm_connections = [
                [5, 7], [7, 9],    # 左肩-左胳-左手腕
                [6, 8], [8, 10]   # 右肩-右胳-右手腕
            ]
            
            # 腰部和腿部 (橙色)
            leg_connections = [
                [11, 13], [13, 15],  # 左臂-左膝-左蹄
                [12, 14], [14, 16]  # 右臂-右膝-右蹄
            ]
            
            # 定义颜色 (RGB) - 更明亮、更鲜艳的配色
            colors = {
                'head': (255, 153, 51),    # 明亮的橙色
                'torso': (51, 153, 255),   # 鲜艳的蓝色
                'arms': (255, 51, 153),    # 亮粉色
                'legs': (153, 255, 51)     # 亮绿色
            }
            
            # 绘制关键点 (使用光晕效果)
            for i, (x, y) in enumerate(keypoints):
                # 跳过坐标为(0,0)的点
                if (x, y) == (0, 0):
                    continue
                
                if i < n_keypoints:  # 确保在有效范围内
                    # 为不同部位的关键点使用不同颜色
                    if i in [0, 1, 2, 3, 4]: # 头部
                        color = colors['head']
                    elif i in [5, 6, 11, 12]: # 躯干
                        color = colors['torso']
                    elif i in [7, 8, 9, 10]: # 手臂
                        color = colors['arms']
                    else: # 腿部
                        color = colors['legs']
                    
                    # 绘制关键点及光晕效果
                    cv2.circle(annotated_frame, (int(x), int(y)), 6, color, -1)
                    cv2.circle(annotated_frame, (int(x), int(y)), 8, color, 1)
            
            # 创建一个函数来绘制不同部位的连接线
            def draw_connections(connections, color, thickness=4):
                for connection in connections:
                    if connection[0] < n_keypoints and connection[1] < n_keypoints:
                        pt1 = (int(keypoints[connection[0]][0]), int(keypoints[connection[0]][1]))
                        pt2 = (int(keypoints[connection[1]][0]), int(keypoints[connection[1]][1]))
                        
                        # 不绘制坐标为(0,0)的点的连接线
                        if pt1[0] == 0 and pt1[1] == 0 or pt2[0] == 0 and pt2[1] == 0:
                            continue
                        
                        # 使用带有渐变的线条增强视觉效果
                        for i in range(thickness, 0, -2):
                            alpha = 0.6 if i == thickness else 0.3
                            blend_color = tuple(int(c * alpha) for c in color)
                            cv2.line(annotated_frame, pt1, pt2, blend_color, i)
            
            # 绘制各个部位的连接
            draw_connections(head_connections, colors['head'])
            draw_connections(torso_connections, colors['torso'])
            draw_connections(arm_connections, colors['arms'])
            draw_connections(leg_connections, colors['legs'])
                    
        # 图像已经是RGB格式，直接返回
        return annotated_frame
    
    def draw_angle(self, img, angle_point, angle, exercise_type):
        """在特定关节处显示角度文本，不显示连接线"""
        try:
            # 获取显示位置
            display_point = self.exercise_counter.get_angle_point(angle_point, exercise_type)
            
            if display_point:
                # 在关节点处只显示角度文本，不绘制连接线
                cv2.putText(img, f"{int(angle)}°", display_point, 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        except Exception as e:
            print(f"绘制角度时出错: {e}")
            
        return img
    
    def set_skeleton_visibility(self, show):
        """设置是否显示骨架"""
        self.show_skeleton = show
