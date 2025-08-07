#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试测试脚本
"""

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.gui.main_window import MainWindow


def debug_test():
    """调试测试"""
    app = QApplication(sys.argv)
    app.setApplicationName("真寻Bot GUI")
    app.setApplicationVersion("0.1.0")
    app.setOrganizationName("HibiKier")
    app.setStyle("Fusion")

    # 创建主窗口
    main_window = MainWindow()
    main_window.show()

    print("=== 调试测试 ===")
    print("请测试以下操作:")
    print("1. 点击'设置'按钮")
    print("2. 再点击'主页'按钮")
    print("3. 观察控制台输出")
    print("4. 检查页面是否正确切换")

    return app.exec()


if __name__ == "__main__":
    debug_test()
