# -*- coding: utf-8 -*-
"""
设置页面
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


class SettingsPage(QWidget):
    """设置页面"""

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
        title = QLabel("应用设置")
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
        subtitle = QLabel("配置应用程序的各种设置选项")
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

        # 基本设置标签页
        basic_tab = self.create_basic_settings_tab()
        self.tab_widget.addTab(basic_tab, "基本设置")

        # 界面设置标签页
        ui_tab = self.create_ui_settings_tab()
        self.tab_widget.addTab(ui_tab, "界面设置")

        # 高级设置标签页
        advanced_tab = self.create_advanced_settings_tab()
        self.tab_widget.addTab(advanced_tab, "高级设置")

        layout.addWidget(self.tab_widget)

    def create_basic_settings_tab(self):
        """创建基本设置标签页"""
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

        # 应用信息配置组
        app_group = self.create_form_group(
            "应用信息", [("应用名称", "app_name", "真寻Bot GUI", "line")]
        )
        scroll_layout.addWidget(app_group)

        # 语言设置配置组
        language_group = self.create_form_group(
            "语言设置",
            [
                ("界面语言", "language", ["简体中文", "English", "日本語"], "combo"),
                ("时区设置", "timezone", "Asia/Shanghai", "line"),
            ],
        )
        scroll_layout.addWidget(language_group)

        # 更新设置配置组
        update_group = self.create_form_group(
            "更新设置",
            [
                ("自动检查更新", "auto_update", True, "check"),
                ("更新服务器", "update_server", "https://api.github.com", "line"),
            ],
        )
        scroll_layout.addWidget(update_group)

        scroll_layout.addStretch()
        scroll_area.setWidget(scroll_widget)

        main_layout = QVBoxLayout(widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll_area)

        return widget

    def create_ui_settings_tab(self):
        """创建界面设置标签页"""
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

        # 主题设置配置组
        theme_group = self.create_form_group(
            "主题设置",
            [
                ("主题模式", "theme", ["浅色", "深色", "自动"], "combo"),
                ("主色调", "primary_color", "#007acc", "line"),
                ("圆角大小", "border_radius", "8", "spin"),
            ],
        )
        scroll_layout.addWidget(theme_group)

        # 字体设置配置组
        font_group = self.create_form_group(
            "字体设置",
            [
                ("字体大小", "font_size", "14", "spin"),
                ("字体族", "font_family", "Microsoft YaHei", "line"),
                ("启用字体平滑", "font_smoothing", True, "check"),
            ],
        )
        scroll_layout.addWidget(font_group)

        scroll_layout.addStretch()
        scroll_area.setWidget(scroll_widget)

        main_layout = QVBoxLayout(widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll_area)

        return widget

    def create_advanced_settings_tab(self):
        """创建高级设置标签页"""
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

        # 性能设置配置组
        performance_group = self.create_form_group(
            "性能设置",
            [
                ("启用硬件加速", "hardware_acceleration", True, "check"),
                ("最大内存使用", "max_memory", "1024", "spin"),
                ("缓存大小", "cache_size", "256", "spin"),
            ],
        )
        scroll_layout.addWidget(performance_group)

        # 调试设置配置组
        debug_group = self.create_form_group(
            "调试设置",
            [
                ("启用调试模式", "debug_mode", False, "check"),
                (
                    "日志级别",
                    "log_level",
                    ["INFO", "DEBUG", "WARNING", "ERROR"],
                    "combo",
                ),
                ("日志文件路径", "log_file", "./logs/app.log", "line"),
            ],
        )
        scroll_layout.addWidget(debug_group)

        # 其他设置
        other_group = self.create_form_group(
            "其他设置",
            [("配置说明", "config_note", "在这里添加其他配置说明...", "text")],
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

        # 重置按钮
        reset_btn = QPushButton("重置")
        reset_btn.setFixedHeight(36)
        reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 600;
                padding: 0 20px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
            QPushButton:pressed {
                background-color: #545b62;
            }
        """)

        # 保存按钮
        save_btn = QPushButton("保存设置")
        save_btn.setFixedHeight(36)
        save_btn.setStyleSheet("""
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

        button_layout.addWidget(reset_btn)
        button_layout.addStretch()
        button_layout.addWidget(save_btn)

        layout.addLayout(button_layout)
