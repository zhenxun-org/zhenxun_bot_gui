# zhenxun_bot_gui

## 项目简介

这是一个基于 PySide6 的 GUI 应用程序，提供现代化的用户界面和丰富的交互功能。

## 功能特性

### 🎨 现代化 UI 设计

- 自定义标题栏
- 侧边栏导航
- 响应式布局
- 流畅的动画效果

### 🔧 弹窗组件系统

#### 基础弹窗类型

- **InfoDialog**: 信息提示弹窗
- **ConfirmDialog**: 确认弹窗
- **WarningDialog**: 警告弹窗
- **ErrorDialog**: 错误弹窗
- **SuccessDialog**: 成功弹窗

#### 🆕 多按钮弹窗功能

- **MultiButtonDialog**: 支持多个按钮的弹窗
- **动态按钮创建**: 运行时添加任意数量的按钮
- **6 种按钮样式**: default、primary、success、warning、danger、info
- **回调函数支持**: 每个按钮可以绑定自定义回调函数
- **信号机制**: button_clicked 信号传递按钮文本
- **完全向后兼容**: 不影响现有的单按钮弹窗

### 🎯 设计特点

- 现代化设计
- 流畅动画
- 精致细节
- 关闭按钮
- 多种按钮样式

### 🎬 动画效果

- 淡入动画: 250ms (OutBack 缓动)
- 淡出动画: 200ms (InCubic 缓动)
- 平滑的透明度变化

## 快速开始

### 安装依赖

```bash
pip install poetry
poetry install
```

### 运行应用

```bash
poetry run python run.py
```

## 弹窗使用示例

### 基础用法

```python
from src.gui.widgets import show_info_dialog, show_confirm_dialog

# 显示信息弹窗
show_info_dialog("提示", "这是一个信息弹窗", parent)

# 显示确认弹窗
show_confirm_dialog("确认", "确定要执行此操作吗？", parent)
```

### 多按钮弹窗

```python
from src.gui.widgets import show_multi_button_dialog

# 定义按钮配置
buttons = [
    {"text": "取消", "type": "default"},
    {"text": "保存", "type": "primary"},
    {"text": "删除", "type": "danger"}
]

# 显示多按钮弹窗
show_multi_button_dialog(
    "操作确认",
    "请选择要执行的操作：",
    buttons,
    parent
)
```

### 带回调函数的多按钮弹窗

```python
def on_save():
    print("执行保存操作...")

def on_delete():
    print("执行删除操作...")

buttons = [
    {"text": "取消", "type": "default"},
    {"text": "保存", "type": "primary", "callback": on_save},
    {"text": "删除", "type": "danger", "callback": on_delete}
]

show_multi_button_dialog(
    "文件操作",
    "请选择要执行的文件操作：",
    buttons,
    parent
)
```

## 按钮样式类型

| 类型      | 颜色     | 用途     | 示例       |
| --------- | -------- | -------- | ---------- |
| `default` | 灰色边框 | 次要操作 | 取消、关闭 |
| `primary` | 蓝色     | 主要操作 | 确认、保存 |
| `success` | 绿色     | 成功操作 | 完成、发布 |
| `warning` | 黄色     | 警告操作 | 草稿、预览 |
| `danger`  | 红色     | 危险操作 | 删除、重置 |
| `info`    | 青色     | 信息操作 | 查看、分享 |

## 项目结构

```
zhenxun_bot_gui/
├── src/
│   ├── gui/
│   │   ├── widgets/
│   │   │   ├── global_dialog.py      # 弹窗组件
│   │   │   ├── animated_button.py    # 动画按钮
│   │   │   └── __init__.py
│   │   ├── pages/                    # 页面组件
│   │   └── main_window.py           # 主窗口
│   └── utils/                        # 工具模块
├── assets/                           # 资源文件
├── run.py                           # 启动脚本
└── README.md                        # 项目文档
```

## 开发指南

### 添加新的弹窗类型

```python
from src.gui.widgets import GlobalDialog

class CustomDialog(GlobalDialog):
    def __init__(self, title="", content="", parent=None):
        super().__init__(parent)
        self.set_dialog_content(title, content)
        # 添加自定义按钮
        self.add_button("自定义", "primary")
```

### 自定义按钮样式

```python
# 在 GlobalDialog 中修改 _set_button_style 方法
def _set_button_style(self, button, button_type):
    # 添加自定义样式逻辑
    pass
```

## 注意事项

- 弹窗固定大小为 440x320 像素
- 圆角设计为 16px
- 支持阴影效果
- 包含 "×" 关闭按钮
- 点击关闭按钮会触发 `cancelled` 信号
- 多按钮弹窗支持 `button_clicked` 信号

## 演示脚本

- `demo_multi_button_dialog.py`: 多按钮弹窗功能演示
- `test_multi_button.py`: 多按钮弹窗功能测试
- `demo_beautified_dialog.py`: 美化弹窗演示

## 文档

- `MULTI_BUTTON_DIALOG_GUIDE.md`: 详细的多按钮弹窗使用指南
- `UI_BEAUTIFICATION_SUMMARY.md`: UI 美化改进总结

## 许可证

本项目采用 MIT 许可证。

---

_最后更新: 2024 年_
