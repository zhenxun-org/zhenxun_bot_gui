# -*- coding: utf-8 -*-
"""
通用全局弹窗组件 - 符合当前主页主题审美设计
支持多按钮配置
"""

from PySide6.QtCore import QEasingCurve, QPoint, QPropertyAnimation, Qt, Signal
from PySide6.QtGui import QFont, QIcon, QMouseEvent, QPixmap
from PySide6.QtWidgets import (
    QDialog,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)


class GlobalDialog(QDialog):
    """通用全局弹窗组件 - 支持多按钮"""
    
    # 定义信号
    confirmed = Signal()  # 确认信号
    cancelled = Signal()  # 取消信号
    button_clicked = Signal(str)  # 按钮点击信号，传递按钮文本
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.buttons = []  # 存储按钮列表
        self.dragging = False  # 拖拽状态
        self.drag_position = QPoint()  # 拖拽位置
        self.setup_ui()
        self.setup_animations()
        
    def setup_ui(self):
        """设置UI"""
        # 设置无边框和背景透明
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # 设置固定大小
        self.setFixedSize(440, 320)
        
        # 主布局
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # 创建弹窗内容容器
        self.content_widget = QWidget()
        self.content_widget.setObjectName("dialog_content")
        self.content_widget.setStyleSheet("""
            #dialog_content {
                background-color: white;
                border-radius: 16px;
                border: 1px solid #e1e5e9;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
            }
        """)
        
        content_layout = QVBoxLayout(self.content_widget)
        content_layout.setContentsMargins(32, 32, 32, 32)
        content_layout.setSpacing(24)
        
        # 标题区域
        self.create_title_area(content_layout)
        
        # 内容区域
        self.create_content_area(content_layout)
        
        # 按钮区域
        self.create_button_area(content_layout)
        
        self.main_layout.addWidget(self.content_widget)
        
    def create_title_area(self, layout):
        """创建标题区域"""
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(15)
        
        # 图标
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(28, 28)
        self.icon_label.setStyleSheet("""
            background: transparent;
            border-radius: 6px;
        """)
        title_layout.addWidget(self.icon_label)
        
        # 标题
        self.title_label = QLabel()
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setWeight(QFont.Weight.Bold)
        self.title_label.setFont(title_font)
        self.title_label.setStyleSheet("""
            QLabel {
                color: #1a202c;
                background: transparent;
                font-family: "Segoe UI", "Microsoft YaHei", sans-serif;
            }
        """)
        title_layout.addWidget(self.title_label)
        
        # 弹性空间
        title_layout.addItem(
            QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        )
        
        # 关闭按钮
        self.close_button = QPushButton("×")
        self.close_button.setFixedSize(28, 28)
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #6c757d;
                border: none;
                font-size: 20px;
                font-weight: bold;
                border-radius: 14px;
                font-family: "Segoe UI", "Microsoft YaHei", sans-serif;
            }
            QPushButton:hover {
                background-color: #f1f3f4;
                color: #495057;
            }
            QPushButton:pressed {
                background-color: #e8eaed;
                color: #212529;
            }
        """)
        self.close_button.clicked.connect(self.close_action)
        title_layout.addWidget(self.close_button)
        
        layout.addLayout(title_layout)
        
    def create_content_area(self, layout):
        """创建内容区域"""
        self.content_label = QLabel()
        self.content_label.setWordWrap(True)
        self.content_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.content_label.setStyleSheet("""
            QLabel {
                color: #4a5568;
                font-size: 15px;
                line-height: 1.6;
                background: transparent;
                padding: 0px;
                font-family: "Segoe UI", "Microsoft YaHei", sans-serif;
            }
        """)
        layout.addWidget(self.content_label)
        
        # 添加弹性空间
        layout.addItem(
            QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        )
        
    def create_button_area(self, layout):
        """创建按钮区域"""
        self.button_layout = QHBoxLayout()
        self.button_layout.setContentsMargins(0, 0, 0, 0)
        self.button_layout.setSpacing(12)
        
        # 添加弹性空间
        self.button_layout.addItem(
            QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        )
        
        layout.addLayout(self.button_layout)
        
    def add_button(self, text, button_type="default", callback=None):
        """添加按钮
        
        Args:
            text (str): 按钮文本
            button_type (str): 按钮类型 ("default", "primary", "success", "warning", "danger", "info")
            callback (callable): 按钮点击回调函数
        """
        button = QPushButton(text)
        button.setFixedSize(88, 40)
        
        # 设置按钮样式
        self._set_button_style(button, button_type)
        
        # 连接信号
        if callback:
            button.clicked.connect(lambda: self._button_clicked(text, callback))
        else:
            button.clicked.connect(lambda: self._button_clicked(text))
        
        # 添加到布局
        self.button_layout.addWidget(button)
        self.buttons.append(button)
        
        return button
    
    def _set_button_style(self, button, button_type):
        """设置按钮样式"""
        base_style = """
            QPushButton {
                border-radius: 8px;
                font-size: 14px;
                font-weight: 500;
                font-family: "Segoe UI", "Microsoft YaHei", sans-serif;
            }
        """
        
        if button_type == "primary":
            style = base_style + """
                QPushButton {
                    background-color: #007acc;
                    color: white;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #0056b3;
                }
                QPushButton:pressed {
                    background-color: #004085;
                }
            """
        elif button_type == "success":
            style = base_style + """
                QPushButton {
                    background-color: #28a745;
                    color: white;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #218838;
                }
                QPushButton:pressed {
                    background-color: #1e7e34;
                }
            """
        elif button_type == "warning":
            style = base_style + """
                QPushButton {
                    background-color: #ffc107;
                    color: #212529;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #e0a800;
                }
                QPushButton:pressed {
                    background-color: #d39e00;
                }
            """
        elif button_type == "danger":
            style = base_style + """
                QPushButton {
                    background-color: #dc3545;
                    color: white;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #c82333;
                }
                QPushButton:pressed {
                    background-color: #bd2130;
                }
            """
        elif button_type == "info":
            style = base_style + """
                QPushButton {
                    background-color: #17a2b8;
                    color: white;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #138496;
                }
                QPushButton:pressed {
                    background-color: #117a8b;
                }
            """
        else:  # default
            style = base_style + """
                QPushButton {
                    background-color: #f8f9fa;
                    color: #495057;
                    border: 1px solid #e2e8f0;
                }
                QPushButton:hover {
                    background-color: #e9ecef;
                    border-color: #cbd5e0;
                }
                QPushButton:pressed {
                    background-color: #dee2e6;
                }
            """
        
        button.setStyleSheet(style)
    
    def _button_clicked(self, button_text, callback=None):
        """按钮点击处理"""
        # 存储被点击的按钮文本
        if hasattr(self, 'clicked_button_text'):
            self.clicked_button_text = button_text
        
        self.button_clicked.emit(button_text)
        if callback:
            callback()
        self.fade_out_animation.start()
    
    def clear_buttons(self):
        """清除所有按钮"""
        for button in self.buttons:
            button.deleteLater()
        self.buttons.clear()
        
    def setup_animations(self):
        """设置动画效果"""
        # 淡入动画
        self.fade_in_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.fade_in_effect)
        self.fade_in_effect.setOpacity(0.0)
        
        self.fade_in_animation = QPropertyAnimation(self.fade_in_effect, b"opacity")
        self.fade_in_animation.setDuration(250)
        self.fade_in_animation.setStartValue(0.0)
        self.fade_in_animation.setEndValue(1.0)
        self.fade_in_animation.setEasingCurve(QEasingCurve.Type.OutBack)
        
        # 淡出动画
        self.fade_out_animation = QPropertyAnimation(self.fade_in_effect, b"opacity")
        self.fade_out_animation.setDuration(200)
        self.fade_out_animation.setStartValue(1.0)
        self.fade_out_animation.setEndValue(0.0)
        self.fade_out_animation.setEasingCurve(QEasingCurve.Type.InCubic)
        self.fade_out_animation.finished.connect(self.close)
        
    def showEvent(self, event):
        """显示事件 - 启动淡入动画"""
        super().showEvent(event)
        self.fade_in_animation.start()
        
    def close_action(self):
        """关闭操作"""
        self.cancelled.emit()
        self.fade_out_animation.start()
    
    def mousePressEvent(self, event: QMouseEvent):
        """鼠标按下事件 - 开始拖拽"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
        else:
            super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """鼠标移动事件 - 拖拽窗口"""
        if event.buttons() & Qt.MouseButton.LeftButton and self.dragging:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
        else:
            super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        """鼠标释放事件 - 结束拖拽"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            event.accept()
        else:
            super().mouseReleaseEvent(event)
        
    def set_dialog_content(self, title, content, icon_path=None):
        """设置弹窗内容"""
        self.title_label.setText(title)
        self.content_label.setText(content)
        
        if icon_path:
            pixmap = QPixmap(icon_path)
            if not pixmap.isNull():
                self.icon_label.setPixmap(
                    pixmap.scaled(
                        28, 28,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                )
        else:
            # 默认图标
            self.icon_label.setPixmap(QPixmap("assets/icons/logo.png").scaled(
                28, 28,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            ))


class InfoDialog(GlobalDialog):
    """信息提示弹窗"""
    
    def __init__(self, title="提示", content="", parent=None):
        super().__init__(parent)
        self.set_dialog_content(
            title=title,
            content=content,
            icon_path="assets/icons/logo.png"
        )
        # 添加确定按钮
        self.add_button("确定", "primary")


class ConfirmDialog(GlobalDialog):
    """确认弹窗"""
    
    def __init__(self, title="确认", content="", parent=None):
        super().__init__(parent)
        self.set_dialog_content(
            title=title,
            content=content,
            icon_path="assets/icons/logo.png"
        )
        # 添加取消和确认按钮
        self.add_button("取消", "default")
        self.add_button("确认", "primary")


class WarningDialog(GlobalDialog):
    """警告弹窗"""
    
    def __init__(self, title="警告", content="", parent=None):
        super().__init__(parent)
        self.set_dialog_content(
            title=title,
            content=content,
            icon_path="assets/icons/logo.png"
        )
        # 添加取消和确定按钮
        self.add_button("取消", "default")
        self.add_button("确定", "warning")


class ErrorDialog(GlobalDialog):
    """错误弹窗"""
    
    def __init__(self, title="错误", content="", parent=None):
        super().__init__(parent)
        self.set_dialog_content(
            title=title,
            content=content,
            icon_path="assets/icons/logo.png"
        )
        # 添加确定按钮
        self.add_button("确定", "danger")


class SuccessDialog(GlobalDialog):
    """成功弹窗"""
    
    def __init__(self, title="成功", content="", parent=None):
        super().__init__(parent)
        self.set_dialog_content(
            title=title,
            content=content,
            icon_path="assets/icons/logo.png"
        )
        # 添加确定按钮
        self.add_button("确定", "success")


class MultiButtonDialog(GlobalDialog):
    """多按钮弹窗"""
    
    def __init__(self, title="", content="", buttons=None, parent=None):
        """
        初始化多按钮弹窗
        
        Args:
            title (str): 标题
            content (str): 内容
            buttons (list): 按钮配置列表，格式为 [{"text": "按钮文本", "type": "按钮类型", "callback": 回调函数}, ...]
            parent: 父窗口
        """
        super().__init__(parent)
        self.clicked_button_text = None  # 存储被点击的按钮文本
        self.set_dialog_content(
            title=title,
            content=content,
            icon_path="assets/icons/logo.png"
        )
        
        # 添加按钮
        if buttons:
            for button_config in buttons:
                text = button_config.get("text", "按钮")
                button_type = button_config.get("type", "default")
                callback = button_config.get("callback", None)
                self.add_button(text, button_type, callback)


class ProgressDialog(GlobalDialog):
    """进度条弹窗"""
    
    def __init__(self, title="", content="", parent=None):
        super().__init__(parent)
        self.set_dialog_content(
            title=title,
            content=content,
            icon_path="assets/icons/logo.png"
        )
        
        # 创建进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #e1e5e9;
                border-radius: 6px;
                text-align: center;
                font-size: 12px;
                background-color: #f8f9fa;
                height: 20px;
                margin: 10px 0px;
            }
            QProgressBar::chunk {
                background-color: #007acc;
                border-radius: 5px;
            }
        """)
        
        # 清除原有按钮
        self.clear_buttons()
        
        # 添加进度条到内容区域
        self.add_progress_bar_to_content()
        
        # 重新设置按钮布局为垂直布局
        self.setup_vertical_button_layout()
        
        # 添加取消按钮
        self.add_progress_button("取消", "default")
    
    def add_progress_bar_to_content(self):
        """将进度条添加到内容区域"""
        try:
            # 尝试将进度条添加到内容布局
            if hasattr(self, 'content_widget') and self.content_widget.layout():
                self.content_widget.layout().addWidget(self.progress_bar)
        except:
            # 如果失败，直接添加到主布局
            self.main_layout.addWidget(self.progress_bar)
    
    def setup_vertical_button_layout(self):
        """设置垂直按钮布局"""
        # 清除原有的水平按钮布局
        if hasattr(self, 'button_layout'):
            # 移除所有按钮
            while self.button_layout.count():
                item = self.button_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
        
        # 创建新的垂直按钮布局
        self.button_layout = QVBoxLayout()
        self.button_layout.setContentsMargins(0, 0, 0, 0)
        self.button_layout.setSpacing(10)
        
        # 尝试将新的按钮布局添加到内容布局中
        try:
            if hasattr(self, 'content_widget') and self.content_widget.layout():
                self.content_widget.layout().addLayout(self.button_layout)
            else:
                # 如果失败，添加到主布局
                self.main_layout.addLayout(self.button_layout)
        except:
            # 如果失败，添加到主布局
            self.main_layout.addLayout(self.button_layout)
    
    def add_progress_button(self, text, button_type="default", callback=None):
        """为进度条弹窗添加按钮 - 按钮占满宽度"""
        button = QPushButton(text)
        button.setFixedHeight(40)  # 只固定高度，宽度自适应
        button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        # 设置按钮样式
        self._set_button_style(button, button_type)
        
        # 连接信号
        if callback:
            button.clicked.connect(lambda: self._button_clicked(text, callback))
        else:
            button.clicked.connect(lambda: self._button_clicked(text))
        
        # 添加到布局
        self.button_layout.addWidget(button)
        self.buttons.append(button)
        
        return button
    
    def set_progress(self, value):
        """设置进度值"""
        self.progress_bar.setValue(value)
    
    def set_status(self, status):
        """设置状态文本"""
        self.content_label.setText(status)


