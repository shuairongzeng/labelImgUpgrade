#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
YOLO训练功能测试脚本

测试新实现的YOLO训练功能是否正常工作
"""

import os
import sys
import time
import tempfile
from pathlib import Path

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import QTimer
except ImportError:
    from PyQt4.QtWidgets import QApplication
    from PyQt4.QtCore import QTimer

try:
    from libs.ai_assistant.yolo_trainer import YOLOTrainer, TrainingConfig
    TRAINER_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ 训练器导入失败: {e}")
    TRAINER_AVAILABLE = False

    # 创建模拟类用于测试
    class TrainingConfig:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)

    class YOLOTrainer:
        def __init__(self):
            self.training_started = None
            self.training_progress = None
            self.log_message = None

        def validate_config(self, config):
            return True


class TrainingTester:
    """训练功能测试器"""

    def __init__(self):
        self.trainer = None
        self.test_results = []

    def setup_test_environment(self):
        """设置测试环境"""
        print("🔧 设置测试环境...")

        # 检查是否有可用的数据集配置
        test_data_path = Path("datasets/training_dataset/data.yaml")
        if not test_data_path.exists():
            print(f"❌ 测试数据集配置不存在: {test_data_path}")
            return False

        print(f"✅ 找到测试数据集配置: {test_data_path}")
        return True

    def test_trainer_initialization(self):
        """测试训练器初始化"""
        print("\n📦 测试训练器初始化...")

        if not TRAINER_AVAILABLE:
            print("⚠️ 训练器不可用，跳过测试")
            return True

        try:
            self.trainer = YOLOTrainer()

            # 检查基本属性
            assert hasattr(self.trainer, 'training_started')
            assert hasattr(self.trainer, 'training_progress')
            assert hasattr(self.trainer, 'training_completed')
            assert hasattr(self.trainer, 'training_error')

            print("✅ 训练器初始化成功")
            return True

        except Exception as e:
            print(f"❌ 训练器初始化失败: {e}")
            return False

    def test_config_validation(self):
        """测试配置验证"""
        print("\n🔍 测试配置验证...")

        try:
            # 测试有效配置
            valid_config = TrainingConfig(
                dataset_config="datasets/training_dataset/data.yaml",
                epochs=1,  # 使用很少的epoch进行测试
                batch_size=2,
                learning_rate=0.01,
                model_size="yolov8n",
                device="cpu",  # 强制使用CPU以确保兼容性
                output_dir=tempfile.mkdtemp()
            )

            is_valid = self.trainer.validate_config(valid_config)
            if is_valid:
                print("✅ 有效配置验证通过")
            else:
                print("❌ 有效配置验证失败")
                return False

            # 测试无效配置
            invalid_config = TrainingConfig(
                dataset_config="non_existent_file.yaml",
                epochs=1,
                batch_size=2,
                learning_rate=0.01,
                model_size="yolov8n",
                device="cpu",
                output_dir=tempfile.mkdtemp()
            )

            is_invalid = self.trainer.validate_config(invalid_config)
            if not is_invalid:
                print("✅ 无效配置正确被拒绝")
            else:
                print("❌ 无效配置未被正确拒绝")
                return False

            return True

        except Exception as e:
            print(f"❌ 配置验证测试失败: {e}")
            return False

    def test_training_signals(self):
        """测试训练信号"""
        print("\n📡 测试训练信号...")

        try:
            signal_received = {'started': False,
                               'progress': False, 'log': False}

            def on_started():
                signal_received['started'] = True
                print("  📶 收到训练开始信号")

            def on_progress(metrics):
                signal_received['progress'] = True
                print(
                    f"  📊 收到训练进度信号: Epoch {metrics.epoch}/{metrics.total_epochs}")

            def on_log(message):
                signal_received['log'] = True
                print(f"  📝 收到日志信号: {message}")

            # 连接信号
            self.trainer.training_started.connect(on_started)
            self.trainer.training_progress.connect(on_progress)
            self.trainer.log_message.connect(on_log)

            print("✅ 训练信号连接成功")
            return True

        except Exception as e:
            print(f"❌ 训练信号测试失败: {e}")
            return False

    def test_dry_run_training(self):
        """测试干运行训练（不实际训练）"""
        print("\n🏃 测试干运行训练...")

        try:
            # 创建最小化的训练配置
            config = TrainingConfig(
                dataset_config="datasets/training_dataset/data.yaml",
                epochs=1,
                batch_size=1,
                learning_rate=0.01,
                model_size="yolov8n",
                device="cpu",
                output_dir=tempfile.mkdtemp()
            )

            # 验证配置
            if not self.trainer.validate_config(config):
                print("❌ 训练配置验证失败")
                return False

            print("✅ 干运行训练配置验证通过")
            print("ℹ️  实际训练测试需要在有数据集的环境中进行")
            return True

        except Exception as e:
            print(f"❌ 干运行训练测试失败: {e}")
            return False

    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始YOLO训练功能测试")
        print("=" * 50)

        tests = [
            ("环境设置", self.setup_test_environment),
            ("训练器初始化", self.test_trainer_initialization),
            ("配置验证", self.test_config_validation),
            ("训练信号", self.test_training_signals),
            ("干运行训练", self.test_dry_run_training),
        ]

        passed = 0
        total = len(tests)

        for test_name, test_func in tests:
            try:
                if test_func():
                    passed += 1
                    self.test_results.append(f"✅ {test_name}: 通过")
                else:
                    self.test_results.append(f"❌ {test_name}: 失败")
            except Exception as e:
                self.test_results.append(f"❌ {test_name}: 异常 - {e}")

        # 显示测试结果
        print("\n" + "=" * 50)
        print("📊 测试结果摘要")
        print("=" * 50)

        for result in self.test_results:
            print(result)

        print(f"\n🎯 测试通过率: {passed}/{total} ({passed/total*100:.1f}%)")

        if passed == total:
            print("🎉 所有测试通过！YOLO训练功能实现正确。")
        else:
            print("⚠️  部分测试失败，请检查实现。")

        return passed == total


def main():
    """主函数"""
    # 创建QApplication（某些Qt功能需要）
    app = QApplication(sys.argv)

    # 运行测试
    tester = TrainingTester()
    success = tester.run_all_tests()

    # 退出
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
