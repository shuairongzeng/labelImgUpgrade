# -*- coding: utf-8 -*-
"""
UI样式配置文件
统一管理labelImg应用的所有UI样式，减少重复代码，提升维护性
"""

class UIColors:
    """统一的颜色调色板"""
    
    # 主色调
    PRIMARY = "#1976d2"
    PRIMARY_LIGHT = "#42a5f5" 
    PRIMARY_DARK = "#1565c0"
    
    # 辅助色
    SECONDARY = "#4caf50"
    SECONDARY_LIGHT = "#66bb6a"
    SECONDARY_DARK = "#388e3c"
    
    # 状态色
    SUCCESS = "#4caf50"
    SUCCESS_LIGHT = "#e8f5e8"
    SUCCESS_DARK = "#388e3c"
    WARNING = "#ff9800"
    WARNING_LIGHT = "#fff3e0"
    WARNING_DARK = "#e65100"
    ERROR = "#f44336"
    ERROR_LIGHT = "#ffebee"
    ERROR_DARK = "#c62828"
    INFO = "#2196f3"
    INFO_LIGHT = "#e3f2fd"
    INFO_DARK = "#1565c0"
    
    # 中性色
    GREY_50 = "#fafafa"
    GREY_100 = "#f5f5f5"
    GREY_200 = "#eeeeee"
    GREY_300 = "#e0e0e0"
    GREY_400 = "#bdbdbd"
    GREY_500 = "#9e9e9e"
    GREY_600 = "#757575"
    GREY_700 = "#616161"
    GREY_800 = "#424242"
    GREY_900 = "#212121"
    
    # 文本色
    TEXT_PRIMARY = "#212121"
    TEXT_SECONDARY = "#757575"
    TEXT_DISABLED = "#bdbdbd"
    TEXT_INVERSE = "#ffffff"
    
    # 背景色
    BACKGROUND = "#ffffff"
    SURFACE = "#ffffff"
    OVERLAY = "rgba(0, 0, 0, 0.1)"

class UISpacing:
    """统一的间距系统"""
    XS = "2px"
    SM = "4px"
    MD = "8px"
    LG = "12px"
    XL = "16px"
    XXL = "24px"
    XXXL = "32px"

class UIRadius:
    """统一的圆角设置"""
    SM = "4px"
    MD = "6px"
    LG = "8px"
    XL = "12px"
    ROUND = "50%"

class UIShadows:
    """统一的阴影效果"""
    NONE = "none"
    SM = "0 1px 3px rgba(0, 0, 0, 0.12)"
    MD = "0 2px 6px rgba(0, 0, 0, 0.16)"
    LG = "0 4px 12px rgba(0, 0, 0, 0.15)"
    XL = "0 8px 24px rgba(0, 0, 0, 0.15)"

class UITransitions:
    """统一的过渡动画"""
    FAST = "0.15s ease-out"
    NORMAL = "0.25s ease-out"
    SLOW = "0.35s ease-out"
    
    # 特殊动画效果
    BOUNCE = "0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55)"
    SMOOTH = "0.3s cubic-bezier(0.4, 0, 0.2, 1)"
    ELASTIC = "0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275)"
    
    # 组合动画属性
    ALL_FAST = f"all {FAST}"
    ALL_NORMAL = f"all {NORMAL}"
    ALL_SLOW = f"all {SLOW}"
    ALL_BOUNCE = f"all {BOUNCE}"
    ALL_SMOOTH = f"all {SMOOTH}"
    ALL_ELASTIC = f"all {ELASTIC}"

