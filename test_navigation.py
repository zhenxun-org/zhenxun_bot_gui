#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试导航功能
"""

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.gui.main_window import MainWindow


def test_navigation():
    """测试导航功能"""
    app = QApplication(sys.argv)
    app.setApplicationName("真寻Bot GUI")
    app.setApplicationVersion("0.1.0")
    app.setOrganizationName("HibiKier")
    app.setStyle("Fusion")

    # 创建主窗口
    main_window = MainWindow()
    main_window.show()

    print("测试导航功能:")
    print("1. 点击左侧边栏的'主页'按钮应该显示主页内容")
    print("2. 点击左侧边栏的'设置'按钮应该显示设置页面内容")
    print("3. 切换时应该有动画效果")
    print("4. 窗口标题应该相应更新")

    return app.exec()


if __name__ == "__main__":
    test_navigation()
