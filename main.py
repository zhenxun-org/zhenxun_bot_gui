#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
真寻Bot GUI主程序入口
"""

import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QDialog

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.gui.intro_dialog import IntroDialog
from src.gui.main_window import MainWindow
from src.utils.config import ConfigManager


def main():
    """主程序入口"""
    # 创建应用程序实例
    app = QApplication(sys.argv)
    app.setApplicationName("真寻Bot GUI")
    app.setApplicationVersion("0.1.0")
    app.setOrganizationName("HibiKier")

    # 设置应用程序样式
    app.setStyle("Fusion")

    # 配置管理器
    config_manager = ConfigManager()

    # 检查是否首次启动
    if config_manager.is_first_run():
        # 显示介绍对话框
        intro_dialog = IntroDialog()
        if intro_dialog.exec() == QDialog.Accepted:
            # 标记为非首次启动
            config_manager.set_first_run_completed()
        else:
            # 用户关闭了介绍对话框，退出程序
            return 0

    # 创建并显示主窗口
    main_window = MainWindow()
    main_window.show()

    # 启动事件循环
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
