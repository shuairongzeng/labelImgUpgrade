# 🤖 AI模型存储目录

这个目录用于存储labelImg AI助手使用的YOLO模型文件。

## 📁 目录结构

```
models/
├── README.md           # 本文件
├── yolov8n.pt         # YOLOv8 Nano模型 (自动下载)
├── yolov8s.pt         # YOLOv8 Small模型 (可选)
├── yolov8m.pt         # YOLOv8 Medium模型 (可选)
├── yolov8l.pt         # YOLOv8 Large模型 (可选)
├── yolov8x.pt         # YOLOv8 Extra Large模型 (可选)
└── custom/            # 自定义模型目录
    ├── my_model.pt    # 用户自定义模型
    └── ...
```

## 🚀 支持的模型格式

- **PyTorch模型** (`.pt`): 推荐格式，完全支持
- **ONNX模型** (`.onnx`): 跨平台格式，性能优化
- **TensorRT模型** (`.engine`): NVIDIA GPU加速格式

## 📊 预训练模型说明

### YOLOv8系列模型

| 模型 | 大小 | mAP | 速度 | 推荐用途 |
|------|------|-----|------|----------|
| YOLOv8n | 6.2MB | 37.3 | 最快 | 快速预标注 |
| YOLOv8s | 21.5MB | 44.9 | 快 | 平衡性能 |
| YOLOv8m | 49.7MB | 50.2 | 中等 | 高精度标注 |
| YOLOv8l | 83.7MB | 52.9 | 慢 | 专业标注 |
| YOLOv8x | 136.7MB | 53.9 | 最慢 | 最高精度 |

### 支持的类别 (COCO数据集)

YOLOv8预训练模型支持80个类别：

```
0: person          20: elephant       40: wine glass     60: dining table
1: bicycle         21: bear           41: cup            61: toilet
2: car             22: zebra          42: fork           62: tv
3: motorcycle      23: giraffe        43: knife          63: laptop
4: airplane        24: backpack       44: spoon          64: mouse
5: bus             25: umbrella       45: bowl           65: remote
6: train           26: handbag        46: banana         66: keyboard
7: truck           27: tie            47: apple          67: cell phone
8: boat            28: suitcase       48: sandwich       68: microwave
9: traffic light   29: frisbee        49: orange         69: oven
10: fire hydrant   30: skis           50: broccoli       70: toaster
11: stop sign      31: snowboard      51: carrot         71: sink
12: parking meter  32: sports ball    52: hot dog        72: refrigerator
13: bench          33: kite           53: pizza          73: book
14: bird           34: baseball bat   54: donut          74: clock
15: cat            35: baseball glove 55: cake           75: vase
16: dog            36: skateboard     56: chair          76: scissors
17: horse          37: surfboard      57: couch          77: teddy bear
18: sheep          38: tennis racket  58: potted plant   78: hair drier
19: cow            39: bottle         59: bed            79: toothbrush
```

## 📥 模型下载

### 自动下载
首次使用时，AI助手会自动下载YOLOv8n模型。

### 手动下载
如需其他模型，可以手动下载：

```bash
# 下载YOLOv8s模型
wget https://github.com/ultralytics/assets/releases/download/v8.3.0/yolov8s.pt

# 下载YOLOv8m模型  
wget https://github.com/ultralytics/assets/releases/download/v8.3.0/yolov8m.pt
```

## 🔧 自定义模型

### 添加自定义模型

1. 将模型文件复制到 `models/custom/` 目录
2. 确保模型文件格式正确 (`.pt`, `.onnx`, 或 `.engine`)
3. 在AI助手界面中选择自定义模型

### 模型要求

- **输入格式**: RGB图像
- **输入尺寸**: 建议640x640 (可配置)
- **输出格式**: YOLO标准输出格式

### 训练自定义模型

使用ultralytics训练自定义模型：

```python
from ultralytics import YOLO

# 加载预训练模型
model = YOLO('yolov8n.pt')

# 训练模型
model.train(
    data='path/to/dataset.yaml',
    epochs=100,
    imgsz=640,
    batch=16
)

# 保存模型
model.save('models/custom/my_model.pt')
```

## ⚙️ 模型配置

在 `config/ai_settings.yaml` 中可以为不同模型设置特定参数：

```yaml
model_configs:
  "my_custom_model.pt":
    prediction:
      default_confidence: 0.4
      image_size: 640
    performance:
      memory_limit: 1024
```

## 🔍 模型验证

AI助手会自动验证模型：

- ✅ 文件格式检查
- ✅ 模型结构验证
- ✅ 类别信息提取
- ✅ 推理测试

## 📝 使用建议

### 选择合适的模型

- **快速标注**: 使用YOLOv8n，速度最快
- **平衡需求**: 使用YOLOv8s，性能均衡
- **高精度**: 使用YOLOv8m或更大模型
- **特定领域**: 训练自定义模型

### 性能优化

- **GPU加速**: 安装CUDA版本的PyTorch
- **模型量化**: 使用ONNX或TensorRT格式
- **批量处理**: 调整批处理大小
- **图像尺寸**: 根据需求调整输入尺寸

## 🚨 注意事项

1. **版权**: 确保使用的模型符合版权要求
2. **隐私**: 自定义模型可能包含敏感信息
3. **兼容性**: 不同版本的模型可能不兼容
4. **存储空间**: 大模型占用较多磁盘空间

## 🆘 故障排除

### 常见问题

**Q: 模型加载失败**
A: 检查文件完整性，重新下载模型

**Q: 预测结果不准确**  
A: 调整置信度阈值，或使用更大的模型

**Q: 内存不足**
A: 使用较小的模型，或调整批处理大小

**Q: 速度太慢**
A: 使用GPU加速，或选择更小的模型

---

**模型管理说明完成！** 🎯
