# -*- coding: utf-8 -*-
"""
主页
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class HomePage(QWidget):
    """主页"""

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        """设置UI"""
        # 设置背景色
        self.setStyleSheet("""
            QWidget {
                background-color: #fafbfc;
            }
        """)

        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(0)

        # 页面标题
        title = QLabel("机器人配置")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setWeight(QFont.Weight.Bold)
        title.setFont(title_font)
        title.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                background: transparent;
                margin-bottom: 10px;
            }
        """)
        main_layout.addWidget(title)

        # 副标题
        subtitle = QLabel("在添加机器人之前，您需要做一些配置")
        subtitle.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                font-size: 14px;
                background: transparent;
                margin-bottom: 20px;
            }
        """)
        main_layout.addWidget(subtitle)

        # 创建标签页
        self.create_tab_widget(main_layout)

        # 底部操作按钮
        self.create_action_buttons(main_layout)

    def create_tab_widget(self, layout):
        """创建标签页组件"""
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #e1e5e9;
                background-color: white;
                border-radius: 8px;
                margin-top: -1px;
            }
            QTabBar::tab {
                background-color: #f8f9fa;
                color: #495057;
                padding: 12px 24px;
                margin-right: 2px;
                border: 1px solid #e1e5e9;
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }
            QTabBar::tab:selected {
                background-color: white;
                color: #007acc;
                border-bottom: 1px solid white;
            }
            QTabBar::tab:hover:!selected {
                background-color: #e9ecef;
            }
        """)

        # 基本配置标签页
        basic_tab = self.create_basic_config_tab()
        self.tab_widget.addTab(basic_tab, "基本配置")

        # 连接配置标签页
        connection_tab = self.create_connection_config_tab()
        self.tab_widget.addTab(connection_tab, "连接配置")

        # 高级配置标签页
        advanced_tab = self.create_advanced_config_tab()
        self.tab_widget.addTab(advanced_tab, "高级配置")

        layout.addWidget(self.tab_widget)

    def create_basic_config_tab(self):
        """创建基本配置标签页"""
        widget = QWidget()
        widget.setStyleSheet("background-color: white;")

        # 使用滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: white;
            }
        """)

        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(30, 30, 30, 30)
        scroll_layout.setSpacing(25)

        # Bot名称配置组
        bot_group = self.create_form_group(
            "Bot 名称", [("设置机器人的名称", "bot_name", "QIAO Bot", "line")]
        )
        scroll_layout.addWidget(bot_group)

        # Bot QQ配置组
        qq_group = self.create_form_group(
            "Bot QQ", [("设置机器人 QQ 号, 不能为空", "bot_qq", "114514", "line")]
        )
        scroll_layout.addWidget(qq_group)

        # 音乐签名URL配置组
        music_group = self.create_form_group(
            "音乐签名URL",
            [
                (
                    "用于处理音乐相关请求, 为空则使用内置签名服务器",
                    "music_url",
                    "https://example...",
                    "line",
                )
            ],
        )
        scroll_layout.addWidget(music_group)

        scroll_layout.addStretch()
        scroll_area.setWidget(scroll_widget)

        main_layout = QVBoxLayout(widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll_area)

        return widget

    def create_connection_config_tab(self):
        """创建连接配置标签页"""
        widget = QWidget()
        widget.setStyleSheet("background-color: white;")

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: white;
            }
        """)

        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(30, 30, 30, 30)
        scroll_layout.setSpacing(25)

        # WebSocket配置组
        ws_group = self.create_form_group(
            "WebSocket 配置",
            [
                ("监听地址", "ws_host", "localhost", "line"),
                ("监听端口", "ws_port", "3001", "spin"),
            ],
        )
        scroll_layout.addWidget(ws_group)

        # HTTP配置组
        http_group = self.create_form_group(
            "HTTP API 配置",
            [
                ("HTTP地址", "http_host", "localhost", "line"),
                ("HTTP端口", "http_port", "3000", "spin"),
                ("启用HTTP", "enable_http", True, "check"),
            ],
        )
        scroll_layout.addWidget(http_group)

        scroll_layout.addStretch()
        scroll_area.setWidget(scroll_widget)

        main_layout = QVBoxLayout(widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll_area)

        return widget

    def create_advanced_config_tab(self):
        """创建高级配置标签页"""
        widget = QWidget()
        widget.setStyleSheet("background-color: white;")

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: white;
            }
        """)

        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(30, 30, 30, 30)
        scroll_layout.setSpacing(25)

        # 日志配置组
        log_group = self.create_form_group(
            "日志配置",
            [
                (
                    "日志级别",
                    "log_level",
                    ["DEBUG", "INFO", "WARNING", "ERROR"],
                    "combo",
                ),
                ("启用文件日志", "file_log", True, "check"),
            ],
        )
        scroll_layout.addWidget(log_group)

        # 数据库配置组
        db_group = self.create_form_group(
            "数据库配置",
            [
                ("数据库类型", "db_type", ["SQLite", "MySQL", "PostgreSQL"], "combo"),
                ("数据库地址", "db_host", "localhost", "line"),
                ("数据库端口", "db_port", "5432", "spin"),
            ],
        )
        scroll_layout.addWidget(db_group)

        # 其他配置
        other_group = self.create_form_group(
            "其他配置",
            [("配置说明", "config_note", "在这里添加额外的配置说明...", "text")],
        )
        scroll_layout.addWidget(other_group)

        scroll_layout.addStretch()
        scroll_area.setWidget(scroll_widget)

        main_layout = QVBoxLayout(widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll_area)

        return widget

    def create_form_group(self, title, fields):
        """创建表单组"""
        group = QGroupBox(title)
        group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: 600;
                color: #2c3e50;
                border: 1px solid #e1e5e9;
                border-radius: 8px;
                margin-top: 10px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
                background-color: white;
            }
        """)

        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        form_layout.setContentsMargins(20, 25, 20, 20)

        for field in fields:
            if len(field) == 4:
                label_text, field_name, default_value, field_type = field
                widget = self.create_form_field(field_type, default_value)

                # 创建标签
                label = QLabel(label_text)
                label.setStyleSheet("""
                    QLabel {
                        color: #495057;
                        font-size: 13px;
                        background: transparent;
                    }
                """)

                form_layout.addRow(label, widget)

        group.setLayout(form_layout)
        return group

    def create_form_field(self, field_type, default_value):
        """创建表单字段"""
        field_style = """
            QLineEdit, QSpinBox, QComboBox {
                padding: 8px 12px;
                border: 1px solid #ced4da;
                border-radius: 6px;
                font-size: 13px;
                background-color: white;
                min-height: 20px;
            }
            QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
                border-color: #007acc;
                outline: none;
            }
            QTextEdit {
                padding: 8px 12px;
                border: 1px solid #ced4da;
                border-radius: 6px;
                font-size: 13px;
                background-color: white;
                min-height: 60px;
            }
            QTextEdit:focus {
                border-color: #007acc;
                outline: none;
            }
            QCheckBox {
                font-size: 13px;
                color: #495057;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 1px solid #ced4da;
                border-radius: 3px;
                background-color: white;
            }
            QCheckBox::indicator:checked {
                background-color: #007acc;
                border-color: #007acc;
            }
        """

        if field_type == "line":
            widget = QLineEdit()
            if isinstance(default_value, str):
                widget.setPlaceholderText(default_value)
            widget.setStyleSheet(field_style)
            return widget
        elif field_type == "spin":
            widget = QSpinBox()
            widget.setMaximum(99999)
            if isinstance(default_value, str) and default_value.isdigit():
                widget.setValue(int(default_value))
            widget.setStyleSheet(field_style)
            return widget
        elif field_type == "check":
            widget = QCheckBox()
            if isinstance(default_value, bool):
                widget.setChecked(default_value)
            widget.setStyleSheet(field_style)
            return widget
        elif field_type == "combo":
            widget = QComboBox()
            if isinstance(default_value, list):
                widget.addItems(default_value)
            widget.setStyleSheet(field_style)
            return widget
        elif field_type == "text":
            widget = QTextEdit()
            if isinstance(default_value, str):
                widget.setPlaceholderText(default_value)
            widget.setStyleSheet(field_style)
            return widget

        return QWidget()

    def create_action_buttons(self, layout):
        """创建操作按钮"""
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 20, 0, 0)
        button_layout.setSpacing(10)

        # 删除按钮
        delete_btn = QPushButton("🗑️")
        delete_btn.setFixedSize(40, 36)
        delete_btn.setToolTip("删除配置")
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:pressed {
                background-color: #bd2130;
            }
        """)

        # 测试弹窗按钮
        test_dialog_btn = QPushButton("测试弹窗")
        test_dialog_btn.setFixedHeight(36)
        test_dialog_btn.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 600;
                padding: 0 20px;
            }
            QPushButton:hover {
                background-color: #138496;
            }
            QPushButton:pressed {
                background-color: #117a8b;
            }
        """)
        test_dialog_btn.clicked.connect(self.show_test_dialog)

        # 添加按钮
        add_btn = QPushButton("+ 添加")
        add_btn.setFixedHeight(36)
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #007acc;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 600;
                padding: 0 20px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #004085;
            }
        """)

        button_layout.addWidget(delete_btn)
        button_layout.addWidget(test_dialog_btn)
        button_layout.addStretch()
        button_layout.addWidget(add_btn)

        layout.addLayout(button_layout)

    def show_test_dialog(self):
        """显示测试弹窗"""
        from ..widgets import (
            show_confirm_dialog,
            show_error_dialog,
            show_info_dialog,
            show_multi_button_dialog,
            show_success_dialog,
            show_warning_dialog,
        )
        
        # 显示多按钮弹窗演示
        buttons = [
            {"text": "取消", "type": "default"},
            {"text": "了解更多", "type": "info"},
            {"text": "立即体验", "type": "primary"}
        ]
        
        show_multi_button_dialog(
            "多按钮弹窗功能",
            "🎉 新增多按钮支持功能！\n\n✨ 功能亮点：\n• 支持动态添加多个按钮\n• 6种按钮样式类型：default、primary、success、warning、danger、info\n• 支持按钮回调函数\n• 保持原有的美观设计\n• 流畅的动画效果\n\n🔧 技术特性：\n• 按钮类型：default(灰色)、primary(蓝色)、success(绿色)、warning(黄色)、danger(红色)、info(青色)\n• 支持自定义回调函数\n• 信号机制：button_clicked信号传递按钮文本\n• 完全向后兼容原有弹窗类型",
            buttons,
            self
        )