# 便捷函数
def show_info_dialog(title, content, parent=None):
    """显示信息弹窗"""
    dialog = InfoDialog(title, content, parent)
    dialog.exec()
    return dialog.result() == QDialog.DialogCode.Accepted


def show_confirm_dialog(title, content, parent=None):
    """显示确认弹窗"""
    dialog = ConfirmDialog(title, content, parent)
    dialog.exec()
    return dialog.result() == QDialog.DialogCode.Accepted


def show_warning_dialog(title, content, parent=None):
    """显示警告弹窗"""
    dialog = WarningDialog(title, content, parent)
    dialog.exec()
    return dialog.result() == QDialog.DialogCode.Accepted


def show_error_dialog(title, content, parent=None):
    """显示错误弹窗"""
    dialog = ErrorDialog(title, content, parent)
    dialog.exec()
    return dialog.result() == QDialog.DialogCode.Accepted


def show_success_dialog(title, content, parent=None):
    """显示成功弹窗"""
    dialog = SuccessDialog(title, content, parent)
    dialog.exec()
    return dialog.result() == QDialog.DialogCode.Accepted


def show_multi_button_dialog(title, content, buttons, parent=None):
    """显示多按钮弹窗"""
    dialog = MultiButtonDialog(title, content, buttons, parent)
    dialog.exec()
    return dialog.clicked_button_text if hasattr(dialog, 'clicked_button_text') else None


def show_progress_dialog(title, content, parent=None):
    """显示进度条弹窗"""
    dialog = ProgressDialog(title, content, parent)
    dialog.exec()
    return dialog  # 返回对话框实例而不是布尔值 