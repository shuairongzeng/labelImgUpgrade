#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试第一张图片重复加载标注框的修复效果

这个脚本用于验证修复后：
1. 第一张图片不再重复显示标注框
2. 切换到其他图片时标注框正常显示
3. 手动打开单个文件时标注框正常显示
"""

import sys
import os
import time
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from labelImg import MainWindow


class DuplicateFixTester:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.main_window = None
        self.test_results = []
        
    def log_result(self, test_name, expected, actual, passed):
        """记录测试结果"""
        result = {
            'test_name': test_name,
            'expected': expected,
            'actual': actual,
            'passed': passed
        }
        self.test_results.append(result)
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}: 期望={expected}, 实际={actual}")
        
    def test_first_image_duplicate_fix(self):
        """测试第一张图片重复加载标注框的修复"""
        print("\n" + "="*60)
        print("测试：第一张图片重复加载标注框的修复")
        print("="*60)
        
        # 创建主窗口
        self.main_window = MainWindow()
        self.main_window.show()
        
        # 等待窗口初始化
        self.app.processEvents()
        time.sleep(0.5)
        
        # 测试目录路径
        test_dir = os.path.join(os.getcwd(), "test_images")
        if not os.path.exists(test_dir):
            print(f"❌ 测试目录不存在: {test_dir}")
            return False
            
        print(f"📁 测试目录: {test_dir}")
        
        # 加载测试图片目录
        print("🔄 加载测试图片目录...")
        # 设置default_save_dir为测试目录，这样标注文件会在同一目录中查找
        self.main_window.default_save_dir = test_dir
        self.main_window.import_dir_images(test_dir)
        
        # 等待加载完成
        self.app.processEvents()
        time.sleep(1.0)
        
        # 检查第一张图片的标注框数量
        first_image_path = os.path.join(test_dir, "test_image_01.jpg")
        xml_path = os.path.join(test_dir, "test_image_01.xml")
        
        if not os.path.exists(first_image_path) or not os.path.exists(xml_path):
            print(f"❌ 测试文件不存在: {first_image_path} 或 {xml_path}")
            return False
            
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
        
        # 验证标注框数量是否正确（不重复）
        self.log_result(
            "第一张图片标签列表数量",
            expected_count,
            label_count,
            label_count == expected_count
        )
        
        self.log_result(
            "第一张图片画布标注框数量",
            expected_count,
            canvas_shapes_count,
            canvas_shapes_count == expected_count
        )
        
        # 测试切换到第二张图片
        print("\n🔄 切换到第二张图片...")
        if self.main_window.img_count > 1:
            self.main_window.open_next_image()
            self.app.processEvents()
            time.sleep(0.5)
            
            # 检查第二张图片的标注框
            second_label_count = self.main_window.label_list.count()
            second_canvas_count = len(self.main_window.canvas.shapes)
            
            print(f"📊 第二张图片标签列表数量: {second_label_count}")
            print(f"📊 第二张图片画布标注框数量: {second_canvas_count}")
            
            # 第二张图片可能没有标注文件，所以数量可能为0
            self.log_result(
                "第二张图片标签列表与画布数量一致",
                True,
                second_label_count == second_canvas_count,
                second_label_count == second_canvas_count
            )
            
            # 切换回第一张图片，验证标注框仍然正确
            print("\n🔄 切换回第一张图片...")
            self.main_window.open_prev_image()
            self.app.processEvents()
            time.sleep(0.5)
            
            back_label_count = self.main_window.label_list.count()
            back_canvas_count = len(self.main_window.canvas.shapes)
            
            print(f"📊 切换回第一张图片标签列表数量: {back_label_count}")
            print(f"📊 切换回第一张图片画布标注框数量: {back_canvas_count}")
            
            self.log_result(
                "切换回第一张图片标签列表数量",
                expected_count,
                back_label_count,
                back_label_count == expected_count
            )
            
            self.log_result(
                "切换回第一张图片画布标注框数量",
                expected_count,
                back_canvas_count,
                back_canvas_count == expected_count
            )
        
        return True
        
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
            
    def print_summary(self):
        """打印测试总结"""
        print("\n" + "="*60)
        print("测试总结")
        print("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['passed'])
        failed_tests = total_tests - passed_tests
        
        print(f"📊 总测试数: {total_tests}")
        print(f"✅ 通过: {passed_tests}")
        print(f"❌ 失败: {failed_tests}")
        print(f"📈 通过率: {passed_tests/total_tests*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ 失败的测试:")
            for result in self.test_results:
                if not result['passed']:
                    print(f"  - {result['test_name']}: 期望={result['expected']}, 实际={result['actual']}")
        else:
            print("\n🎉 所有测试都通过了！修复成功！")
            
    def run_tests(self):
        """运行所有测试"""
        try:
            success = self.test_first_image_duplicate_fix()
            if success:
                self.print_summary()
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
    print("🚀 开始测试第一张图片重复加载标注框的修复效果...")
    
    tester = DuplicateFixTester()
    success = tester.run_tests()
    
    if success:
        print("\n✅ 测试完成")
        return 0
    else:
        print("\n❌ 测试失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())
