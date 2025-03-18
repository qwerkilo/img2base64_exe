import base64
from PIL import Image
from io import BytesIO
from typing import Tuple, Optional

class ImageProcessor:
    def __init__(self, max_size_kb: int = 30, max_image_size: int = 768, image_quality: int = 95):
        self.max_size_kb = max_size_kb
        self.max_image_size = max_image_size
        self.image_quality = image_quality

    def process_image(self, file_path: str, image_tag: str = 'image') -> Tuple[str, str]:
        """处理图片并返回base64字符串和markdown格式的字符串
        
        Args:
            file_path: 图片文件路径
            image_tag: Markdown链接中的图片标签名称，默认为'image'
        """
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
            
            # 转换为bytes并进行质量压缩
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
            
            # 针对不同格式使用不同的压缩策略
            buffer = BytesIO()
            if save_format in ['PNG', 'GIF']:
                # 对于PNG和GIF，先尝试转换为RGB模式并使用有损压缩
                if img.mode in ['RGBA', 'LA'] or (save_format == 'PNG' and img.mode == 'P'):
                    # 如果有透明通道，先尝试保留透明度进行压缩
                    img.save(buffer, format=save_format, optimize=True)
                    if len(buffer.getvalue()) / 1024 > self.max_size_kb:
                        # 如果仍然过大，转换为RGB并使用JPEG压缩
                        buffer = BytesIO()
                        rgb_img = img.convert('RGB')
                        save_format = 'JPEG'
                        mime_type = 'jpeg'
                        img = rgb_img
                else:
                    # 直接转换为JPEG进行压缩
                    save_format = 'JPEG'
                    mime_type = 'jpeg'
            
            # 使用递进式压缩
            current_quality = self.image_quality
            min_quality = 20 if save_format == 'WEBP' else 5
            
            while True:
                buffer = BytesIO()
                img.save(buffer, format=save_format, quality=current_quality, optimize=True)
                current_size = len(buffer.getvalue()) / 1024  # 转换为KB
                
                if current_size <= self.max_size_kb or current_quality <= min_quality:
                    break
                
                # 使用更激进的质量调整策略
                size_ratio = current_size / self.max_size_kb
                if size_ratio > 3:
                    quality_reduction = int(current_quality * 0.5)
                else:
                    quality_reduction = int(current_quality * 0.3)
                
                current_quality = max(current_quality - quality_reduction, min_quality)
            
            if current_size > self.max_size_kb:
                # 如果还是太大，尝试进一步缩小图片尺寸
                if width > 300 or height > 300:
                    scale_factor = 0.8
                    new_width = int(width * scale_factor)
                    new_height = int(height * scale_factor)
                    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    buffer = BytesIO()
                    img.save(buffer, format=save_format, quality=min_quality, optimize=True)
                    current_size = len(buffer.getvalue()) / 1024
                
                if current_size > self.max_size_kb:
                    raise ValueError(f"处理后的图片大小（{current_size:.1f}KB）超过了限制（{self.max_size_kb}KB）")

            
            base64_str = base64.b64encode(buffer.getvalue()).decode()
            markdown_str = f"![{image_tag}](data:image/{mime_type};base64,{base64_str})"
            
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