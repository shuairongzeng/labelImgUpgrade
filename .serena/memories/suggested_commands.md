# 建议的开发命令

## 运行项目
```bash
python labelImg.py
```

## 测试相关
```bash
# 运行特定测试
python test_auto_configure_training.py
python test_yolo_export.py

# 运行AI助手测试
python test_ai_assistant_panel.py
```

## 调试和验证
```bash
# 验证修改
python verify_fixes.py
python verify_implementation.py

# 调试特定功能
python debug_annotation_loading.py
python test_class_consistency.py
```

## 打包相关
```bash
# Windows打包
.\打包labelImg.bat

# 使用PyInstaller
pyinstaller labelImg.spec
```

## 配置管理
```bash
# 同步类别配置
python sync_class_config.py

# 创建类别配置
python create_class_config.py
```

## 系统工具 (Windows)
- `dir` - 列出文件
- `type` - 查看文件内容  
- `findstr` - 搜索文本
- `copy` - 复制文件
- `move` - 移动文件
- `del` - 删除文件