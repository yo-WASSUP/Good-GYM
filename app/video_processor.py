"""
视频处理模块 - 负责图像更新和姿态检测
"""

import cv2
import os
import time
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import QTimer
from core.translations import Translations as T

class VideoProcessor:
    """视频处理器类"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.pose_interval_seconds = 1 / 20
        self.metric_interval_seconds = 0.25
        self._last_pose_time = 0
        self._last_metric_time = 0
        self._cached_pose = None

    def reset_pose_cache(self):
        self._last_pose_time = 0
        self._last_metric_time = 0
        self._cached_pose = None

    def _get_pose_result(self, inference_frame):
        frame_shape = inference_frame.shape[:2]
        now = time.perf_counter()
        should_infer = (
            self._cached_pose is None
            or self._cached_pose["shape"] != frame_shape
            or now - self._last_pose_time >= self.pose_interval_seconds
        )

        did_infer = False
        if should_infer:
            inference_start = time.perf_counter()
            _, current_angle, angle_point, keypoints = self.main_window.pose_processor.process_frame(
                inference_frame, self.main_window.exercise_type
            )
            inference_ms = (time.perf_counter() - inference_start) * 1000
            if hasattr(self.main_window, "status_rail"):
                self.main_window.status_rail.update_inference(inference_ms)

            self._cached_pose = {
                "current_angle": current_angle,
                "angle_point": angle_point,
                "keypoints": keypoints,
                "shape": frame_shape,
            }
            self._last_pose_time = now
            did_infer = True

        return self._cached_pose, did_infer
    
    def update_image(self, frame, inference_frame=None, fps=0):
        """更新图像显示并处理姿态检测"""
        try:
            if inference_frame is not None and not hasattr(inference_frame, "shape"):
                fps = inference_frame
                inference_frame = None

            if getattr(self.main_window, "suspend_video_processing", False):
                return

            # 更新FPS值
            now = time.perf_counter()
            self.main_window.current_fps = fps
            should_update_metrics = now - self._last_metric_time >= self.metric_interval_seconds
            if should_update_metrics and hasattr(self.main_window, "status_rail"):
                self.main_window.status_rail.update_fps(fps)
                self._last_metric_time = now
            
            # 使用推理帧进行姿态检测（如果可用）
            if inference_frame is None:
                inference_frame = frame
            
            # 姿态处理器处理推理帧，获取关键点信息和角度点
            pose_result, pose_updated = self._get_pose_result(inference_frame)
            current_angle = pose_result["current_angle"]
            angle_point = pose_result["angle_point"]
            keypoints = pose_result["keypoints"]
            pose_height, pose_width = pose_result["shape"]
            
            # 准备高分辨率显示帧
            display_frame = frame.copy()
            
            # 计算缩放比例（推理帧到显示帧）
            scale_x = display_frame.shape[1] / pose_width
            scale_y = display_frame.shape[0] / pose_height
            
            # 如果有关键点信息，在高分辨率帧上绘制骨架
            if keypoints is not None and self.main_window.pose_processor.show_skeleton:
                # 将关键点坐标缩放到显示帧尺寸
                scaled_keypoints = keypoints.copy()
                scaled_keypoints[:, 0] *= scale_x
                scaled_keypoints[:, 1] *= scale_y
                
                # 在高分辨率帧上绘制骨架
                display_frame = self.draw_skeleton_on_frame(display_frame, scaled_keypoints)
            
            # 先缩放角度点坐标（基于推理帧尺寸）
            if angle_point is not None and len(angle_point) == 3:
                # 先缩放到显示帧尺寸
                scaled_angle_point = [
                    [int(angle_point[0][0] * scale_x), int(angle_point[0][1] * scale_y)],
                    [int(angle_point[1][0] * scale_x), int(angle_point[1][1] * scale_y)],
                    [int(angle_point[2][0] * scale_x), int(angle_point[2][1] * scale_y)]
                ]
            else:
                scaled_angle_point = None
            
            # 如果启用镜像模式，先应用镜像处理
            if self.main_window.mirror_mode and not getattr(self.main_window.video_thread, 'mirror', False):
                display_frame = cv2.flip(display_frame, 1)
                # 镜像后需要调整角度点坐标（因为显示帧被镜像了）
                if scaled_angle_point is not None:
                    frame_width = display_frame.shape[1]
                    # 镜像 x 坐标：frame_width - x
                    scaled_angle_point = [
                        [int(frame_width - scaled_angle_point[0][0]), scaled_angle_point[0][1]],
                        [int(frame_width - scaled_angle_point[1][0]), scaled_angle_point[1][1]],
                        [int(frame_width - scaled_angle_point[2][0]), scaled_angle_point[2][1]]
                    ]
            
            # 在镜像后绘制角度线（这样角度线位置就正确了）
            if scaled_angle_point is not None:
                display_frame = self.draw_angle_lines(display_frame, scaled_angle_point, current_angle)
            
            # 转换BGR到RGB（Qt需要RGB格式）
            display_frame = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
            
            # 更新视频显示
            self.main_window.video_display.update_image(display_frame)
            
            # 更新UI组件
            if pose_updated:
                self.update_ui_components(current_angle, keypoints)
            
        except Exception as e:
            print(f"Error updating image: {e}")
    
    def draw_skeleton_on_frame(self, frame, keypoints):
        """在高分辨率帧上绘制骨架"""
        try:
            # 定义连接关系 (COCO 17 keypoint format)
            connections = [
                # Head and face
                [0, 1], [0, 2], [1, 3], [2, 4],  # nose-eyes-ears
                # Torso
                [5, 6],   # left_shoulder-right_shoulder
                [5, 11],  # left_shoulder-left_hip
                [6, 12],  # right_shoulder-right_hip
                [11, 12], # left_hip-right_hip
                # Arms
                [5, 7], [7, 9],    # left_shoulder-left_elbow-left_wrist
                [6, 8], [8, 10],   # right_shoulder-right_elbow-right_wrist
                # Legs
                [11, 13], [13, 15], # left_hip-left_knee-left_ankle
                [12, 14], [14, 16]  # right_hip-right_knee-right_ankle
            ]
            
            # 定义颜色 (BGR format)
            colors = {
                'head': (51, 153, 255),    # Blue
                'torso': (255, 153, 51),   # Orange
                'arms': (153, 255, 51),    # Green
                'legs': (255, 51, 153)     # Pink
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
                    if pt1_idx in [0, 1, 2, 3, 4]:  # Head
                        color = colors['head']
                    elif pt1_idx in [5, 6, 11, 12]:  # Torso
                        color = colors['torso']
                    elif pt1_idx in [7, 8, 9, 10]:  # Arms
                        color = colors['arms']
                    else:  # Legs
                        color = colors['legs']
                    
                    # 绘制连接线 - 根据分辨率调整线条粗细
                    line_thickness = max(2, int(frame.shape[1] / 640 * 3))
                    cv2.line(frame, 
                            (int(pt1[0]), int(pt1[1])), 
                            (int(pt2[0]), int(pt2[1])), 
                            color, line_thickness)
            
            # 绘制关键点
            for i, point in enumerate(keypoints):
                if point[0] == 0 and point[1] == 0:  # 跳过无效点
                    continue
                
                # 选择颜色
                if i in [0, 1, 2, 3, 4]:  # Head
                    color = colors['head']
                elif i in [5, 6, 11, 12]:  # Torso
                    color = colors['torso']
                elif i in [7, 8, 9, 10]:  # Arms
                    color = colors['arms']
                else:  # Legs
                    color = colors['legs']
                
                # 根据分辨率调整关键点大小
                point_radius = max(3, int(frame.shape[1] / 640 * 5))
                cv2.circle(frame, (int(point[0]), int(point[1])), point_radius, color, -1)
                cv2.circle(frame, (int(point[0]), int(point[1])), point_radius + 2, color, 2)
            
            return frame
            
        except Exception as e:
            print(f"Error drawing skeleton: {e}")
            return frame
    
    def draw_angle_lines(self, frame, angle_point, angle_value):
        """在帧上绘制角度线和角度值"""
        try:
            if angle_point is None or len(angle_point) != 3:
                return frame
            
            pt1, pt2, pt3 = angle_point
            
            # 检查点是否有效（不是 (0, 0) 且在帧范围内）
            frame_height, frame_width = frame.shape[:2]
            if (pt1[0] == 0 and pt1[1] == 0) or (pt2[0] == 0 and pt2[1] == 0) or (pt3[0] == 0 and pt3[1] == 0):
                return frame
            
            # 检查坐标是否在有效范围内（防止坐标超出帧范围导致绘制到错误位置）
            if (pt1[0] < 0 or pt1[0] >= frame_width or pt1[1] < 0 or pt1[1] >= frame_height or
                pt2[0] < 0 or pt2[0] >= frame_width or pt2[1] < 0 or pt2[1] >= frame_height or
                pt3[0] < 0 or pt3[0] >= frame_width or pt3[1] < 0 or pt3[1] >= frame_height):
                # 坐标超出范围，不绘制
                return frame
            
            # 定义角度线颜色（黄色，BGR格式）
            angle_color = (0, 255, 255)  # Yellow
            
            # 根据分辨率调整线条粗细
            line_thickness = max(2, int(frame.shape[1] / 640 * 2))
            
            # 绘制两条角度线：pt1-pt2 和 pt2-pt3
            cv2.line(frame, (pt1[0], pt1[1]), (pt2[0], pt2[1]), angle_color, line_thickness)
            cv2.line(frame, (pt2[0], pt2[1]), (pt3[0], pt3[1]), angle_color, line_thickness)
            
            # 在中间点（pt2）绘制一个小圆圈
            circle_radius = max(4, int(frame.shape[1] / 640 * 6))
            cv2.circle(frame, (pt2[0], pt2[1]), circle_radius, angle_color, -1)
            
            # 在角度点附近显示角度值（如果角度值有效）
            if angle_value is not None:
                # 计算文本位置（在中间点上方）
                text_x = pt2[0]
                text_y = pt2[1] - 20
                
                # 确保文本位置在帧内
                if text_y < 20:
                    text_y = pt2[1] + 30
                
                # 绘制角度值文本（使用数字和deg避免特殊字符显示问题）
                font_scale = max(0.5, frame.shape[1] / 640 * 0.6)
                # 使用 "deg" 代替度符号，避免显示问题
                text = f"{int(angle_value)} deg"
                cv2.putText(frame, text, (text_x, text_y), 
                           cv2.FONT_HERSHEY_SIMPLEX, font_scale, angle_color, 2)
            
            return frame
            
        except Exception as e:
            print(f"Error drawing angle lines: {e}")
            return frame
    
    def update_ui_components(self, current_angle, keypoints):
        """更新UI组件显示"""
        try:
            # 更新角度显示 - 注释掉这部分代码
            # if current_angle is not None:
            #     self.main_window.control_panel.update_angle(str(int(current_angle)), self.main_window.exercise_type)
            
            # 更新阶段显示（上/下）
            if hasattr(self.main_window.exercise_counter, 'stage'):
                stage = self.main_window.exercise_counter.stage
                if hasattr(self.main_window, "status_rail"):
                    self.main_window.status_rail.update_phase(stage)
                self.main_window.control_panel.update_phase(stage)
            
            # 获取当前计数 - 直接使用计数器属性
            current_count = self.main_window.exercise_counter.counter
            
            # 如果计数增加且不是重置操作，播放声音（但不自动记录）
            if current_count > self.main_window.current_count and not self.main_window.is_resetting:
                # 为每次计数增加播放计数声音
                self.main_window.sound_manager.play_count_sound()
                
                # 每10次计数播放成功声音
                if current_count % 10 == 0:
                    self.main_window.sound_manager.play_milestone_sound(current_count)
                    self.main_window.statusBar.showMessage(f"Congratulations on completing {current_count} {self.main_window.control_panel.exercise_display_map[self.main_window.exercise_type]}!")
                
                # 更新缓存的当前计数
                self.main_window.current_count = current_count
            
            # 更新计数器显示
            if hasattr(self.main_window, "status_rail"):
                self.main_window.status_rail.update_counter(str(current_count))
            self.main_window.control_panel.update_counter(str(current_count))
        except Exception as e:
            print(f"Error updating image: {str(e)}")
    
    def change_camera(self, index):
        """切换摄像头"""
        self.main_window.suspend_video_processing = True
        self.reset_pose_cache()
        self.main_window.statusBar.showMessage(f"Switching to camera {index}...")
        self.main_window.current_camera_id = index
        self.main_window.is_camera_source = True
        self.main_window.current_video_file = None
        self.main_window.video_thread.set_camera(index)
        self.main_window.video_thread.set_rotation(self.main_window.rotation_mode)
        self.main_window.video_thread.set_mirror(self.main_window.mirror_mode)
        if hasattr(self.main_window, "status_rail"):
            self.main_window.status_rail.update_camera(index)
        QTimer.singleShot(250, lambda: setattr(self.main_window, "suspend_video_processing", False))
        self.main_window.statusBar.showMessage(f"Switched to camera {index}")
    
    def toggle_rotation(self, rotate):
        """切换视频旋转模式"""
        # 更新视频线程旋转设置
        self.reset_pose_cache()
        self.main_window.rotation_mode = rotate
        self.main_window.video_thread.set_rotation(rotate)
        
        # 更新视频显示方向设置
        # rotate=True表示竖屏，False表示横屏
        self.main_window.video_display.set_orientation(portrait_mode=rotate)
        
        if rotate:
            self.main_window.toggle_rotation_action.setText("Turn off rotation mode")
            self.main_window.statusBar.showMessage("Switched to portrait mode (full camera frame)")
        else:
            self.main_window.toggle_rotation_action.setText("Turn on rotation mode")
            self.main_window.statusBar.showMessage("Switched to landscape mode (full camera frame)")
    
    def toggle_skeleton(self, show):
        """切换骨架显示"""
        self.main_window.pose_processor.set_skeleton_visibility(show)
        if hasattr(self.main_window, 'toggle_skeleton_action'):
            self.main_window.toggle_skeleton_action.setChecked(show)
        if show:
            self.main_window.statusBar.showMessage("Show skeleton lines")
        else:
            self.main_window.statusBar.showMessage("Hide skeleton lines")
    
    def toggle_mirror(self, mirror):
        """切换镜像模式"""
        self.reset_pose_cache()
        self.main_window.mirror_mode = mirror
        # 同步更新 video_thread 的镜像设置
        if hasattr(self.main_window, 'video_thread'):
            self.main_window.video_thread.set_mirror(mirror)
        self.main_window.statusBar.showMessage(f"Mirror mode: {'ON' if mirror else 'OFF'}")
        
        # 更新菜单动作状态
        if hasattr(self.main_window, 'toggle_mirror_action'):
            self.main_window.toggle_mirror_action.setChecked(mirror)
    
    def open_video_file(self):
        """打开视频文件"""
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(
            self.main_window,
            T.get("open_video"),
            "",
            T.get("video_files"),
            options=options
        )
        
        if file_name:
            try:
                self.reset_pose_cache()
                # 清除当前计数状态
                self.main_window.reset_exercise_state()
                
                # 切换到运动模式（如果当前不是）
                if hasattr(self.main_window, 'stacked_layout') and hasattr(self.main_window, 'exercise_container'):
                    if not self.main_window.stacked_layout.currentWidget() == self.main_window.exercise_container:
                        self.main_window.switch_to_workout_mode()
                
                # 设置状态栏信息
                video_name = os.path.basename(file_name)
                self.main_window.statusBar.showMessage(f"Current video: {video_name}")
                self.main_window.is_camera_source = False
                self.main_window.current_video_file = file_name
                
                # 将文件路径传递给视频线程，设置为非循环播放模式
                self.main_window.video_thread.set_video_file(file_name, loop=False)
            except Exception as e:
                print(f"Error opening video file: {e}")
                self.main_window.statusBar.showMessage(f"Failed to open video file: {str(e)}")
    
    def switch_to_camera_mode(self):
        """切换回摄像头模式"""
        try:
            # 清除当前计数状态
            self.main_window.reset_exercise_state()
            
            # 切换到运动模式（如果当前不是）
            if hasattr(self.main_window, 'stacked_layout') and hasattr(self.main_window, 'exercise_container'):
                if not self.main_window.stacked_layout.currentWidget() == self.main_window.exercise_container:
                    self.main_window.switch_to_workout_mode()
                
            # 设置状态栏信息
            self.reset_pose_cache()
            self.main_window.statusBar.showMessage("Current mode: Camera")
            
            # 返回摄像头模式
            camera_id = getattr(self.main_window, "current_camera_id", 0)
            self.main_window.is_camera_source = True
            self.main_window.current_video_file = None
            self.main_window.video_thread.set_camera(camera_id)
        except Exception as e:
            print(f"Error switching to camera mode: {e}")
            self.main_window.statusBar.showMessage(f"Failed to switch to camera mode: {str(e)}")
    
    def change_device(self, device):
        """切换推理设备 (cpu/cuda)"""
        try:
            if device == self.main_window.device:
                return

            # 停止视频处理
            self.main_window.suspend_video_processing = True
            self.reset_pose_cache()
            self.main_window.video_thread.stop()

            self.main_window.statusBar.showMessage(f"Switching device to: {device}...")

            old_device = self.main_window.device
            self.main_window.device = device

            print(f"Switching device: {old_device} -> {device}")

            # 更新RTMPose处理器设备
            self.main_window.pose_processor.update_device(device)

            # 重新初始化视频线程
            self.main_window.setup_video_thread()
            QTimer.singleShot(500, self.main_window.start_video)

            self.main_window.statusBar.showMessage(
                f"RTMPose ({self.main_window.model_mode}) on {device}")
            self.main_window.update_runtime_badge()
            QTimer.singleShot(250, lambda: setattr(self.main_window, "suspend_video_processing", False))

        except Exception as e:
            error_msg = f"Device switching failed: {str(e)}"
            self.main_window.statusBar.showMessage(error_msg)
            print(error_msg)

            try:
                self.main_window.device = old_device
                self.main_window.pose_processor.update_device(old_device)
                self.main_window.setup_video_thread()
                QTimer.singleShot(500, self.main_window.start_video)
                self.main_window.statusBar.showMessage(f"Rolled back to {old_device}")
                self.main_window.update_runtime_badge()
                QTimer.singleShot(250, lambda: setattr(self.main_window, "suspend_video_processing", False))
            except:
                self.main_window.statusBar.showMessage("Critical error in device switching")

    def change_model(self, model_mode):
        """切换RTMPose模型模式"""
        try:
            if model_mode == self.main_window.model_mode:
                # 如果是相同模式，无需重新加载
                return

            # 停止视频处理
            self.main_window.suspend_video_processing = True
            self.reset_pose_cache()
            self.main_window.video_thread.stop()

            # 显示状态信息
            self.main_window.statusBar.showMessage(f"Switching RTMPose mode to: {model_mode}...")

            # 更新模型模式
            old_model_mode = self.main_window.model_mode
            self.main_window.model_mode = model_mode

            print(f"Switching RTMPose mode: {old_model_mode} -> {model_mode}")

            # 更新RTMPose处理器模式
            self.main_window.pose_processor.update_model(model_mode)

            # 重新初始化视频线程
            self.main_window.setup_video_thread()

            # 重新启动视频处理
            QTimer.singleShot(500, self.main_window.start_video)  # 延迟500ms后开始视频

            # 更新状态栏
            self.main_window.statusBar.showMessage(f"Switched to RTMPose {model_mode} mode")
            self.main_window.update_runtime_badge()
            QTimer.singleShot(250, lambda: setattr(self.main_window, "suspend_video_processing", False))

        except Exception as e:
            # 如果切换失败，显示错误消息
            error_msg = f"RTMPose mode switching failed: {str(e)}"
            self.main_window.statusBar.showMessage(error_msg)
            print(error_msg)

            # 尝试回滚到原始模式
            try:
                self.main_window.model_mode = old_model_mode
                self.main_window.pose_processor.update_model(old_model_mode)
                self.main_window.setup_video_thread()
                QTimer.singleShot(500, self.main_window.start_video)
                self.main_window.statusBar.showMessage(f"Rolled back to RTMPose {old_model_mode} mode")
                self.main_window.update_runtime_badge()
                QTimer.singleShot(250, lambda: setattr(self.main_window, "suspend_video_processing", False))

            except:
                # 如果回滚也失败，显示严重错误
                self.main_window.statusBar.showMessage("Critical error in RTMPose mode switching") 