class ButtonStyles:
    """统一的按钮样式"""
    
    @staticmethod
    def primary_button():
        """主要按钮样式 - 带动画效果"""
        return f"""
            QPushButton {{
                background-color: {UIColors.PRIMARY};
                color: white;
                border: none;
                border-radius: {UIRadius.MD};
                padding: {UISpacing.SM} {UISpacing.MD};
                font-weight: 600;
                font-size: 13px;
                min-height: 20px;
                transition: {UITransitions.ALL_SMOOTH};
            }}
            QPushButton:hover {{
                background-color: {UIColors.PRIMARY_DARK};
                transform: translateY(-1px);
                box-shadow: {UIShadows.MD};
            }}
            QPushButton:pressed {{
                background-color: {UIColors.PRIMARY_DARK};
                transform: translateY(0px);
                box-shadow: {UIShadows.SM};
                transition: {UITransitions.ALL_FAST};
            }}
            QPushButton:disabled {{
                background-color: {UIColors.GREY_400};
                color: {UIColors.GREY_600};
                transform: none;
                box-shadow: none;
            }}
        """
    
    @staticmethod
    def secondary_button():
        """次要按钮样式 - 带动画效果"""
        return f"""
            QPushButton {{
                background-color: {UIColors.WARNING};
                color: white;
                border: none;
                border-radius: {UIRadius.MD};
                padding: {UISpacing.SM} {UISpacing.MD};
                font-weight: 500;
                font-size: 12px;
                min-height: 16px;
                transition: {UITransitions.ALL_SMOOTH};
            }}
            QPushButton:hover {{
                background-color: {UIColors.WARNING_DARK};
                transform: scale(1.02);
                box-shadow: {UIShadows.MD};
            }}
            QPushButton:pressed {{
                background-color: {UIColors.WARNING_DARK};
                transform: scale(0.98);
                box-shadow: {UIShadows.SM};
                transition: {UITransitions.ALL_FAST};
            }}
            QPushButton:disabled {{
                background-color: {UIColors.GREY_400};
                color: {UIColors.GREY_600};
                transform: none;
                box-shadow: none;
            }}
        """
    
    @staticmethod
    def danger_button():
        """危险按钮样式 - 带震动动画效果"""
        return f"""
            QPushButton {{
                background-color: {UIColors.ERROR};
                color: white;
                border: 2px solid {UIColors.ERROR};
                border-radius: {UIRadius.MD};
                padding: {UISpacing.SM} {UISpacing.MD};
                font-weight: 600;
                font-size: 12px;
                min-height: 16px;
                transition: {UITransitions.ALL_SMOOTH};
            }}
            QPushButton:hover {{
                background-color: #d32f2f;
                border-color: #c62828;
                transform: translateY(-1px);
                box-shadow: 0 4px 8px rgba(244, 67, 54, 0.4);
                animation: pulse 1.5s infinite;
            }}
            QPushButton:pressed {{
                background-color: #c62828;
                border-color: #b71c1c;
                transform: translateY(0px);
                box-shadow: {UIShadows.SM};
                transition: {UITransitions.ALL_FAST};
            }}
            QPushButton:disabled {{
                background-color: {UIColors.GREY_400};
                color: {UIColors.GREY_600};
                border-color: {UIColors.GREY_400};
                transform: none;
                box-shadow: none;
                animation: none;
            }}
            @keyframes pulse {{
                0% {{ box-shadow: 0 4px 8px rgba(244, 67, 54, 0.4); }}
                50% {{ box-shadow: 0 6px 12px rgba(244, 67, 54, 0.6); }}
                100% {{ box-shadow: 0 4px 8px rgba(244, 67, 54, 0.4); }}
            }}
        """
    
    @staticmethod
    def outline_button():
        """轮廓按钮样式 - 带动画效果"""
        return f"""
            QPushButton {{
                background-color: transparent;
                color: {UIColors.PRIMARY};
                border: 2px solid {UIColors.PRIMARY};
                border-radius: {UIRadius.MD};
                padding: {UISpacing.SM} {UISpacing.MD};
                font-weight: 500;
                font-size: 12px;
                min-height: 16px;
                transition: {UITransitions.ALL_SMOOTH};
            }}
            QPushButton:hover {{
                background-color: {UIColors.PRIMARY};
                color: white;
                transform: scale(1.05);
                box-shadow: {UIShadows.MD};
            }}
            QPushButton:pressed {{
                background-color: {UIColors.PRIMARY_DARK};
                color: white;
                border-color: {UIColors.PRIMARY_DARK};
                transform: scale(1.02);
                transition: {UITransitions.ALL_FAST};
            }}
            QPushButton:disabled {{
                background-color: transparent;
                color: {UIColors.GREY_500};
                border-color: {UIColors.GREY_400};
                transform: none;
                box-shadow: none;
            }}
        """
    
    @staticmethod
    def icon_button():
        """图标按钮样式 - 带旋转动画"""
        return f"""
            QPushButton {{
                background-color: transparent;
                color: {UIColors.GREY_600};
                border: none;
                border-radius: {UIRadius.ROUND};
                padding: {UISpacing.SM};
                font-size: 16px;
                min-width: 32px;
                min-height: 32px;
                transition: {UITransitions.ALL_SMOOTH};
            }}
            QPushButton:hover {{
                background-color: {UIColors.GREY_200};
                color: {UIColors.PRIMARY};
                transform: rotate(5deg) scale(1.1);
                box-shadow: {UIShadows.SM};
            }}
            QPushButton:pressed {{
                background-color: {UIColors.GREY_300};
                transform: rotate(0deg) scale(1.05);
                transition: {UITransitions.ALL_FAST};
            }}
            QPushButton:disabled {{
                background-color: transparent;
                color: {UIColors.GREY_400};
                transform: none;
                box-shadow: none;
            }}
        """
    
    @staticmethod
    def floating_action_button():
        """浮动操作按钮 - 带弹跳动画"""
        return f"""
            QPushButton {{
                background-color: {UIColors.SUCCESS};
                color: white;
                border: none;
                border-radius: {UIRadius.ROUND};
                padding: {UISpacing.MD};
                font-weight: 600;
                font-size: 16px;
                min-width: 48px;
                min-height: 48px;
                transition: {UITransitions.ALL_BOUNCE};
                box-shadow: {UIShadows.LG};
            }}
            QPushButton:hover {{
                background-color: {UIColors.SUCCESS_DARK};
                transform: scale(1.15) translateY(-2px);
                box-shadow: {UIShadows.XL};
            }}
            QPushButton:pressed {{
                background-color: {UIColors.SUCCESS_DARK};
                transform: scale(1.05) translateY(0px);
                box-shadow: {UIShadows.MD};
                transition: {UITransitions.ALL_FAST};
            }}
            QPushButton:disabled {{
                background-color: {UIColors.GREY_400};
                color: {UIColors.GREY_600};
                transform: none;
                box-shadow: {UIShadows.SM};
            }}
        """

