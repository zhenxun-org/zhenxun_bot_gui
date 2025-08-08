# -*- coding: utf-8 -*-
"""
侧边栏组件 - 现代简约设计
"""

import re

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, QRect, Qt, Signal
from PySide6.QtGui import QBrush, QColor, QPainter, QPalette, QPen, QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QGraphicsDropShadowEffect, QLabel, QVBoxLayout, QWidget


class NavButton(QWidget):
    """现代导航按钮"""

    clicked = Signal(int)

    def __init__(self, icon_path: str, tooltip: str, index: int, parent=None):
        super().__init__(parent)
        self.index = index
        self.is_active = False
        self.tooltip_text = tooltip
        self.icon_path = icon_path

        self.setup_ui()
        # 按钮宽度为侧边栏宽度减去左右边距
        sidebar_width = 84  # 侧边栏宽度
        button_width = sidebar_width - 8  # 左右各4px边距
        self.setFixedSize(button_width, 66)
        self.setToolTip(tooltip)

    def setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)  # 增加按钮内容上下内边距
        layout.setSpacing(14)  # 增加图标和文本之间的上下间距

        # 图标标签
        self.icon_label = QLabel()
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setFixedSize(20, 20)  # 调小图标尺寸

        # 文字标签
        self.text_label = QLabel(self.tooltip_text)
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_label.setFixedHeight(14)  # 调小文字高度

        # 设置图标
        self.set_icon()

        # 垂直布局：图标在上，文字在下
        layout.addWidget(self.icon_label, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self.text_label, 0, Qt.AlignmentFlag.AlignHCenter)
        self.update_style(animated=False)

    def set_icon(self, color=None):
        """设置图标"""
        if self.icon_path.endswith((".svg", ".png", ".jpg", ".jpeg")):
            if self.icon_path.endswith(".svg") and color:
                # 对于SVG文件，动态修改颜色
                try:
                    with open(self.icon_path, "r", encoding="utf-8") as f:
                        svg_content = f.read()

                    # 移除原有的fill属性并添加新的颜色
                    svg_content = re.sub(r'fill="[^"]*"', "", svg_content)
                    svg_content = re.sub(r"<svg", f'<svg fill="{color}"', svg_content)

                    # 使用QSvgRenderer渲染修改后的SVG
                    renderer = QSvgRenderer()
                    renderer.load(svg_content.encode("utf-8"))

                    # 创建pixmap并渲染
                    pixmap = QPixmap(20, 20)
                    pixmap.fill(Qt.GlobalColor.transparent)
                    painter = QPainter(pixmap)
                    renderer.render(painter)
                    painter.end()

                    self.icon_label.setPixmap(pixmap)
                except Exception as e:
                    # 如果SVG处理失败，回退到普通方法
                    pixmap = QPixmap(self.icon_path)
                    if not pixmap.isNull():
                        pixmap = pixmap.scaled(
                            20,
                            20,
                            Qt.AspectRatioMode.KeepAspectRatio,
                            Qt.TransformationMode.SmoothTransformation,
                        )
                        self.icon_label.setPixmap(pixmap)
                    else:
                        self.icon_label.setText("🏠")
            else:
                # 普通图片处理
                pixmap = QPixmap(self.icon_path)
                if not pixmap.isNull():
                    pixmap = pixmap.scaled(
                        20,
                        20,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation,
                    )
                    self.icon_label.setPixmap(pixmap)
                else:
                    self.icon_label.setText("🏠")
        else:
            self.icon_label.setText(self.icon_path)

    def update_style(self, animated=True):
        """更新样式 - 重新设计的简单有效系统"""
        if self.is_active:
            # 选中状态：使用调色板设置背景色
            palette = self.palette()
            palette.setColor(QPalette.ColorRole.Window, QColor("#ffffff"))
            self.setPalette(palette)
            self.setAutoFillBackground(True)

            # 清除样式表，让调色板生效
            self.setStyleSheet("")

            # 轻微阴影
            shadow = QGraphicsDropShadowEffect(self)
            shadow.setBlurRadius(8)
            shadow.setColor(QColor(0, 0, 0, 15))
            shadow.setOffset(0, 2)
            self.setGraphicsEffect(shadow)

            # 图标和文字都使用青色
            self.icon_label.setStyleSheet("""
                QLabel {
                    background-color: transparent;
                    border: none;
                    color: #17a2b8;
                }
            """)
            self.text_label.setStyleSheet("""
                QLabel {
                    background-color: transparent;
                    border: none;
                    color: #17a2b8;
                    font-size: 12px;
                    font-weight: 500;
                }
            """)

            # 更新图标颜色为青色
            self.set_icon("#17a2b8")
        else:
            # 未选中状态：透明背景
            palette = self.palette()
            palette.setColor(QPalette.ColorRole.Window, QColor(0, 0, 0, 0))
            self.setPalette(palette)
            self.setAutoFillBackground(False)

            # 清除样式表
            self.setStyleSheet("")

            self.setGraphicsEffect(QGraphicsDropShadowEffect())

            # 图标和文字使用深灰色
            self.icon_label.setStyleSheet("""
                QLabel {
                    background-color: transparent;
                    border: none;
                    color: #6c757d;
                }
            """)
            self.text_label.setStyleSheet("""
                QLabel {
                    background-color: transparent;
                    border: none;
                    color: #6c757d;
                    font-size: 12px;
                    font-weight: 400;
                }
            """)

            # 更新图标颜色为深灰色
            self.set_icon("#6c757d")
        self.repaint()

    def paintEvent(self, event):
        """自定义绘制事件 - 添加左边线条和圆角效果"""
        super().paintEvent(event)

        if self.is_active:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            # 先绘制圆角背景 - 使用更深的背景色
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor("#f0f0f0")))  # 更深的灰色背景
            painter.drawRoundedRect(0, 4, self.width(), self.height() - 8, 12, 12)

            # 再绘制左边青色圆角竖条 - 使用主色调
            pen = QPen(QColor("#17a2b8"), 0)
            painter.setPen(pen)
            painter.setBrush(QBrush(QColor("#17a2b8")))
            bar_x = 2  # 调整左边条位置
            bar_y = 22
            bar_w = 4
            bar_h = self.height() - 44
            painter.drawRoundedRect(bar_x, bar_y, bar_w, bar_h, 3, 3)

    def set_active(self, active: bool):
        """设置激活状态"""
        if self.is_active == active:
            return
        self.is_active = active
        self.update_style()

    def mousePressEvent(self, event):
        """鼠标点击事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.index)
        super().mousePressEvent(event)


class Sidebar(QWidget):
    """现代侧边栏"""

    page_changed = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.nav_buttons = []
        self.setup_ui()

    def setup_ui(self):
        """设置UI"""
        self.setFixedWidth(84)  # 侧边栏宽度
        self.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                border-right: 1px solid #e9ecef;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 16, 0, 16)  # 取消左右边距
        layout.setSpacing(4)  # 增加按钮之间的上下间距

        # 导航按钮配置
        nav_items = [
            ("assets/icons/home.svg", "主页", 0),
            ("assets/icons/setting.svg", "设置", 1),
            ("assets/icons/environment.svg", "环境", 2),
        ]

        for icon, tooltip, index in nav_items:
            btn = NavButton(icon, tooltip, index)
            btn.clicked.connect(self.on_nav_clicked)
            self.nav_buttons.append(btn)
            layout.addWidget(btn, 0, Qt.AlignmentFlag.AlignHCenter)  # 居中对齐

        # 默认激活第一个
        if self.nav_buttons:
            self.nav_buttons[0].set_active(True)

        layout.addStretch()

    def on_nav_clicked(self, index: int):
        """导航点击处理"""
        print(f"侧边栏点击: index={index}")

        if index == -1:
            print(f"无效的索引，跳过处理")
            return

        # 如果点击的是当前激活的按钮，不处理
        for i, btn in enumerate(self.nav_buttons):
            if i == index and btn.is_active:
                print(f"点击当前激活按钮，跳过处理")
                return

        print(f"开始处理侧边栏点击: index={index}")

        # 更新按钮状态
        for i, btn in enumerate(self.nav_buttons):
            btn.set_active(i == index)

        # 发送信号
        self.page_changed.emit(index)

    def set_active_page(self, index: int):
        """设置活跃页面"""
        for i, btn in enumerate(self.nav_buttons):
            btn.set_active(i == index)
