#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试页面显示问题
"""

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.gui.main_window import MainWindow


def debug_pages():
    """调试页面显示问题"""
    app = QApplication(sys.argv)
    app.setApplicationName("真寻Bot GUI")
    app.setApplicationVersion("0.1.0")
    app.setOrganizationName("HibiKier")
    app.setStyle("Fusion")

    # 创建主窗口
    main_window = MainWindow()
    main_window.show()

    # 检查页面状态
    content_area = main_window.content_area
    print(f"=== 页面调试信息 ===")
    print(f"内容区域页面数量: {content_area.count()}")
    print(f"当前页面索引: {content_area.currentIndex()}")

    for i in range(content_area.count()):
        widget = content_area.widget(i)
        print(f"页面 {i}: {type(widget).__name__}, 可见性: {widget.isVisible()}")
        if hasattr(widget, "windowTitle"):
            print(f"  标题: {widget.windowTitle()}")
        if hasattr(widget, "objectName"):
            print(f"  对象名: {widget.objectName()}")

    print("\n=== 测试步骤 ===")
    print("1. 检查启动时是否显示主页内容")
    print("2. 点击'设置'按钮，检查是否显示设置页内容")
    print("3. 点击'主页'按钮，检查是否显示主页内容")
    print("4. 如果页面空白，检查控制台输出")

    return app.exec()


if __name__ == "__main__":
    debug_pages()
