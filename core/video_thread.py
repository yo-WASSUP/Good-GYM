import cv2
import numpy as np
import time
import os
from PyQt5.QtCore import Qt, QThread, pyqtSignal

class VideoThread(QThread):
    """处理视频流的线程，避免UI卡顿"""
    change_pixmap_signal = pyqtSignal(np.ndarray, float)  # 增加FPS参数
    
    def __init__(self, camera_id=0, width=640, height=480, rotate=True):
        super().__init__()
        self.camera_id = camera_id
        self.width = width
        self.height = height
        self.rotate = rotate
        self._run_flag = True
        self.buffer_size = 1  # 缓冲区大小，设为1避免延迟
        self.video_file = None  # 本地视频文件路径
        self.is_camera = True  # 是否使用摄像头
        self.fps = 30  # 默认帧率
        self.loop_video = False  # 控制是否循环播放视频
        self.video_ended = False  # 标记视频是否已结束
    
    def set_camera(self, camera_id):
        """切换摄像头"""
        if self.isRunning():
            self._run_flag = False
            self.wait()
        self.camera_id = camera_id
        self.video_file = None  # 清除视频文件路径
        self.is_camera = True  # 切换回摄像头模式
        self._run_flag = True
        self.start()
    
    def set_rotation(self, rotate):
        """设置是否旋转视频"""
        self.rotate = rotate
        
    def set_resolution(self, width, height):
        """设置分辨率"""
        self.width = width
        self.height = height
        
    def set_video_file(self, file_path, loop=False):
        """设置视频文件路径
        
        Args:
            file_path (str): 视频文件路径
            loop (bool): 是否循环播放视频，默认为False
        """
        if self.isRunning():
            self._run_flag = False
            self.wait()
        self.video_file = file_path
        self.is_camera = False  # 切换到视频文件模式
        self.loop_video = loop  # 设置是否循环播放
        self.video_ended = False  # 重置视频结束标志
        
        # 预先检测视频宽高比以决定应用哪种旋转模式
        self.auto_detect_orientation(file_path)
        
        self._run_flag = True
        self.start()
        
    def auto_detect_orientation(self, file_path):
        """自动检测视频文件的宽高比并设置适当的旋转模式"""
        try:
            if not os.path.exists(file_path):
                print(f"错误：视频文件不存在 {file_path}")
                return
                
            temp_cap = cv2.VideoCapture(file_path)
            if not temp_cap.isOpened():
                print(f"错误：无法打开视频文件进行宽高比检测 {file_path}")
                return
                
            # 获取原始视频尺寸信息（不依赖帧读取）
            original_width = int(temp_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            original_height = int(temp_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            # 如果能获取到第一帧，使用第一帧的尺寸信息以确认
            ret, first_frame = temp_cap.read()
            if ret:
                height, width = first_frame.shape[:2]
                # 检查帧尺寸与视频尺寸是否一致
                if height != original_height or width != original_width:
                    # 如果有差异，采用帧的尺寸
                    original_width = width
                    original_height = height
                    print("帧尺寸与视频尺寸不同，使用帧的尺寸信息")
            
            # 释放临时摄像头
            temp_cap.release()
            
            # 计算宽高比
            aspect_ratio = original_width / original_height
            
            # 判断视频方向
            # 竖向比例小于0.8，横向比例大于1.3，中间值为正方形
            is_vertical = aspect_ratio < 0.8
            
            # 如果是竖向视频(9:16)
            if is_vertical:
                print(f"检测到竖向视频 (宽高比: {aspect_ratio:.2f}, 尺寸: {original_width}x{original_height})")
                self.rotate = False  # 不发生旋转
                # 设置宽度为原高度的一半，保持敬业的竖向显示
                self.width = max(360, original_width)  # 确保最小宽度
                self.height = int(self.width * original_height / original_width)
            # 否则为横向视频(16:9)
            else:
                print(f"检测到横向视频 (宽高比: {aspect_ratio:.2f}, 尺寸: {original_width}x{original_height})")
                self.rotate = False  # 同样不旋转
                # 调整尺寸保持横向显示
                self.height = 360  # 固定高度
                self.width = int(self.height * aspect_ratio)  # 根据原始宽高比计算宽度
        except Exception as e:
            print(f"视频宽高比检测出错: {str(e)}")
            # 出错时使用默认值
            self.rotate = False
        except Exception as e:
            print(f"视频宽高比检测出错: {str(e)}")
            # 出错时保持原始设置
    
    def run(self):
        """主线程循环"""
        # 根据模式打开视频源（摄像头或文件）
        if self.is_camera:
            self.cap = cv2.VideoCapture(self.camera_id)
            if not self.cap.isOpened():
                print(f"错误：无法打开摄像头 {self.camera_id}")
                return
                
            # 设置分辨率和缓冲区（仅适用于摄像头）
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, self.buffer_size)
            
            # 摄像头模式默认旋转（默认为竖屏模式）
            self.rotate = True
            
            print(f"摄像头已打开：ID={self.camera_id}, 分辨率={int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}")
        else:
            # 打开视频文件
            if not os.path.exists(self.video_file):
                print(f"错误：视频文件不存在 {self.video_file}")
                return
                
            self.cap = cv2.VideoCapture(self.video_file)
            if not self.cap.isOpened():
                print(f"错误：无法打开视频文件 {self.video_file}")
                return
                
            video_name = os.path.basename(self.video_file)
            print(f"视频文件已打开：{video_name}, 分辨率={int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}")
            
            # 获取实际帧率（可能与请求的不同）
            real_fps = int(self.cap.get(cv2.CAP_PROP_FPS))
            if real_fps == 0:
                real_fps = 30  # 默认值
            
            # 限制最高帧率为30fps
            self.fps = min(real_fps, 30)
            print(f"帧率: 原始{real_fps}fps, 当前显示{self.fps}fps")
        
        # 初始化FPS计算
        frame_count = 0
        start_time = time.time()
        fps_display = 0
        update_interval = 10  # 每10帧更新一次FPS显示
        
        # 运行标志
        while self._run_flag:
            ret, frame = self.cap.read()
            if ret:
                # 降采样到更小的尺寸进行处理
                frame = cv2.resize(frame, (self.width, self.height))
                
                # 如果需要旋转（竖屏模式）
                if self.rotate:
                    # 旋转90度，得到9:16比例 (使用INTER_NEAREST加速旋转)
                    frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
                
                # 计算FPS
                frame_count += 1
                if frame_count % update_interval == 0:
                    end_time = time.time()
                    elapsed_time = end_time - start_time
                    fps_display = frame_count / elapsed_time
                    frame_count = 0
                    start_time = time.time()
                
                # 发送帧和FPS信息
                self.change_pixmap_signal.emit(frame, fps_display)
            else:
                # 当读取视频文件失败时，如果是视频文件模式
                if not self.is_camera and self.video_file:
                    # 检查是否要循环播放
                    if self.loop_video:
                        # 循环模式：重置到开头继续播放
                        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        ret, frame = self.cap.read()
                        if ret:
                            # 发送帧和FPS信息
                            self.change_pixmap_signal.emit(frame, fps_display)
                        else:
                            # 如果重置仍然无法读取，输出警告
                            print("警告：视频文件播放结束且无法重新循环")
                            self.video_ended = True
                    else:
                        # 非循环模式：标记视频结束
                        if not self.video_ended:
                            print("视频播放完成，已停止在最后一帧")
                            self.video_ended = True
                else:
                    print("警告：无法读取视频帧")
            
            # 按照目标帧率定时读取帧并控制播放速度
            time.sleep(1/self.fps)  # 限制为指定帧率
        
        # 释放资源
        self.cap.release()
    
    def stop(self):
        """停止线程"""
        self._run_flag = False
        self.wait()