class InteractionStyles:
    """交互式组件样式"""
    
    @staticmethod
    def animated_list_item():
        """带动画的列表项样式"""
        return f"""
            QListWidget::item {{
                background-color: transparent;
                border: none;
                border-radius: {UIRadius.SM};
                padding: {UISpacing.SM};
                margin: 2px;
                color: {UIColors.GREY_800};
                border-left: 3px solid transparent;
                transition: {UITransitions.ALL_SMOOTH};
            }}
            QListWidget::item:hover {{
                background-color: {UIColors.GREY_100};
                border-left: 3px solid {UIColors.PRIMARY};
                transform: translateX(4px);
                box-shadow: {UIShadows.SM};
            }}
            QListWidget::item:selected {{
                background-color: {UIColors.PRIMARY_LIGHT};
                color: {UIColors.PRIMARY_DARK};
                border-left: 3px solid {UIColors.PRIMARY};
                font-weight: 600;
                transform: translateX(6px);
                box-shadow: {UIShadows.MD};
            }}
        """
    
    @staticmethod
    def animated_progress_bar():
        """带动画的进度条样式"""
        return f"""
            QProgressBar {{
                border: 2px solid {UIColors.PRIMARY};
                border-radius: {UIRadius.LG};
                text-align: center;
                font-size: 11px;
                font-weight: 700;
                color: {UIColors.PRIMARY};
                background-color: {UIColors.GREY_100};
                min-height: 20px;
                transition: {UITransitions.ALL_SMOOTH};
            }}
            QProgressBar:hover {{
                border-color: {UIColors.PRIMARY_DARK};
                box-shadow: {UIShadows.MD};
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {UIColors.SUCCESS}, stop:0.5 #66bb6a, stop:1 #81c784);
                border-radius: {UIRadius.MD};
                margin: 1px;
                animation: progressFlow 2s ease-in-out infinite;
            }}
            @keyframes progressFlow {{
                0% {{ background-position: 0% 50%; }}
                50% {{ background-position: 100% 50%; }}
                100% {{ background-position: 0% 50%; }}
            }}
        """
    
    @staticmethod
    def animated_input_field():
        """带动画的输入框样式"""
        return f"""
            QLineEdit {{
                background-color: white;
                border: 2px solid {UIColors.GREY_300};
                border-radius: {UIRadius.MD};
                padding: {UISpacing.SM} {UISpacing.MD};
                color: {UIColors.GREY_800};
                font-size: 13px;
                transition: {UITransitions.ALL_SMOOTH};
            }}
            QLineEdit:hover {{
                border-color: {UIColors.PRIMARY};
                box-shadow: 0 0 0 3px rgba(33, 150, 243, 0.1);
            }}
            QLineEdit:focus {{
                border-color: {UIColors.PRIMARY};
                box-shadow: 0 0 0 3px rgba(33, 150, 243, 0.2);
                transform: scale(1.02);
            }}
            QLineEdit:disabled {{
                background-color: {UIColors.GREY_100};
                border-color: {UIColors.GREY_300};
                color: {UIColors.GREY_500};
                transform: none;
                box-shadow: none;
            }}
        """
    
    @staticmethod
    def animated_combobox():
        """带动画的下拉框样式"""
        return f"""
            QComboBox {{
                background-color: white;
                border: 1px solid {UIColors.GREY_300};
                border-radius: {UIRadius.SM};
                padding: {UISpacing.SM} {UISpacing.MD};
                min-width: 100px;
                font-size: 12px;
                transition: {UITransitions.ALL_SMOOTH};
            }}
            QComboBox:hover {{
                border-color: {UIColors.PRIMARY};
                box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.1);
            }}
            QComboBox:focus {{
                border-color: {UIColors.PRIMARY};
                box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.2);
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border: 2px solid {UIColors.GREY_600};
                width: 6px;
                height: 6px;
                border-top: none;
                border-right: none;
                transform: rotate(-45deg);
            }}
            QComboBox QAbstractItemView {{
                border: 1px solid {UIColors.GREY_300};
                border-radius: {UIRadius.SM};
                background-color: white;
                selection-background-color: {UIColors.PRIMARY_LIGHT};
                outline: none;
            }}
        """
    
    @staticmethod
    def animated_group_box():
        """带动画的分组框样式"""
        return f"""
            QGroupBox {{
                background-color: white;
                border: 2px solid {UIColors.GREY_300};
                border-radius: {UIRadius.LG};
                margin: {UISpacing.SM} 0;
                padding-top: {UISpacing.MD};
                font-weight: 600;
                color: {UIColors.GREY_800};
                transition: {UITransitions.ALL_SMOOTH};
            }}
            QGroupBox:hover {{
                border-color: {UIColors.PRIMARY};
                box-shadow: {UIShadows.SM};
                transform: translateY(-1px);
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: {UISpacing.MD};
                padding: 0 {UISpacing.SM};
                background-color: white;
                border-radius: {UIRadius.SM};
                transition: {UITransitions.ALL_SMOOTH};
            }}
            QGroupBox:hover::title {{
                color: {UIColors.PRIMARY};
                background-color: {UIColors.PRIMARY_LIGHT};
            }}
        """

