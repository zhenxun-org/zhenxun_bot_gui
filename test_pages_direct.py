#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接测试页面组件
"""

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.gui.pages.home_page import HomePage
from src.gui.pages.settings_page import SettingsPage


def test_pages_direct():
    """直接测试页面组件"""
    app = QApplication(sys.argv)
    app.setApplicationName("真寻Bot GUI")
    app.setApplicationVersion("0.1.0")
    app.setOrganizationName("HibiKier")
    app.setStyle("Fusion")

    # 创建主窗口
    main_window = QMainWindow()
    main_window.setWindowTitle("页面组件测试")
    main_window.setMinimumSize(800, 600)

    # 创建中央widget
    central_widget = QWidget()
    main_window.setCentralWidget(central_widget)

    # 创建布局
    layout = QVBoxLayout(central_widget)

    # 测试主页组件
    print("=== 测试主页组件 ===")
    home_page = HomePage()
    layout.addWidget(home_page)
    print(f"主页组件类型: {type(home_page)}")
    print(f"主页组件可见性: {home_page.isVisible()}")
    print(f"主页组件大小: {home_page.size()}")

    # 测试设置页组件
    print("\n=== 测试设置页组件 ===")
    settings_page = SettingsPage()
    layout.addWidget(settings_page)
    print(f"设置页组件类型: {type(settings_page)}")
    print(f"设置页组件可见性: {settings_page.isVisible()}")
    print(f"设置页组件大小: {settings_page.size()}")

    main_window.show()

    print("\n=== 测试说明 ===")
    print("1. 如果页面组件正常显示，说明组件本身没问题")
    print("2. 如果页面组件不显示，说明组件有问题")
    print("3. 检查页面是否有内容")

    return app.exec()


if __name__ == "__main__":
    test_pages_direct()
