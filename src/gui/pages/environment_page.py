import ctypes
import datetime
import json
import os
import platform
import shutil
import subprocess
import sys
import tarfile
import tempfile
import webbrowser
import zipfile
from pathlib import Path

import requests
from PySide6.QtCore import Qt, QThread, QTimer, Signal
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from src.gui.intro_dialog import IntroDialog, IntroPage
from src.gui.widgets.animated_button import AnimatedButton


def request_admin_privileges():
    """请求管理员权限"""
    if platform.system() == "Windows":
        if not ctypes.windll.shell32.IsUserAnAdmin():
            # 尝试以管理员权限重新启动
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, " ".join(sys.argv), None, 1
            )
            sys.exit(0)
    else:
        # Unix-like 系统
        if os.geteuid() != 0:
            try:
                os.execvp("sudo", ["sudo"] + sys.argv)
            except OSError:
                pass


class SmartDownloadManager(QThread):
    """智能下载管理器"""

    progress_updated = Signal(int)
    status_updated = Signal(str)
    download_finished = Signal(bool, str)

    def __init__(self, url, target_name):
        super().__init__()
        self.url = url
        self.target_name = target_name
        self.temp_dir = None
        self.extract_dir = None

    def run(self):
        try:
            # 创建临时目录
            self.temp_dir = Path(tempfile.mkdtemp())

            # 下载文件
            self.status_updated.emit("正在下载...")
            downloaded_file = self._download_file()

            # 解压文件
            self.status_updated.emit("正在解压...")
            extracted_dir = self._extract_file(downloaded_file)

            # 安装到永久位置
            self.status_updated.emit("正在安装...")
            permanent_dir = self._install_to_permanent_location(extracted_dir)

            # 配置PATH
            self.status_updated.emit("正在配置环境变量...")
            self._configure_path(permanent_dir)

            # 保存安装信息
            self._save_installation_info(permanent_dir)

            # 清理临时文件
            if self.temp_dir and self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)

            self.download_finished.emit(True, f"{self.target_name} 安装成功！")

        except Exception as e:
            # 清理临时文件
            if self.temp_dir and self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
            self.download_finished.emit(False, f"安装失败: {str(e)}")

    def _download_file(self):
        """下载文件"""
        if self.temp_dir is None:
            raise Exception("临时目录未初始化")

        response = requests.get(self.url, stream=True)
        response.raise_for_status()

        total_size = int(response.headers.get("content-length", 0))
        downloaded_size = 0

        downloaded_file = self.temp_dir / f"{self.target_name}.zip"
        with open(downloaded_file, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded_size += len(chunk)
                    if total_size > 0:
                        progress = int((downloaded_size / total_size) * 100)
                        self.progress_updated.emit(progress)

        return downloaded_file

    def _extract_file(self, file_path):
        """解压文件"""
        if self.temp_dir is None:
            raise Exception("临时目录未初始化")

        extract_dir = self.temp_dir / "extracted"
        extract_dir.mkdir(exist_ok=True)

        with zipfile.ZipFile(file_path, "r") as zip_ref:
            zip_ref.extractall(extract_dir)

        return extract_dir

    def _install_to_permanent_location(self, extracted_dir):
        """安装到永久位置"""
        # 确定安装目录
        if platform.system() == "Windows":
            install_dir = (
                Path.home() / "AppData" / "Local" / "Programs" / self.target_name
            )
        else:
            install_dir = Path.home() / ".local" / "bin" / self.target_name

        # 创建安装目录
        install_dir.mkdir(parents=True, exist_ok=True)

        # 复制文件
        if extracted_dir.exists():
            for item in extracted_dir.iterdir():
                if item.is_dir():
                    shutil.copytree(item, install_dir / item.name, dirs_exist_ok=True)
                else:
                    shutil.copy2(item, install_dir)

        return install_dir

    def _configure_path(self, permanent_dir):
        """配置PATH环境变量"""
        if platform.system() == "Windows":
            self._configure_windows_path(permanent_dir)
        else:
            self._configure_unix_path(permanent_dir)

    def _configure_windows_path(self, permanent_dir):
        """配置Windows PATH"""
        try:
            import winreg

            # 获取当前用户的PATH
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                "Environment",
                0,
                winreg.KEY_READ | winreg.KEY_WRITE,
            )
            current_path = winreg.QueryValueEx(key, "Path")[0]

            # 检查是否已经在PATH中
            path_to_add = str(permanent_dir)
            if path_to_add not in current_path:
                # 添加到PATH
                new_path = current_path + ";" + path_to_add
                winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, new_path)
                winreg.CloseKey(key)

                # 刷新环境变量
                self._refresh_environment_variables()

        except Exception as e:
            print(f"配置Windows PATH失败: {e}")

    def _configure_unix_path(self, permanent_dir):
        """配置Unix PATH"""
        try:
            # 获取shell配置文件
            rc_file = self._get_shell_rc_file()
            if not rc_file:
                return

            # 检查是否已经在PATH中
            path_to_add = str(permanent_dir)
            with open(rc_file, "r") as f:
                content = f.read()

            if path_to_add not in content:
                # 添加到PATH
                export_line = f'\nexport PATH="$PATH:{path_to_add}"\n'
                with open(rc_file, "a") as f:
                    f.write(export_line)

                # 刷新当前进程的环境变量
                self._refresh_environment_variables()

        except Exception as e:
            print(f"配置Unix PATH失败: {e}")

    def _refresh_environment_variables(self):
        """刷新环境变量"""
        try:
            if platform.system() == "Windows":
                # Windows: 通知系统环境变量已更改
                import ctypes

                ctypes.windll.user32.SendMessageW(0xFFFF, 0x001A, 0, 0)
            else:
                # Unix: 重新加载shell配置
                os.environ["PATH"] = (
                    subprocess.check_output(["bash", "-c", "echo $PATH"])
                    .decode()
                    .strip()
                )
        except Exception as e:
            print(f"刷新环境变量失败: {e}")

    def _get_shell_rc_file(self):
        """获取shell配置文件路径"""
        home = Path.home()
        shell = os.environ.get("SHELL", "")

        if "bash" in shell:
            return home / ".bashrc"
        elif "zsh" in shell:
            return home / ".zshrc"
        elif "fish" in shell:
            return home / ".config" / "fish" / "config.fish"
        else:
            # 默认使用bash
            return home / ".bashrc"

    def _find_bin_directory(self, base_dir: Path):
        """查找bin目录"""
        for item in base_dir.rglob("bin"):
            if item.is_dir():
                return item
        return None

    def _save_installation_info(self, permanent_dir):
        """保存安装信息"""
        info = {
            "install_dir": str(permanent_dir),
            "install_time": datetime.datetime.now().isoformat(),
            "version": "1.0.0",
        }

        info_file = permanent_dir / "install_info.json"
        with open(info_file, "w") as f:
            json.dump(info, f, indent=2)


