#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
真寻Bot GUI主程序入口
"""

import os
import platform
import sys
from pathlib import Path

# 在Windows上隐藏控制台窗口
if platform.system() == "Windows":
    import ctypes
    # 隐藏控制台窗口
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    
    # 重定向输出到日志文件
    log_file = Path("app.log")
    sys.stdout = open(log_file, "w", encoding="utf-8")
    sys.stderr = open(log_file, "a", encoding="utf-8")

# 请求管理员权限
from src.gui.pages.environment_page import request_admin_privileges

request_admin_privileges()

from PySide6.QtWidgets import QApplication

from src.gui.main_window import MainWindow


def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 设置应用程序信息
    app.setApplicationName("真寻Bot GUI")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("真寻Bot")
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    # 运行应用程序
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
