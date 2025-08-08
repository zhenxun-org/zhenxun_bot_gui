# -*- coding: utf-8 -*-
"""
动画按钮组件 - 可复用的动画按钮
"""

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, QRect, Qt, QTimer
from PySide6.QtWidgets import QPushButton


class AnimatedButton(QPushButton):
    """带动画效果的按钮组件"""

    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setMouseTracking(True)

        # 记录当前样式类型
        self.current_style = "default"

        # 默认样式
        self.setDefaultStyle()

    def setDefaultStyle(self):
        """设置默认样式"""
        self.current_style = "default"
        self.setStyleSheet("""
            QPushButton {
                background-color: #007acc;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 600;
                padding: 8px 16px;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #004085;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
        """)

    def setSecondaryStyle(self):
        """设置次要按钮样式（灰色）"""
        self.current_style = "secondary"
        self.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 600;
                padding: 8px 16px;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
            QPushButton:pressed {
                background-color: #495057;
            }
            QPushButton:disabled {
                background-color: #adb5bd;
            }
        """)

    def setSuccessStyle(self):
        """设置成功按钮样式（绿色）"""
        self.current_style = "success"
        self.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 600;
                padding: 8px 16px;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
        """)

    def setWarningStyle(self):
        """设置警告按钮样式（橙色）"""
        self.current_style = "warning"
        self.setStyleSheet("""
            QPushButton {
                background-color: #ffc107;
                color: #212529;
                border: none;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 600;
                padding: 8px 16px;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #e0a800;
            }
            QPushButton:pressed {
                background-color: #d39e00;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
        """)

    def setDangerStyle(self):
        """设置危险按钮样式（红色）"""
        self.current_style = "danger"
        self.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 600;
                padding: 8px 16px;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:pressed {
                background-color: #bd2130;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
        """)

    def mousePressEvent(self, event):
        """鼠标点击事件 - 添加点击动画"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.animate_click()
        super().mousePressEvent(event)

    def animate_click(self):
        """点击动画效果 - 只使用颜色变化"""
        # 根据当前样式类型设置正确的按下颜色
        if self.current_style == "secondary":
            pressed_color = "#495057"  # 灰色按钮的按下颜色
        elif self.current_style == "success":
            pressed_color = "#1e7e34"  # 绿色按钮的按下颜色
        elif self.current_style == "warning":
            pressed_color = "#d39e00"  # 橙色按钮的按下颜色
        elif self.current_style == "danger":
            pressed_color = "#bd2130"  # 红色按钮的按下颜色
        else:
            pressed_color = "#004085"  # 默认蓝色按钮的按下颜色

        # 立即改变颜色（按下效果）
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {pressed_color};
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 600;
                padding: 8px 16px;
                min-height: 20px;
            }}
        """)

        # 使用定时器延迟恢复颜色
        QTimer.singleShot(150, self.restore_click_color)

    def restore_click_color(self):
        """恢复点击颜色"""
        # 根据当前样式类型恢复正确的样式
        if self.current_style == "secondary":
            self.setSecondaryStyle()
        elif self.current_style == "success":
            self.setSuccessStyle()
        elif self.current_style == "warning":
            self.setWarningStyle()
        elif self.current_style == "danger":
            self.setDangerStyle()
        else:
            self.setDefaultStyle()


class AnimatedNavButton(AnimatedButton):
    """带动画效果的导航按钮"""

    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setNavStyle()

    def setNavStyle(self):
        """设置导航按钮样式"""
        self.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #6c757d;
                border: none;
                border-radius: 8px;
                font-size: 12px;
                font-weight: 400;
                padding: 8px 12px;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #f8f9fa;
                color: #495057;
            }
            QPushButton:pressed {
                background-color: #e9ecef;
                color: #212529;
            }
            QPushButton:disabled {
                background-color: transparent;
                color: #adb5bd;
            }
        """)

    def setActiveStyle(self):
        """设置激活状态的导航按钮样式"""
        self.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 12px;
                font-weight: 500;
                padding: 8px 12px;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #138496;
            }
            QPushButton:pressed {
                background-color: #117a8b;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
        """)
