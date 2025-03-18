import base64
from PIL import Image
from io import BytesIO
from typing import Tuple, Optional

class ImageProcessor:
    def __init__(self, max_size_kb: int = 30, max_image_size: int = 768, image_quality: int = 95):
        self.max_size_kb = max_size_kb
        self.max_image_size = max_image_size
        self.image_quality = image_quality

    def process_image(self, file_path: str) -> Tuple[str, str]:
        """处理图片并返回base64字符串和markdown格式的字符串"""
        with Image.open(file_path) as img:
            # 检查图片格式
            if img.format not in ['PNG', 'JPEG', 'JPG', 'GIF', 'BMP', 'WEBP']:
                raise ValueError(f"不支持的图片格式：{img.format or '未知'}, 请使用PNG、JPEG、GIF、BMP或WEBP格式的图片")
            
            # 检查图片尺寸并在需要时进行缩放
            width, height = img.size
            if width > self.max_image_size or height > self.max_image_size:
                ratio = min(self.max_image_size / width, self.max_image_size / height)
                new_width = int(width * ratio)
                new_height = int(height * ratio)
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # 转换为bytes
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
                img.save(buffer, format=save_format, quality=self.image_quality)
            else:
                img.save(buffer, format=save_format, optimize=True)
            
            # 检查文件大小
            current_size = len(buffer.getvalue()) / 1024  # 转换为KB
            if current_size > self.max_size_kb:
                raise ValueError(f"处理后的图片大小（{current_size:.1f}KB）超过了限制（{self.max_size_kb}KB）")
            
            base64_str = base64.b64encode(buffer.getvalue()).decode()
            markdown_str = f"![image](data:image/{mime_type};base64,{base64_str})"
            
            return base64_str, markdown_str

    def update_settings(self, max_size_kb: Optional[int] = None,
                       max_image_size: Optional[int] = None,
                       image_quality: Optional[int] = None) -> None:
        """更新图片处理设置"""
        if max_size_kb is not None:
            self.max_size_kb = max_size_kb
        if max_image_size is not None:
            self.max_image_size = max_image_size
        if image_quality is not None:
            self.image_quality = image_quality