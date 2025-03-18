import sys
import base64
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout,
                             QWidget, QTextEdit, QStatusBar, QFrame)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QDragEnterEvent, QDropEvent, QPalette, QColor, QFont
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

        # 创建提示标签
        self.label = QLabel("将图片文件拖放到这里")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
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
        layout.addWidget(self.label)

        # 创建结果文本框
        self.result_text = QTextEdit()
        self.result_text.setPlaceholderText("转换结果将显示在这里")
        self.result_text.setReadOnly(True)
        self.result_text.setMinimumHeight(200)
        layout.addWidget(self.result_text)

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
            a0.setDropAction(Qt.DropAction.IgnoreAction)

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
                    max_size = 512
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
                    
                    # 保存图片并检查文件大小
                    max_size_kb = 30
                    quality = 95
                    compression_count = 0
                    while True:
                        buffer.seek(0)
                        buffer.truncate()
                        
                        if save_format == 'JPEG':
                            img.save(buffer, format=save_format, quality=quality)
                        else:
                            img.save(buffer, format=save_format, optimize=True)
                        
                        # 检查文件大小
                        current_size = len(buffer.getvalue()) / 1024  # 转换为KB
                        if current_size <= max_size_kb:
                            break
                            
                        # 如果文件仍然过大，继续压缩
                        compression_count += 1
                        self.statusBar.showMessage(f"正在压缩图片...（第{compression_count}次尝试）当前大小：{current_size:.1f}KB")
                        QApplication.processEvents()

                        if quality > 5:  # 控制最低质量
                            quality -= 5
                        else:  # 如果质量已经很低，尝试缩小尺寸
                            width, height = img.size
                            if width <= 50 or height <= 50:  # 控制最小尺寸
                                break
                            new_width = int(width * 0.9)
                            new_height = int(height * 0.9)
                            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                            quality = 95  # 重置质量开始新一轮压缩
                    
                    self.statusBar.showMessage("正在生成Base64编码...")
                    QApplication.processEvents()
                    img_bytes = buffer.getvalue()
                    base64_str = base64.b64encode(img_bytes).decode()
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
    sys.exit(app.exec())

if __name__ == "__main__":
    main()