import sys
import base64
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QTextEdit
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDragEnterEvent, QDropEvent
from PIL import Image
from io import BytesIO
from typing import Optional

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("图片转Base64工具")
        self.setAcceptDrops(True)
        self.resize(600, 400)

        # 创建主窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # 创建提示标签
        self.label = QLabel("将图片文件拖放到这里")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet(
            "QLabel { border: 2px dashed #aaa; border-radius: 5px; padding: 20px; }"
        )
        layout.addWidget(self.label)

        # 创建结果文本框
        self.result_text = QTextEdit()
        self.result_text.setPlaceholderText("转换结果将显示在这里")
        self.result_text.setReadOnly(True)
        layout.addWidget(self.result_text)

    
    def dragEnterEvent(self, a0: Optional[QDragEnterEvent]):
        assert a0 is not None
        mime_data: Optional[QMimeData] = a0.mimeData()  # type: ignore
        if mime_data is not None and mime_data.hasUrls():
            a0.accept()
        else:
            a0.setDropAction(Qt.DropAction.IgnoreAction)

    def dropEvent(self, a0: QDropEvent) -> None:
        mime_data = a0.mimeData()
        if mime_data and mime_data.hasUrls():
            files = [u.toLocalFile() for u in mime_data.urls()]
        else:
            files = []
        for file_path in files:
            try:
                # 读取图片文件
                with Image.open(file_path) as img:
                    # 检查图片格式
                    if img.format not in ['PNG', 'JPEG', 'JPG', 'GIF', 'BMP', 'WEBP']:
                        raise ValueError(f"不支持的图片格式：{img.format or '未知'}, 请使用PNG、JPEG、GIF、BMP或WEBP格式的图片")
                    
                    # 检查图片尺寸并在需要时进行缩放
                    width, height = img.size
                    max_size = 512
                    if width > max_size or height > max_size:
                        # 计算缩放比例
                        ratio = min(max_size / width, max_size / height)
                        new_width = int(width * ratio)
                        new_height = int(height * ratio)
                        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    
                    # 转换为bytes，确保指定正确的格式
                    buffer = BytesIO()
                    original_format = img.format or 'PNG'
                    # 处理特殊格式
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
                        img.save(buffer, format=save_format, quality=95)
                    else:
                        img.save(buffer, format=save_format)
                    
                    img_bytes = buffer.getvalue()
                    
                    # 转换为base64
                    base64_str = base64.b64encode(img_bytes).decode()
                    
                    # 生成Typora兼容的Markdown图片链接
                    markdown_str = f"![image](data:image/{mime_type};base64,{base64_str})"
                    
                    # 显示结果并复制到剪贴板
                    self.result_text.setText(markdown_str)
                    QApplication.clipboard().setText(markdown_str)
                    self.label.setText("转换成功！已复制到剪贴板，继续拖放新的图片文件")
            except Exception as e:
                self.result_text.setText(f"转换失败：{str(e)}")
                self.label.setText("转换失败，请重试")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()