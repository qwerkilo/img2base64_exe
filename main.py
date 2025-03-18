import sys
import base64
import json
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout,
                             QWidget, QTextEdit, QStatusBar, QFrame, QHBoxLayout,
                             QSpinBox, QTabWidget, QPushButton, QMessageBox)
from PySide6.QtCore import QTimer
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QMimeData
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QPalette, QColor, QFont
from PIL import Image
from io import BytesIO
from typing import Optional

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("图片转Base64工具")
        self.setAcceptDrops(True)
        self.resize(800, 600)
        self.processing = False  # 添加处理状态标志
        self.config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
        self.load_config()  # 加载配置

        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                          stop:0 #f6f7f8, stop:1 #e9ebee);
            }
            QLabel {
                font-family: 'Microsoft YaHei', 'Arial';
                font-size: 14px;
                color: #2c3e50;
            }
            QSpinBox {
                background-color: white;
                border: 1px solid #dcdde1;
                border-radius: 4px;
                padding: 4px;
                font-size: 14px;
                min-width: 80px;
            }
            QTextEdit {
                background-color: white;
                border: 1px solid #dcdde1;
                border-radius: 8px;
                padding: 10px;
                font-family: 'Consolas', 'Courier New';
                font-size: 13px;
                selection-background-color: #74b9ff;
            }
            QStatusBar {
                background-color: #f5f6fa;
                color: #576574;
                font-size: 12px;
            }
        """)

        # 创建主窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # 创建标签页
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #dcdde1;
                border-radius: 8px;
                background-color: white;
            }
            QTabBar::tab {
                background: #f5f6fa;
                border: 1px solid #dcdde1;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 8px 12px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: white;
                border-bottom: none;
                margin-bottom: -1px;
            }
        """)

        # 创建主要功能标签页
        main_tab = QWidget()
        main_layout = QVBoxLayout(main_tab)

        # 创建设置标签页
        settings_tab = QWidget()
        settings_layout = QVBoxLayout(settings_tab)
        
        # 文件大小限制设置
        size_limit_container = QHBoxLayout()
        size_limit_label = QLabel("文件大小限制(KB):")
        self.size_limit_input = QSpinBox()
        self.size_limit_input.setRange(1, 1000)  # 设置范围1KB到1000KB
        self.size_limit_input.setValue(self.max_size_kb)
        self.size_limit_input.valueChanged.connect(self.update_size_limit)
        size_limit_container.addWidget(size_limit_label)
        size_limit_container.addWidget(self.size_limit_input)
        size_limit_container.addStretch()
        settings_layout.addLayout(size_limit_container)

        # 图片最大尺寸设置
        max_size_container = QHBoxLayout()
        max_size_label = QLabel("图片最大尺寸(像素):")
        self.max_size_input = QSpinBox()
        self.max_size_input.setRange(100, 2000)  # 设置范围100到2000像素
        self.max_size_input.setValue(self.max_image_size)  # 使用配置文件中的值
        self.max_size_input.valueChanged.connect(self.update_max_size)
        max_size_container.addWidget(max_size_label)
        max_size_container.addWidget(self.max_size_input)
        max_size_container.addStretch()
        settings_layout.addLayout(max_size_container)

        # 图片质量设置
        quality_container = QHBoxLayout()
        quality_label = QLabel("图片质量(1-100):")
        self.quality_input = QSpinBox()
        self.quality_input.setRange(1, 100)  # 设置范围1到100
        self.quality_input.setValue(self.image_quality)  # 使用配置值
        self.quality_input.valueChanged.connect(self.update_quality)
        quality_container.addWidget(quality_label)
        quality_container.addWidget(self.quality_input)
        quality_container.addStretch()
        settings_layout.addLayout(quality_container)

        # 添加保存按钮
        save_button = QPushButton("保存设置")
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #0984e3;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0878d4;
            }
            QPushButton:pressed {
                background-color: #076ebf;
            }
        """)
        save_button.clicked.connect(self.save_config)
        settings_layout.addWidget(save_button)
        
        settings_layout.addStretch()

        # 创建提示标签
        self.label = QLabel("将图片文件拖放到这里")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("""
            QLabel {
                border: 2px dashed #74b9ff;
                border-radius: 12px;
                padding: 40px;
                background-color: rgba(116, 185, 255, 0.1);
                font-size: 16px;
                font-weight: bold;
            }
            QLabel:hover {
                background-color: rgba(116, 185, 255, 0.2);
                border-color: #0984e3;
            }
        """)
        self.label.setMinimumHeight(150)
        main_layout.addWidget(self.label)

        # 创建结果文本框
        self.result_text = QTextEdit()
        self.result_text.setPlaceholderText("转换结果将显示在这里")
        self.result_text.setReadOnly(True)
        self.result_text.setMinimumHeight(200)
        main_layout.addWidget(self.result_text)

        # 添加标签页
        tab_widget.addTab(main_tab, "转换")
        tab_widget.addTab(settings_tab, "设置")
        layout.addWidget(tab_widget)

        # 创建状态栏
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("准备就绪，等待拖入图片...")

    def load_config(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.max_size_kb = config.get('max_size_kb', 30)
                    self.max_image_size = config.get('max_image_size', 768)
                    self.image_quality = config.get('image_quality', 95)
            else:
                self.max_size_kb = 30  # 默认大小限制
                self.max_image_size = 768
                self.image_quality = 95
        except Exception as e:
            self.statusBar.showMessage(f"加载配置失败：{str(e)}")
            self.max_size_kb = 30
            self.max_image_size = 768
            self.image_quality = 95

    def save_config(self):
        try:
            # 获取当前设置值
            config = {
                'max_size_kb': self.size_limit_input.value(),
                'max_image_size': self.max_size_input.value(),
                'image_quality': self.quality_input.value()
            }
            
            # 保存到配置文件
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4)
            
            # 更新内部变量
            self.max_size_kb = config['max_size_kb']
            self.max_image_size = config['max_image_size']
            self.image_quality = config['image_quality']
            
            # 添加保存成功的视觉反馈
            save_button = self.sender()
            original_style = save_button.styleSheet()
            save_button.setStyleSheet("""
                QPushButton {
                    background-color: #27ae60;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-size: 14px;
                    font-weight: bold;
                }
            """)
            self.statusBar.showMessage("设置已成功保存！")
            
            # 显示成功消息对话框
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setWindowTitle("保存成功")
            msg_box.setText("设置已成功保存！")
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: white;
                }
                QMessageBox QLabel {
                    color: #2c3e50;
                    font-size: 14px;
                    min-width: 200px;
                }
                QPushButton {
                    background-color: #0984e3;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-size: 14px;
                    min-width: 80px;
                }
                QPushButton:hover {
                    background-color: #0878d4;
                }
            """)
            msg_box.exec_()
            
            # 1秒后恢复按钮样式
            QTimer.singleShot(1000, lambda: save_button.setStyleSheet(original_style))
            
        except Exception as e:
            self.statusBar.showMessage(f"保存配置失败：{str(e)}")
            save_button = self.sender()
            save_button.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-size: 14px;
                    font-weight: bold;
                }
            """)



        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                          stop:0 #f6f7f8, stop:1 #e9ebee);
            }
            QLabel {
                font-family: 'Microsoft YaHei', 'Arial';
                font-size: 14px;
                color: #2c3e50;
            }
            QSpinBox {
                background-color: white;
                border: 1px solid #dcdde1;
                border-radius: 4px;
                padding: 4px;
                font-size: 14px;
                min-width: 80px;
            }
            QTextEdit {
                background-color: white;
                border: 1px solid #dcdde1;
                border-radius: 8px;
                padding: 10px;
                font-family: 'Consolas', 'Courier New';
                font-size: 13px;
                selection-background-color: #74b9ff;
            }
            QStatusBar {
                background-color: #f5f6fa;
                color: #576574;
                font-size: 12px;
            }
        """)

        # 创建主窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # 创建标签页
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #dcdde1;
                border-radius: 8px;
                background-color: white;
            }
            QTabBar::tab {
                background: #f5f6fa;
                border: 1px solid #dcdde1;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 8px 12px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: white;
                border-bottom: none;
                margin-bottom: -1px;
            }
        """)

        # 创建主要功能标签页
        main_tab = QWidget()
        main_layout = QVBoxLayout(main_tab)

        # 创建设置标签页
        settings_tab = QWidget()
        settings_layout = QVBoxLayout(settings_tab)
        
        # 文件大小限制设置
        size_limit_container = QHBoxLayout()
        size_limit_label = QLabel("文件大小限制(KB):")
        self.size_limit_input = QSpinBox()
        self.size_limit_input.setRange(1, 1000)  # 设置范围1KB到1000KB
        self.size_limit_input.setValue(self.max_size_kb)
        self.size_limit_input.valueChanged.connect(self.update_size_limit)
        size_limit_container.addWidget(size_limit_label)
        size_limit_container.addWidget(self.size_limit_input)
        size_limit_container.addStretch()
        settings_layout.addLayout(size_limit_container)

        # 图片最大尺寸设置
        max_size_container = QHBoxLayout()
        max_size_label = QLabel("图片最大尺寸(像素):")
        self.max_size_input = QSpinBox()
        self.max_size_input.setRange(100, 2000)  # 设置范围100到2000像素
        self.max_size_input.setValue(self.max_image_size)  # 使用配置文件中的值
        self.max_size_input.valueChanged.connect(self.update_max_size)
        max_size_container.addWidget(max_size_label)
        max_size_container.addWidget(self.max_size_input)
        max_size_container.addStretch()
        settings_layout.addLayout(max_size_container)

        # 图片质量设置
        quality_container = QHBoxLayout()
        quality_label = QLabel("图片质量(1-100):")
        self.quality_input = QSpinBox()
        self.quality_input.setRange(1, 100)  # 设置范围1到100
        self.quality_input.setValue(self.image_quality)  # 使用配置值
        self.quality_input.valueChanged.connect(self.update_quality)
        quality_container.addWidget(quality_label)
        quality_container.addWidget(self.quality_input)
        quality_container.addStretch()
        settings_layout.addLayout(quality_container)

        # 添加保存按钮
        save_button = QPushButton("保存设置")
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #0984e3;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0878d4;
            }
            QPushButton:pressed {
                background-color: #076ebf;
            }
        """)
        save_button.clicked.connect(self.save_config)
        settings_layout.addWidget(save_button)
        
        settings_layout.addStretch()

        # 创建提示标签
        self.label = QLabel("将图片文件拖放到这里")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("""
            QLabel {
                border: 2px dashed #74b9ff;
                border-radius: 12px;
                padding: 40px;
                background-color: rgba(116, 185, 255, 0.1);
                font-size: 16px;
                font-weight: bold;
            }
            QLabel:hover {
                background-color: rgba(116, 185, 255, 0.2);
                border-color: #0984e3;
            }
        """)
        self.label.setMinimumHeight(150)
        main_layout.addWidget(self.label)

        # 创建结果文本框
        self.result_text = QTextEdit()
        self.result_text.setPlaceholderText("转换结果将显示在这里")
        self.result_text.setReadOnly(True)
        self.result_text.setMinimumHeight(200)
        main_layout.addWidget(self.result_text)

        # 添加标签页
        tab_widget.addTab(main_tab, "转换")
        tab_widget.addTab(settings_tab, "设置")
        layout.addWidget(tab_widget)

        # 创建状态栏
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("准备就绪，等待拖入图片...")

    
    def dragEnterEvent(self, a0: Optional[QDragEnterEvent]):
        assert a0 is not None
        mime_data: Optional[QMimeData] = a0.mimeData()  # type: ignore
        if mime_data is not None and mime_data.hasUrls():
            a0.accept()
        else:
            a0.setDropAction(Qt.IgnoreAction)

    def update_size_limit(self, value):
        self.max_size_kb = value
        self.statusBar.showMessage(f"已更新文件大小限制为: {value}KB")

    def update_max_size(self, value):
        self.max_image_size = value
        self.statusBar.showMessage(f"已更新图片最大尺寸为: {value}像素")

    def update_quality(self, value):
        self.statusBar.showMessage(f"已更新图片质量为: {value}")

    def dropEvent(self, a0: QDropEvent) -> None:
        if self.processing:  # 如果正在处理，则不接受新的拖放
            return
        mime_data = a0.mimeData()
        if mime_data and mime_data.hasUrls():
            files = [u.toLocalFile() for u in mime_data.urls()]
        else:
            files = []
        for file_path in files:
            try:
                self.processing = True  # 设置处理标志
                self.label.setText("正在处理图片，请稍候...")
                self.statusBar.showMessage("正在处理图片...")
                self.label.setStyleSheet("""
                    QLabel {
                        border: 2px solid #fdcb6e;
                        border-radius: 12px;
                        padding: 40px;
                        background-color: rgba(253, 203, 110, 0.1);
                        font-size: 16px;
                        font-weight: bold;
                        color: #b17012;
                    }
                """)
                QApplication.processEvents()  # 确保UI更新

                # 读取图片文件
                with Image.open(file_path) as img:
                    # 检查图片格式
                    if img.format not in ['PNG', 'JPEG', 'JPG', 'GIF', 'BMP', 'WEBP']:
                        raise ValueError(f"不支持的图片格式：{img.format or '未知'}, 请使用PNG、JPEG、GIF、BMP或WEBP格式的图片")
                    
                    # 检查图片尺寸并在需要时进行缩放
                    width, height = img.size
                    max_size = self.max_size_input.value()
                    if width > max_size or height > max_size:
                        self.statusBar.showMessage("正在调整图片尺寸...")
                        QApplication.processEvents()
                        ratio = min(max_size / width, max_size / height)
                        new_width = int(width * ratio)
                        new_height = int(height * ratio)
                        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    
                    # 转换为bytes，确保指定正确的格式
                    buffer = BytesIO()
                    original_format = img.format or 'PNG'
                    format_mapping = {
                        'JPEG': ('JPEG', 'jpeg'),
                        'JPG': ('JPEG', 'jpeg'),
                        'PNG': ('PNG', 'png'),
                        'GIF': ('GIF', 'gif'),
                        'BMP': ('BMP', 'bmp'),
                        'WEBP': ('WEBP', 'webp')
                    }
                    
                    save_format, mime_type = format_mapping.get(original_format, ('PNG', 'png'))
                    
                    # 保存图片
                    if save_format == 'JPEG':
                        img.save(buffer, format=save_format, quality=self.quality_input.value())
                    else:
                        img.save(buffer, format=save_format, optimize=True)
                    
                    # 检查文件大小
                    current_size = len(buffer.getvalue()) / 1024  # 转换为KB
                    if current_size > self.max_size_kb:
                        raise ValueError(f"处理后的图片大小（{current_size:.1f}KB）超过了限制（{self.max_size_kb}KB）")
                    
                    base64_str = base64.b64encode(buffer.getvalue()).decode()
                    markdown_str = f"![image](data:image/{mime_type};base64,{base64_str})"
                    
                    # 显示结果并复制到剪贴板
                    self.result_text.setText(markdown_str)
                    QApplication.clipboard().setText(markdown_str)
                    success_msg = "转换成功！已复制到剪贴板，继续拖放新的图片文件"
                    self.label.setText(success_msg)
                    self.statusBar.showMessage(success_msg)
                    # 添加成功动画效果
                    self.label.setStyleSheet("""
                        QLabel {
                            border: 2px solid #00b894;
                            border-radius: 12px;
                            padding: 40px;
                            background-color: rgba(0, 184, 148, 0.1);
                            font-size: 16px;
                            font-weight: bold;
                            color: #00b894;
                        }
                    """)
            except Exception as e:
                self.result_text.setText(f"转换失败：{str(e)}")
                error_msg = f"转换失败：{str(e)}"
                self.label.setText("转换失败，请重试")
                self.statusBar.showMessage(error_msg)
                # 添加失败动画效果
                self.label.setStyleSheet("""
                    QLabel {
                        border: 2px solid #d63031;
                        border-radius: 12px;
                        padding: 40px;
                        background-color: rgba(214, 48, 49, 0.1);
                        font-size: 16px;
                        font-weight: bold;
                        color: #d63031;
                    }
                """)
            finally:
                self.processing = False  # 重置处理标志

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()