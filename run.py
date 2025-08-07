#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
真寻Bot GUI运行脚本
使用此脚本来启动应用程序
"""

import os
import sys

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from main import main

    if __name__ == "__main__":
        sys.exit(main())
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保已安装所需依赖:")
    print("pip install PySide6")
    sys.exit(1)
except Exception as e:
    print(f"启动错误: {e}")
    sys.exit(1)
