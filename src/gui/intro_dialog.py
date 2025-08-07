# -*- coding: utf-8 -*-
"""
首次启动介绍对话框
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)


class IntroPage(QWidget):
    """介绍页面基类"""

    def __init__(self, title: str, content: str, parent=None):
        super().__init__(parent)
        self.setup_ui(title, content)

    def setup_ui(self, title: str, content: str):
        """设置UI - 简约页面设计"""
        layout = QVBoxLayout(self)
        layout.setSpacing(24)
        layout.setContentsMargins(40, 40, 40, 40)

        # 图标占位符
        if "欢迎" in title:
            icon_text = "WELCOME"
        elif "功能" in title:
            icon_text = "FEATURE"
        else:
            icon_text = "GUIDE"

        icon_placeholder = QLabel(icon_text)
        icon_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_placeholder.setFixedSize(80, 80)
        icon_placeholder.setStyleSheet("""
            background-color: #f3f4f6;
            border-radius: 12px;
            color: #6b7280;
            font-size: 12px;
            font-weight: 700;
        """)
        layout.addWidget(icon_placeholder, 0, Qt.AlignmentFlag.AlignCenter)

        # 标题
        title_label = QLabel(title)
        title_font = QFont()
        title_font.setPointSize(22)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            color: #111827;
            background: transparent;
            margin: 16px 0;
        """)
        layout.addWidget(title_label)

        # 内容
        content_label = QLabel(content)
        content_label.setWordWrap(True)
        content_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_label.setStyleSheet("""
            color: #6b7280;
            font-size: 15px;
            line-height: 1.6;
            background: transparent;
        """)
        layout.addWidget(content_label)

        layout.addStretch()


