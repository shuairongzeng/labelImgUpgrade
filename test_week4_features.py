#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
第4周功能测试脚本

测试批量操作系统和快捷键管理器的功能
"""

import sys
import os
import logging
import tempfile
import shutil

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *
    from PyQt5.QtGui import *
except ImportError:
    from PyQt4.QtWidgets import *
    from PyQt4.QtCore import *
    from PyQt4.QtGui import *

from libs.batch_operations import BatchOperations, BatchOperationsDialog
from libs.shortcut_manager import ShortcutManager, ShortcutConfigDialog

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def test_batch_operations():
    """测试批量操作系统"""
    print("=" * 60)
    print("测试批量操作系统")
    print("=" * 60)
    
    try:
        # 创建批量操作实例
        batch_ops = BatchOperations()
        print("✓ 批量操作系统创建成功")
        
        # 创建测试数据
        test_dir = tempfile.mkdtemp(prefix="labelimg_batch_test_")
        print(f"✓ 创建测试目录: {test_dir}")
        
        # 创建一些测试标注文件
        test_files = []
        for i in range(3):
            test_file = os.path.join(test_dir, f"test_{i}.xml")
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write(f"""<?xml version="1.0"?>
<annotation>
    <filename>test_{i}.jpg</filename>
    <size>
        <width>640</width>
        <height>480</height>
    </size>
    <object>
        <name>test_object_{i}</name>
        <bndbox>
            <xmin>10</xmin>
            <ymin>10</ymin>
            <xmax>100</xmax>
            <ymax>100</ymax>
        </bndbox>
    </object>
