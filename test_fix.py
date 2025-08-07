#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修复效果
"""

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.gui.main_window import MainWindow


def test_fix():
    """测试修复效果"""
    app = QApplication(sys.argv)
    app.setApplicationName("真寻Bot GUI")
    app.setApplicationVersion("0.1.0")
    app.setOrganizationName("HibiKier")
    app.setStyle("Fusion")

    # 创建主窗口
    main_window = MainWindow()
    main_window.show()

    print("=== 修复测试 ===")
    print("1. 点击左侧边栏按钮应该正常切换页面")
    print("2. 快速点击不会导致页面显示异常")
    print("3. 动画过程中不会重复触发切换")
    print("4. 窗口标题会正确更新")
    print("5. 侧边栏按钮状态正确")

    return app.exec()


if __name__ == "__main__":
    test_fix()
