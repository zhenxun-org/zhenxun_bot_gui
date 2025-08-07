#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单调试脚本 - 不使用动画
"""

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication, QStackedWidget

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.gui.main_window import MainWindow


def simple_debug():
    """简单调试 - 不使用动画"""
    app = QApplication(sys.argv)
    app.setApplicationName("真寻Bot GUI")
    app.setApplicationVersion("0.1.0")
    app.setOrganizationName("HibiKier")
    app.setStyle("Fusion")

    # 创建主窗口
    main_window = MainWindow()

    # 替换为简单的QStackedWidget，不使用动画
    from src.gui.pages.home_page import HomePage
    from src.gui.pages.settings_page import SettingsPage

    simple_stack = QStackedWidget()
    simple_stack.addWidget(HomePage())
    simple_stack.addWidget(SettingsPage())

    # 替换原来的content_area（使用类型转换）
    main_window.content_area = simple_stack  # type: ignore

    # 重新设置连接
    def simple_change_page(index):
        print(f"简单切换页面: {index}")
        simple_stack.setCurrentIndex(index)
        main_window.sidebar.set_active_page(index)

        page_names = ["主页", "设置"]
        if 0 <= index < len(page_names):
            main_window.setWindowTitle(f"真寻Bot GUI - {page_names[index]}")

    main_window.sidebar.page_changed.connect(simple_change_page)

    main_window.show()

    print("=== 简单调试 ===")
    print("使用简单的QStackedWidget，不使用动画")
    print("测试步骤:")
    print("1. 启动后应该显示主页")
    print("2. 点击'设置'按钮，应该切换到设置页")
    print("3. 点击'主页'按钮，应该切换回主页")
    print("4. 如果这个版本正常，说明问题在动画上")

    return app.exec()


if __name__ == "__main__":
    simple_debug()
