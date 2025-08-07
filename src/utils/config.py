# -*- coding: utf-8 -*-
"""
配置管理器
"""

import json
from pathlib import Path
from typing import Any, Dict


class ConfigManager:
    """配置管理器类"""

    def __init__(self):
        """初始化配置管理器"""
        self.config_dir = Path.home() / ".zhenxun_bot_gui"
        self.config_file = self.config_dir / "config.json"
        self.config_dir.mkdir(exist_ok=True)

        # 默认配置
        self.default_config = {
            "first_run": True,
            "window_size": [1200, 800],
            "window_position": [100, 100],
            "theme": "light",
            "language": "zh_CN",
        }

        self._load_config()

    def _load_config(self) -> None:
        """加载配置文件"""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    self.config = json.load(f)
                # 合并默认配置，确保所有键都存在
                for key, value in self.default_config.items():
                    if key not in self.config:
                        self.config[key] = value
            except (json.JSONDecodeError, IOError):
                self.config = self.default_config.copy()
        else:
            self.config = self.default_config.copy()

    def _save_config(self) -> None:
        """保存配置文件"""
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"保存配置文件失败: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        return self.config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """设置配置值"""
        self.config[key] = value
        self._save_config()

    def is_first_run(self) -> bool:
        """检查是否首次运行"""
        return self.config.get("first_run", True)

    def set_first_run_completed(self) -> None:
        """标记首次运行已完成"""
        self.set("first_run", False)

    def get_window_geometry(self) -> Dict[str, Any]:
        """获取窗口几何信息"""
        return {
            "size": self.get("window_size", [1200, 800]),
            "position": self.get("window_position", [100, 100]),
        }

    def save_window_geometry(self, size: tuple, position: tuple) -> None:
        """保存窗口几何信息"""
        self.set("window_size", list(size))
        self.set("window_position", list(position))
