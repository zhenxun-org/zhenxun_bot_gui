#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单最终测试
"""

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.gui.main_window import MainWindow


def simple_final_test():
    """简单最终测试"""
    app = QApplication(sys.argv)
    app.setApplicationName("真寻Bot GUI")
    app.setApplicationVersion("0.1.0")
    app.setOrganizationName("HibiKier")
    app.setStyle("Fusion")

    # 创建主窗口
    main_window = MainWindow()
    main_window.show()

    print("=== 简单最终测试 ===")
    print("现在使用最简单的页面切换，不使用动画")
    print("测试步骤:")
    print("1. 启动后应该显示主页内容")
    print("2. 点击'设置'按钮，应该切换到设置页内容")
    print("3. 点击'主页'按钮，应该切换回主页内容")
    print("4. 页面内容应该正常显示，不再空白")

    return app.exec()


if __name__ == "__main__":
    simple_final_test()
