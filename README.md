# 真寻 Bot GUI

一个基于 PySide6 的现代化 GUI 界面，用于管理真寻 Bot。

## 功能特性

- 🎨 现代化 UI 设计
- 🔧 环境检测与配置
- 📱 响应式布局
- 🎯 直观的操作界面

## 快速启动

### Windows 用户

1. **双击启动**（推荐）：直接双击 `启动真寻Bot.bat` 文件
2. **命令行启动**：运行 `start.bat`

### Linux/Mac 用户

```bash
chmod +x start.sh
./start.sh
```

### 开发者启动

```bash
poetry install
poetry run python start_gui.pyw
```

## 启动说明

- 程序启动时会自动隐藏控制台窗口
- 所有日志信息会保存到 `app.log` 文件中
- 如需查看详细日志，请查看项目根目录下的 `app.log` 文件

## 管理员权限说明

程序需要管理员权限来配置系统 PATH 环境变量。启动时会自动请求权限：

- **Windows**: 会弹出 UAC 提示，点击"是"即可
- **Linux/Mac**: 会要求输入 sudo 密码

如果权限获取失败，某些功能（如 FFmpeg 自动配置 PATH）可能无法正常工作。

## 项目结构

```
zhenxun_bot_gui/
├── src/
│   ├── gui/           # GUI相关代码
│   └── utils/         # 工具函数
├── assets/            # 资源文件
├── start_gui.pyw      # 主启动文件（隐藏控制台）
├── 启动真寻Bot.bat    # Windows双击启动脚本
└── README.md
```

## 开发环境

- Python 3.8+
- PySide6
- Poetry（包管理）

## 许可证

MIT License
