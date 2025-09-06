import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'libs'))

try:
    from batch_prediction_dialog import BatchPredictionDialog
    print('PASS - 批量预测对话框导入成功')
except Exception as e:
    print(f'FAIL - 批量预测对话框导入失败: {e}')

try:
    from ai_assistant_panel import AIAssistantPanel
    print('PASS - AI面板导入成功')
except Exception as e:
    print(f'FAIL - AI面板导入失败: {e}')

print('导入测试完成')