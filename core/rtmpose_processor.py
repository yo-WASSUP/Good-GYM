import os
import cv2
import sys
from rtmlib import Wholebody, draw_skeleton

class RTMPoseProcessor:
    """使用RTMPose进行姿态检测的处理器"""
    
    def __init__(self, exercise_counter, mode='balanced', backend='onnxruntime', device='cpu'):
        self.exercise_counter = exercise_counter
        self.show_skeleton = True
        self.conf_threshold = 0.5
        self.device = device
        self.backend = backend
        
        # 初始化RTMPose模型
        self.init_rtmpose(mode)
        
        self.keypoint_mapping = self.get_keypoint_mapping()
    
    def get_models_dir(self):
        """获取模型文件目录，兼容开发环境和打包环境"""
        if getattr(sys, 'frozen', False):
            # 打包后的环境，模型文件在临时目录中
            base_path = sys._MEIPASS
            models_dir = os.path.join(base_path, 'models')
        else:
            # 开发环境，模型文件在项目目录中
            models_dir = './models'
        
        return models_dir
    
    def init_rtmpose(self, mode='balanced'):
        """初始化RTMPose模型"""
        try:
            print(f"正在初始化RTMPose模型 (模式: {mode}, 后端: {self.backend}, 设备: {self.device})")
            
            # 检查是否有本地模型文件
            models_dir = self.get_models_dir()
            if os.path.exists(models_dir):
                # 尝试使用本地模型
                det_model = os.path.join(models_dir, 'yolox_nano_8xb8-300e_humanart-40f6f0d0.onnx')
                
                # 根据模式选择不同的姿态检测模型
                if mode == 'lightweight':
                    pose_model = os.path.join(models_dir, 'rtmpose-t_simcc-body7_pt-body7_420e-256x192-026a1439_20230504.onnx')
                    pose_input_size = (192, 256)
                elif mode == 'performance':
                    pose_model = os.path.join(models_dir, 'rtmpose-m_simcc-body7_pt-body7_420e-256x192-e48f03d0_20230504.onnx')
                    pose_input_size = (192, 256)
                else:  # balanced
                    pose_model = os.path.join(models_dir, 'rtmpose-s_simcc-body7_pt-body7_420e-256x192-acd4a1ef_20230504.onnx')
                    pose_input_size = (192, 256)
                
                if os.path.exists(det_model) and os.path.exists(pose_model):
                    print(f"使用本地模型文件 ({mode}模式)")
                    self.wholebody = Wholebody(
                        det=det_model,
                        det_input_size=(416, 416),
                        pose=pose_model,
                        pose_input_size=pose_input_size,
                        backend=self.backend,
                        device=self.device
                    )
                    print("RTMPose本地模型初始化成功")
                    return
                else:
                    print("本地模型文件不完整，使用在线下载")
            else:
                print("models目录不存在，使用在线下载")
            
            # 如果本地文件不存在，使用在线模式
            print("使用在线模式下载模型")
            self.wholebody = Wholebody(
                mode=mode,
                backend=self.backend,
                device=self.device
            )
                
            print("RTMPose在线模型初始化成功")
            
        except Exception as e:
            print(f"RTMPose初始化失败: {e}")
            # 如果指定模式失败，尝试使用默认模式
            try:
                print("尝试使用默认balanced模式...")
                self.wholebody = Wholebody(
                    mode='balanced',
                    backend=self.backend,
                    device=self.device
                )
                print("RTMPose默认模式初始化成功")
            except Exception as e2:
                print(f"RTMPose默认模式初始化也失败: {e2}")
                raise e2
    
    def get_keypoint_mapping(self):
        """获取关键点映射 (COCO 17关键点格式)"""
        # RTMPose和YOLO都使用COCO 17关键点格式，顺序相同
        # 0: nose, 1: left_eye, 2: right_eye, 3: left_ear, 4: right_ear
        # 5: left_shoulder, 6: right_shoulder, 7: left_elbow, 8: right_elbow
        # 9: left_wrist, 10: right_wrist, 11: left_hip, 12: right_hip
        # 13: left_knee, 14: right_knee, 15: left_ankle, 16: right_ankle
        return list(range(17))  # 1:1映射
    
    def update_model(self, mode='balanced'):
        """更新模型"""
        print(f"更新RTMPose模型到模式: {mode}")
        self.init_rtmpose(mode)
        print(f"RTMPose处理器已更新到模式: {mode}")
    
    def process_frame(self, frame, exercise_type):
        """处理单帧图像进行姿态检测和运动计数"""
        # 尺寸检查，如果帧太大则缩小
        h, w = frame.shape[:2]
        original_size = (w, h)
        
        # RTMPose适合处理较高分辨率，但为了性能还是限制一下
        if w > 640 or h > 640:
            scale = min(640/w, 640/h)
            frame = cv2.resize(frame, (int(w*scale), int(h*scale)))
            scale_factor = scale
        else:
            scale_factor = 1.0
        
        # 复制帧以在其上绘制
        output_frame = frame.copy()
        
        # 初始化结果
        current_angle = None
        angle_point = None
        keypoints = None
        
        try:
            # 使用RTMPose进行姿态检测
            detected_keypoints, scores = self.wholebody(frame)
            
            # 处理结果
            if detected_keypoints is not None and len(detected_keypoints) > 0:
                # 获取第一个人的关键点 (最高置信度)
                keypoints = detected_keypoints[0]  # shape: (17, 2)
                confidence_scores = scores[0] if scores is not None else None
                
                # 过滤低置信度的关键点
                if confidence_scores is not None:
                    valid_mask = confidence_scores > self.conf_threshold
                    keypoints[~valid_mask] = [0, 0]  # 将低置信度的点设为(0,0)
                
                # 如果需要缩放回原始尺寸
                if scale_factor != 1.0:
                    keypoints = keypoints / scale_factor
                    # 同时调整输出帧大小
                    output_frame = cv2.resize(output_frame, original_size)
                
                # 根据运动类型获取相应的角度和关节点
                current_angle, angle_point = self.get_exercise_angle(keypoints, exercise_type)
                
                # 在图像上绘制骨架（如果启用）
                if self.show_skeleton:
                    output_frame = self.draw_rtmpose_skeleton(output_frame, keypoints, confidence_scores)
            
        except Exception as e:
            print(f"RTMPose处理失败: {e}")
            # 发生错误时返回原始帧
            pass
        
        # BGR转RGB（PyQt需要RGB格式）
        output_frame = cv2.cvtColor(output_frame, cv2.COLOR_BGR2RGB)
        
        return output_frame, current_angle, keypoints
    
    def get_exercise_angle(self, keypoints, exercise_type):
        """根据运动类型获取角度"""
        current_angle = None
        angle_point = None
        
        try:
            if exercise_type == "squat":
                current_angle = self.exercise_counter.count_squat(keypoints)
                if current_angle is not None:
                    angle_point = [keypoints[12], keypoints[14], keypoints[16]]
            elif exercise_type == "pushup":
                current_angle = self.exercise_counter.count_pushup(keypoints)
                if current_angle is not None:
                    angle_point = [keypoints[6], keypoints[8], keypoints[10]]
            elif exercise_type == "situp":
                current_angle = self.exercise_counter.count_situp(keypoints)
                if current_angle is not None:
                    angle_point = [keypoints[5], keypoints[11], keypoints[12]]
            elif exercise_type == "bicep_curl":
                current_angle = self.exercise_counter.count_bicep_curl(keypoints)
                if current_angle is not None:
                    angle_point = [keypoints[6], keypoints[8], keypoints[10]]
            elif exercise_type == "lateral_raise":
                current_angle = self.exercise_counter.count_lateral_raise(keypoints)
                if current_angle is not None:
                    angle_point = [keypoints[12], keypoints[6], keypoints[8]]
            elif exercise_type == "overhead_press":
                current_angle = self.exercise_counter.count_overhead_press(keypoints)
                if current_angle is not None:
                    angle_point = [keypoints[12], keypoints[6], keypoints[8]]
            elif exercise_type == "leg_raise":
                current_angle = self.exercise_counter.count_leg_raise(keypoints)
                if current_angle is not None:
                    if hasattr(self.exercise_counter, 'prev_leg') and self.exercise_counter.prev_leg == 'left':
                        angle_point = [keypoints[11], keypoints[13], keypoints[15]]
                    else:
                        angle_point = [keypoints[12], keypoints[14], keypoints[16]]
            elif exercise_type == "knee_raise":
                current_angle = self.exercise_counter.count_knee_raise(keypoints)
                if current_angle is not None:
                    angle_point = [keypoints[12], keypoints[14], keypoints[16]]
            elif exercise_type == "left_knee_press":
                current_angle = self.exercise_counter.count_left_knee_press(keypoints)
                if current_angle is not None:
                    angle_point = [keypoints[11], keypoints[13], keypoints[15]]
            elif exercise_type == "right_knee_press":
                current_angle = self.exercise_counter.count_right_knee_press(keypoints)
                if current_angle is not None:
                    angle_point = [keypoints[12], keypoints[14], keypoints[16]]
        except Exception as e:
            print(f"计算运动角度时出错: {e}")
            
        return current_angle, angle_point
    
    def draw_rtmpose_skeleton(self, img, keypoints, confidence_scores=None):
        """在图像上绘制RTMPose骨架"""
        if keypoints is None or len(keypoints) == 0:
            return img
        
        annotated_frame = img.copy()
        
        # 定义连接关系 (COCO 17关键点格式)
        connections = [
            # 头部和面部
            [0, 1], [0, 2], [1, 3], [2, 4],  # 鼻子-眼睛-耳朵
            # 躯干
            [5, 6],   # 左肩-右肩
            [5, 11],  # 左肩-左髋
            [6, 12],  # 右肩-右髋
            [11, 12], # 左髋-右髋
            # 手臂
            [5, 7], [7, 9],    # 左肩-左肘-左腕
            [6, 8], [8, 10],   # 右肩-右肘-右腕
            # 腿部
            [11, 13], [13, 15], # 左髋-左膝-左踝
            [12, 14], [14, 16]  # 右髋-右膝-右踝
        ]
        
        # 定义颜色 (BGR格式)
        colors = {
            'head': (51, 153, 255),    # 蓝色
            'torso': (255, 153, 51),   # 橙色
            'arms': (153, 255, 51),    # 绿色
            'legs': (255, 51, 153)     # 粉色
        }
        
        # 绘制连接线
        for connection in connections:
            pt1_idx, pt2_idx = connection
            if pt1_idx < len(keypoints) and pt2_idx < len(keypoints):
                pt1 = keypoints[pt1_idx]
                pt2 = keypoints[pt2_idx]
                
                # 跳过无效点
                if (pt1[0] == 0 and pt1[1] == 0) or (pt2[0] == 0 and pt2[1] == 0):
                    continue
                
                # 选择颜色
                if pt1_idx in [0, 1, 2, 3, 4]:  # 头部
                    color = colors['head']
                elif pt1_idx in [5, 6, 11, 12]:  # 躯干
                    color = colors['torso']
                elif pt1_idx in [7, 8, 9, 10]:  # 手臂
                    color = colors['arms']
                else:  # 腿部
                    color = colors['legs']
                
                # 绘制连接线
                cv2.line(annotated_frame, 
                        (int(pt1[0]), int(pt1[1])), 
                        (int(pt2[0]), int(pt2[1])), 
                        color, 3)
        
        # 绘制关键点
        for i, point in enumerate(keypoints):
            if point[0] == 0 and point[1] == 0:  # 跳过无效点
                continue
                
            # 根据置信度调整透明度
            alpha = 1.0
            if confidence_scores is not None and i < len(confidence_scores):
                alpha = min(1.0, confidence_scores[i] / self.conf_threshold)
            
            # 选择颜色
            if i in [0, 1, 2, 3, 4]:  # 头部
                color = colors['head']
            elif i in [5, 6, 11, 12]:  # 躯干
                color = colors['torso']
            elif i in [7, 8, 9, 10]:  # 手臂
                color = colors['arms']
            else:  # 腿部
                color = colors['legs']
            
            # 应用透明度
            color = tuple(int(c * alpha) for c in color)
            
            # 绘制关键点
            cv2.circle(annotated_frame, (int(point[0]), int(point[1])), 5, color, -1)
            cv2.circle(annotated_frame, (int(point[0]), int(point[1])), 7, color, 2)
        
        return annotated_frame
    
    def set_skeleton_visibility(self, show):
        """设置骨架显示状态"""
        self.show_skeleton = show
        print(f"RTMPose骨架显示: {'开启' if show else '关闭'}") 