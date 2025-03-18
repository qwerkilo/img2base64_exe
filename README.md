# img2base64

一个简单而强大的图片转Base64工具，支持拖拽操作，快速将图片转换为Markdown兼容的Base64编码字符串。

## 功能特点

- 支持多种图片格式（PNG, JPG, JPEG, GIF, BMP, WEBP）
- 简单易用的拖拽界面
- 自动优化图片尺寸，确保转换后的文件大小合理
- 转换结果自动复制到剪贴板
- 生成Typora兼容的Markdown图片链接
- 无需联网，本地转换，保护隐私

## 安装说明

### 方式一：直接使用

1. 从Release页面下载最新的可执行文件（img2base64.exe）
2. 双击运行即可使用，无需安装

### 方式二：从源码运行

1. 确保已安装Python 3.6+
2. 克隆或下载本仓库
3. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
4. 运行程序：
   ```bash
   python main.py
   ```

## 使用方法

1. 运行程序，会出现一个带有虚线边框的窗口
2. 将图片文件直接拖放到窗口中
3. 程序会自动将图片转换为Base64编码，并生成Markdown格式的图片链接
4. 转换结果会自动复制到剪贴板，可以直接粘贴使用

## 注意事项

- 支持的最大图片尺寸为512x512，超过此尺寸的图片会自动等比例缩放
- 为保证转换效果，建议使用PNG或JPG格式的图片
- JPEG格式的图片会以95%的质量进行压缩，以平衡文件大小和图片质量

## 版本历史

### v1.0.0
- 首次发布
- 实现基本的图片转Base64功能
- 支持多种图片格式
- 添加自动图片优化功能

## 项目结构

```
.
├── main.py           # 主程序文件，包含GUI界面和图片转换逻辑
├── requirements.txt  # 项目依赖文件
├── main.spec        # PyInstaller打包配置文件
├── .gitignore       # Git忽略文件配置
└── README.md        # 项目说明文档
```

## 开源协议

MIT License