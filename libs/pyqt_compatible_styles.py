# -*- coding: utf-8 -*-
"""
PyQt5兼容的样式配置

PyQt5的QStyleSheet不支持CSS3的某些属性，如：
- transition (过渡动画)
- transform (变换)
- box-shadow (阴影)
- animation (动画)

本文件提供PyQt5兼容的替代样式
"""

from .ui_styles import UIColors, UISpacing, UIBorderRadius


class PyQtCompatibleStyles:
    """PyQt5兼容样式"""
    
    @staticmethod
    def primary_button():
        """主要按钮样式（兼容版本）"""
        return f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {UIColors.PRIMARY}, 
                    stop:1 {UIColors.PRIMARY_DARK});
                color: {UIColors.WHITE};
                border: 2px solid {UIColors.PRIMARY};
                border-radius: {UIBorderRadius.MD}px;
                padding: {UISpacing.MD}px {UISpacing.LG}px;
                font-weight: bold;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {UIColors.PRIMARY_LIGHT}, 
                    stop:1 {UIColors.PRIMARY});
                border: 2px solid {UIColors.PRIMARY_LIGHT};
            }}
            QPushButton:pressed {{
                background: {UIColors.PRIMARY_DARK};
                border: 2px solid {UIColors.PRIMARY_DARK};
            }}
            QPushButton:disabled {{
                background: {UIColors.DISABLED};
                color: {UIColors.DISABLED_TEXT};
                border: 2px solid {UIColors.DISABLED};
            }}
        """
    
    @staticmethod
    def success_button():
        """成功按钮样式（兼容版本）"""
        return f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {UIColors.SUCCESS}, 
                    stop:1 #43A047);
                color: {UIColors.WHITE};
                border: 2px solid {UIColors.SUCCESS};
                border-radius: {UIBorderRadius.MD}px;
                padding: {UISpacing.MD}px {UISpacing.LG}px;
                font-weight: bold;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #66BB6A, 
                    stop:1 {UIColors.SUCCESS});
                border: 2px solid #66BB6A;
            }}
            QPushButton:pressed {{
                background: #43A047;
                border: 2px solid #43A047;
            }}
        """
    
    @staticmethod
    def danger_button():
        """危险按钮样式（兼容版本）"""
        return f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {UIColors.DANGER}, 
                    stop:1 #D32F2F);
                color: {UIColors.WHITE};
                border: 2px solid {UIColors.DANGER};
                border-radius: {UIBorderRadius.MD}px;
                padding: {UISpacing.MD}px {UISpacing.LG}px;
                font-weight: bold;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #EF5350, 
                    stop:1 {UIColors.DANGER});
                border: 2px solid #EF5350;
            }}
            QPushButton:pressed {{
                background: #D32F2F;
                border: 2px solid #D32F2F;
            }}
        """
    
    @staticmethod
    def modern_list():
        """现代化列表样式（兼容版本）"""
        return f"""
            QListWidget {{
                background: {UIColors.WHITE};
                border: 1px solid {UIColors.BORDER};
                border-radius: {UIBorderRadius.SM}px;
                padding: {UISpacing.SM}px;
                font-size: 13px;
                selection-background-color: {UIColors.PRIMARY_LIGHT};
            }}
            QListWidget::item {{
                background: {UIColors.WHITE};
                border: 1px solid transparent;
                border-radius: {UIBorderRadius.SM}px;
                padding: {UISpacing.SM}px;
                margin: 2px;
            }}
            QListWidget::item:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {UIColors.BACKGROUND_LIGHT}, 
                    stop:1 {UIColors.WHITE});
                border: 1px solid {UIColors.PRIMARY_LIGHT};
            }}
            QListWidget::item:selected {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {UIColors.PRIMARY_LIGHT}, 
                    stop:1 {UIColors.PRIMARY});
                color: {UIColors.WHITE};
                border: 1px solid {UIColors.PRIMARY};
            }}
        """
    
    @staticmethod
    def animated_input_field():
        """动画输入框样式（兼容版本）"""
        return f"""
            QLineEdit {{
                background: {UIColors.WHITE};
                border: 2px solid {UIColors.BORDER};
                border-radius: {UIBorderRadius.SM}px;
                padding: {UISpacing.MD}px;
                font-size: 13px;
                color: {UIColors.TEXT_PRIMARY};
            }}
            QLineEdit:focus {{
                border: 2px solid {UIColors.PRIMARY};
                background: {UIColors.BACKGROUND_LIGHT};
            }}
            QLineEdit:hover {{
                border: 2px solid {UIColors.PRIMARY_LIGHT};
            }}
        """
    
    @staticmethod
    def status_indicator(status_type: str = "success"):
        """状态指示器样式（兼容版本）"""
        color_map = {
            "success": UIColors.SUCCESS,
            "warning": UIColors.WARNING,
            "error": UIColors.DANGER,
            "info": UIColors.INFO
        }
        
        color = color_map.get(status_type, UIColors.SUCCESS)
        
        return f"""
            QLabel {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {color}, 
                    stop:1 rgba(0,0,0,0.1));
                color: {UIColors.WHITE};
                border: 1px solid {color};
                border-radius: {UIBorderRadius.SM}px;
                padding: {UISpacing.SM}px {UISpacing.MD}px;
                font-weight: bold;
                font-size: 12px;
            }}
        """
    
    @staticmethod
    def progress_bar():
        """进度条样式（兼容版本）"""
        return f"""
            QProgressBar {{
                background: {UIColors.BACKGROUND_LIGHT};
                border: 1px solid {UIColors.BORDER};
                border-radius: {UIBorderRadius.SM}px;
                text-align: center;
                font-weight: bold;
                font-size: 12px;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {UIColors.PRIMARY_LIGHT}, 
                    stop:1 {UIColors.PRIMARY});
                border-radius: {UIBorderRadius.SM}px;
                margin: 1px;
            }}
        """
    
    @staticmethod
    def group_box():
        """分组框样式（兼容版本）"""
        return f"""
            QGroupBox {{
                font-weight: bold;
                font-size: 14px;
                color: {UIColors.TEXT_PRIMARY};
                border: 2px solid {UIColors.BORDER};
                border-radius: {UIBorderRadius.MD}px;
                margin-top: 1ex;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 {UISpacing.SM}px 0 {UISpacing.SM}px;
                background: {UIColors.WHITE};
                color: {UIColors.PRIMARY};
            }}
        """
    
    @staticmethod
    def tab_widget():
        """标签页样式（兼容版本）"""
        return f"""
            QTabWidget::pane {{
                border: 1px solid {UIColors.BORDER};
                border-radius: {UIBorderRadius.SM}px;
                background: {UIColors.WHITE};
            }}
            QTabBar::tab {{
                background: {UIColors.BACKGROUND_LIGHT};
                border: 1px solid {UIColors.BORDER};
                padding: {UISpacing.MD}px {UISpacing.LG}px;
                margin-right: 2px;
                font-size: 13px;
            }}
            QTabBar::tab:selected {{
                background: {UIColors.WHITE};
                border-bottom: 2px solid {UIColors.PRIMARY};
                color: {UIColors.PRIMARY};
                font-weight: bold;
            }}
            QTabBar::tab:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {UIColors.WHITE}, 
                    stop:1 {UIColors.BACKGROUND_LIGHT});
            }}
        """


def get_compatible_material_style():
    """获取兼容的Material Design样式"""
    styles = PyQtCompatibleStyles()
    
    return f"""
        /* 全局样式 */
        QWidget {{
            font-family: "Segoe UI", "Roboto", "Arial", sans-serif;
            color: {UIColors.TEXT_PRIMARY};
            background: {UIColors.WHITE};
        }}
        
        /* 主窗口样式 */
        QMainWindow {{
            background: {UIColors.BACKGROUND_LIGHT};
        }}
        
        /* 菜单栏样式 */
        QMenuBar {{
            background: {UIColors.WHITE};
            border-bottom: 1px solid {UIColors.BORDER};
            padding: 2px;
        }}
        QMenuBar::item {{
            background: transparent;
            padding: {UISpacing.SM}px {UISpacing.MD}px;
            border-radius: {UIBorderRadius.SM}px;
        }}
        QMenuBar::item:selected {{
            background: {UIColors.PRIMARY_LIGHT};
            color: {UIColors.WHITE};
        }}
        
        /* 工具栏样式 */
        QToolBar {{
            background: {UIColors.WHITE};
            border: 1px solid {UIColors.BORDER};
            spacing: {UISpacing.SM}px;
            padding: {UISpacing.SM}px;
        }}
        QToolButton {{
            background: transparent;
            border: 1px solid transparent;
            border-radius: {UIBorderRadius.SM}px;
            padding: {UISpacing.SM}px;
            margin: 2px;
        }}
        QToolButton:hover {{
            background: {UIColors.PRIMARY_LIGHT};
            border: 1px solid {UIColors.PRIMARY};
        }}
        QToolButton:pressed {{
            background: {UIColors.PRIMARY};
            color: {UIColors.WHITE};
        }}
        
        /* 状态栏样式 */
        QStatusBar {{
            background: {UIColors.WHITE};
            border-top: 1px solid {UIColors.BORDER};
            padding: {UISpacing.SM}px;
        }}
        QStatusBar::item {{
            border: none;
        }}
        
        /* 滚动条样式 */
        QScrollBar:vertical {{
            background: {UIColors.BACKGROUND_LIGHT};
            width: 12px;
            border-radius: 6px;
        }}
        QScrollBar::handle:vertical {{
            background: {UIColors.BORDER};
            border-radius: 6px;
            min-height: 20px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: {UIColors.PRIMARY_LIGHT};
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            border: none;
            background: none;
        }}
        
        /* 分隔器样式 */
        QSplitter::handle {{
            background: {UIColors.BORDER};
        }}
        QSplitter::handle:horizontal {{
            width: 2px;
        }}
        QSplitter::handle:vertical {{
            height: 2px;
        }}
        
        /* 停靠窗口样式 */
        QDockWidget {{
            color: {UIColors.TEXT_PRIMARY};
            font-weight: bold;
        }}
        QDockWidget::title {{
            background: {UIColors.PRIMARY_LIGHT};
            color: {UIColors.WHITE};
            padding: {UISpacing.SM}px;
            border-radius: {UIBorderRadius.SM}px;
        }}
    """