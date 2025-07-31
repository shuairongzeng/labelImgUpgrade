#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试真实使用场景：模拟用户通过菜单打开目录的操作
"""

import sys
import os
import time
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from labelImg import MainWindow


class RealScenarioTester:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.main_window = None
        
    def test_real_scenario(self):
        """测试真实使用场景"""
        print("\n" + "="*60)
        print("测试真实使用场景：通过菜单打开目录")
        print("="*60)
        
        # 创建主窗口
        self.main_window = MainWindow()
        self.main_window.show()
        
        # 等待窗口初始化
        self.app.processEvents()
        time.sleep(1.0)
        
        # 测试目录路径
        test_dir = os.path.join(os.getcwd(), "test_images")
        print(f"📁 测试目录: {test_dir}")
        
        # 模拟用户通过菜单打开目录的操作
        # 这会调用open_dir_dialog中的逻辑
        print("🔄 模拟用户通过菜单打开目录...")
        
        # 设置目录路径并调用import_dir_images
        self.main_window.last_open_dir = test_dir
        self.main_window.dir_name = test_dir
        self.main_window.default_save_dir = test_dir  # 设置保存目录
        
        # 更新状态栏
        self.main_window.statusBar().showMessage('%s . Annotation will be saved to %s' %
                                                 ('Open Directory', self.main_window.default_save_dir))
        
        # 调用import_dir_images（这是open_dir_dialog中的关键调用）
        self.main_window.import_dir_images(test_dir)
        
        # 等待加载完成
        self.app.processEvents()
        time.sleep(2.0)
        
        # 检查第一张图片的标注框数量
        first_image_path = os.path.join(test_dir, "test_image_01.jpg")
        xml_path = os.path.join(test_dir, "test_image_01.xml")
        
        print(f"🖼️ 第一张图片: {first_image_path}")
        print(f"📄 标注文件: {xml_path}")
        
        # 检查当前加载的标注框数量
        label_count = self.main_window.label_list.count()
        canvas_shapes_count = len(self.main_window.canvas.shapes)
        
        print(f"📊 标签列表中的标注框数量: {label_count}")
        print(f"📊 画布中的标注框数量: {canvas_shapes_count}")
        
        # 从XML文件读取期望的标注框数量
        expected_count = self.count_objects_in_xml(xml_path)
        print(f"📊 XML文件中的标注框数量: {expected_count}")
        
        # 验证是否有重复
        if label_count == expected_count * 2:
            print("❌ 检测到重复加载！标注框数量是期望的2倍")
            print("❌ 修复失败")
            return False
        elif label_count == expected_count:
            print("✅ 没有重复加载，标注框数量正确")
            print("✅ 修复成功")
            return True
        else:
            print(f"⚠️ 意外的标注框数量: {label_count}")
            return False
            
    def count_objects_in_xml(self, xml_path):
        """从XML文件中计算标注框数量"""
        try:
            import xml.etree.ElementTree as ET
            tree = ET.parse(xml_path)
            root = tree.getroot()
            objects = root.findall('object')
            return len(objects)
        except Exception as e:
            print(f"❌ 解析XML文件失败: {e}")
            return 0
            
    def run_test(self):
        """运行测试"""
        try:
            success = self.test_real_scenario()
            return success
        except Exception as e:
            print(f"❌ 测试过程中发生错误: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            if self.main_window:
                self.main_window.close()
            self.app.quit()


def main():
    """主函数"""
    print("🚀 开始测试真实使用场景...")
    
    tester = RealScenarioTester()
    success = tester.run_test()
    
    if success:
        print("\n✅ 真实场景测试通过")
        return 0
    else:
        print("\n❌ 真实场景测试失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())
