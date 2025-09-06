#!/usr/bin/env python3
"""
测试默认路径设置
"""
import sys
import os
import tempfile

# 添加libs目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'libs'))

from batch_prediction_dialog import BatchPredictionDialog

def test_path_initialization():
    """测试路径初始化"""
    print("=== 测试默认路径设置 ===")
    
    # 测试1: 空路径
    print("\\n测试1: 空路径")
    dialog1 = BatchPredictionDialog(None, "")
    print(f"  default_path: '{dialog1.default_path}'")
    print(f"  current_path: '{dialog1.current_path}'")
    
    # 测试2: 有效路径
    test_path = tempfile.gettempdir()
    print(f"\\n测试2: 有效路径 ({test_path})")
    dialog2 = BatchPredictionDialog(None, test_path)
    print(f"  default_path: '{dialog2.default_path}'")
    print(f"  current_path: '{dialog2.current_path}'")
    
    # 测试3: 不存在的路径
    fake_path = "/this/path/does/not/exist"
    print(f"\\n测试3: 不存在的路径 ({fake_path})")
    dialog3 = BatchPredictionDialog(None, fake_path)
    print(f"  default_path: '{dialog3.default_path}'")
    print(f"  current_path: '{dialog3.current_path}'")
    
    # 测试4: 当前工作目录
    cwd = os.getcwd()
    print(f"\\n测试4: 当前工作目录 ({cwd})")
    dialog4 = BatchPredictionDialog(None, cwd)
    print(f"  default_path: '{dialog4.default_path}'")
    print(f"  current_path: '{dialog4.current_path}'")
    
    print("\\n=== 路径初始化测试完成 ===")

def test_mock_parent():
    """测试模拟父窗口"""
    print("\\n=== 测试模拟父窗口路径获取 ===")
    
    class MockParent:
        def __init__(self):
            self.lastOpenDir = tempfile.gettempdir()
            self.filePath = os.path.join(tempfile.gettempdir(), "test.jpg")
            self.currentPath = tempfile.gettempdir()
            self.dirName = tempfile.gettempdir()
    
    mock_parent = MockParent()
    print(f"模拟父窗口属性:")
    print(f"  lastOpenDir: {mock_parent.lastOpenDir}")
    print(f"  filePath: {mock_parent.filePath}")
    print(f"  currentPath: {mock_parent.currentPath}")
    print(f"  dirName: {mock_parent.dirName}")
    
    # 测试不同属性的获取
    test_path = mock_parent.lastOpenDir
    print(f"\\n使用路径: {test_path}")
    dialog = BatchPredictionDialog(None, test_path)
    print(f"  对话框current_path: '{dialog.current_path}'")

if __name__ == '__main__':
    try:
        test_path_initialization()
        test_mock_parent()
        print("\\n所有测试完成!")
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()