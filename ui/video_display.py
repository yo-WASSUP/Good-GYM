from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy, QFrame
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap, QPainter

class VideoDisplay(QWidget):
    """Video display component"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # Set background to black for better viewing
        self.setStyleSheet("background-color: black;")
        
        # Layout setup - use center alignment
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.layout.setAlignment(Qt.AlignCenter)
        
        # Create image label for video display
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("border: none;")
        self.image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Auto-expand to fit container
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.layout.addWidget(self.image_label, 0, Qt.AlignCenter)
        
        # Default settings
        self.is_portrait = True
        self.aspect_ratio = 9/16  # Default portrait ratio
        self.set_orientation(self.is_portrait)
    
    def update_image(self, frame):
        """Update image display"""
        try:
            # Convert OpenCV format to QImage
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            convert_to_qt_format = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            
            # Detect frame aspect ratio and update settings
            frame_aspect_ratio = w / h
            self.update_aspect_ratio(frame_aspect_ratio)
            
            # Calculate display area size
            label_width = self.width()
            label_height = self.height()
            
            if label_width > 0 and label_height > 0:
                # For vertical videos, use KeepAspectRatioByExpanding to fill dimensions
                # For horizontal videos, use KeepAspectRatio to show complete content
                aspect_mode = Qt.KeepAspectRatioByExpanding if self.is_portrait and frame_aspect_ratio < 1 else Qt.KeepAspectRatio
                
                qt_img = convert_to_qt_format.scaled(
                    label_width,
                    label_height,
                    aspect_mode,
                    Qt.SmoothTransformation  # Use smooth transformation for better quality
                )
            else:
                qt_img = convert_to_qt_format
            
            # Display image
            self.image_label.setPixmap(QPixmap.fromImage(qt_img))
            
            # Scale image label to fit container
            self.image_label.setScaledContents(True)
            self.image_label.adjustSize()
        except Exception as e:
            print(f"Error updating image: {e}")
    
    def resizeEvent(self, event):
        """Maintain aspect ratio when component is resized"""
        super().resizeEvent(event)
        # When component size changes, adjust internal label size
        self.adjust_size()
        
    def adjust_size(self):
        """Adjust internal label size to fit container size while maintaining aspect ratio"""
        width = self.width()
        height = self.height()
        
        # Calculate target height or width
        target_height = width / self.aspect_ratio
        target_width = height * self.aspect_ratio
        
        # Decide which dimension to use based on container size
        if target_height <= height:
            # Use width as base
            new_size = (width, int(target_height))
            margin_h = 0
            margin_v = (height - int(target_height)) // 2
        else:
            # Use height as base
            new_size = (int(target_width), height)
            margin_h = (width - int(target_width)) // 2
            margin_v = 0
            
        # Set label size and margins
        self.layout.setContentsMargins(margin_h, margin_v, margin_h, margin_v)
        
    def update_aspect_ratio(self, frame_aspect_ratio):
        """Update display settings based on actual frame aspect ratio
        
        Args:
            frame_aspect_ratio (float): Frame aspect ratio
        """
        # Determine if it's a vertical video
        is_vertical = frame_aspect_ratio < 1
        
        # Use actual frame aspect ratio
        self.aspect_ratio = frame_aspect_ratio
        
        # Update orientation flag
        self.is_portrait = is_vertical
        
    def set_orientation(self, portrait_mode=True):
        """Set video display orientation
        
        Args:
            portrait_mode (bool): True for portrait mode (9:16), False for landscape mode (16:9)
        """
        self.is_portrait = portrait_mode
        
        if portrait_mode:
            # Portrait mode - 9:16 ratio
            self.aspect_ratio = 9/16
            self.image_label.setMinimumSize(360, 640)
        else:
            # Landscape mode - 16:9 ratio
            self.aspect_ratio = 16/9
            self.image_label.setMinimumSize(640, 360)
        
        # Adjust size to fit new aspect ratio
        self.adjust_size()