class SmartDownloadDialog(QDialog):
    """智能下载对话框"""

    def __init__(self, url, target_name, parent=None):
        super().__init__(parent)
        self.url = url
        self.target_name = target_name
        self.setup_ui()

    def setup_ui(self):
        """设置UI"""
        self.setWindowTitle(f"下载 {self.target_name}")
        self.setFixedSize(400, 200)

        layout = QVBoxLayout(self)

        # 状态标签
        self.status_label = QLabel("准备下载...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        layout.addWidget(self.progress_bar)

        # 开始下载
        self.start_download()

    def start_download(self):
        """开始下载"""
        self.download_manager = SmartDownloadManager(self.url, self.target_name)
        self.download_manager.progress_updated.connect(self.progress_bar.setValue)
        self.download_manager.status_updated.connect(self.status_label.setText)
        self.download_manager.download_finished.connect(self.on_download_finished)
        self.download_manager.start()

    def on_download_finished(self, success, message):
        """下载完成回调"""
        if success:
            QMessageBox.information(self, "下载完成", message)
        else:
            QMessageBox.critical(self, "下载失败", message)
        self.accept()


class CustomDownloadDialog(QDialog):
    """自定义下载对话框"""

    def __init__(self, title, message, parent=None):
        super().__init__(parent)
        self.clicked_button = None
        self.setup_ui(title, message)

    def setup_ui(self, title, message):
        """设置UI"""
        self.setWindowTitle(title)
        self.setFixedSize(400, 200)

        layout = QVBoxLayout(self)

        # 消息标签
        message_label = QLabel(message)
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message_label.setWordWrap(True)
        layout.addWidget(message_label)

        # 按钮布局
        button_layout = QHBoxLayout()

        # 自动下载按钮
        auto_btn = QPushButton("自动下载")
        auto_btn.clicked.connect(lambda: self.button_clicked("auto"))
        button_layout.addWidget(auto_btn)

        # 手动下载按钮
        manual_btn = QPushButton("手动下载")
        manual_btn.clicked.connect(lambda: self.button_clicked("manual"))
        button_layout.addWidget(manual_btn)

        # 取消按钮
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(lambda: self.button_clicked("cancel"))
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

    def button_clicked(self, button_type):
        """按钮点击事件"""
        self.clicked_button = button_type
        self.accept()

    def get_clicked_button(self):
        """获取点击的按钮"""
        return self.clicked_button


class CustomResultDialog(QDialog):
    """自定义结果对话框"""

    def __init__(self, title, message, parent=None):
        super().__init__(parent)
        self.setup_ui(title, message)

    def setup_ui(self, title, message):
        """设置UI"""
        self.setWindowTitle(title)
        self.setFixedSize(400, 200)

        layout = QVBoxLayout(self)

        # 消息标签
        message_label = QLabel(message)
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message_label.setWordWrap(True)
        layout.addWidget(message_label)

        # 确定按钮
        ok_btn = QPushButton("确定")
        ok_btn.clicked.connect(self.accept)
        layout.addWidget(ok_btn)


class EnvironmentDetector(QThread):
    """环境检测器"""

    python_detected = Signal(bool, str, str)  # found, path, version
    ffmpeg_detected = Signal(bool, str, str)  # found, path, version
    detection_finished = Signal()

    def __init__(self):
        super().__init__()
        self.python_path = ""
        self.ffmpeg_path = ""
        self.detect_python_only = False
        self.detect_ffmpeg_only = False

    def run(self):
        """运行检测"""
        if self.detect_python_only:
            self.auto_detect_python()
        elif self.detect_ffmpeg_only:
            self.auto_detect_ffmpeg()
        else:
            # 默认检测两个
            self.auto_detect_python()
            self.auto_detect_ffmpeg()
        self.detection_finished.emit()

    def auto_detect_python(self):
        """自动检测Python"""
        try:
            # 检查系统PATH中的Python
            result = subprocess.run(
                ["python", "--version"], capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                version = result.stdout.strip() or result.stderr.strip()
                # 获取python命令的完整路径
                python_path = shutil.which("python")
                if python_path:
                    # 强制转换为小写扩展名
                    normalized_path = self._normalize_path(python_path)
                    self.python_detected.emit(True, normalized_path, version)
                else:
                    self.python_detected.emit(True, "python", version)
                return

            # 检查python3
            result = subprocess.run(
                ["python3", "--version"], capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                version = result.stdout.strip() or result.stderr.strip()
                # 获取python3命令的完整路径
                python_path = shutil.which("python3")
                if python_path:
                    # 强制转换为小写扩展名
                    normalized_path = self._normalize_path(python_path)
                    self.python_detected.emit(True, normalized_path, version)
                else:
                    self.python_detected.emit(True, "python3", version)
                return

            # 检查py命令（Windows）
            if platform.system() == "Windows":
                result = subprocess.run(
                    ["py", "--version"], capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    version = result.stdout.strip() or result.stderr.strip()
                    # 获取py命令的完整路径
                    python_path = shutil.which("py")
                    if python_path:
                        # 强制转换为小写扩展名
                        normalized_path = self._normalize_path(python_path)
                        self.python_detected.emit(True, normalized_path, version)
                    else:
                        self.python_detected.emit(True, "py", version)
                    return

            # 检查常见安装路径
            common_paths = []
            if platform.system() == "Windows":
                common_paths = [
                    r"C:\Python311\python.exe",
                    r"C:\Python310\python.exe",
                    r"C:\Python39\python.exe",
                    r"C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311\python.exe",
                    r"C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python310\python.exe",
                    r"C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python39\python.exe",
                ]
            else:
                common_paths = [
                    "/usr/bin/python3",
                    "/usr/local/bin/python3",
                    "/opt/homebrew/bin/python3",
                ]

            for path in common_paths:
                if platform.system() == "Windows":
                    path = os.path.expandvars(path)
                if os.path.exists(path):
                    try:
                        result = subprocess.run(
                            [path, "--version"],
                            capture_output=True,
                            text=True,
                            timeout=5,
                        )
                        if result.returncode == 0:
                            version = result.stdout.strip() or result.stderr.strip()
                            # 强制转换为小写扩展名
                            normalized_path = self._normalize_path(path)
                            self.python_detected.emit(True, normalized_path, version)
                            return
                    except:
                        pass

            self.python_detected.emit(False, "未找到Python", "")

        except Exception as e:
            self.python_detected.emit(False, f"检测失败: {str(e)}", "")

    def auto_detect_ffmpeg(self):
        """自动检测FFmpeg"""
        try:
            # 检查系统PATH中的FFmpeg
            result = subprocess.run(
                ["ffmpeg", "-version"], capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                # 提取版本信息
                version_line = result.stdout.split("\n")[0] if result.stdout else ""
                # 获取ffmpeg命令的完整路径
                ffmpeg_path = shutil.which("ffmpeg")
                if ffmpeg_path:
                    # 强制转换为小写扩展名
                    normalized_path = self._normalize_path(ffmpeg_path)
                    self.ffmpeg_detected.emit(True, normalized_path, version_line)
                else:
                    self.ffmpeg_detected.emit(True, "ffmpeg", version_line)
                return

            # 检查常见安装路径
            common_paths = []
            if platform.system() == "Windows":
                common_paths = [
                    r"C:\ffmpeg\bin\ffmpeg.exe",
                    r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
                    r"C:\Program Files (x86)\ffmpeg\bin\ffmpeg.exe",
                ]
            else:
                common_paths = [
                    "/usr/bin/ffmpeg",
                    "/usr/local/bin/ffmpeg",
                    "/opt/homebrew/bin/ffmpeg",
                ]

            for path in common_paths:
                if platform.system() == "Windows":
                    path = os.path.expandvars(path)
                if os.path.exists(path):
                    try:
                        result = subprocess.run(
                            [path, "-version"],
                            capture_output=True,
                            text=True,
                            timeout=5,
                        )
                        if result.returncode == 0:
                            version_line = (
                                result.stdout.split("\n")[0] if result.stdout else ""
                            )
                            # 强制转换为小写扩展名
                            normalized_path = self._normalize_path(path)
                            self.ffmpeg_detected.emit(
                                True, normalized_path, version_line
                            )
                            return
                    except:
                        pass

            self.ffmpeg_detected.emit(False, "未找到FFmpeg", "")

        except Exception as e:
            self.ffmpeg_detected.emit(False, f"检测失败: {str(e)}", "")

    def _normalize_path(self, path):
        """标准化路径，确保扩展名为小写"""
        normalized = os.path.normpath(path)
        # 在Windows上强制转换为小写扩展名
        if platform.system() == "Windows" and normalized.lower().endswith(".exe"):
            # 确保扩展名为小写
            base_path = normalized[:-4]  # 移除.EXE
            return base_path + ".exe"
        return normalized


class EnvironmentPage(QWidget):
    """环境检测页面"""

    def __init__(self):
        super().__init__()
        self.detector = EnvironmentDetector()
        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        """设置UI"""
        # 设置背景色
        self.setStyleSheet("""
            QWidget {
                background-color: #fafbfc;
            }
        """)

        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(0)

        # 页面标题
        title = QLabel("环境检测")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setWeight(QFont.Weight.Bold)
        title.setFont(title_font)
        title.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                background: transparent;
                margin-bottom: 10px;
            }
        """)
        main_layout.addWidget(title)

        # 副标题
        subtitle = QLabel("检测并配置Python和FFmpeg环境")
        subtitle.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                font-size: 14px;
                background: transparent;
                margin-bottom: 20px;
            }
        """)
        main_layout.addWidget(subtitle)

        # 创建内容区域
        self.create_content_area(main_layout)

    def create_content_area(self, layout):
        """创建内容区域"""
        # 使用滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #f1f3f4;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background-color: #c1c5c8;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #a8acaf;
            }
        """)

        # 创建内容容器
        content_widget = QWidget()
        content_widget.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 8px;
            }
        """)
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(25)

        # 创建Python检测组
        self.create_python_group(content_layout)

        # 创建FFmpeg检测组
        self.create_ffmpeg_group(content_layout)

        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)

    def create_python_group(self, layout):
        """创建Python检测组"""
        group = QGroupBox("Python 检测")
        group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: 600;
                color: #2c3e50;
                border: 1px solid #e1e5e9;
                border-radius: 8px;
                margin-top: 10px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
                background-color: white;
            }
        """)

        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        form_layout.setContentsMargins(20, 25, 20, 20)

        # Python路径输入框
        self.python_path_edit = QLineEdit()
        self.python_path_edit.setPlaceholderText("Python可执行文件路径")
        self.python_path_edit.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.python_path_edit.setEnabled(True)
        self.python_path_edit.setReadOnly(True)
        self.python_path_edit.setAcceptDrops(False)
        self.python_path_edit.setStyleSheet("""
            QLineEdit {
                padding: 8px 12px;
                border: 1px solid #ced4da;
                border-radius: 6px;
                font-size: 13px;
                background-color: #f8f9fa;
                min-height: 20px;
                color: #495057;
            }
            QLineEdit:hover {
                border-color: #adb5bd;
            }
            QLineEdit:enabled {
                background-color: #f8f9fa;
            }
            QLineEdit:disabled {
                background-color: #e9ecef;
                color: #6c757d;
            }
        """)

        # 创建标签
        python_label = QLabel("Python路径")
        python_label.setStyleSheet("""
            QLabel {
                color: #495057;
                font-size: 13px;
                background: transparent;
            }
        """)
        form_layout.addRow(python_label, self.python_path_edit)

        # 创建按钮布局
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        # 自动检测按钮
        self.auto_detect_python_btn = AnimatedButton("自动检测")
        button_layout.addWidget(self.auto_detect_python_btn)

        # 浏览按钮
        browse_btn = AnimatedButton("浏览")
        browse_btn.setSecondaryStyle()
        browse_btn.clicked.connect(self.browse_python_path)
        button_layout.addWidget(browse_btn)

        # 添加按钮到表单
        button_label = QLabel("操作")
        button_label.setStyleSheet("""
            QLabel {
                color: #495057;
                font-size: 13px;
                background: transparent;
            }
        """)
        form_layout.addRow(button_label, button_layout)

        # Python状态标签
        self.python_status_label = QLabel("等待检测...")
        self.python_status_label.setStyleSheet("""
            QLabel {
                color: #6c757d;
                font-size: 12px;
                border: none; 
                padding: 0; 
                margin: 0;
            }
        """)
        status_label = QLabel("状态")
        status_label.setStyleSheet("""
            QLabel {
                color: #495057;
                font-size: 13px;
                background: transparent;
            }
        """)
        form_layout.addRow(status_label, self.python_status_label)

        group.setLayout(form_layout)
        layout.addWidget(group)

    def create_ffmpeg_group(self, layout):
        """创建FFmpeg检测组"""
        group = QGroupBox("FFmpeg 检测")
        group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: 600;
                color: #2c3e50;
                border: 1px solid #e1e5e9;
                border-radius: 8px;
                margin-top: 10px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
                background-color: white;
            }
        """)

        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        form_layout.setContentsMargins(20, 25, 20, 20)

        # FFmpeg路径输入框
        self.ffmpeg_path_edit = QLineEdit()
        self.ffmpeg_path_edit.setPlaceholderText("FFmpeg可执行文件路径")
        self.ffmpeg_path_edit.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.ffmpeg_path_edit.setEnabled(True)
        self.ffmpeg_path_edit.setReadOnly(True)
        self.ffmpeg_path_edit.setAcceptDrops(False)
        self.ffmpeg_path_edit.setStyleSheet("""
            QLineEdit {
                padding: 8px 12px;
                border: 1px solid #ced4da;
                border-radius: 6px;
                font-size: 13px;
                background-color: #f8f9fa;
                min-height: 20px;
                color: #495057;
            }
            QLineEdit:hover {
                border-color: #adb5bd;
            }
            QLineEdit:enabled {
                background-color: #f8f9fa;
            }
            QLineEdit:disabled {
                background-color: #e9ecef;
                color: #6c757d;
            }
        """)

        # 创建标签
        ffmpeg_label = QLabel("FFmpeg路径:")
        ffmpeg_label.setStyleSheet("""
            QLabel {
                color: #495057;
                font-size: 13px;
                background: transparent;
            }
        """)
        form_layout.addRow(ffmpeg_label, self.ffmpeg_path_edit)

        # 创建按钮布局
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        # 自动检测按钮
        self.auto_detect_ffmpeg_btn = AnimatedButton("自动检测")
        button_layout.addWidget(self.auto_detect_ffmpeg_btn)

        # 浏览按钮
        browse_btn = AnimatedButton("浏览")
        browse_btn.setSecondaryStyle()
        browse_btn.clicked.connect(self.browse_ffmpeg_path)
        button_layout.addWidget(browse_btn)

        # 添加按钮到表单
        button_label = QLabel("操作:")
        button_label.setStyleSheet("""
            QLabel {
                color: #495057;
                font-size: 13px;
                background: transparent;
            }
        """)
        form_layout.addRow(button_label, button_layout)

        # FFmpeg状态标签
        self.ffmpeg_status_label = QLabel("等待检测...")
        self.ffmpeg_status_label.setStyleSheet("""
            QLabel {
                color: #6c757d;
                font-size: 12px;
                border: none; 
                padding: 0; 
                margin: 0;
            }
        """)
        status_label = QLabel("状态:")
        status_label.setStyleSheet("""
            QLabel {
                color: #495057;
                font-size: 13px;
                background: transparent;
            }
        """)
        form_layout.addRow(status_label, self.ffmpeg_status_label)

        group.setLayout(form_layout)
        layout.addWidget(group)

    def setup_connections(self):
        """设置信号连接"""
        self.auto_detect_python_btn.clicked.connect(self.auto_detect_python)
        self.auto_detect_ffmpeg_btn.clicked.connect(self.auto_detect_ffmpeg)
        self.detector.python_detected.connect(self.on_python_detected)
        self.detector.ffmpeg_detected.connect(self.on_ffmpeg_detected)
        self.detector.detection_finished.connect(self.on_detection_finished)

    def showEvent(self, event):
        """页面显示事件"""
        super().showEvent(event)

    def start_detection(self):
        """开始检测"""
        self.detector.python_path = self.python_path_edit.text().strip()
        self.detector.ffmpeg_path = self.ffmpeg_path_edit.text().strip()
        self.detector.start()

    def on_python_detected(self, found, path, version):
        """Python检测结果"""
        if found:
            self.python_path_edit.setText(path)
            self.python_status_label.setText(f"✅ 检测成功 ({version})")
            self.python_status_label.setStyleSheet("""
                QLabel {
                    color: #28a745;
                    font-size: 12px;
                    border: none; padding: 0; margin: 0;
                }
            """)
        else:
            self.python_status_label.setText(f"❌ 检测失败 ({version})")
            self.python_status_label.setStyleSheet("""
                QLabel {
                    color: #dc3545;
                    font-size: 12px;
                    border: none; padding: 0; margin: 0;
                }
            """)

    def show_python_download_dialog(self):
        """显示Python下载对话框"""
        dialog = CustomDownloadDialog(
            "Python未安装", "检测到Python未安装，是否要下载并安装Python？", self
        )
        dialog.exec()

        if dialog.get_clicked_button() == "auto":
            self.download_python_3_11()
        elif dialog.get_clicked_button() == "manual":
            webbrowser.open("https://www.python.org/downloads/")

    def download_python_3_11(self):
        """下载Python 3.11"""
        if platform.system() == "Windows":
            url = "https://www.python.org/ftp/python/3.11.0/python-3.11.0-amd64.exe"
        else:
            url = "https://www.python.org/ftp/python/3.11.0/Python-3.11.0.tgz"

        dialog = SmartDownloadDialog(url, "Python", self)
        dialog.exec()

    def on_ffmpeg_detected(self, found, path, version):
        """FFmpeg检测结果"""
        if found:
            self.ffmpeg_path_edit.setText(path)
            self.ffmpeg_status_label.setText(f"✅ 检测成功 ({version})")
            self.ffmpeg_status_label.setStyleSheet("""
                QLabel {
                    color: #28a745;
                    font-size: 12px;
                    border: none; 
                    padding: 0; 
                    margin: 0;
                }
            """)
        else:
            self.ffmpeg_status_label.setText(f"❌ 检测失败 ({version})")
            self.ffmpeg_status_label.setStyleSheet("""
                QLabel {
                    color: #dc3545;
                    font-size: 12px;
                    border: none; 
                    padding: 0; 
                    margin: 0;
                }
            """)
            # 显示下载对话框
            self.show_ffmpeg_download_dialog()

    def check_and_add_ffmpeg_to_path(self, ffmpeg_path: str):
        """检查并添加FFmpeg到PATH"""
        try:
            # 检查FFmpeg是否在PATH中
            result = subprocess.run(
                ["ffmpeg", "-version"], capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                return True

            # 如果不在PATH中，尝试添加到PATH
            ffmpeg_dir = str(Path(ffmpeg_path).parent)
            if platform.system() == "Windows":
                self._add_ffmpeg_to_windows_path(ffmpeg_dir)
            else:
                self._add_ffmpeg_to_unix_path(ffmpeg_dir)

            return True

        except Exception as e:
            print(f"添加FFmpeg到PATH失败: {e}")
            return False

    def _add_ffmpeg_to_windows_path(self, ffmpeg_dir: str):
        """添加FFmpeg到Windows PATH"""
        try:
            import winreg

            # 获取当前用户的PATH
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                "Environment",
                0,
                winreg.KEY_READ | winreg.KEY_WRITE,
            )
            current_path = winreg.QueryValueEx(key, "Path")[0]

            # 检查是否已经在PATH中
            if ffmpeg_dir not in current_path:
                # 添加到PATH
                new_path = current_path + ";" + ffmpeg_dir
                winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, new_path)
                winreg.CloseKey(key)

                # 刷新环境变量
                self._refresh_current_process_environment()

        except Exception as e:
            print(f"添加FFmpeg到Windows PATH失败: {e}")

    def _add_ffmpeg_to_unix_path(self, ffmpeg_dir: str):
        """添加FFmpeg到Unix PATH"""
        try:
            # 获取shell配置文件
            rc_file = self._get_shell_rc_file()
            if not rc_file:
                return

            # 检查是否已经在PATH中
            with open(rc_file, "r") as f:
                content = f.read()

            if ffmpeg_dir not in content:
                # 添加到PATH
                export_line = f'\nexport PATH="$PATH:{ffmpeg_dir}"\n'
                with open(rc_file, "a") as f:
                    f.write(export_line)

                # 刷新当前进程的环境变量
                self._refresh_current_process_environment()

        except Exception as e:
            print(f"添加FFmpeg到Unix PATH失败: {e}")

    def _get_shell_rc_file(self):
        """获取shell配置文件路径"""
        home = Path.home()
        shell = os.environ.get("SHELL", "")

        if "bash" in shell:
            return home / ".bashrc"
        elif "zsh" in shell:
            return home / ".zshrc"
        elif "fish" in shell:
            return home / ".config" / "fish" / "config.fish"
        else:
            # 默认使用bash
            return home / ".bashrc"

    def _refresh_current_process_environment(self):
        """刷新当前进程的环境变量"""
        try:
            if platform.system() == "Windows":
                # Windows: 通知系统环境变量已更改
                import ctypes

                ctypes.windll.user32.SendMessageW(0xFFFF, 0x001A, 0, 0)
            else:
                # Unix: 重新加载shell配置
                os.environ["PATH"] = (
                    subprocess.check_output(["bash", "-c", "echo $PATH"])
                    .decode()
                    .strip()
                )
        except Exception as e:
            print(f"刷新环境变量失败: {e}")

    def show_ffmpeg_download_dialog(self):
        """显示FFmpeg下载对话框"""
        dialog = FFmpegDownloadDialog(self)
        result = dialog.exec()

        # 如果用户完成了下载，重新检测FFmpeg
        if result == QDialog.DialogCode.Accepted:
            QTimer.singleShot(1000, self.auto_detect_ffmpeg)

    def download_ffmpeg(self):
        """下载FFmpeg"""
        if platform.system() == "Windows":
            url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
        else:
            url = "https://evermeet.cx/ffmpeg/getrelease/zip"

        dialog = SmartDownloadDialog(url, "FFmpeg", self)
        dialog.exec()

    def browse_python_path(self):
        """浏览Python路径"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择Python可执行文件", "", "Python Files (*.exe);;All Files (*)"
        )
        if file_path:
            # 标准化路径，确保扩展名显示为小写
            normalized_path = self._normalize_path(file_path)
            self.python_path_edit.setText(normalized_path)
            # 立即验证文件是否有效
            self.detect_selected_python(normalized_path)

    def browse_ffmpeg_path(self):
        """浏览FFmpeg路径"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择FFmpeg可执行文件", "", "FFmpeg Files (*.exe);;All Files (*)"
        )
        if file_path:
            # 标准化路径，确保扩展名显示为小写
            normalized_path = self._normalize_path(file_path)
            self.ffmpeg_path_edit.setText(normalized_path)
            # 立即验证文件是否有效
            self.detect_selected_ffmpeg(normalized_path)

    def detect_selected_python(self, file_path: str):
        """检测选中的Python文件"""
        try:
            # 首先检查文件是否存在
            if not os.path.exists(file_path):
                self.on_python_detected(False, "文件不存在", "")
                return

            # 检查文件是否可执行
            if not os.access(file_path, os.X_OK):
                self.on_python_detected(False, "文件不可执行", "")
                return

            # 尝试运行Python文件获取版本信息
            result = subprocess.run(
                [file_path, "--version"], capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                version = result.stdout.strip() or result.stderr.strip()
                self.on_python_detected(True, file_path, version)
            else:
                self.on_python_detected(False, "无效的Python文件", "")
        except subprocess.TimeoutExpired:
            self.on_python_detected(False, "文件执行超时", "")
        except Exception as e:
            self.on_python_detected(False, f"检测失败: {str(e)}", "")

    def detect_selected_ffmpeg(self, file_path: str):
        """检测选中的FFmpeg文件"""
        try:
            # 首先检查文件是否存在
            if not os.path.exists(file_path):
                self.on_ffmpeg_detected(False, "文件不存在", "")
                return

            # 检查文件是否可执行
            if not os.access(file_path, os.X_OK):
                self.on_ffmpeg_detected(False, "文件不可执行", "")
                return

            # 尝试运行FFmpeg文件获取版本信息
            result = subprocess.run(
                [file_path, "-version"], capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                version = result.stdout.strip() or result.stderr.strip()
                self.on_ffmpeg_detected(True, file_path, version)
            else:
                self.on_ffmpeg_detected(False, "无效的FFmpeg文件", "")
        except subprocess.TimeoutExpired:
            self.on_ffmpeg_detected(False, "文件执行超时", "")
        except Exception as e:
            self.on_ffmpeg_detected(False, f"检测失败: {str(e)}", "")

    def on_detection_finished(self):
        """检测完成"""
        pass

    def auto_detect_python(self):
        """自动检测Python"""
        self.detector.detect_python_only = True
        self.detector.detect_ffmpeg_only = False
        self.detector.start()

    def auto_detect_ffmpeg(self):
        """自动检测FFmpeg"""
        self.detector.detect_python_only = False
        self.detector.detect_ffmpeg_only = True
        self.detector.start()

    def _normalize_path(self, path):
        """标准化路径，确保扩展名为小写"""
        normalized = os.path.normpath(path)
        # 在Windows上强制转换为小写扩展名
        if platform.system() == "Windows" and normalized.lower().endswith(".exe"):
            # 确保扩展名为小写
            base_path = normalized[:-4]  # 移除.EXE
            return base_path + ".exe"
        return normalized


class FFmpegDownloadDialog(QDialog):
    """FFmpeg下载对话框 - 简化版本"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.download_manager = None
        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        """设置UI - 简化版本"""
        self.setWindowTitle("FFmpeg安装")
        self.setFixedSize(400, 300)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowCloseButtonHint)
        self.setModal(True)

        # 设置背景
        self.setStyleSheet("""
            QDialog {
                background-color: white;
                border: 1px solid #e1e5e9;
                border-radius: 0px;
            }
        """)

        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 25, 30, 25)
        main_layout.setSpacing(20)

        # 图标和标题
        icon_layout = QHBoxLayout()

        # 图标容器 - 添加背景和边框效果
        icon_container = QWidget()
        icon_container.setFixedSize(50, 50)
        icon_container.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border: 2px solid #e9ecef;
                border-radius: 8px;
            }
        """)
        icon_container_layout = QVBoxLayout(icon_container)
        icon_container_layout.setContentsMargins(8, 8, 8, 8)

        icon_label = QLabel("🎬")
        icon_label.setStyleSheet("""
            font-size: 24px;
            background: transparent;
        """)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_container_layout.addWidget(icon_label)

        icon_layout.addWidget(icon_container)

        # 标题区域
        title_container = QWidget()
        title_container.setStyleSheet("""
            QWidget {
                background: transparent;
            }
        """)
        title_layout = QVBoxLayout(title_container)
        title_layout.setContentsMargins(15, 0, 0, 0)
        title_layout.setSpacing(4)

        title_label = QLabel("FFmpeg未检测到")
        title_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #333;
            background: transparent;
        """)
        title_layout.addWidget(title_label)

        # 副标题
        subtitle_label = QLabel("需要安装FFmpeg来处理多媒体文件")
        subtitle_label.setStyleSheet("""
            font-size: 13px;
            color: #6c757d;
            background: transparent;
        """)
        title_layout.addWidget(subtitle_label)

        icon_layout.addWidget(title_container)
        icon_layout.addStretch()
        main_layout.addLayout(icon_layout)

        # 说明文字
        desc_label = QLabel(
            "检测到您的系统中未安装FFmpeg。\n\nFFmpeg是处理音频和视频文件的重要工具，真寻Bot需要它来处理多媒体文件。\n\n是否要自动下载并安装FFmpeg？"
        )
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("""
            color: #666;
            font-size: 14px;
            line-height: 1.5;
            padding: 20px;
            background-color: #f8f9fa;
            border-radius: 6px;
        """)
        main_layout.addWidget(desc_label)

        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)

        # 取消按钮
        self.cancel_button = AnimatedButton("取消")
        self.cancel_button.setSecondaryStyle()
        self.cancel_button.setFixedHeight(40)
        self.cancel_button.clicked.connect(self.reject)

        # 下载按钮
        self.download_button = AnimatedButton("开始下载")
        self.download_button.setFixedHeight(40)
        self.download_button.clicked.connect(self.start_download)

        button_layout.addWidget(self.cancel_button)
        button_layout.addStretch()
        button_layout.addWidget(self.download_button)

        main_layout.addLayout(button_layout)

    def setup_connections(self):
        """设置信号连接"""
        pass

    def start_download(self):
        """开始下载"""
        # 关闭当前对话框
        self.accept()

        # 创建下载进度对话框
        download_dialog = FFmpegDownloadProgressDialog(self.parent())
        download_dialog.exec()


class FFmpegDownloadProgressDialog(QDialog):
    """FFmpeg下载进度对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.download_manager = None
        self.setup_ui()
        self.setup_connections()
        self.start_download()

    def setup_ui(self):
        """设置UI"""
        self.setWindowTitle("FFmpeg下载")
        self.setFixedSize(600, 350)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowCloseButtonHint)
        self.setModal(True)

        # 设置背景
        self.setStyleSheet("""
            QDialog {
                background-color: white;
                border: 1px solid #e1e5e9;
                border-radius: 8px;
            }
        """)

        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 30, 40, 30)
        main_layout.setSpacing(25)

        # 图标和标题
        icon_layout = QHBoxLayout()

        # 图标容器 - 添加背景和边框效果
        icon_container = QWidget()
        icon_container.setFixedSize(50, 50)
        icon_container.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border: 2px solid #e9ecef;
                border-radius: 8px;
            }
        """)
        icon_container_layout = QVBoxLayout(icon_container)
        icon_container_layout.setContentsMargins(8, 8, 8, 8)

        icon_label = QLabel("🎬")
        icon_label.setStyleSheet("""
            font-size: 24px;
            background: transparent;
        """)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_container_layout.addWidget(icon_label)

        icon_layout.addWidget(icon_container)

        # 标题区域
        title_container = QWidget()
        title_container.setStyleSheet("""
            QWidget {
                background: transparent;
            }
        """)
        title_layout = QVBoxLayout(title_container)
        title_layout.setContentsMargins(15, 0, 0, 0)
        title_layout.setSpacing(4)

        title_label = QLabel("正在下载FFmpeg")
        title_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #333;
            background: transparent;
        """)
        title_layout.addWidget(title_label)

        # 副标题
        subtitle_label = QLabel("正在从官方源下载，请稍候...")
        subtitle_label.setStyleSheet("""
            font-size: 13px;
            color: #6c757d;
            background: transparent;
        """)
        title_layout.addWidget(subtitle_label)

        icon_layout.addWidget(title_container)
        icon_layout.addStretch()
        main_layout.addLayout(icon_layout)

        # 状态文字 - 简化为一个框
        self.status_label = QLabel("正在从官方源下载FFmpeg，请稍候...")
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet("""
            color: #495057;
            font-size: 15px;
            line-height: 1.6;
            background-color: #f8f9fa;
            border: 2px solid #dee2e6;
            border-radius: 0px;
            padding: 20px;
            margin: 10px 0px;
        """)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setMinimumHeight(60)
        main_layout.addWidget(self.status_label)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #e1e5e9;
                border-radius: 6px;
                text-align: center;
                font-size: 12px;
                background-color: #f8f9fa;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #007acc;
                border-radius: 5px;
            }
        """)
        main_layout.addWidget(self.progress_bar)

        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)

        # 取消按钮 - 拉满宽度
        self.cancel_button = AnimatedButton("取消")
        self.cancel_button.setSecondaryStyle()
        self.cancel_button.setFixedHeight(45)
        self.cancel_button.clicked.connect(self.cancel_download)

        button_layout.addWidget(self.cancel_button)

        main_layout.addLayout(button_layout)

    def setup_connections(self):
        """设置信号连接"""
        pass

    def start_download(self):
        """开始下载"""
        # 设置下载URL
        if platform.system() == "Windows":
            url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
        else:
            url = "https://evermeet.cx/ffmpeg/getrelease/zip"

        # 创建下载管理器
        self.download_manager = SmartDownloadManager(url, "FFmpeg")
        self.download_manager.progress_updated.connect(self.update_progress)
        self.download_manager.status_updated.connect(self.update_status)
        self.download_manager.download_finished.connect(self.on_download_finished)
        self.download_manager.start()

    def update_progress(self, value):
        """更新进度条"""
        self.progress_bar.setValue(value)

    def update_status(self, status):
        """更新状态"""
        # 根据不同的状态显示不同的信息
        if "下载" in status or "Download" in status:
            self.status_label.setText("正在从官方源下载FFmpeg，请稍候...")
            # self.dynamic_status.setText("正在下载………") # This line was removed as per the edit hint
        elif "解压" in status or "解压" in status:
            self.status_label.setText("正在解压FFmpeg文件，请稍候...")
            # self.dynamic_status.setText("正在解压………") # This line was removed as per the edit hint
        elif "安装" in status or "配置" in status:
            self.status_label.setText("正在安装和配置FFmpeg，请稍候...")
            # self.dynamic_status.setText("正在安装………") # This line was removed as per the edit hint
        else:
            self.status_label.setText("正在从官方源下载FFmpeg，请稍候...")
            # self.dynamic_status.setText("正在下载………") # This line was removed as per the edit hint

    def on_download_finished(self, success, message):
        """下载完成"""
        if success:
            # 创建安装完成对话框
            completion_dialog = FFmpegInstallationCompleteDialog(self)
            completion_dialog.exec()
            self.accept()
        else:
            # 显示错误消息
            QMessageBox.warning(
                self,
                "下载失败",
                f"下载过程中出现错误：{message}\n\n请检查网络连接后重试。",
            )
            self.reject()

    def cancel_download(self):
        """取消下载"""
        if self.download_manager and self.download_manager.isRunning():
            self.download_manager.terminate()
            self.download_manager.wait()
        self.reject()

    def closeEvent(self, event):
        """关闭事件"""
        if self.download_manager and self.download_manager.isRunning():
            self.download_manager.terminate()
            self.download_manager.wait()
        super().closeEvent(event)


class FFmpegInstallationCompleteDialog(QDialog):
    """FFmpeg安装完成对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """设置UI"""
        self.setWindowTitle("安装完成")
        self.setFixedSize(300, 200)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowCloseButtonHint)
        self.setModal(True)

        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # 成功图标和标题
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)

        # 成功图标
        success_icon = QLabel("✅")
        success_icon.setStyleSheet("""
            font-size: 24px;
            background: transparent;
        """)
        header_layout.addWidget(success_icon)

        # 标题
        title_label = QLabel("安装完成")
        title_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            background: transparent;
        """)
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        main_layout.addLayout(header_layout)

        # 状态消息
        status_label = QLabel("FFmpeg 已成功安装并配置到PATH")
        status_label.setStyleSheet("""
            font-size: 12px;
            background: transparent;
        """)
        main_layout.addWidget(status_label)

        # 提示消息
        tip_label = QLabel("请重新启动命令行或IDE以使用新的PATH设置")
        tip_label.setStyleSheet("""
            font-size: 11px;
            color: #666;
            background: transparent;
        """)
        tip_label.setWordWrap(True)
        main_layout.addWidget(tip_label)

        main_layout.addStretch()

        # 确定按钮
        ok_button = AnimatedButton("确定")
        ok_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                font-size: 12px;
                font-weight: bold;
                padding: 6px 12px;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        ok_button.clicked.connect(self.accept)
        main_layout.addWidget(ok_button)