class StatusIndicatorStyles:
    """状态指示器样式"""
    
    @staticmethod
    def success_indicator():
        """成功状态指示器 - 带闪烁动画"""
        return f"""
            QLabel {{
                background-color: {UIColors.SUCCESS_LIGHT};
                color: {UIColors.SUCCESS_DARK};
                border: 1px solid {UIColors.SUCCESS};
                border-radius: {UIRadius.SM};
                padding: {UISpacing.XS} {UISpacing.SM};
                font-weight: 600;
                font-size: 12px;
                transition: {UITransitions.ALL_SMOOTH};
                animation: successPulse 2s ease-in-out infinite;
            }}
            @keyframes successPulse {{
                0% {{ box-shadow: 0 0 0 0 rgba(76, 175, 80, 0.7); }}
                70% {{ box-shadow: 0 0 0 10px rgba(76, 175, 80, 0); }}
                100% {{ box-shadow: 0 0 0 0 rgba(76, 175, 80, 0); }}
            }}
        """
    
    @staticmethod
    def warning_indicator():
        """警告状态指示器 - 带摇摆动画"""
        return f"""
            QLabel {{
                background-color: {UIColors.WARNING_LIGHT};
                color: {UIColors.WARNING_DARK};
                border: 1px solid {UIColors.WARNING};
                border-radius: {UIRadius.SM};
                padding: {UISpacing.XS} {UISpacing.SM};
                font-weight: 600;
                font-size: 12px;
                transition: {UITransitions.ALL_SMOOTH};
                animation: warningShake 3s ease-in-out infinite;
            }}
            @keyframes warningShake {{
                0%, 100% {{ transform: translateX(0); }}
                25% {{ transform: translateX(-2px); }}
                75% {{ transform: translateX(2px); }}
            }}
        """
    
    @staticmethod
    def error_indicator():
        """错误状态指示器 - 带强烈闪烁动画"""
        return f"""
            QLabel {{
                background-color: {UIColors.ERROR_LIGHT};
                color: {UIColors.ERROR};
                border: 1px solid {UIColors.ERROR};
                border-radius: {UIRadius.SM};
                padding: {UISpacing.XS} {UISpacing.SM};
                font-weight: 600;
                font-size: 12px;
                transition: {UITransitions.ALL_SMOOTH};
                animation: errorBlink 1s ease-in-out infinite;
            }}
            @keyframes errorBlink {{
                0%, 50% {{ opacity: 1; }}
                25%, 75% {{ opacity: 0.3; }}
            }}
        """
    
    @staticmethod
    def info_indicator():
        """信息状态指示器"""
        return f"""
            QLabel {{
                background-color: {UIColors.INFO_LIGHT};
                color: {UIColors.INFO_DARK};
                border: 1px solid {UIColors.INFO};
                border-radius: {UIRadius.SM};
                padding: {UISpacing.XS} {UISpacing.SM};
                font-weight: 600;
                font-size: 12px;
                transition: {UITransitions.ALL_SMOOTH};
            }}
        """