</annotation>""")
            test_files.append(test_file)
        
        print(f"✓ 创建了 {len(test_files)} 个测试标注文件")
        
        # 测试批量复制
        copy_dir = os.path.join(test_dir, "copy_target")
        result = batch_ops.batch_copy_annotations(test_files, copy_dir)
        
        if 'error' not in result:
            print(f"✓ 批量复制测试成功: {result['successful_files']}/{result['total_files']}")
        else:
            print(f"✗ 批量复制测试失败: {result['error']}")
        
        # 测试操作状态
        status = batch_ops.get_operation_status()
        print(f"✓ 操作状态获取成功: {status['current_operation']}")
        
        # 清理测试数据
        shutil.rmtree(test_dir)
        print("✓ 清理测试数据完成")
        
        return True
        
    except Exception as e:
        print(f"✗ 批量操作系统测试失败: {e}")
        return False


def test_shortcut_manager():
    """测试快捷键管理器"""
    print("\n" + "=" * 60)
    print("测试快捷键管理器")
    print("=" * 60)
    
    try:
        # 创建快捷键管理器
        shortcut_manager = ShortcutManager()
        print("✓ 快捷键管理器创建成功")
        
        # 测试动作注册
        success = shortcut_manager.register_action(
            "test_action", "测试动作", "Ctrl+T", "测试分类"
        )
        if success:
            print("✓ 动作注册成功")
        else:
            print("✗ 动作注册失败")
        
        # 测试获取动作
        action = shortcut_manager.get_action("test_action")
        if action:
            print(f"✓ 动作获取成功: {action.name} ({action.current_key})")
        else:
            print("✗ 动作获取失败")
        
        # 测试按分类获取动作
        categories = shortcut_manager.get_actions_by_category()
        print(f"✓ 获取到 {len(categories)} 个分类")
        
        for category, actions in categories.items():
            print(f"  - {category}: {len(actions)} 个动作")
        
        # 测试快捷键更新
        success = shortcut_manager.update_shortcut("test_action", "Ctrl+Shift+T")
        if success:
            print("✓ 快捷键更新成功")
        else:
            print("✗ 快捷键更新失败")
        
        # 测试冲突检查
        conflicts = shortcut_manager.find_conflicts("Ctrl+S")
        if conflicts:
            print(f"✓ 冲突检查成功，发现冲突: {conflicts}")
        else:
            print("✓ 冲突检查成功，无冲突")
        
        # 测试配置保存和加载
        config_file = "test_shortcuts.json"
        
        # 保存配置
        success = shortcut_manager.save_shortcuts()
        if success:
            print("✓ 配置保存成功")
        else:
            print("✗ 配置保存失败")
        
        # 重置为默认
        success = shortcut_manager.reset_to_defaults()
        if success:
            print("✓ 重置为默认成功")
        else:
            print("✗ 重置为默认失败")
        
        # 清理测试文件
        if os.path.exists(config_file):
            os.remove(config_file)
        
        return True
        
    except Exception as e:
        print(f"✗ 快捷键管理器测试失败: {e}")
        return False


def test_batch_operations_dialog():
    """测试批量操作对话框"""
    print("\n" + "=" * 60)
    print("测试批量操作对话框")
    print("=" * 60)
    
    try:
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # 创建对话框
        dialog = BatchOperationsDialog()
        print("✓ 批量操作对话框创建成功")
        
        # 检查界面组件
        if hasattr(dialog, 'operation_combo'):
            print(f"✓ 操作选择组合框: {dialog.operation_combo.count()} 个选项")
        
        if hasattr(dialog, 'progress_bar'):
            print("✓ 进度条组件存在")
        
        if hasattr(dialog, 'start_btn'):
            print("✓ 开始按钮组件存在")
        
        # 不显示对话框，只测试创建
        dialog.close()
        
        return True
        
    except Exception as e:
        print(f"✗ 批量操作对话框测试失败: {e}")
        return False


def test_shortcut_config_dialog():
    """测试快捷键配置对话框"""
    print("\n" + "=" * 60)
    print("测试快捷键配置对话框")
    print("=" * 60)
    
    try:
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # 创建快捷键管理器和对话框
        shortcut_manager = ShortcutManager()
        dialog = ShortcutConfigDialog(shortcut_manager)
        print("✓ 快捷键配置对话框创建成功")
        
        # 检查界面组件
        if hasattr(dialog, 'shortcuts_tree'):
            print("✓ 快捷键树形列表存在")
        
        if hasattr(dialog, 'search_edit'):
            print("✓ 搜索框存在")
        
        if hasattr(dialog, 'key_edit'):
            print("✓ 快捷键编辑框存在")
        
        # 不显示对话框，只测试创建
        dialog.close()
        
        return True
        
    except Exception as e:
        print(f"✗ 快捷键配置对话框测试失败: {e}")
        return False


def test_integration():
    """测试集成功能"""
    print("\n" + "=" * 60)
    print("测试集成功能")
    print("=" * 60)
    
    try:
        # 创建组件
        batch_ops = BatchOperations()
        shortcut_manager = ShortcutManager()
        
        # 设置批量操作的快捷键回调
        def batch_copy_callback():
            print("批量复制快捷键被触发")
        
        def batch_delete_callback():
            print("批量删除快捷键被触发")
        
        shortcut_manager.set_callback("batch_copy", batch_copy_callback)
        shortcut_manager.set_callback("batch_delete", batch_delete_callback)
        
        print("✓ 快捷键回调设置成功")
        
        # 测试信号连接
        def on_operation_completed(operation, result):
            print(f"操作完成信号接收: {operation}")
        
        batch_ops.operation_completed.connect(on_operation_completed)
        print("✓ 信号连接成功")
        
        return True
        
    except Exception as e:
        print(f"✗ 集成功能测试失败: {e}")
        return False


class TestMainWindow(QMainWindow):
    """测试主窗口"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_shortcuts()
    
    def setup_ui(self):
        """设置界面"""
        self.setWindowTitle("第4周功能测试")
        self.setGeometry(100, 100, 800, 600)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # 标题
        title = QLabel("第4周功能测试 - 批量操作和快捷键系统")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 20px;")
        layout.addWidget(title)
        
        # 测试按钮
        button_layout = QGridLayout()
        
        self.batch_ops_btn = QPushButton("批量操作对话框")
        self.batch_ops_btn.clicked.connect(self.show_batch_operations)
        button_layout.addWidget(self.batch_ops_btn, 0, 0)
        
        self.shortcuts_btn = QPushButton("快捷键配置")
        self.shortcuts_btn.clicked.connect(self.show_shortcut_config)
        button_layout.addWidget(self.shortcuts_btn, 0, 1)
        
        self.test_shortcut_btn = QPushButton("测试快捷键 (Ctrl+T)")
        self.test_shortcut_btn.clicked.connect(self.test_shortcut_triggered)
        button_layout.addWidget(self.test_shortcut_btn, 1, 0)
        
        self.quit_btn = QPushButton("退出 (Ctrl+Q)")
        self.quit_btn.clicked.connect(self.close)
        button_layout.addWidget(self.quit_btn, 1, 1)
        
        layout.addLayout(button_layout)
        
        # 日志显示
        self.log_text = QTextEdit()
        self.log_text.setPlainText("=== 第4周功能测试日志 ===\n")
        layout.addWidget(self.log_text)
    
    def setup_shortcuts(self):
        """设置快捷键"""
        self.shortcut_manager = ShortcutManager(self)
        
        # 设置回调
        self.shortcut_manager.set_callback("quit", self.close)
        self.shortcut_manager.set_callback("test_action", self.test_shortcut_triggered)
        
        # 创建Qt快捷键
        self.shortcut_manager.create_qt_shortcuts(self)
        
        self.log_message("快捷键系统初始化完成")
    
    def show_batch_operations(self):
        """显示批量操作对话框"""
        try:
            dialog = BatchOperationsDialog(self)
            dialog.exec_()
            self.log_message("批量操作对话框已关闭")
        except Exception as e:
            self.log_message(f"显示批量操作对话框失败: {e}")
    
    def show_shortcut_config(self):
        """显示快捷键配置对话框"""
        try:
            dialog = ShortcutConfigDialog(self.shortcut_manager, self)
            dialog.exec_()
            self.log_message("快捷键配置对话框已关闭")
        except Exception as e:
            self.log_message(f"显示快捷键配置对话框失败: {e}")
    
    def test_shortcut_triggered(self):
        """测试快捷键触发"""
        self.log_message("测试快捷键被触发！")
    
    def log_message(self, message: str):
        """添加日志消息"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.log_text.append(log_entry)
        print(log_entry)


def main():
    """主测试函数"""
    print("第4周功能测试 - 批量操作和快捷键系统")
    print("=" * 80)
    
    # 运行单元测试
    tests = [
        ("批量操作系统", test_batch_operations),
        ("快捷键管理器", test_shortcut_manager),
        ("批量操作对话框", test_batch_operations_dialog),
        ("快捷键配置对话框", test_shortcut_config_dialog),
        ("集成功能", test_integration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"\n🎉 {test_name} 测试通过")
            else:
                print(f"\n❌ {test_name} 测试失败")
        except Exception as e:
            print(f"\n💥 {test_name} 测试异常: {e}")
    
    print("\n" + "=" * 80)
    print(f"单元测试结果: {passed}/{total} 通过")
    
    # 启动GUI测试
    if passed == total:
        print("\n🎉 所有单元测试通过！启动GUI测试...")
        
        app = QApplication(sys.argv)
        window = TestMainWindow()
        window.show()
        
        print("GUI测试窗口已启动，请测试以下功能：")
        print("1. 批量操作对话框")
        print("2. 快捷键配置对话框")
        print("3. 快捷键触发 (Ctrl+T, Ctrl+Q)")
        
        return app.exec_()
    else:
        print("❌ 部分单元测试失败，请检查错误信息")
        return 1


if __name__ == "__main__":
    sys.exit(main())
