from PyQt5.QtWidgets import (QWidget, QLabel, QProgressBar, QTableWidget, 
                             QHeaderView, QFrame, QGroupBox, QVBoxLayout, QHBoxLayout)
from PyQt5.QtCore import Qt, QSize, QRectF
from PyQt5.QtGui import QFont, QColor, QPainter, QPen, QBrush, QPainterPath
import datetime
from ..styles import AppStyles

class StyledGroupBox(QGroupBox):
    """样式化分组框组件"""
    
    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.setStyleSheet(AppStyles.get_group_box_style() + """
            QGroupBox { 
                font-family: 'Microsoft YaHei';
                font-size: 18px; 
                font-weight: bold;
                padding-top: 25px;
            }
        """)


class StyledProgressBar(QProgressBar):
    """样式化进度条组件"""
    
    def __init__(self, color="#3498db", parent=None):
        super().__init__(parent)
        self.setRange(0, 100)
        self.setValue(0)
        self.setTextVisible(True)
        self.setFormat("%v / 0")  # 初始加载时不知道目标值
        self.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid #bdc3c7;
                border-radius: 10px;
                text-align: center;
                height: 25px;
                font-family: 'Microsoft YaHei';
                font-size: 14px;
                font-weight: bold;
                margin-top: 5px;
                margin-bottom: 10px;
                padding: 0px;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 8px;
            }}
        """)


class DayCircleIndicator(QWidget):
    """七个圆圈表示每周健身进度的自定义组件"""
    
    def __init__(self, parent=None, days=7, active_color="#3498db", inactive_color="#ecf0f1", 
                 partial_color="#a6dcff"):
        super().__init__(parent)
        self.days = days  # 总天数
        
        # 初始化当前状态
        # 0=未开始，1=部分完成，2=完全完成
        self.day_status = [0] * self.days
        
        # 颜色设置
        self.active_color = active_color      # 完成的圆圈颜色
        self.inactive_color = inactive_color  # 未开始的圆圈颜色
        self.partial_color = partial_color    # 部分完成的圆圈颜色
        
        # 不同周几的标签
        self.day_labels = ["一", "二", "三", "四", "五", "六", "日"]
        
        # 设置布局和大小
        self.setMinimumHeight(50)
        self.setMaximumHeight(80)
        
    def setDaysProgress(self, completed, partial=0):
        """这是向后兼容的方法，使用数字设置进度
        
        Args:
            completed: 完全完成的天数
            partial: 部分完成的天数
        """
        # 重置所有状态
        self.day_status = [0] * self.days
        
        # 设置完成状态，从前往后填充
        for i in range(min(completed, self.days)):
            self.day_status[i] = 2  # 完全完成
            
        # 设置部分完成状态
        for i in range(completed, min(completed + partial, self.days)):
            self.day_status[i] = 1  # 部分完成
            
        self.update()  # 刷新绘制
        
    def setDayStatus(self, day_status):
        """设置每天的状态
        
        Args:
            day_status: 一个长度为7的数组，对应周一到周日的状态
                       0=未开始，1=部分完成，2=完全完成
        """
        if len(day_status) != self.days:
            print(f"警告: 提供的状态数组长度({len(day_status)})与预期的天数({self.days})不匹配")
            return
            
        self.day_status = day_status[:]
        self.update()  # 刷新绘制
        
    def paintEvent(self, event):
        """绘制圆圈"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)  # 抗锯齿
        
        # 计算圆圈的大小和间距
        width = self.width()
        height = self.height()
        circle_diameter = min(height - 20, (width - 20) / self.days)  # 保留更多垂直空间
        
        # 调整为合适的大小
        circle_diameter = min(circle_diameter, 40)  # 最大直径40px
        
        # 计算开始位置使圆圈居中
        margin = (width - (circle_diameter * self.days + (self.days - 1) * 10)) / 2
        
        # 圆圈垂直居中
        y_center = height / 2 - 5  # 小幅度上移，为文字说明留空间
        
        # 创建字体
        font = painter.font()
        font.setPointSize(8)
        painter.setFont(font)
        
        # 绘制圆圈与文本
        for i in range(self.days):
            x = margin + i * (circle_diameter + 10)  # 水平位置，包括间距
            circle_rect = QRectF(x, y_center - circle_diameter/2, circle_diameter, circle_diameter)
            
            # 根据状态绘制圆圈
            if self.day_status[i] == 2:  # 完全完成
                # 填充圆圈
                painter.setPen(QPen(QColor(self.active_color), 2))
                painter.setBrush(QBrush(QColor(self.active_color)))
                painter.drawEllipse(circle_rect)
            elif self.day_status[i] == 1:  # 部分完成
                # 绘制外圈
                painter.setPen(QPen(QColor(self.active_color), 2))
                painter.setBrush(Qt.NoBrush)
                painter.drawEllipse(circle_rect)
                
                # 绘制半填充，在底部显示半圆
                painter.setBrush(QBrush(QColor(self.partial_color)))
                path = QPainterPath()
                path.moveTo(circle_rect.center())
                # 绘制底部半圆：从180度(左侧)开始，扫描180度到0度(右侧)
                path.arcTo(circle_rect, 180, 180)  # 底部半圆
                path.lineTo(circle_rect.center())
                painter.drawPath(path)
            else:  # 未开始
                # 空心圆圈
                painter.setPen(QPen(QColor(self.inactive_color), 2))
                painter.setBrush(Qt.NoBrush)
                painter.drawEllipse(circle_rect)
                
            # 在圆圈下方添加周几文本
            text_rect = QRectF(x, y_center + circle_diameter/2 + 2, circle_diameter, 15)
            painter.setPen(QPen(QColor("#34495e")))
            painter.drawText(text_rect, Qt.AlignCenter, self.day_labels[i])
                
        painter.end()