class SpecialGroupBoxStyles:
    """特殊分组框样式"""
    
    @staticmethod
    def primary_action_group():
        """主要操作分组框 - 带发光动画"""
        return f"""
            QGroupBox {{
                background-color: #f8fff8;
                border: 2px solid {UIColors.SUCCESS};
                border-radius: {UIRadius.LG};
                margin: {UISpacing.SM} 0;
                padding-top: {UISpacing.MD};
                font-weight: 600;
                color: {UIColors.SUCCESS_DARK};
                transition: {UITransitions.ALL_SMOOTH};
                animation: primaryGlow 3s ease-in-out infinite;
            }}
            QGroupBox:hover {{
                border-color: {UIColors.SUCCESS_DARK};
                box-shadow: 0 0 15px rgba(76, 175, 80, 0.3);
                transform: translateY(-1px);
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: {UISpacing.MD};
                padding: 0 {UISpacing.SM};
                background-color: #f8fff8;
                color: {UIColors.SUCCESS_DARK};
                border-radius: {UIRadius.SM};
                transition: {UITransitions.ALL_SMOOTH};
            }}
            QGroupBox:hover::title {{
                background-color: {UIColors.SUCCESS_LIGHT};
                color: {UIColors.SUCCESS_DARK};
                box-shadow: {UIShadows.SM};
            }}
            @keyframes primaryGlow {{
                0%, 100% {{ box-shadow: 0 0 5px rgba(76, 175, 80, 0.2); }}
                50% {{ box-shadow: 0 0 10px rgba(76, 175, 80, 0.4); }}
            }}
        """
    
    @staticmethod
    def danger_action_group():
        """危险操作分组框 - 带警告动画"""
        return f"""
            QGroupBox {{
                background-color: #fff8f0;
                border: 2px solid {UIColors.WARNING};
                border-radius: {UIRadius.LG};
                margin: {UISpacing.SM} 0;
                padding-top: {UISpacing.MD};
                font-weight: 600;
                color: {UIColors.WARNING_DARK};
                transition: {UITransitions.ALL_SMOOTH};
                animation: dangerPulse 4s ease-in-out infinite;
            }}
            QGroupBox:hover {{
                border-color: {UIColors.ERROR};
                background-color: #ffebee;
                box-shadow: 0 0 15px rgba(255, 152, 0, 0.3);
                animation: dangerWarning 0.5s ease-in-out infinite;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: {UISpacing.MD};
                padding: 0 {UISpacing.SM};
                background-color: #fff8f0;
                color: {UIColors.WARNING_DARK};
                border-radius: {UIRadius.SM};
                transition: {UITransitions.ALL_SMOOTH};
            }}
            QGroupBox:hover::title {{
                background-color: {UIColors.WARNING_LIGHT};
                color: {UIColors.ERROR};
                font-weight: 700;
            }}
            @keyframes dangerPulse {{
                0%, 100% {{ border-color: {UIColors.WARNING}; }}
                50% {{ border-color: #ff7043; }}
            }}
            @keyframes dangerWarning {{
                0%, 100% {{ transform: translateX(0); }}
                25% {{ transform: translateX(-1px); }}
                75% {{ transform: translateX(1px); }}
            }}
        """

