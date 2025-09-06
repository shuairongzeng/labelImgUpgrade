#!/usr/bin/env python3
import os
import sys
import tempfile

print("当前工作目录:", os.getcwd())
print("临时目录:", tempfile.gettempdir())
print("Python版本:", sys.version)

# 测试简单的路径操作
test_path = tempfile.gettempdir()
print(f"测试路径: {test_path}")
print(f"路径存在: {os.path.exists(test_path)}")

# 添加libs并测试导入
libs_path = os.path.join(os.getcwd(), 'libs')
print(f"Libs路径: {libs_path}")
print(f"Libs存在: {os.path.exists(libs_path)}")

if libs_path not in sys.path:
    sys.path.insert(0, libs_path)

try:
    print("尝试导入batch_prediction_dialog...")
    import batch_prediction_dialog
    print("导入成功!")
    
    print("尝试创建BatchPredictionDialog实例...")
    # 不创建实际的QApplication，只测试类导入
    BatchPredictionDialog = batch_prediction_dialog.BatchPredictionDialog
    print("类导入成功!")
    
except Exception as e:
    print(f"导入失败: {e}")
    import traceback
    traceback.print_exc()