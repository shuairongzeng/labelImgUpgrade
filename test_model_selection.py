#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试模型选择功能
"""

import sys
import os
import logging

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_training_config():
    """测试训练配置类"""
    try:
        from libs.ai_assistant.yolo_trainer import TrainingConfig
        
        # 测试预训练模型配置
        config1 = TrainingConfig(
            dataset_config="test.yaml",
            epochs=100,
            batch_size=16,
            learning_rate=0.01,
            model_type="pretrained",
            model_path="yolov8n.pt",
            model_name="yolov8n",
            device="cpu",
            output_dir="runs/train"
        )
        
        print("✅ 预训练模型配置创建成功:")
        print(f"   模型类型: {config1.model_type}")
        print(f"   模型路径: {config1.model_path}")
        print(f"   模型名称: {config1.model_name}")
        
        # 测试自定义模型配置
        config2 = TrainingConfig(
            dataset_config="test.yaml",
            epochs=100,
            batch_size=16,
            learning_rate=0.01,
            model_type="custom",
            model_path="models/custom/my_model.pt",
            model_name="my_model.pt",
            device="cpu",
            output_dir="runs/train"
        )
        
        print("\n✅ 自定义模型配置创建成功:")
        print(f"   模型类型: {config2.model_type}")
        print(f"   模型路径: {config2.model_path}")
        print(f"   模型名称: {config2.model_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ 训练配置测试失败: {str(e)}")
        return False

def test_model_manager():
    """测试模型管理器"""
    try:
        from libs.ai_assistant.model_manager import ModelManager
        
        # 创建模型管理器
        manager = ModelManager()
        
        # 扫描模型
        models = manager.scan_models()
        print(f"\n🔍 扫描到 {len(models)} 个模型:")
        for model in models:
            print(f"   📄 {model}")
            
        return True
        
    except Exception as e:
        print(f"❌ 模型管理器测试失败: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("🧪 开始测试模型选择功能...")
    
    # 测试训练配置
    print("\n" + "="*50)
    print("📋 测试训练配置类")
    print("="*50)
    config_ok = test_training_config()
    
    # 测试模型管理器
    print("\n" + "="*50)
    print("📦 测试模型管理器")
    print("="*50)
    manager_ok = test_model_manager()
    
    # 总结
    print("\n" + "="*50)
    print("📊 测试结果总结")
    print("="*50)
    print(f"训练配置类: {'✅ 通过' if config_ok else '❌ 失败'}")
    print(f"模型管理器: {'✅ 通过' if manager_ok else '❌ 失败'}")
    
    if config_ok and manager_ok:
        print("\n🎉 所有测试通过！模型选择功能修复成功。")
        return True
    else:
        print("\n⚠️ 部分测试失败，请检查相关代码。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
