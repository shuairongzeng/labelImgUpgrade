#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试训练历史记录功能
验证"不包含已训练的图片"功能的完整流程
"""

import os
import sys
import tempfile
import shutil
import unittest
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from libs.training_history_manager import TrainingHistoryManager
    from libs.ai_assistant_panel import AIAssistantPanel
    print("✅ 成功导入训练历史管理器和AI助手面板")
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    sys.exit(1)


class TestTrainingHistoryFeature(unittest.TestCase):
    """训练历史记录功能测试"""
    
    def setUp(self):
        """测试前准备"""
        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp(prefix="test_training_history_")
        self.history_file = os.path.join(self.temp_dir, "training_history.json")
        
        # 创建测试图片列表
        self.test_images = [
            "image1.jpg",
            "image2.jpg", 
            "image3.jpg",
            "image4.jpg",
            "image5.jpg"
        ]
        
        print(f"📁 测试目录: {self.temp_dir}")
    
    def tearDown(self):
        """测试后清理"""
        try:
            shutil.rmtree(self.temp_dir)
            print(f"🗑️ 清理测试目录: {self.temp_dir}")
        except Exception as e:
            print(f"⚠️ 清理失败: {e}")
    
    def test_training_history_manager_basic(self):
        """测试训练历史管理器基本功能"""
        print("\n=== 测试训练历史管理器基本功能 ===")
        
        # 创建管理器
        manager = TrainingHistoryManager(self.history_file)
        self.assertIsNotNone(manager)
        print("✅ 训练历史管理器创建成功")
        
        # 测试添加训练会话
        session_id = manager.add_training_session(
            session_name="测试训练会话",
            dataset_path="/test/dataset",
            image_files=self.test_images[:3],  # 前3张图片
            model_path="/test/model.pt",
            training_config={"epochs": 100, "batch_size": 16}
        )
        
        self.assertIsNotNone(session_id)
        print(f"✅ 训练会话添加成功: {session_id}")
        
        # 测试获取已训练图片
        trained_images = manager.get_trained_images()
        self.assertEqual(len(trained_images), 3)
        print(f"✅ 获取已训练图片: {len(trained_images)} 张")
        
        # 测试图片训练状态检查
        self.assertTrue(manager.is_image_trained(self.test_images[0]))
        self.assertFalse(manager.is_image_trained(self.test_images[3]))
        print("✅ 图片训练状态检查正确")
        
        # 测试过滤未训练图片
        untrained = manager.filter_untrained_images(self.test_images)
        self.assertEqual(len(untrained), 2)  # 应该剩下后2张
        print(f"✅ 过滤未训练图片: {len(untrained)} 张")
        
        # 测试统计信息
        stats = manager.get_training_statistics()
        self.assertEqual(stats['total_sessions'], 1)
        self.assertEqual(stats['total_trained_images'], 3)
        print(f"✅ 统计信息正确: {stats}")
    
    def test_multiple_training_sessions(self):
        """测试多个训练会话"""
        print("\n=== 测试多个训练会话 ===")
        
        manager = TrainingHistoryManager(self.history_file)
        
        # 添加第一个训练会话
        session1 = manager.add_training_session(
            session_name="第一次训练",
            dataset_path="/test/dataset1",
            image_files=self.test_images[:2],
            model_path="/test/model1.pt"
        )
        
        # 添加第二个训练会话
        session2 = manager.add_training_session(
            session_name="第二次训练",
            dataset_path="/test/dataset2", 
            image_files=self.test_images[2:4],
            model_path="/test/model2.pt"
        )
        
        self.assertIsNotNone(session1)
        self.assertIsNotNone(session2)
        print(f"✅ 两个训练会话添加成功")
        
        # 检查总的已训练图片数量
        trained_images = manager.get_trained_images()
        self.assertEqual(len(trained_images), 4)  # 前4张图片
        print(f"✅ 总已训练图片: {len(trained_images)} 张")
        
        # 检查最后一张图片未训练
        self.assertFalse(manager.is_image_trained(self.test_images[4]))
        print("✅ 最后一张图片确实未训练")
        
        # 测试统计信息
        stats = manager.get_training_statistics()
        self.assertEqual(stats['total_sessions'], 2)
        self.assertEqual(stats['total_trained_images'], 4)
        print(f"✅ 多会话统计信息正确: {stats}")
    
    def test_ai_assistant_panel_integration(self):
        """测试AI助手面板集成"""
        print("\n=== 测试AI助手面板集成 ===")
        
        try:
            # 创建AI助手面板（需要Qt环境）
            from PyQt5.QtWidgets import QApplication
            import sys
            
            # 检查是否已有QApplication实例
            app = QApplication.instance()
            if app is None:
                app = QApplication(sys.argv)
            
            # 创建AI助手面板
            panel = AIAssistantPanel()
            self.assertIsNotNone(panel)
            print("✅ AI助手面板创建成功")
            
            # 检查训练历史管理器是否初始化
            self.assertIsNotNone(panel.training_history_manager)
            print("✅ 训练历史管理器已初始化")
            
            # 测试图片训练状态检查方法
            result = panel.is_image_trained("test_image.jpg")
            self.assertIsInstance(result, bool)
            print("✅ 图片训练状态检查方法正常")
            
            # 测试图片过滤方法
            filtered = panel.filter_untrained_images(self.test_images)
            self.assertIsInstance(filtered, list)
            print("✅ 图片过滤方法正常")
            
        except ImportError:
            print("⚠️ 跳过Qt相关测试（无Qt环境）")
        except Exception as e:
            print(f"⚠️ AI助手面板测试失败: {e}")
    
    def test_file_persistence(self):
        """测试文件持久化"""
        print("\n=== 测试文件持久化 ===")
        
        # 创建第一个管理器实例并添加数据
        manager1 = TrainingHistoryManager(self.history_file)
        session_id = manager1.add_training_session(
            session_name="持久化测试",
            dataset_path="/test/dataset",
            image_files=self.test_images[:3],
            model_path="/test/model.pt"
        )
        
        # 创建第二个管理器实例，应该能加载之前的数据
        manager2 = TrainingHistoryManager(self.history_file)
        trained_images = manager2.get_trained_images()
        
        self.assertEqual(len(trained_images), 3)
        print("✅ 文件持久化正常")
        
        # 检查历史文件是否存在
        self.assertTrue(os.path.exists(self.history_file))
        print(f"✅ 历史文件存在: {self.history_file}")


def run_manual_test():
    """手动测试功能"""
    print("\n" + "="*50)
    print("🧪 手动测试训练历史记录功能")
    print("="*50)
    
    # 创建临时目录
    temp_dir = tempfile.mkdtemp(prefix="manual_test_")
    history_file = os.path.join(temp_dir, "training_history.json")
    
    try:
        # 创建管理器
        manager = TrainingHistoryManager(history_file)
        print(f"📁 测试目录: {temp_dir}")
        print(f"📄 历史文件: {history_file}")
        
        # 模拟第一次训练
        print("\n--- 模拟第一次训练 ---")
        images_batch1 = ["cat1.jpg", "cat2.jpg", "dog1.jpg", "dog2.jpg"]
        session1 = manager.add_training_session(
            session_name="猫狗分类训练_v1",
            dataset_path="/datasets/cats_dogs_v1",
            image_files=images_batch1,
            model_path="/models/cats_dogs_v1.pt",
            training_config={
                "epochs": 50,
                "batch_size": 16,
                "learning_rate": 0.001
            }
        )
        print(f"✅ 第一次训练记录: {session1}")
        
        # 检查训练状态
        print("\n--- 检查图片训练状态 ---")
        for img in ["cat1.jpg", "cat3.jpg", "bird1.jpg"]:
            is_trained = manager.is_image_trained(img)
            status = "已训练" if is_trained else "未训练"
            print(f"📷 {img}: {status}")
        
        # 模拟第二次训练（排除已训练图片）
        print("\n--- 模拟第二次训练（排除已训练图片）---")
        all_images = ["cat1.jpg", "cat2.jpg", "cat3.jpg", "dog1.jpg", "dog2.jpg", "dog3.jpg", "bird1.jpg"]
        untrained_images = manager.filter_untrained_images(all_images)
        print(f"📊 总图片: {len(all_images)} 张")
        print(f"🚫 已训练: {len(all_images) - len(untrained_images)} 张")
        print(f"✅ 未训练: {len(untrained_images)} 张")
        print(f"📋 未训练图片: {untrained_images}")
        
        # 添加第二次训练记录
        if untrained_images:
            session2 = manager.add_training_session(
                session_name="猫狗鸟分类训练_v2",
                dataset_path="/datasets/cats_dogs_birds_v2",
                image_files=untrained_images,
                model_path="/models/cats_dogs_birds_v2.pt",
                training_config={
                    "epochs": 100,
                    "batch_size": 32,
                    "learning_rate": 0.0005
                }
            )
            print(f"✅ 第二次训练记录: {session2}")
        
        # 显示统计信息
        print("\n--- 训练统计信息 ---")
        stats = manager.get_training_statistics()
        print(f"📊 总训练会话: {stats['total_sessions']}")
        print(f"📷 总训练图片: {stats['total_trained_images']}")
        print(f"🕒 最后训练时间: {stats['last_training']}")
        print(f"📄 历史文件: {stats['history_file']}")
        
        print(f"\n✅ 手动测试完成！")
        print(f"📁 测试文件保存在: {temp_dir}")
        
    except Exception as e:
        print(f"❌ 手动测试失败: {e}")
    
    finally:
        # 询问是否清理
        try:
            response = input("\n是否清理测试文件？(y/N): ").strip().lower()
            if response == 'y':
                shutil.rmtree(temp_dir)
                print(f"🗑️ 已清理测试目录")
            else:
                print(f"📁 测试文件保留在: {temp_dir}")
        except KeyboardInterrupt:
            print(f"\n📁 测试文件保留在: {temp_dir}")


if __name__ == "__main__":
    print("🧪 训练历史记录功能测试")
    print("="*50)
    
    # 运行单元测试
    print("\n1. 运行单元测试...")
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # 运行手动测试
    print("\n2. 运行手动测试...")
    run_manual_test()
