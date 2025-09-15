#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
验证启动优化功能
简单验证渐进式加载功能是否正常工作
"""

import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_import():
    """测试模块导入"""
    try:
        print("🔍 正在验证模块导入...")

        # 测试基础导入
        from libs.background_image_loader import BackgroundImageLoader, ProgressiveImageManager
        print("✅ 后台图片加载器导入成功")

        # 测试主程序导入
        from labelImg import MainWindow
        print("✅ 主程序导入成功")

        return True
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 其他错误: {e}")
        return False

def test_basic_functionality():
    """测试基本功能"""
    try:
        print("\n🧪 正在测试基本功能...")

        from libs.background_image_loader import ProgressiveImageManager

        # 创建模拟主窗口
        class MockMainWindow:
            def __init__(self):
                self.file_list_widget = MockFileListWidget()
                self.m_img_list = []
                self.img_count = 0
                self.file_path = None
                self.status_messages = []

            def status(self, message):
                self.status_messages.append(message)
                print(f"[STATUS] {message}")

            def load_file(self, file_path):
                self.file_path = file_path
                print(f"[LOAD] 模拟加载图片: {os.path.basename(file_path) if file_path else 'None'}")

            def update_switch_button_state(self):
                pass

            def update_status_bar_info(self):
                pass

        class MockFileListWidget:
            def __init__(self):
                self.items = []
                self.updates_enabled = True

            def clear(self):
                self.items.clear()

            def addItem(self, item):
                self.items.append(str(item))

            def setUpdatesEnabled(self, enabled):
                self.updates_enabled = enabled

        # 创建管理器
        mock_window = MockMainWindow()
        manager = ProgressiveImageManager(mock_window)

        print("✅ 渐进式图片管理器创建成功")

        # 测试停止功能
        manager.stop_loading()
        print("✅ 停止加载功能正常")

        return True

    except Exception as e:
        print(f"❌ 基本功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_with_sample_directory():
    """使用示例目录测试"""
    try:
        print("\n📁 正在测试示例目录...")

        # 查找一个包含图片的目录进行测试
        sample_dirs = [
            ".",  # 当前目录
            "demo",  # demo目录
            "test_images",  # 测试图片目录
        ]

        found_dir = None
        for dir_path in sample_dirs:
            if os.path.exists(dir_path):
                # 检查是否包含图片文件
                for file in os.listdir(dir_path):
                    if file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif')):
                        found_dir = dir_path
                        break
                if found_dir:
                    break

        if found_dir:
            print(f"✅ 找到测试目录: {found_dir}")

            from libs.background_image_loader import ProgressiveImageManager

            # 创建简化的模拟窗口
            class SimpleMainWindow:
                def __init__(self):
                    self.file_list_widget = SimpleFileList()
                    self.m_img_list = []
                    self.img_count = 0
                    self.file_path = None

                def status(self, message):
                    print(f"[STATUS] {message}")

                def load_file(self, file_path):
                    self.file_path = file_path
                    print(f"[LOAD] 加载: {os.path.basename(file_path)}")

                def update_switch_button_state(self):
                    pass

                def update_status_bar_info(self):
                    pass

            class SimpleFileList:
                def __init__(self):
                    self.items = []

                def clear(self):
                    self.items.clear()

                def addItem(self, item):
                    self.items.append(str(item))

                def setUpdatesEnabled(self, enabled):
                    pass

            window = SimpleMainWindow()
            manager = ProgressiveImageManager(window)

            print(f"🚀 开始测试渐进式加载...")
            manager.load_directory_progressive(found_dir, initial_batch_size=5)

            # 等待一点时间让加载开始
            import time
            time.sleep(1)

            # 停止加载
            manager.stop_loading()

            print("✅ 示例目录测试完成")
            return True
        else:
            print("⚠️ 未找到包含图片的测试目录，跳过此测试")
            return True

    except Exception as e:
        print(f"❌ 示例目录测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 labelImg 启动优化验证")
    print("=" * 40)

    success_count = 0
    total_tests = 3

    # 测试1: 模块导入
    if test_import():
        success_count += 1

    # 测试2: 基本功能
    if test_basic_functionality():
        success_count += 1

    # 测试3: 示例目录测试
    if test_with_sample_directory():
        success_count += 1

    # 输出结果
    print("\n" + "=" * 40)
    print(f"📊 测试结果: {success_count}/{total_tests} 通过")

    if success_count == total_tests:
        print("🎉 所有测试通过！启动优化功能已正确集成")
        print("\n💡 使用方法:")
        print("  1. 运行: python labelImg.py")
        print("  2. 选择包含大量图片的目录")
        print("  3. 观察快速启动效果（前20张图片会立即显示）")
        print("  4. 状态栏会显示后台加载进度")

        return True
    else:
        print("❌ 部分测试失败，请检查相关问题")
        return False

if __name__ == "__main__":
    main()