class LabelStyles:
    """统一的标签样式类"""
    
    @staticmethod
    def status_success():
        """成功状态标签"""
        return f"""
            QLabel {{
                font-weight: 600;
                padding: {UISpacing.SM} {UISpacing.MD};
                border-radius: {UIRadius.SM};
                background-color: {UIColors.SUCCESS_LIGHT};
                color: {UIColors.SECONDARY_DARK};
                transition: all {UITransitions.FAST};
            }}
        """
    
    @staticmethod
    def status_warning():
        """警告状态标签"""
        return f"""
            QLabel {{
                font-weight: 600;
                padding: {UISpacing.SM} {UISpacing.MD};
                border-radius: {UIRadius.SM};
                background-color: {UIColors.WARNING_LIGHT};
                color: #ef6c00;
                transition: all {UITransitions.FAST};
            }}
        """
    
    @staticmethod
    def status_info():
        """信息状态标签"""
        return f"""
            QLabel {{
                font-weight: 600;
                padding: {UISpacing.SM} {UISpacing.MD};
                border-radius: {UIRadius.SM};
                background-color: {UIColors.INFO_LIGHT};
                color: {UIColors.PRIMARY_DARK};
                transition: all {UITransitions.FAST};
            }}
        """
    
    @staticmethod
    def info_label():
        """普通信息标签"""
        return f"""
            QLabel {{
                color: {UIColors.TEXT_SECONDARY};
                font-size: 12px;
                padding: {UISpacing.SM} {UISpacing.MD};
                background-color: {UIColors.GREY_100};
                border-radius: {UIRadius.SM};
                margin: {UISpacing.SM} {UISpacing.MD};
            }}
        """
    
    @staticmethod
    def title_label():
        """标题标签"""
        return f"""
            QLabel {{
                font-size: 36px;
                font-weight: bold;
                color: {UIColors.PRIMARY};
                background: transparent;
                margin: {UISpacing.XL};
            }}
        """
    
    @staticmethod
    def subtitle_label():
        """副标题标签"""
        return f"""
            QLabel {{
                font-size: 16px;
                color: {UIColors.TEXT_PRIMARY};
                background: transparent;
                margin: {UISpacing.MD};
            }}
        """
    
    @staticmethod
    def section_title():
        """章节标题"""
        return f"""
            QLabel {{
                font-size: 18px;
                font-weight: 600;
                color: {UIColors.PRIMARY};
                background: transparent;
                margin: {UISpacing.XL} 0 {UISpacing.MD} 0;
            }}
        """
    
    @staticmethod
    def feature_item():
        """功能列表项"""
        return f"""
            QLabel {{
                font-size: 14px;
                color: {UIColors.TEXT_PRIMARY};
                background: transparent;
                padding: {UISpacing.XS};
            }}
        """

