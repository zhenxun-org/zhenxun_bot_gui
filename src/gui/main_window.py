# -*- coding: utf-8 -*-
"""
主窗口类
"""

from PySide6.QtCore import QEasingCurve, QPoint, QPropertyAnimation, QSize, Qt, Signal
from PySide6.QtGui import QFont, QIcon, QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QSplitter,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from ..utils.config import ConfigManager
from .pages.environment_page import EnvironmentPage
from .pages.home_page import HomePage
from .pages.settings_page import SettingsPage
from .sidebar import Sidebar


class AnimatedStackedWidget(QStackedWidget):
    """带多种动画效果的堆叠窗口部件"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.animation = None
        self.opacity_effect = None
        self.current_animation_type = "fade"  # fade, slide, scale
        self.is_animating = False  # 添加动画状态锁定

    def fade_to_index(self, index):
        """淡入淡出切换页面"""
        if index == self.currentIndex():
            print(f"已经是目标页面，跳过切换: index={index}")
            return

        print(f"开始淡入淡出动画: index={index}")
        self.is_animating = True

        # 先切换页面
        self.setCurrentIndex(index)

        # 确保目标页面可见
        target_widget = self.currentWidget()
        if target_widget:
            target_widget.show()
            target_widget.raise_()

        # 然后添加淡入动画
        effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(effect)

        fade_in = QPropertyAnimation(effect, b"opacity")
        fade_in.setDuration(300)
        fade_in.setStartValue(0.0)
        fade_in.setEndValue(1.0)
        fade_in.setEasingCurve(QEasingCurve.Type.OutCubic)

        def on_fade_in_finished():
            print(f"淡入淡出动画完成: index={index}")
            # 创建一个空的QGraphicsOpacityEffect来替代None
            empty_effect = QGraphicsOpacityEffect()
            self.setGraphicsEffect(empty_effect)
            self.is_animating = False
            print(f"动画状态已重置: is_animating={self.is_animating}")
            # 确保当前页面可见
            current_widget = self.currentWidget()
            if current_widget:
                current_widget.show()
                current_widget.raise_()

        fade_in.finished.connect(on_fade_in_finished)
        fade_in.start()

    def slide_to_index(self, index, direction="right"):
        """滑动切换页面 - 简化为直接切换"""
        if index == self.currentIndex():
            print(f"已经是目标页面，跳过切换: index={index}")
            return

        print(f"开始滑动动画: index={index}, direction={direction}")
        self.is_animating = True

        # 直接切换页面，不使用复杂的滑动动画
        self.setCurrentIndex(index)

        # 确保目标页面可见
        target_widget = self.currentWidget()
        if target_widget:
            target_widget.show()
            target_widget.raise_()

        # 使用简单的淡入效果代替滑动
        effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(effect)

        fade_in = QPropertyAnimation(effect, b"opacity")
        fade_in.setDuration(300)
        fade_in.setStartValue(0.0)
        fade_in.setEndValue(1.0)
        fade_in.setEasingCurve(QEasingCurve.Type.OutCubic)

        def on_slide_finished():
            print(f"滑动动画完成: index={index}")
            # 创建一个空的QGraphicsOpacityEffect来替代None
            empty_effect = QGraphicsOpacityEffect()
            self.setGraphicsEffect(empty_effect)
            self.is_animating = False
            print(f"动画状态已重置: is_animating={self.is_animating}")
            # 确保当前页面可见
            current_widget = self.currentWidget()
            if current_widget:
                current_widget.show()
                current_widget.raise_()

        fade_in.finished.connect(on_slide_finished)
        fade_in.start()

    def scale_to_index(self, index):
        """缩放切换页面"""
        if index == self.currentIndex():
            print(f"已经是目标页面，跳过切换: index={index}")
            return

        print(f"开始缩放动画: index={index}")
        self.is_animating = True

        # 先切换页面
        self.setCurrentIndex(index)
        target_widget = self.currentWidget()

        if not target_widget:
            print(f"缩放动画失败: 目标页面组件无效")
            self.is_animating = False
            return

        # 确保目标页面可见
        target_widget.show()
        target_widget.raise_()

        # 创建缩放效果
        effect = QGraphicsOpacityEffect(target_widget)
        target_widget.setGraphicsEffect(effect)

        # 缩放动画
        scale_anim = QPropertyAnimation(effect, b"opacity")
        scale_anim.setDuration(350)
        scale_anim.setStartValue(0.0)
        scale_anim.setEndValue(1.0)
        scale_anim.setEasingCurve(QEasingCurve.Type.OutBack)

        def on_scale_finished():
            print(f"缩放动画完成: index={index}")
            # 修复setGraphicsEffect的None参数问题
            target_widget.setGraphicsEffect(QGraphicsOpacityEffect())
            self.is_animating = False
            print(f"动画状态已重置: is_animating={self.is_animating}")
            # 确保当前页面可见
            current_widget = self.currentWidget()
            if current_widget:
                current_widget.show()
                current_widget.raise_()

        scale_anim.finished.connect(on_scale_finished)
        scale_anim.start()

    def slide_in_direction(self, index, direction):
        """根据方向滑动切换页面"""
        self.slide_to_index(index, direction)

    def switch_with_animation(self, index, animation_type="fade"):
        """使用指定动画类型切换页面"""
        print(
            f"尝试切换动画: index={index}, type={animation_type}, is_animating={self.is_animating}"
        )

        # 简化逻辑：直接执行动画，不检查状态
        if animation_type == "fade":
            self.fade_to_index(index)
        elif animation_type == "slide":
            self.slide_to_index(index, "right")
        elif animation_type == "scale":
            self.scale_to_index(index)
        else:
            # 默认使用淡入淡出
            self.fade_to_index(index)


class CustomTitleBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(50)  # 增加标题栏高度到80px
        self.setStyleSheet("""
            background: #fafbfc;
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 0, 14, 0)
        layout.setSpacing(10)

        # 左侧 logo
        avatar = QLabel()
        avatar.setFixedSize(28, 28)
        pix = QPixmap("assets/icons/logo.png")
        if not pix.isNull():
            avatar.setPixmap(
                pix.scaled(
                    28,
                    28,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
        avatar.setStyleSheet("background: transparent;")
        layout.addWidget(avatar)

        # 应用名
        title = QLabel("真寻Bot GUI")
        title.setStyleSheet("""
            font-size: 14px;
            font-weight: 500;
            color: #2c3e50;
            background: transparent;
            margin-left: 10px;
        """)
        layout.addWidget(title)

        # 弹性空间
        layout.addItem(
            QSpacerItem(
                40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
            )
        )

        # 按钮通用样式 - 模拟系统原生标题栏按钮
        btn_style = """
            QPushButton {
                border: none;
                background: transparent;
                color: #5a6c7d;
                font-size: 16px;
                font-weight: 400;
                font-family: "Segoe UI", "Microsoft YaHei";
                min-width: 46px;
                min-height: 32px;
                margin: 0px;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: rgba(0, 0, 0, 0.1);
                color: #2c3e50;
            }
            QPushButton:hover QIcon {
                color: #2c3e50;
            }
            QPushButton:pressed {
                background-color: rgba(0, 0, 0, 0.2);
            }
            QPushButton:pressed QIcon {
                color: #2c3e50;
            }
        """

        # 最小化按钮
        btn_min = QPushButton()
        btn_min.setFixedSize(46, 32)
        btn_min.setIcon(QIcon("assets/icons/minimize.svg"))
        btn_min.setStyleSheet(btn_style)
        btn_min.setFocusPolicy(Qt.FocusPolicy.NoFocus)  # 禁用焦点，避免焦点框
        if parent and hasattr(parent, "showMinimized"):
            btn_min.clicked.connect(parent.showMinimized)
        layout.addWidget(btn_min)

        # 最大化/还原按钮
        btn_max = QPushButton()
        btn_max.setFixedSize(46, 32)
        btn_max.setIcon(QIcon("assets/icons/maximize.svg"))
        btn_max.setStyleSheet(btn_style)
        btn_max.setFocusPolicy(Qt.FocusPolicy.NoFocus)  # 禁用焦点，避免焦点框
        if (
            parent
            and hasattr(parent, "showNormal")
            and hasattr(parent, "isMaximized")
            and hasattr(parent, "showMaximized")
        ):
            # 创建切换图标的函数
            def toggle_maximize():
                if parent.isMaximized():
                    parent.showNormal()
                    btn_max.setIcon(QIcon("assets/icons/maximize.svg"))
                else:
                    parent.showMaximized()
                    btn_max.setIcon(QIcon("assets/icons/restore.svg"))

            btn_max.clicked.connect(toggle_maximize)

            # 初始化图标状态
            if parent.isMaximized():
                btn_max.setIcon(QIcon("assets/icons/restore.svg"))
            else:
                btn_max.setIcon(QIcon("assets/icons/maximize.svg"))
        layout.addWidget(btn_max)

        # 创建自定义关闭按钮类
        class CloseButton(QPushButton):
            def __init__(self, parent=None):
                super().__init__(parent)
                self.normal_icon = QIcon("assets/icons/close.svg")
                self.white_icon = QIcon("assets/icons/close_white.svg")
                self.setIcon(self.normal_icon)

                # 设置样式
                self.setStyleSheet("""
                    QPushButton {
                        border: none;
                        background: transparent;
                        color: #5a6c7d;
                        font-size: 16px;
                        font-weight: 400;
                        font-family: "Segoe UI", "Microsoft YaHei";
                        min-width: 46px;
                        min-height: 32px;
                        margin: 0px;
                        padding: 0px;
                        outline: none;
                    }
                    QPushButton:hover {
                        background-color: #e81123;
                        color: white;
                        border: none;
                        outline: none;
                    }
                    QPushButton:pressed {
                        background-color: #c50e1f;
                        color: white;
                        border: none;
                        outline: none;
                    }
                    QPushButton:focus {
                        border: none;
                        outline: none;
                    }
                """)

            def enterEvent(self, event):
                self.setIcon(self.white_icon)
                super().enterEvent(event)

            def leaveEvent(self, event):
                self.setIcon(self.normal_icon)
                super().leaveEvent(event)

        # 使用自定义关闭按钮
        btn_close = CloseButton()
        btn_close.setFixedSize(46, 32)
        btn_close.setFocusPolicy(Qt.FocusPolicy.NoFocus)  # 禁用焦点，避免焦点框

        if parent and hasattr(parent, "close"):
            btn_close.clicked.connect(parent.close)
        layout.addWidget(btn_close)

        self._drag_pos = None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            p = self.window()
            self._drag_pos = (
                event.globalPosition().toPoint() - p.frameGeometry().topLeft()
            )
            event.accept()

    def mouseMoveEvent(self, event):
        if self._drag_pos and event.buttons() == Qt.MouseButton.LeftButton:
            p = self.window()
            p.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None


class MainWindow(QMainWindow):
    """主窗口类"""

    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager()
        self.current_page_index = 0  # 添加当前页面索引跟踪
        self._anim_mask = None
        self._fade_anim = None

        # 强制设置初始窗口大小
        self.resize(1200, 800)
        print(f"__init__: 强制设置初始大小 1200x800")

        self.setup_ui()
        self.setup_connections()
        self.restore_geometry()

        # 确保窗口大小正确
        if self.width() > 1920 or self.height() > 1080:  # 如果窗口过大
            self.resize(1200, 800)
            # 居中显示
            screen_geometry = self.screen().geometry()
            x = (screen_geometry.width() - 1200) // 2
            y = (screen_geometry.height() - 800) // 2
            self.move(x, y)
            print(f"__init__: 检测到窗口过大，重置为 1200x800")

    def setup_ui(self):
        """设置UI"""
        self.setWindowTitle("真寻Bot GUI - 图形化管理界面")
        self.setMinimumSize(1000, 700)

        # 设置应用程序图标
        try:
            icon = QIcon("assets/icons/logo.png")
            self.setWindowIcon(icon)
        except Exception as e:
            print(f"设置应用程序图标失败: {e}")

        # 设置无边框和背景透明，实现圆角窗口
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # 中央widget
        central_widget = QWidget()
        central_widget.setObjectName("centralwidget")
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 给central_widget加圆角和背景色
        central_widget.setStyleSheet("""
            #centralwidget {
                background: #fafbfc;
                border-radius: 12px;
                border: 1px solid #e1e5e9;
            }
        """)

        # 自定义标题栏（高度更高）
        self.title_bar = CustomTitleBar(self)
        main_layout.addWidget(self.title_bar)

        # 左侧边栏
        self.sidebar = Sidebar()
        self.sidebar.setFixedWidth(84)  # 同步侧边栏宽度

        # 右侧内容区域 - 使用带动画的堆叠窗口
        self.content_area = AnimatedStackedWidget()
        self.content_area.setStyleSheet("""
            QStackedWidget {
                background-color: #f8f9fa;
                border-radius: 12px;
                border: 1px solid #e1e5e9;
                border-bottom-left-radius: 0;
            }
        """)
        self.create_pages()

        # 创建分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self.sidebar)
        splitter.addWidget(self.content_area)
        splitter.setHandleWidth(0)
        splitter.setStretchFactor(0, 0)  # 侧边栏不拉伸
        splitter.setStretchFactor(1, 1)  # 内容区自动填充
        # 设置初始大小分配，确保没有间距
        splitter.setSizes([84, 1000])  # 侧边栏84px，内容区占剩余空间
        main_layout.addWidget(splitter)

        # 设置窗口样式（整体圆角）
        self.setStyleSheet("""
            QMainWindow {
                background-color: #fafbfc;
                border-radius: 12px;
            }
            QWidget#centralwidget {
                border-radius: 12px;
            }
            QStackedWidget {
                background-color: #f8f9fa;
                border-radius: 12px;
            }
        """)

    def create_pages(self):
        """创建页面"""
        # 主页
        self.home_page = HomePage()
        self.content_area.addWidget(self.home_page)

        # 设置页面
        self.settings_page = SettingsPage()
        self.content_area.addWidget(self.settings_page)

        # 环境检测页面
        self.environment_page = EnvironmentPage()
        self.content_area.addWidget(self.environment_page)

    def setup_connections(self):
        """设置信号连接"""
        # 连接侧边栏的页面切换信号
        self.sidebar.page_changed.connect(self.change_page)

    def change_page(self, index: int):
        """切换页面 - 使用遮罩淡出动画，保证内容正常显示"""
        print(f"=== 页面切换请求 ===")
        print(f"目标索引: {index}")
        print(f"当前页面索引: {self.current_page_index}")
        print(f"内容区域页面数量: {self.content_area.count()}")

        if index == self.current_page_index:
            print(f"已经是当前页面，跳过切换")
            return

        if 0 <= index < self.content_area.count():
            print(f"索引有效，开始切换页面")

            # 1. 创建遮罩
            if self._anim_mask is not None:
                self._anim_mask.deleteLater()
                self._anim_mask = None

            # 截图当前内容
            pixmap = self.content_area.grab()
            self._anim_mask = QLabel(self.content_area)  # 遮罩加到内容区
            self._anim_mask.setPixmap(pixmap)
            self._anim_mask.setGeometry(
                self.content_area.rect()
            )  # 用rect而不是geometry
            self._anim_mask.setAttribute(
                Qt.WidgetAttribute.WA_TransparentForMouseEvents
            )
            self._anim_mask.show()
            self._anim_mask.raise_()

            # 2. 切换到目标页面
            self.content_area.setCurrentIndex(index)
            target_widget = self.content_area.currentWidget()
            if target_widget:
                target_widget.show()
                target_widget.raise_()
                print(f"目标页面已显示: {type(target_widget).__name__}")

            # 3. 遮罩做淡出动画
            effect = QGraphicsOpacityEffect(self._anim_mask)
            self._anim_mask.setGraphicsEffect(effect)
            self._fade_anim = QPropertyAnimation(effect, b"opacity")
            self._fade_anim.setDuration(300)
            self._fade_anim.setStartValue(1.0)
            self._fade_anim.setEndValue(0.0)
            self._fade_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

            def on_anim_finished():
                if self._anim_mask is not None:
                    self._anim_mask.deleteLater()
                    self._anim_mask = None
                self._fade_anim = None
                print("遮罩动画完成，已移除遮罩")

            self._fade_anim.finished.connect(on_anim_finished)
            self._fade_anim.start()

            # 更新当前页面索引
            self.current_page_index = index
            print(f"当前页面索引已更新为: {self.current_page_index}")

            # 更新侧边栏状态
            self.sidebar.set_active_page(index)
            print(f"侧边栏状态已更新")

            # 更新窗口标题
            page_names = ["主页", "设置", "检测"]
            if 0 <= index < len(page_names):
                new_title = f"真寻Bot GUI - {page_names[index]}"
                self.setWindowTitle(new_title)
                print(f"窗口标题已更新为: {new_title}")
        else:
            print(f"无效的页面索引: {index}")
            print(f"有效索引范围: 0-{self.content_area.count() - 1}")

    def restore_geometry(self):
        """恢复窗口几何信息"""
        geometry = self.config_manager.get_window_geometry()
        size = geometry["size"]
        position = geometry["position"]

        print(f"restore_geometry: 从配置读取大小 {size}, 位置 {position}")

        # 检查是否是首次运行或窗口大小异常（全屏）
        screen_geometry = self.screen().geometry()
        is_fullscreen_size = (
            size[0] >= screen_geometry.width() and size[1] >= screen_geometry.height()
        )

        print(
            f"restore_geometry: 屏幕大小 {screen_geometry.width()}x{screen_geometry.height()}"
        )
        print(f"restore_geometry: 是否全屏大小 {is_fullscreen_size}")

        if is_fullscreen_size:
            # 如果是全屏大小，使用默认的正常大小
            self.resize(1200, 800)
            # 居中显示
            x = (screen_geometry.width() - 1200) // 2
            y = (screen_geometry.height() - 800) // 2
            self.move(x, y)
            print(f"restore_geometry: 重置为正常大小 1200x800, 位置 ({x}, {y})")
        else:
            # 使用保存的大小和位置
            self.resize(size[0], size[1])
            self.move(position[0], position[1])
            print(
                f"restore_geometry: 使用保存的大小 {size[0]}x{size[1]}, 位置 ({position[0]}, {position[1]})"
            )

    def closeEvent(self, event):
        """窗口关闭事件"""
        # 检查窗口是否处于最大化状态
        if not self.isMaximized():
            # 只有在非最大化状态下才保存窗口几何信息
            size = (self.width(), self.height())
            position = (self.x(), self.y())

            # 检查是否是全屏大小
            screen_geometry = self.screen().geometry()
            is_fullscreen_size = (
                size[0] >= screen_geometry.width()
                and size[1] >= screen_geometry.height()
            )

            if not is_fullscreen_size:
                self.config_manager.save_window_geometry(size, position)

        event.accept()
