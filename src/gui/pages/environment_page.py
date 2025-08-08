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
from src.gui.widgets import (
    show_confirm_dialog,
    show_error_dialog,
    show_info_dialog,
    show_multi_button_dialog,
    show_progress_dialog,
    show_success_dialog,
    show_warning_dialog,
)
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


class SmartDownloadDialog:
    """智能下载对话框 - 使用全局弹窗系统"""

    def __init__(self, url, target_name, parent=None):
        self.url = url
        self.target_name = target_name
        self.parent = parent
        self.download_manager = None
        self.progress_dialog = None

    def exec(self):
        """执行下载"""
        # 创建进度条弹窗
        from src.gui.widgets.global_dialog import ProgressDialog
        self.progress_dialog = ProgressDialog(
            f"下载 {self.target_name}",
            "正在准备下载...",
            self.parent
        )
        
        # 开始下载
        self.start_download()
        
        # 显示进度条弹窗
        self.progress_dialog.exec()

    def start_download(self):
        """开始下载"""
        self.download_manager = SmartDownloadManager(self.url, self.target_name)
        
        # 连接进度信号到进度条
        self.download_manager.progress_updated.connect(self.progress_dialog.set_progress)
        self.download_manager.status_updated.connect(self.progress_dialog.set_status)
        self.download_manager.download_finished.connect(self.on_download_finished)
        
        self.download_manager.start()

    def on_download_finished(self, success, message):
        """下载完成回调"""
        # 关闭进度条弹窗
        if self.progress_dialog:
            self.progress_dialog.close()
        
        if success:
            show_success_dialog("下载完成", message, self.parent)
        else:
            show_error_dialog("下载失败", message, self.parent)





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
        buttons = [
            {"text": "自动下载", "type": "primary"},
            {"text": "手动下载", "type": "info"},
            {"text": "取消", "type": "default"}
        ]
        
        result = show_multi_button_dialog(
            "Python未安装",
            "检测到Python未安装，是否要下载并安装Python？",
            buttons,
            self,
        )

        if result == "自动下载":
            self.download_python_3_11()
        elif result == "手动下载":
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
        buttons = [
            {"text": "开始下载", "type": "primary"},
            {"text": "取消", "type": "default"}
        ]
        
        result = show_multi_button_dialog(
            "FFmpeg未检测到",
            "检测到您的系统中未安装FFmpeg。\n\nFFmpeg是处理音频和视频文件的重要工具，真寻Bot需要它来处理多媒体文件。\n\n是否要自动下载并安装FFmpeg？",
            buttons,
            self,
        )

        # 如果用户选择了下载，开始下载流程
        if result == "开始下载":
            self.start_ffmpeg_download()

    def start_ffmpeg_download(self):
        """开始FFmpeg下载流程"""
        # 设置下载URL
        if platform.system() == "Windows":
            url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
        else:
            url = "https://evermeet.cx/ffmpeg/getrelease/zip"

        # 创建下载进度对话框
        download_dialog = FFmpegDownloadProgressDialog(self)
        download_dialog.exec()
        
        # 下载完成后重新检测FFmpeg
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





class FFmpegDownloadProgressDialog:
    """FFmpeg下载进度对话框 - 使用全局弹窗系统"""

    def __init__(self, parent=None):
        self.parent = parent
        self.download_manager = None
        self.progress_dialog = None

    def exec(self):
        """执行下载"""
        # 创建进度条弹窗
        from src.gui.widgets.global_dialog import ProgressDialog
        self.progress_dialog = ProgressDialog(
            "正在下载FFmpeg",
            "正在从官方源下载FFmpeg，请稍候...",
            self.parent
        )
        
        # 开始下载
        self.start_download()
        
        # 显示进度条弹窗
        self.progress_dialog.exec()

    def start_download(self):
        """开始下载"""
        # 设置下载URL
        if platform.system() == "Windows":
            url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
        else:
            url = "https://evermeet.cx/ffmpeg/getrelease/zip"

        # 创建下载管理器
        self.download_manager = SmartDownloadManager(url, "FFmpeg")
        
        # 连接进度信号到进度条
        self.download_manager.progress_updated.connect(self.progress_dialog.set_progress)
        self.download_manager.status_updated.connect(self.progress_dialog.set_status)
        self.download_manager.download_finished.connect(self.on_download_finished)
        
        self.download_manager.start()

    def on_download_finished(self, success, message):
        """下载完成"""
        # 关闭进度条弹窗
        if self.progress_dialog:
            self.progress_dialog.close()
        
        if success:
            # 显示安装完成对话框
            show_success_dialog(
                "安装完成",
                "FFmpeg 已成功安装并配置到PATH\n\n请重新启动命令行或IDE以使用新的PATH设置",
                self.parent
            )
        else:
            # 显示错误消息
            show_error_dialog(
                "下载失败",
                f"下载过程中出现错误：{message}\n\n请检查网络连接后重试。",
                self.parent
            )



