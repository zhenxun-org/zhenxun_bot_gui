#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试动画效果
"""

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.gui.main_window import MainWindow


def test_animation():
    """测试动画效果"""
    app = QApplication(sys.argv)
    app.setApplicationName("真寻Bot GUI")
    app.setApplicationVersion("0.1.0")
    app.setOrganizationName("HibiKier")
    app.setStyle("Fusion")

    # 创建主窗口
    main_window = MainWindow()
    main_window.show()

    print("=== 动画效果测试 ===")
    print("现在使用简单的淡入淡出动画")
    print("测试步骤:")
    print("1. 启动后应该显示主页内容")
    print("2. 点击'设置'按钮，应该切换到设置页（带淡入动画）")
    print("3. 点击'主页'按钮，应该切换回主页（带淡入动画）")
    print("4. 观察是否有平滑的淡入效果")
    print("5. 页面内容应该正常显示，动画不影响内容")

    return app.exec()


if __name__ == "__main__":
    test_animation()