class IntroDialog(QDialog):
    """首次启动介绍对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_page = 0
        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        """设置UI - 简约设计"""
        self.setWindowTitle("欢迎使用真寻Bot GUI")
        self.setFixedSize(700, 500)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowCloseButtonHint)

        # 设置背景
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
            }
        """)

        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(24)

        # 内容容器
        content_container = QWidget()
        content_container.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e1e5e9;
            }
        """)
        container_layout = QVBoxLayout(content_container)
        container_layout.setContentsMargins(40, 32, 40, 24)
        container_layout.setSpacing(0)

        # 页面堆栈
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setStyleSheet("background: transparent;")

        # 创建介绍页面
        self.create_intro_pages()

        container_layout.addWidget(self.stacked_widget)

        # 页面指示器
        self.create_page_indicator(container_layout)

        # 底部按钮区域
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 16, 0, 0)
        button_layout.setSpacing(12)

        # 跳过按钮
        self.skip_button = QPushButton("跳过")
        self.skip_button.setFixedHeight(40)
        self.skip_button.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #6b7280;
                border: 1px solid #e1e5e9;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 500;
                padding: 0 20px;
            }
            QPushButton:hover {
                border-color: #9ca3af;
                background-color: #f8f9fa;
            }
        """)

        # 上一步按钮
        self.prev_button = QPushButton("上一步")
        self.prev_button.setEnabled(False)
        self.prev_button.setFixedHeight(40)
        self.prev_button.setStyleSheet("""
            QPushButton {
                background-color: #9ca3af;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 500;
                padding: 0 20px;
            }
            QPushButton:hover:enabled {
                background-color: #6b7280;
            }
            QPushButton:disabled {
                background-color: #e1e5e9;
                color: #9ca3af;
            }
        """)

        # 下一步/完成按钮
        self.next_button = QPushButton("下一步")
        self.next_button.setFixedHeight(40)
        self.next_button.setStyleSheet("""
            QPushButton {
                background-color: #007acc;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 600;
                padding: 0 24px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #004085;
            }
        """)

        button_layout.addWidget(self.skip_button)
        button_layout.addStretch()
        button_layout.addWidget(self.prev_button)
        button_layout.addWidget(self.next_button)

        container_layout.addLayout(button_layout)
        main_layout.addWidget(content_container)

    def create_intro_pages(self):
        """创建介绍页面"""
        pages = [
            {
                "title": "欢迎使用真寻Bot GUI",
                "content": """欢迎使用真寻Bot图形化管理界面！

这是一个专为真寻Bot设计的现代化管理工具，让您可以通过直观的图形界面来配置和管理您的机器人。

主要特点：
• 简洁直观的用户界面
• 实时状态监控
• 便捷的配置管理
• 插件管理功能
• 数据统计与分析

让我们开始设置您的机器人吧！""",
            },
            {
                "title": "主要功能介绍",
                "content": """真寻Bot GUI 为您提供以下核心功能：

🏠 主页面板
• 机器人运行状态实时监控
• 关键数据统计展示
• 快速操作入口

⚙️ 设置管理
• 机器人基础配置
• 插件开关控制
• 数据库连接设置
• 日志级别调整

通过左侧菜单栏，您可以轻松在各个功能模块间切换，享受流畅的使用体验。""",
            },
            {
                "title": "开始使用",
                "content": """现在您已经了解了基本功能，可以开始使用真寻Bot GUI了！

快速上手指南：
1. 点击左侧菜单栏的"主页"查看机器人状态
2. 在"设置"页面配置您的机器人参数
3. 根据需要调整各项设置

如果您在使用过程中遇到任何问题，可以：
• 查看程序日志获取详细信息
• 参考官方文档
• 在GitHub仓库提交问题反馈

祝您使用愉快！""",
            },
        ]

        for page_data in pages:
            page = IntroPage(page_data["title"], page_data["content"])
            self.stacked_widget.addWidget(page)

    def create_page_indicator(self, layout):
        """创建页面指示器"""
        indicator_layout = QHBoxLayout()
        indicator_layout.setContentsMargins(0, 20, 0, 0)

        self.indicators = []
        for i in range(3):  # 3个页面
            dot = QLabel("●")
            dot.setAlignment(Qt.AlignmentFlag.AlignCenter)
            dot.setFixedSize(12, 12)
            dot.setStyleSheet("""
                color: #e1e5e9;
                font-size: 8px;
                background: transparent;
            """)
            self.indicators.append(dot)
            indicator_layout.addWidget(dot)

        # 设置第一个为活跃状态
        self.indicators[0].setStyleSheet("""
            color: #007acc;
            font-size: 8px;
            background: transparent;
        """)

        indicator_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addLayout(indicator_layout)

    def update_indicators(self):
        """更新页面指示器"""
        for i, dot in enumerate(self.indicators):
            if i == self.current_page:
                dot.setStyleSheet("""
                    color: #007acc;
                    font-size: 8px;
                    background: transparent;
                """)
            else:
                dot.setStyleSheet("""
                    color: #e1e5e9;
                    font-size: 8px;
                    background: transparent;
                """)

    def setup_connections(self):
        """设置信号连接"""
        self.skip_button.clicked.connect(self.accept)
        self.prev_button.clicked.connect(self.prev_page)
        self.next_button.clicked.connect(self.next_page)

    def prev_page(self):
        """上一页"""
        if self.current_page > 0:
            self.current_page -= 1
            self.stacked_widget.setCurrentIndex(self.current_page)
            self.update_buttons()
            self.update_indicators()

    def next_page(self):
        """下一页"""
        if self.current_page < self.stacked_widget.count() - 1:
            self.current_page += 1
            self.stacked_widget.setCurrentIndex(self.current_page)
            self.update_buttons()
            self.update_indicators()
        else:
            # 最后一页，完成介绍
            self.accept()

    def update_buttons(self):
        """更新按钮状态"""
        # 上一步按钮
        self.prev_button.setEnabled(self.current_page > 0)

        # 下一步/完成按钮
        if self.current_page == self.stacked_widget.count() - 1:
            self.next_button.setText("开始使用")
        else:
            self.next_button.setText("下一步")
