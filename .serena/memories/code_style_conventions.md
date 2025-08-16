# 代码风格和约定

## 命名约定
- **类名**: PascalCase (如 `AIAssistantPanel`, `ClassConfigManager`)
- **方法名**: snake_case (如 `auto_configure_training_dataset`, `parse_json_annotation`)
- **变量名**: snake_case (如 `annotation_files`, `class_to_id`)
- **常量**: UPPER_CASE (如 `DEFAULT_ENCODING`, `XML_EXT`)

## 文档字符串
- 使用中文文档字符串
- 格式：`"""方法描述"""`
- 复杂方法包含Args和Returns说明

## 错误处理
- 使用try-except块处理异常
- 记录详细的错误日志
- 向用户显示友好的错误消息

## 日志记录
- 使用logger进行日志记录
- 日志级别：INFO, WARNING, ERROR
- 包含emoji表情符号增强可读性

## UI约定
- 使用PyQt5组件
- 中文界面文本
- 统一的样式表设置
- 进度条和状态反馈

## 文件处理
- 支持多种编码格式
- 使用相对路径
- 创建必要的目录结构
- 备份重要文件