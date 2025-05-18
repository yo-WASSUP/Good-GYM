from PyQt5.QtWidgets import QPushButton, QWidget, QHBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QBrush, QPen, QFont

class ToggleSwitch(QPushButton):
    """自定义滑动开关按钮组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setChecked(True)  # 默认开启状态
        self.setMinimumWidth(80)
        self.setMaximumWidth(80)
        self.setMinimumHeight(30)
        self.setMaximumHeight(30)
        
        # 设置颜色
        self.on_color = QColor("#2ecc71")  # 绿色
        self.off_color = QColor("#bdc3c7")  # 灰色
        self.thumb_color = QColor("#ffffff")  # 白色
        self.text_color = QColor("#ffffff")  # 白色
        
        # 连接状态变化信号到更新文本方法
        self.toggled.connect(self.update_text)
        self.update_text(self.isChecked())
    
    def update_text(self, checked):
        """根据状态更新按钮文本"""
        self.setText("开" if checked else "关")
        self.update()  # 强制重绘
    
    def paintEvent(self, event):
        """自定义绘制事件"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 设置字体
        font = QFont("Microsoft YaHei", 10, QFont.Bold)
        painter.setFont(font)
        
        # 确定背景颜色
        bg_color = self.on_color if self.isChecked() else self.off_color
        
        # 绘制背景
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(bg_color))
        painter.drawRoundedRect(0, 0, self.width(), self.height(), 15, 15)
        
        # 绘制滑块
        thumb_radius = self.height() - 6
        thumb_x = self.width() - thumb_radius - 3 if self.isChecked() else 3
        painter.setBrush(QBrush(self.thumb_color))
        painter.drawEllipse(thumb_x, 3, thumb_radius, thumb_radius)
        
        # 绘制文本
        painter.setPen(QPen(self.text_color))
        text_x = 5 if self.isChecked() else self.width() - 30
        painter.drawText(text_x, 0, 30, self.height(), Qt.AlignCenter, self.text())
        
class SwitchControl(QWidget):
    """带标签的滑动开关控件"""
    
    switched = pyqtSignal(bool)
    
    def __init__(self, label_text, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建滑动开关
        self.toggle = ToggleSwitch()
        self.toggle.toggled.connect(self.switched.emit)
        
        # 设置标签
        from PyQt5.QtWidgets import QLabel
        self.label = QLabel(label_text)
        self.label.setStyleSheet("color: #2c3e50; font-size: 14pt;")
        
        # 添加到布局
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.toggle, 0, Qt.AlignRight)
    
    def isChecked(self):
        """返回当前开关状态"""
        return self.toggle.isChecked()
    
    def setChecked(self, checked):
        """设置开关状态"""
        self.toggle.setChecked(checked)
        
    def setText(self, text):
        """设置标签文本"""
        self.label.setText(text)
