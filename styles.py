# 全局样式定义

MAIN_WINDOW_STYLE = """
    QMainWindow {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                  stop:0 #f6f7f8, stop:1 #e9ebee);
    }
"""

LABEL_STYLE = """
    QLabel {
        font-family: 'Microsoft YaHei', 'Arial';
        font-size: 14px;
        color: #2c3e50;
    }
"""

SPIN_BOX_STYLE = """
    QSpinBox {
        background-color: white;
        border: 1px solid #dcdde1;
        border-radius: 4px;
        padding: 4px;
        font-size: 14px;
        min-width: 80px;
    }
    QSpinBox::up-button, QSpinBox::down-button {
        width: 20px;
        height: 12px;
        border: none;
        background-color: #f5f6fa;
        border-radius: 2px;
        margin: 1px;
    }
    QSpinBox::up-button:hover, QSpinBox::down-button:hover {
        background-color: #dcdde1;
    }
    QSpinBox::up-button:pressed, QSpinBox::down-button:pressed {
        background-color: #74b9ff;
    }
"""

TEXT_EDIT_STYLE = """
    QTextEdit {
        background-color: white;
        border: 1px solid #dcdde1;
        border-radius: 8px;
        padding: 10px;
        font-family: 'Consolas', 'Courier New';
        font-size: 13px;
        selection-background-color: #74b9ff;
    }
"""

STATUS_BAR_STYLE = """
    QStatusBar {
        background-color: #f5f6fa;
        color: #576574;
        font-size: 12px;
    }
"""

TAB_WIDGET_STYLE = """
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
"""

SAVE_BUTTON_STYLE = """
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
"""

DROP_LABEL_STYLE = """
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
"""

PROCESSING_LABEL_STYLE = """
    QLabel {
        border: 2px solid #fdcb6e;
        border-radius: 12px;
        padding: 40px;
        background-color: rgba(253, 203, 110, 0.1);
        font-size: 16px;
        font-weight: bold;
        color: #b17012;
    }
"""

SUCCESS_LABEL_STYLE = """
    QLabel {
        border: 2px solid #00b894;
        border-radius: 12px;
        padding: 40px;
        background-color: rgba(0, 184, 148, 0.1);
        font-size: 16px;
        font-weight: bold;
        color: #00b894;
    }
"""

ERROR_LABEL_STYLE = """
    QLabel {
        border: 2px solid #d63031;
        border-radius: 12px;
        padding: 40px;
        background-color: rgba(214, 48, 49, 0.1);
        font-size: 16px;
        font-weight: bold;
        color: #d63031;
    }
"""