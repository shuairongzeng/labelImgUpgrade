#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
真实用户体验测试：模拟用户首次打开模型导出对话框的体验

这个测试脚本会：
1. 创建一个真实的GUI窗口
2. 模拟用户首次打开模型导出对话框
3. 检查模型详细信息是否立即显示
4. 提供可视化的测试结果
"""

import sys
import os
import tempfile
import yaml
import csv
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_test_environment():
    """创建测试环境"""
    temp_dir = tempfile.mkdtemp()
    
    # 创建训练目录结构
    train_dir = os.path.join(temp_dir, "runs", "train", "best_model_test")
    weights_dir = os.path.join(train_dir, "weights")
    os.makedirs(weights_dir, exist_ok=True)
    
    # 创建best.pt模型文件
    best_model = os.path.join(weights_dir, "best.pt")
    with open(best_model, 'wb') as f:
        f.write(b'mock best model data' * 2000)  # 约32KB
    
    # 创建训练配置文件
    args_file = os.path.join(train_dir, "args.yaml")
    config_data = {
        'epochs': 200,
        'batch': 32,
        'data': 'datasets/custom_data.yaml',
        'model': 'yolov8s.pt',
        'lr0': 0.01,
        'imgsz': 640
    }
    
    with open(args_file, 'w', encoding='utf-8') as f:
        yaml.dump(config_data, f, default_flow_style=False)
    
    # 创建优秀的训练结果
    results_data = [
        ['epoch', 'metrics/mAP50(B)', 'metrics/mAP50-95(B)', 'metrics/precision(B)', 'metrics/recall(B)'],
        ['199', '0.923', '0.756', '0.945', '0.912']  # 优秀性能
    ]
    
    results_file = os.path.join(train_dir, "results.csv")
    with open(results_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(results_data)
    
    return temp_dir, best_model

def test_real_user_experience():
    """测试真实用户体验"""
    print("🎭 开始真实用户体验测试...")
    print("   模拟用户首次打开模型导出对话框")
    
    try:
        from PyQt5.QtWidgets import QApplication, QMessageBox
        from PyQt5.QtCore import QTimer
        from libs.model_export_dialog import ModelExportDialog
        
        # 创建应用
        app = QApplication(sys.argv)
        
        # 创建测试环境
        temp_dir, best_model = create_test_environment()
        print(f"✅ 创建测试环境: {best_model}")
        
        # 创建对话框（模拟用户点击菜单）
        print("\n👤 用户操作：点击菜单 -> 导出模型")
        dialog = ModelExportDialog()
        
        # 显示对话框
        dialog.show()
        print("✅ 对话框显示成功")
        
        # 等待延迟初始化完成（模拟真实加载时间）
        print("⏳ 等待模型列表加载...")
        
        def check_initial_state():
            """检查初始状态"""
            print("\n🔍 检查对话框初始状态:")
            
            # 检查模型下拉框
            model_count = dialog.model_combo.count()
            print(f"  模型下拉框选项数量: {model_count}")
            
            if model_count > 0:
                current_index = dialog.model_combo.currentIndex()
                if current_index >= 0:
                    selected_text = dialog.model_combo.currentText()
                    selected_path = dialog.model_combo.itemData(current_index)
                    print(f"  当前选中模型: {selected_text}")
                    print(f"  模型路径: {selected_path}")
                    print("    ✅ 模型已自动选择")
                else:
                    print("    ❌ 没有模型被选中")
                    return False
            else:
                print("    ⚠️ 没有找到可用模型")
            
            # 检查模型名称标签
            model_name_text = dialog.model_name_label.text()
            print(f"  模型名称显示: {model_name_text}")
            
            if model_name_text and "❌" not in model_name_text and "请选择" not in model_name_text:
                print("    ✅ 模型名称信息已显示")
            else:
                print("    ❌ 模型名称信息未显示")
                return False
            
            # 检查性能指标
            if hasattr(dialog, 'map50_bar'):
                mAP50_value = dialog.map50_bar.value()
                print(f"  mAP50 性能指标: {mAP50_value}%")
                
                if mAP50_value > 0:
                    print("    ✅ 性能指标已显示")
                else:
                    print("    ❌ 性能指标未显示")
                    return False
            
            # 检查文件名
            filename = dialog.output_name_edit.text()
            print(f"  自动生成文件名: {filename}")
            
            if filename and filename.strip():
                print("    ✅ 文件名已自动生成")
            else:
                print("    ❌ 文件名未自动生成")
                return False
            
            print("\n🎉 用户体验测试通过！")
            print("   用户首次打开对话框时，所有信息都能立即显示")
            
            # 显示成功消息
            msg = QMessageBox()
            msg.setWindowTitle("测试结果")
            msg.setText("✅ 模型导出对话框初始化修复成功！\n\n"
                       "现在用户首次打开对话框时：\n"
                       "• 最佳模型会自动选择\n"
                       "• 模型详细信息立即显示\n"
                       "• 性能指标正确显示\n"
                       "• 文件名自动生成\n\n"
                       "用户体验得到显著改善！")
            msg.setIcon(QMessageBox.Information)
            msg.exec_()
            
            return True
        
        # 延迟检查，模拟真实的加载过程
        QTimer.singleShot(500, check_initial_state)
        
        # 运行应用（显示对话框）
        # 注意：这里不会阻塞，因为我们只是测试初始化
        app.processEvents()
        
        # 等待一段时间让用户看到结果
        import time
        time.sleep(2)
        
        # 手动调用检查函数
        result = check_initial_state()
        
        # 清理
        dialog.close()
        import shutil
        shutil.rmtree(temp_dir)
        
        return result
        
    except Exception as e:
        print(f"❌ 真实用户体验测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🎭 模型导出对话框 - 真实用户体验测试")
    print("=" * 60)
    
    success = test_real_user_experience()
    
    if success:
        print("\n" + "=" * 60)
        print("🎉 测试成功！用户体验问题已修复")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ 测试失败！需要进一步调试")
        print("=" * 60)
    
    sys.exit(0 if success else 1)
