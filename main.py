import sys
import json
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout,
                             QWidget, QTextEdit, QStatusBar, QHBoxLayout,
                             QSpinBox, QTabWidget, QPushButton, QMessageBox)
from PySide6.QtCore import QTimer
from PySide6.QtCore import Qt, QMimeData
from PySide6.QtGui import QDragEnterEvent, QDropEvent
from typing import Optional
from image_processor import ImageProcessor
from styles import *

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("图片转Base64工具")
        self.setAcceptDrops(True)
        self.resize(800, 600)
        self.processing = False
        self.config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
        self.load_config()
        self.image_processor = ImageProcessor(
            max_size_kb=self.max_size_kb,
            max_image_size=self.max_image_size,
            image_quality=self.image_quality
        )
        self.setup_ui()

    def setup_ui(self):
        self.setStyleSheet(MAIN_WINDOW_STYLE)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # 创建标签页
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet(TAB_WIDGET_STYLE)

        # 创建主要功能标签页
        main_tab = QWidget()
        main_layout = QVBoxLayout(main_tab)
        self.setup_main_tab(main_layout)

        # 创建设置标签页
        settings_tab = QWidget()
        settings_layout = QVBoxLayout(settings_tab)
        self.setup_settings_tab(settings_layout)

        # 添加标签页
        tab_widget.addTab(main_tab, "转换")
        tab_widget.addTab(settings_tab, "设置")
        layout.addWidget(tab_widget)

        # 创建状态栏
        self._statusBar = QStatusBar()
        self.setStatusBar(self._statusBar)
        self._statusBar.setStyleSheet(STATUS_BAR_STYLE)
        self._statusBar.showMessage("准备就绪，等待拖入图片...")

    def setup_main_tab(self, layout):
        # 创建提示标签
        self.label = QLabel("将图片文件拖放到这里")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet(DROP_LABEL_STYLE)
        self.label.setMinimumHeight(150)
        layout.addWidget(self.label)

        # 创建结果文本框
        self.result_text = QTextEdit()
        self.result_text.setPlaceholderText("转换结果将显示在这里")
        self.result_text.setReadOnly(True)
        self.result_text.setMinimumHeight(200)
        self.result_text.setStyleSheet(TEXT_EDIT_STYLE)
        layout.addWidget(self.result_text)

    def setup_settings_tab(self, layout):
        # 文件大小限制设置
        size_limit_container = QHBoxLayout()
        size_limit_label = QLabel("文件大小限制(KB):")
        size_limit_label.setStyleSheet(LABEL_STYLE)
        self.size_limit_input = QSpinBox()
        self.size_limit_input.setRange(1, 1000)
        self.size_limit_input.setValue(self.max_size_kb)
        self.size_limit_input.setSingleStep(1)
        self.size_limit_input.valueChanged.connect(self.update_size_limit)
        self.size_limit_input.setStyleSheet(SPIN_BOX_STYLE)
        size_limit_container.addWidget(size_limit_label)
        size_limit_container.addWidget(self.size_limit_input)
        size_limit_container.addStretch()
        layout.addLayout(size_limit_container)

        # 图片最大尺寸设置
        max_size_container = QHBoxLayout()
        max_size_label = QLabel("图片最大尺寸(像素):")
        max_size_label.setStyleSheet(LABEL_STYLE)
        self.max_size_input = QSpinBox()
        self.max_size_input.setRange(100, 2000)
        self.max_size_input.setValue(self.max_image_size)
        self.max_size_input.setSingleStep(10)
        self.max_size_input.valueChanged.connect(self.update_max_size)
        self.max_size_input.setStyleSheet(SPIN_BOX_STYLE)
        max_size_container.addWidget(max_size_label)
        max_size_container.addWidget(self.max_size_input)
        max_size_container.addStretch()
        layout.addLayout(max_size_container)

        # 图片质量设置
        quality_container = QHBoxLayout()
        quality_label = QLabel("图片质量(1-100):")
        quality_label.setStyleSheet(LABEL_STYLE)
        self.quality_input = QSpinBox()
        self.quality_input.setRange(1, 100)
        self.quality_input.setValue(self.image_quality)
        self.quality_input.setSingleStep(1)
        self.quality_input.valueChanged.connect(self.update_quality)
        self.quality_input.setStyleSheet(SPIN_BOX_STYLE)
        quality_container.addWidget(quality_label)
        quality_container.addWidget(self.quality_input)
        quality_container.addStretch()
        layout.addLayout(quality_container)

        # 添加保存按钮
        save_button = QPushButton("保存设置")
        save_button.setStyleSheet(SAVE_BUTTON_STYLE)
        save_button.clicked.connect(self.save_config)
        layout.addWidget(save_button)
        layout.addStretch()

    def load_config(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.max_size_kb = config.get('max_size_kb', 30)
                    self.max_image_size = config.get('max_image_size', 768)
                    self.image_quality = config.get('image_quality', 95)
            else:
                self.max_size_kb = 30
                self.max_image_size = 768
                self.image_quality = 95
        except Exception as e:
            self._statusBar.showMessage(f"加载配置失败：{str(e)}")
            self.max_size_kb = 30
            self.max_image_size = 768
            self.image_quality = 95

    def save_config(self):
        try:
            config = {
                'max_size_kb': self.size_limit_input.value(),
                'max_image_size': self.max_size_input.value(),
                'image_quality': self.quality_input.value()
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4)
            
            self.image_processor.update_settings(
                max_size_kb=config['max_size_kb'],
                max_image_size=config['max_image_size'],
                image_quality=config['image_quality']
            )
            
            self._statusBar.showMessage("设置已成功保存！")
            self.show_success_message("保存成功", "设置已成功保存！")
            
        except Exception as e:
            self._statusBar.showMessage(f"保存配置失败：{str(e)}")
            self.show_error_message("保存失败", f"保存配置失败：{str(e)}")

    def show_success_message(self, title: str, message: str):
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.setStyleSheet(LABEL_STYLE)
        msg_box.exec_()

    def show_error_message(self, title: str, message: str):
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.setStyleSheet(LABEL_STYLE)
        msg_box.exec_()

    def dragEnterEvent(self, a0: Optional[QDragEnterEvent]):
        assert a0 is not None
        mime_data: Optional[QMimeData] = a0.mimeData()
        if mime_data is not None and mime_data.hasUrls():
            a0.accept()
        else:
            a0.setDropAction(Qt.DropAction.IgnoreAction)

    def update_size_limit(self, value):
        self.max_size_kb = value
        self.image_processor.update_settings(max_size_kb=value)
        self._statusBar.showMessage(f"已更新文件大小限制为: {value}KB")

    def update_max_size(self, value):
        self.max_image_size = value
        self.image_processor.update_settings(max_image_size=value)
        self._statusBar.showMessage(f"已更新图片最大尺寸为: {value}像素")

    def update_quality(self, value):
        self.image_quality = value
        self.image_processor.update_settings(image_quality=value)
        self._statusBar.showMessage(f"已更新图片质量为: {value}")

    def dropEvent(self, a0: QDropEvent) -> None:
        if self.processing:
            return

        mime_data = a0.mimeData()
        if mime_data and mime_data.hasUrls():
            files = [u.toLocalFile() for u in mime_data.urls()]
        else:
            files = []

        for file_path in files:
            try:
                self.processing = True
                self.label.setText("正在处理图片，请稍候...")
                self._statusBar.showMessage("正在处理图片...")
                self.label.setStyleSheet(PROCESSING_LABEL_STYLE)
                QApplication.processEvents()

                base64_str, markdown_str = self.image_processor.process_image(file_path)
                
                self.result_text.setText(markdown_str)
                QApplication.clipboard().setText(markdown_str)
                success_msg = "转换成功！已复制到剪贴板，继续拖放新的图片文件"
                self.label.setText(success_msg)
                self._statusBar.showMessage(success_msg)
                self.label.setStyleSheet(SUCCESS_LABEL_STYLE)

            except Exception as e:
                self.result_text.setText(f"转换失败：{str(e)}")
                error_msg = f"转换失败：{str(e)}"
                self.label.setText("转换失败，请重试")
                self._statusBar.showMessage(error_msg)
                self.label.setStyleSheet(ERROR_LABEL_STYLE)

            finally:
                self.processing = False

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()