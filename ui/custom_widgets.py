from PyQt5.QtWidgets import QPushButton, QWidget, QHBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QBrush, QPen, QFont

class ToggleSwitch(QPushButton):
    """Custom sliding switch button component"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setChecked(True)  # Default on state
        self.setMinimumWidth(50)
        self.setMaximumWidth(50)
        self.setMinimumHeight(24)
        self.setMaximumHeight(24)
        
        # Set colors
        self.on_color = QColor("#38D6B2")
        self.off_color = QColor("#1B2530")
        self.disabled_color = QColor("#171D24")
        self.thumb_color = QColor("#ffffff")  # White
        self.text_color = QColor("#07110F")
        
        # Connect state change signal to update text method
        self.toggled.connect(self.update_text)
        self.update_text(self.isChecked())
    
    def update_text(self, checked):
        """Update button text based on state"""
        self.setText("")
        self.update()  # Force redraw
    
    def paintEvent(self, event):
        """Custom paint event"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Set font
        font = QFont("Microsoft YaHei", 10, QFont.Bold)
        painter.setFont(font)
        
        # Determine background color
        if not self.isEnabled():
            bg_color = self.disabled_color
        else:
            bg_color = self.on_color if self.isChecked() else self.off_color
        
        # Draw background
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(bg_color))
        painter.drawRoundedRect(0, 0, self.width(), self.height(), 13, 13)
        
        # Draw thumb
        thumb_radius = self.height() - 8
        thumb_x = self.width() - thumb_radius - 3 if self.isChecked() else 3
        painter.setBrush(QBrush(QColor("#6B7784") if not self.isEnabled() else self.thumb_color))
        painter.drawEllipse(thumb_x, 4, thumb_radius, thumb_radius)
        
        # Draw text
        painter.setPen(QPen(self.text_color))
        if self.text():
            text_x = 5 if self.isChecked() else self.width() - 30
            painter.drawText(text_x, 0, 30, self.height(), Qt.AlignCenter, self.text())
        
class SwitchControl(QWidget):
    """Sliding switch control with label"""
    
    switched = pyqtSignal(bool)
    
    def __init__(self, label_text, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(12)
        
        # Create sliding switch
        self.toggle = ToggleSwitch()
        self.toggle.toggled.connect(self.switched.emit)
        
        # Set label
        from PyQt5.QtWidgets import QLabel
        self.label = QLabel(label_text)
        self.label.setStyleSheet("color: #D4DCE4; font-size: 10pt; font-weight: 700;")
        
        # Add to layout
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.toggle, 0, Qt.AlignRight)
    
    def isChecked(self):
        """Return current switch state"""
        return self.toggle.isChecked()
    
    def setChecked(self, checked):
        """Set switch state"""
        self.toggle.setChecked(checked)
        
    def setText(self, text):
        """Set label text"""
        self.label.setText(text)
