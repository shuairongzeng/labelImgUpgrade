#!/usr/bin/env python3
"""
测试批量预测对话框的核心逻辑（无GUI）
"""

import sys
import os
import tempfile

# 添加libs目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'libs'))

def test_annotation_detection():
    """测试标注检测逻辑"""
    print("=== 测试标注检测逻辑 ===")
    
    # 创建临时测试目录
    test_dir = tempfile.mkdtemp(prefix="annotation_test_")
    print(f"测试目录: {test_dir}")
    
    try:
        # 创建测试文件
        test_files = {
            "image1.jpg": "未标注图片",
            "image2.png": "未标注图片", 
            "image3.jpg": "已标注图片",
            "image3.xml": "标注文件",  # image3有对应的xml文件
            "image4.bmp": "未标注图片",
            "image5.jpg": "已标注图片",
            "image5.txt": "YOLO标注文件",  # image5有对应的txt文件
        }
        
        for filename, content in test_files.items():
            filepath = os.path.join(test_dir, filename)
            with open(filepath, 'w') as f:
                f.write(content)
        
        # 导入并测试标注检测逻辑
        from batch_prediction_dialog import BatchPredictionDialog
        
        # 创建一个临时对话框实例用于测试
        class MockDialog(BatchPredictionDialog):
            def __init__(self, test_dir):
                # 只初始化必要的属性，不调用父类初始化
                self.current_path = test_dir
        
        dialog = MockDialog(test_dir)
        
        # 测试各个图片的标注状态
        test_cases = [
            ("image1.jpg", False, "应该是未标注"),
            ("image2.png", False, "应该是未标注"),
            ("image3.jpg", True, "应该是已标注(有xml)"),
            ("image4.bmp", False, "应该是未标注"),
            ("image5.jpg", True, "应该是已标注(有txt)"),
        ]
        
        print("\\n检测结果:")
        all_passed = True
        for image_name, expected, description in test_cases:
            result = dialog.is_image_annotated(image_name)
            status = "PASS" if result == expected else "FAIL"
            print(f"  {status} {image_name}: {result} ({description})")
            if result != expected:
                all_passed = False
        
        print(f"\\n测试结果: {'全部通过' if all_passed else '部分失败'}")
        return all_passed
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 清理测试数据
        import shutil
        try:
            shutil.rmtree(test_dir, ignore_errors=True)
        except:
            pass

def test_directory_scanning():
    """测试目录扫描功能"""
    print("\\n=== 测试目录扫描功能 ===")
    
    test_dir = tempfile.mkdtemp(prefix="scan_test_")
    print(f"测试目录: {test_dir}")
    
    try:
        # 创建混合文件
        test_files = {
            # 图片文件
            "photo1.jpg": "图片1",
            "photo2.png": "图片2", 
            "photo3.bmp": "图片3",
            "photo4.tiff": "图片4",
            "photo5.webp": "图片5",
            # 已标注的图片
            "annotated1.jpg": "已标注图片1",
            "annotated1.xml": "标注文件1",
            "annotated2.png": "已标注图片2", 
            "annotated2.txt": "YOLO标注2",
            # 非图片文件
            "document.txt": "文档",
            "readme.md": "说明文件",
        }
        
        for filename, content in test_files.items():
            filepath = os.path.join(test_dir, filename)
            with open(filepath, 'w') as f:
                f.write(content)
        
        # 手动实现扫描逻辑测试
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
        all_images = []
        
        for file_name in os.listdir(test_dir):
            file_path = os.path.join(test_dir, file_name)
            if os.path.isfile(file_path):
                _, ext = os.path.splitext(file_name.lower())
                if ext in image_extensions:
                    all_images.append(file_name)
        
        print(f"发现图片文件: {len(all_images)} 个")
        for img in sorted(all_images):
            print(f"  - {img}")
        
        # 计算需要预测的图片（跳过已标注的）
        to_predict = []
        for img_name in all_images:
            base_name = os.path.splitext(img_name)[0]
            dir_files = os.listdir(test_dir)
            same_name_count = sum(1 for f in dir_files if os.path.splitext(f)[0] == base_name)
            
            if same_name_count <= 1:  # 只有图片文件本身
                to_predict.append(img_name)
        
        print(f"\\n需要预测的图片: {len(to_predict)} 个")
        for img in sorted(to_predict):
            print(f"  - {img}")
        
        print(f"跳过的图片: {len(all_images) - len(to_predict)} 个")
        
        # 验证结果
        expected_total = 7  # photo1-5 + annotated1-2
        expected_to_predict = 5  # photo1-5 (annotated1-2应该被跳过)
        
        result = (len(all_images) == expected_total and len(to_predict) == expected_to_predict)
        print(f"\\n扫描测试: {'通过' if result else '失败'}")
        print(f"  期望总数: {expected_total}, 实际: {len(all_images)}")
        print(f"  期望待预测: {expected_to_predict}, 实际: {len(to_predict)}")
        
        return result
        
    except Exception as e:
        print(f"扫描测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 清理测试数据
        import shutil
        try:
            shutil.rmtree(test_dir, ignore_errors=True)
        except:
            pass

def main():
    """主测试函数"""
    print("批量预测对话框核心逻辑测试")
    print("=" * 50)
    
    test1_result = test_annotation_detection()
    test2_result = test_directory_scanning()
    
    print("\\n" + "=" * 50)
    print("测试总结:")
    print(f"  标注检测测试: {'通过' if test1_result else '失败'}")
    print(f"  目录扫描测试: {'通过' if test2_result else '失败'}")
    print(f"  整体结果: {'全部通过' if test1_result and test2_result else '部分失败'}")

if __name__ == '__main__':
    main()