class MonthCalendarIndicator(QWidget):
    """日历形式显示每月健身进度的组件"""
    
    def __init__(self, parent=None, days_in_month=31, columns=7, 
                 active_color="#27ae60", inactive_color="#ecf0f1", 
                 partial_color="#a5ebc8"):
        super().__init__(parent)
        self.days_in_month = days_in_month  # 月份天数
        self.columns = columns  # 日历列数（一般为7，对应周一到周日）
        
        # 初始化状态数组（每天的状态）
        # 0=未开始，1=部分完成，2=完全完成
        self.day_status = [0] * (self.days_in_month + 1)  # 索引从1开始，对应日期
        
        # 颜色设置
        self.active_color = active_color      # 完成的日期颜色
        self.inactive_color = inactive_color  # 未开始的日期颜色
        self.partial_color = partial_color    # 部分完成的日期颜色
        
        # 设置布局和大小
        self.setMinimumHeight(180)
        self.setMaximumHeight(250)
        
        # 周几标签
        self.weekday_labels = ["一", "二", "三", "四", "五", "六", "日"]
        
        # 计算当前月份的第一天是周几
        today = datetime.date.today()
        self.first_day_weekday = datetime.date(today.year, today.month, 1).weekday()  # 0=周一，6=周日
    
    def setDaysInMonth(self, days_in_month):
        """设置月份天数"""
        self.days_in_month = days_in_month
        # 重置状态数组
        self.day_status = [0] * (days_in_month + 1)  # 0不使用，从1开始
        self.update()  # 触发重绘
    
    def setMonthStart(self, first_day_weekday):
        """设置月份第一天是周几（0=周一，6=周日）"""
        self.first_day_weekday = first_day_weekday
        self.update()
    
    def setDayStatus(self, day, status):
        """设置某一天的状态
        
        Args:
            day: 当月的第几天（1-31）
            status: 状态（0=未开始，1=部分完成，2=完全完成）
        """
        if 1 <= day <= self.days_in_month:
            self.day_status[day] = status
            self.update()
    
    def setMonthStatus(self, status_dict):
        """设置整个月的状态
        
        Args:
            status_dict: 字典，键为当月日期（1-31），值为状态（0,1,2）
        """
        # 重置状态
        self.day_status = [0] * (self.days_in_month + 1)
        
        # 设置每天的状态
        for day, status in status_dict.items():
            if 1 <= day <= self.days_in_month:
                self.day_status[day] = status
        
        self.update()
    
    def paintEvent(self, event):
        """绘制日历形式的指示器"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)  # 抗锯齿
        
        # 计算大小
        width = self.width()
        height = self.height()
        
        # 计算每个日期格子的大小
        cell_width = width / self.columns
        cell_height = min(cell_width * 0.8, (height - 30) / 6)  # 留出空间绘制周几标签
        
        # 设置字体
        header_font = painter.font()
        header_font.setPointSize(10)
        header_font.setBold(True)
        
        day_font = painter.font()
        day_font.setPointSize(9)
        
        # 绘制周凨标签
        painter.setFont(header_font)
        painter.setPen(QPen(QColor("#34495e")))
        
        for i in range(self.columns):
            x = i * cell_width + cell_width / 2
            text_rect = QRectF(i * cell_width, 0, cell_width, 25)
            painter.drawText(text_rect, Qt.AlignCenter, self.weekday_labels[i])
        
        # 绘制日期
        painter.setFont(day_font)
        
        # 计算行数
        rows = (self.days_in_month + self.first_day_weekday - 1) // self.columns + 1
        
        for day in range(1, self.days_in_month + 1):
            # 计算每个日期在网格中的位置
            pos = day + self.first_day_weekday - 1  # 偏移量
            row = pos // self.columns
            col = pos % self.columns
            
            # 计算矩形位置
            x = col * cell_width + 2
            y = row * cell_height + 30  # 留出空间绘制周凨标签
            
            # 绘制日期圆圈和文本
            circle_rect = QRectF(x + 5, y + 2, cell_width - 10, cell_height - 4)
            text_rect = QRectF(x, y, cell_width, cell_height)
            
            # 根据状态着色
            if self.day_status[day] == 2:  # 完全完成
                # 填充圆圈
                painter.setPen(QPen(QColor(self.active_color), 1))
                painter.setBrush(QBrush(QColor(self.active_color)))
                painter.drawRoundedRect(circle_rect, 8, 8)  # 圆角矩形
                
                # 绘制日期文本(白色)
                painter.setPen(QPen(QColor("white")))
            elif self.day_status[day] == 1:  # 部分完成
                # 绘制外框
                painter.setPen(QPen(QColor(self.active_color), 1))
                painter.setBrush(Qt.NoBrush)
                painter.drawRoundedRect(circle_rect, 8, 8)  # 圆角矩形
                
                # 绘制半填充
                half_rect = QRectF(circle_rect.x(), circle_rect.y() + circle_rect.height()/2, 
                                     circle_rect.width(), circle_rect.height()/2)
                painter.setBrush(QBrush(QColor(self.partial_color)))
                painter.drawRoundedRect(half_rect, 0, 0)  # 半填充矩形
                
                # 绘制日期文本(深色)
                painter.setPen(QPen(QColor("#333333")))
            else:  # 未开始
                # 设置浅色圆圈
                painter.setPen(QPen(QColor(self.inactive_color), 1))
                painter.setBrush(Qt.NoBrush)
                painter.drawRoundedRect(circle_rect, 8, 8)  # 圆角矩形
                
                # 绘制日期文本(深色)
                painter.setPen(QPen(QColor("#333333")))
            
            # 绘制日期文本
            painter.drawText(text_rect, Qt.AlignCenter, str(day))
        
        painter.end()


class StyledStatsTable(QTableWidget):
    """样式化统计表格组件"""
    
    def __init__(self, columns=None, parent=None):
        super().__init__(parent)
        
        # 设置列
        if columns:
            self.setColumnCount(len(columns))
            self.setHorizontalHeaderLabels(columns)
        
        # 设置表格行为
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.setEditTriggers(QTableWidget.NoEditTriggers)
        self.setAlternatingRowColors(True)
        
        # 设置样式
        self.setStyleSheet("""
            QTableWidget {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                background-color: white;
                font-family: 'Microsoft YaHei';
                font-size: 14px;
            }
            QTableWidget::item {
                padding: 8px;
                min-height: 35px;
            }
            QHeaderView::section {
                background-color: #ecf0f1;
                padding: 10px;
                border: 1px solid #bdc3c7;
                font-weight: bold;
                font-size: 16px;
                min-height: 30px;
            }
        """)
    
    def add_data_row(self, data, exercise_colors=None, row_index=None):
        """添加一行数据到表格"""
        if row_index is None:
            row_index = self.rowCount()
            self.setRowCount(row_index + 1)
        
        # 添加数据
        for col, value in enumerate(data):
            item = QTableWidget.QTableWidgetItem(str(value))
            
            # 对第一列特殊处理
            if col == 0 and exercise_colors and value in exercise_colors:
                color = exercise_colors.get(value, "#3498db")
                item.setBackground(QColor(color).lighter(180))
            
            # 居中对齐
            if col > 0:
                item.setTextAlignment(Qt.AlignCenter)
                
            self.setItem(row_index, col, item)
