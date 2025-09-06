#!/usr/bin/env python3
import os
import sys

# 模拟labelImg的启动环境
sys.path.insert(0, '.')  # 添加当前目录
sys.path.insert(0, 'libs')  # 添加libs目录

print("Python路径:")
for p in sys.path[:5]:  # 只显示前5个路径
    print(f"  {p}")

print(f"当前工作目录: {os.getcwd()}")

# 测试导入
try:
    import batch_prediction_dialog
    print("PASS - batch_prediction_dialog模块导入成功")
    
    # 测试类导入
    from batch_prediction_dialog import BatchPredictionDialog
    print("PASS - BatchPredictionDialog类导入成功")
    
except Exception as e:
    print(f"FAIL - 批量预测对话框导入失败: {e}")
    import traceback
    traceback.print_exc()

# 测试在包环境中的AI面板导入
try:
    # 模拟作为包运行
    import libs.ai_assistant_panel as ai_panel
    print("PASS - AI面板作为包导入成功")
except Exception as e:
    print(f"INFO - AI面板作为包导入失败 (预期): {e}")

print("\\n测试完成")