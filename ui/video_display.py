from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy, QFrame
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap, QPainter

class VideoDisplay(QWidget):
    """视频显示组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # 设置背景为黑色，便于观看
        self.setStyleSheet("background-color: black;")
        
        # 布局设置 - 使用居中对齐
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.layout.setAlignment(Qt.AlignCenter)
        
        # 创建图像标签用于显示视频
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("border: none;")
        self.image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # 自动扩展以适应容器
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.layout.addWidget(self.image_label, 0, Qt.AlignCenter)
        
        # 默认设置
        self.is_portrait = True
        self.aspect_ratio = 9/16  # 默认竖屏比例
        self.set_orientation(self.is_portrait)
    
    def update_image(self, frame):
        """更新图像显示"""
        try:
            # 将OpenCV格式转换为QImage
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            convert_to_qt_format = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            
            # 检测帧的宽高比并更新设置
            frame_aspect_ratio = w / h
            self.update_aspect_ratio(frame_aspect_ratio)
            
            # 计算显示区域大小
            label_width = self.width()
            label_height = self.height()
            
            if label_width > 0 and label_height > 0:
                # 对于竖向视频，使用KeepAspectRatioByExpanding以填满尺寸
                # 对于横向视频，使用KeepAspectRatio以显示完整内容
                aspect_mode = Qt.KeepAspectRatioByExpanding if self.is_portrait and frame_aspect_ratio < 1 else Qt.KeepAspectRatio
                
                qt_img = convert_to_qt_format.scaled(
                    label_width,
                    label_height,
                    aspect_mode,
                    Qt.SmoothTransformation  # 使用平滑变换提高质量
                )
            else:
                qt_img = convert_to_qt_format
            
            # 显示图像
            self.image_label.setPixmap(QPixmap.fromImage(qt_img))
            
            # 缩放图像标签以适应容器
            self.image_label.setScaledContents(True)
            self.image_label.adjustSize()
        except Exception as e:
            print(f"更新图像时出错: {e}")
    
    def resizeEvent(self, event):
        """当组件调整大小时保持比例"""
        super().resizeEvent(event)
        # 当组件大小变化时，调整内部标签大小
        self.adjust_size()
        
    def adjust_size(self):
        """调整内部标签大小以适应容器大小，同时保持宽高比"""
        width = self.width()
        height = self.height()
        
        # 计算应该使用的高度或宽度
        target_height = width / self.aspect_ratio
        target_width = height * self.aspect_ratio
        
        # 根据容器大小决定使用哪个尺寸
        if target_height <= height:
            # 以宽度为基准
            new_size = (width, int(target_height))
            margin_h = 0
            margin_v = (height - int(target_height)) // 2
        else:
            # 以高度为基准
            new_size = (int(target_width), height)
            margin_h = (width - int(target_width)) // 2
            margin_v = 0
            
        # 设置标签大小和间距
        self.layout.setContentsMargins(margin_h, margin_v, margin_h, margin_v)
        
    def update_aspect_ratio(self, frame_aspect_ratio):
        """根据实际帧的宽高比更新显示设置
        
        Args:
            frame_aspect_ratio (float): 帧的宽高比
        """
        # 判断是否是竖向视频
        is_vertical = frame_aspect_ratio < 1
        
        # 使用实际的帧宽高比
        self.aspect_ratio = frame_aspect_ratio
        
        # 更新方向标记
        self.is_portrait = is_vertical
        
    def set_orientation(self, portrait_mode=True):
        """设置视频显示方向
        
        Args:
            portrait_mode (bool): True为竖屏模式(9:16)，False为横屏模式(16:9)
        """
        self.is_portrait = portrait_mode
        
        if portrait_mode:
            # 竖屏模式 - 9:16比例
            self.aspect_ratio = 9/16
            self.image_label.setMinimumSize(360, 640)
        else:
            # 横屏模式 - 16:9比例
            self.aspect_ratio = 16/9
            self.image_label.setMinimumSize(640, 360)
        
        # 调整大小以适应新的宽高比
        self.adjust_size()