class GroupBoxStyles:
    """统一的分组框样式"""
    
    @staticmethod
    def primary_group():
        """主要分组框样式"""
        return f"""
            QGroupBox {{
                background-color: {UIColors.SUCCESS_LIGHT};
                border: 2px solid {UIColors.SECONDARY};
                border-radius: {UIRadius.LG};
                margin: {UISpacing.MD} 0;
                padding-top: {UISpacing.XL};
                font-weight: 600;
                color: {UIColors.SECONDARY_DARK};
                transition: all {UITransitions.NORMAL};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: {UISpacing.LG};
                padding: 0 {UISpacing.MD};
                background-color: {UIColors.SUCCESS_LIGHT};
                color: {UIColors.SECONDARY_DARK};
            }}
            QGroupBox:hover {{
                border-color: {UIColors.SECONDARY_LIGHT};
                box-shadow: {UIShadows.SM};
            }}
        """
    
    @staticmethod
    def warning_group():
        """警告分组框样式"""
        return f"""
            QGroupBox {{
                background-color: {UIColors.WARNING_LIGHT};
                border: 2px solid {UIColors.WARNING};
                border-radius: {UIRadius.LG};
                margin: {UISpacing.MD} 0;
                padding-top: {UISpacing.XL};
                font-weight: 600;
                color: #e65100;
                transition: all {UITransitions.NORMAL};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: {UISpacing.LG};
                padding: 0 {UISpacing.MD};
                background-color: {UIColors.WARNING_LIGHT};
                color: #e65100;
            }}
            QGroupBox:hover {{
                border-color: #ffb74d;
                box-shadow: {UIShadows.SM};
            }}
        """

class ListStyles:
    """统一的列表样式"""
    
    @staticmethod
    def modern_list():
        """现代化列表样式"""
        return f"""
            QListWidget {{
                background-color: {UIColors.BACKGROUND};
                border: 1px solid {UIColors.GREY_300};
                border-radius: {UIRadius.MD};
                padding: {UISpacing.SM};
                outline: none;
                transition: border-color {UITransitions.FAST};
            }}
            QListWidget:focus {{
                border-color: {UIColors.PRIMARY};
                box-shadow: 0 0 0 2px {UIColors.INFO_LIGHT};
            }}
            QListWidget::item {{
                background-color: transparent;
                border: none;
                border-radius: {UIRadius.SM};
                padding: {UISpacing.MD};
                margin: {UISpacing.XS};
                color: {UIColors.TEXT_PRIMARY};
                border-left: 3px solid transparent;
                transition: all {UITransitions.FAST};
            }}
            QListWidget::item:hover {{
                background-color: {UIColors.GREY_100};
                border-left: 3px solid {UIColors.PRIMARY};
                transform: translateX(2px);
            }}
            QListWidget::item:selected {{
                background-color: {UIColors.INFO_LIGHT};
                color: {UIColors.PRIMARY_DARK};
                border-left: 3px solid {UIColors.PRIMARY};
                font-weight: 500;
                box-shadow: {UIShadows.SM};
            }}
        """

class ToolButtonStyles:
    """统一的工具按钮样式"""
    
    @staticmethod
    def modern_tool_button():
        """现代化工具按钮样式"""
        return f"""
            QToolButton {{
                border: none;
                border-radius: {UIRadius.SM};
                padding: {UISpacing.MD};
                margin: {UISpacing.XS};
                background-color: transparent;
                transition: all {UITransitions.FAST};
            }}
            QToolButton:hover {{
                background-color: {UIColors.INFO_LIGHT};
                transform: scale(1.05);
                box-shadow: {UIShadows.SM};
            }}
            QToolButton:pressed {{
                background-color: {UIColors.PRIMARY_LIGHT};
                transform: scale(0.98);
            }}
            QToolButton:checked {{
                background-color: {UIColors.PRIMARY};
                color: {UIColors.TEXT_INVERSE};
                box-shadow: {UIShadows.MD};
            }}
        """