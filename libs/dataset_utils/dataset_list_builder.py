#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
多目录合并训练清单构建工具（简化实现）

根据多个数据目录生成 YOLO 训练所需的 train.txt/val.txt 与 data.yaml：
- 默认每目录按稳定哈希抽样 val_ratio（默认10%）进入验证集
- 仅收集有同名 .txt 标签的图片（可配置）
- 去重（可配置）
- names/nc 从“激活项目”的 configs/class_config.yaml 读取（若无则回退全局 configs）
"""

from pathlib import Path
from typing import List, Optional, Dict, Callable
import os
import hashlib
import yaml


def _stable_bucket(s: str) -> int:
    h = hashlib.md5(s.encode('utf-8')).digest()
    return int.from_bytes(h[:4], 'little') % 100


def _iter_images_in_dir(images_dir: Path) -> List[Path]:
    exts = {'.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff'}
    return [p for p in images_dir.rglob('*') if p.is_file() and p.suffix.lower() in exts]


def _map_label_for_image(img_path: Path) -> Path:
    parts = list(img_path.parts)
    try:
        for i in range(len(parts) - 1):
            if parts[i].lower() == 'images':
                parts[i] = 'labels'
                return Path(*parts).with_suffix('.txt')
    except Exception:
        pass
    return img_path.with_suffix('.txt')


def _load_project_classes() -> List[str]:
    try:
        from libs.project_manager import get_project_manager
        from libs.class_manager import ClassConfigManager
        pm = get_project_manager()
        cfg_dir = pm.get_project_config_path(pm.get_current_project())
        mgr = ClassConfigManager(str(cfg_dir))
        cfg = mgr.load_class_config()
        classes = cfg.get('classes', [])
        if classes:
            return classes
    except Exception:
        pass
    try:
        from libs.class_manager import ClassConfigManager
        mgr = ClassConfigManager('configs')
        cfg = mgr.load_class_config()
        return cfg.get('classes', [])
    except Exception:
        return []


def build_merged_dataset(
    dirs: List[str],
    output_root: Optional[str] = None,
    val_ratio: float = 0.10,
    absolute_paths: bool = True,
    require_labels: bool = True,
    deduplicate: bool = True,
    fixed_val_list: Optional[List[str]] = None,
    progress: Optional[Callable[[str, str, Optional[dict]], None]] = None,
) -> Dict[str, str]:
    if not dirs:
        raise ValueError('未提供任何目录')

    ts = __import__('datetime').datetime.now().strftime('%Y%m%d_%H%M%S')
    workdir = Path(output_root or Path.cwd() / 'datasets' / '_merged' / ts)
    workdir.mkdir(parents=True, exist_ok=True)

    train_list: List[str] = []
    val_list: List[str] = []
    seen = set()
    dup_skipped = 0
    considered = 0

    for d in dirs:
        d = Path(d)
        img_dir = d / 'images'
        if not img_dir.exists():
            if progress:
                try:
                    progress('dir_skip', str(d), 'images_missing')
                except Exception:
                    pass
            continue

        if progress:
            try:
                progress('dir_start', str(d))
            except Exception:
                pass

        imgs = _iter_images_in_dir(img_dir)
        dir_considered = dir_train = dir_val = dir_dup = 0

        for img in imgs:
            if require_labels:
                lbl = _map_label_for_image(img)
                if not lbl.exists():
                    continue

            considered += 1
            dir_considered += 1

            write_path = str(img.resolve()) if absolute_paths else str(img)
            if deduplicate and write_path in seen:
                dup_skipped += 1
                dir_dup += 1
                continue
            seen.add(write_path)

            bucket = _stable_bucket(str(img).replace(str(d), ''))
            if fixed_val_list is not None:
                train_list.append(write_path)
            else:
                if bucket < int(val_ratio * 100):
                    val_list.append(write_path)
                    dir_val += 1
                else:
                    train_list.append(write_path)
                    dir_train += 1

        if progress:
            try:
                progress('dir_done', str(d), {
                    'considered': dir_considered,
                    'train': dir_train,
                    'val': dir_val,
                    'duplicates': dir_dup
                })
            except Exception:
                pass

    if fixed_val_list is not None:
        fixed_set = set(fixed_val_list)
        new_train = []
        for p in train_list:
            if p in fixed_set:
                val_list.append(p)
            else:
                new_train.append(p)
        train_list = new_train

    train_txt = workdir / 'train.txt'
    val_txt = workdir / 'val.txt'
    train_txt.write_text('\n'.join(train_list), encoding='utf-8')
    val_txt.write_text('\n'.join(val_list), encoding='utf-8')

    classes = _load_project_classes()
    data_yaml = workdir / 'data.yaml'
    # 使用绝对路径作为path，避免Ultralytics将相对路径解释为当前工作目录
    data = {'path': str(workdir.resolve()), 'train': 'train.txt', 'val': 'val.txt'}
    if classes:
        data['nc'] = len(classes)
        data['names'] = classes
    data_yaml.write_text(yaml.dump(data, allow_unicode=True, default_flow_style=False), encoding='utf-8')

    return {
        'workdir': str(workdir),
        'train': str(train_txt),
        'val': str(val_txt),
        'yaml': str(data_yaml),
        'train_count': len(train_list),
        'val_count': len(val_list),
        'duplicates_skipped': dup_skipped,
        'considered': considered,
        'dirs_processed': len(dirs),
    }


def build_merged_voc_dirs(
    dirs: List[str],
    output_root: Optional[str] = None,
    val_ratio: float = 0.10,
    progress: Optional[Callable[[str, str, Optional[dict]], None]] = None,
) -> Dict[str, str]:
    """
    将多个“图片+同名 VOC XML”的目录合并为一个 YOLO 数据集（images/train|val, labels/train|val）。

    - 每个源目录按稳定哈希对图片进行 10% 抽样进 val（可复现）
    - 无 XML 的图片跳过
    - 类别来自当前激活项目（或全局）
    """
    if not dirs:
        raise ValueError('未提供任何目录')

    from xml.etree import ElementTree as ET
    classes = _load_project_classes()
    class_to_id = {name: i for i, name in enumerate(classes)} if classes else {}

    ts = __import__('datetime').datetime.now().strftime('%Y%m%d_%H%M%S')
    workdir = Path(output_root or Path.cwd() / 'datasets' / '_merged' / ts)
    images_train = workdir / 'images' / 'train'
    images_val = workdir / 'images' / 'val'
    labels_train = workdir / 'labels' / 'train'
    labels_val = workdir / 'labels' / 'val'
    for p in [images_train, images_val, labels_train, labels_val]:
        p.mkdir(parents=True, exist_ok=True)

    def _parse_voc_to_yolo(xml_path: Path, img_w: int, img_h: int) -> List[str]:
        try:
            root = ET.parse(str(xml_path)).getroot()
            lines = []
            for obj in root.findall('object'):
                name_el = obj.find('name')
                if name_el is None:
                    continue
                cname = name_el.text.strip()
                if cname not in class_to_id:
                    # 未知类别跳过
                    continue
                bnd = obj.find('bndbox')
                if bnd is None:
                    continue
                xmin = float(bnd.findtext('xmin', '0'))
                ymin = float(bnd.findtext('ymin', '0'))
                xmax = float(bnd.findtext('xmax', '0'))
                ymax = float(bnd.findtext('ymax', '0'))
                # 归一化
                x = max(0.0, (xmin + xmax) / 2.0 / img_w)
                y = max(0.0, (ymin + ymax) / 2.0 / img_h)
                w = max(0.0, (xmax - xmin) / img_w)
                h = max(0.0, (ymax - ymin) / img_h)
                cls_id = class_to_id[cname]
                lines.append(f"{cls_id} {x:.6f} {y:.6f} {w:.6f} {h:.6f}")
            return lines
        except Exception:
            return []

    total_considered = 0
    total_copied_train = 0
    total_copied_val = 0
    total_skipped = 0

    for d in dirs:
        dpath = Path(d)
        if not dpath.exists():
            if progress:
                try:
                    progress('dir_skip', str(dpath), 'not_found')
                except Exception:
                    pass
            continue

        if progress:
            try:
                progress('dir_start', str(dpath))
            except Exception:
                pass

        # 扫描图片
        imgs = [p for p in dpath.rglob('*') if p.suffix.lower() in {'.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff'}]
        dir_considered = 0
        dir_train = 0
        dir_val = 0
        dir_skipped = 0

        for img in imgs:
            xml = img.with_suffix('.xml')
            if not xml.exists():
                dir_skipped += 1
                continue

            # 读尺寸
            try:
                from PIL import Image
                with Image.open(str(img)) as im:
                    w, h = im.size
            except Exception:
                dir_skipped += 1
                continue

            yolo_lines = _parse_voc_to_yolo(xml, w, h)
            if not yolo_lines:
                dir_skipped += 1
                continue

            dir_considered += 1
            total_considered += 1

            # 稳定哈希抽样（按相对路径）
            rel_key = str(img).replace(str(dpath), '')
            bucket = _stable_bucket(rel_key)
            is_val = bucket < int(val_ratio * 100)

            if is_val:
                dst_img = images_val / img.name
                dst_lbl = labels_val / (img.stem + '.txt')
                dir_val += 1
                total_copied_val += 1
            else:
                dst_img = images_train / img.name
                dst_lbl = labels_train / (img.stem + '.txt')
                dir_train += 1
                total_copied_train += 1

            # 拷贝图片
            try:
                __import__('shutil').copy2(str(img), str(dst_img))
            except Exception:
                dir_skipped += 1
                continue

            # 写标签
            dst_lbl.write_text('\n'.join(yolo_lines), encoding='utf-8')

        total_skipped += dir_skipped
        if progress:
            try:
                progress('dir_done', str(dpath), {
                    'considered': dir_considered,
                    'train': dir_train,
                    'val': dir_val,
                    'skipped': dir_skipped
                })
            except Exception:
                pass

    # 写 data.yaml
    data_yaml = workdir / 'data.yaml'
    # 使用绝对路径作为path，避免相对路径在不同工作目录下解析错误
    data = {
        'path': str(workdir.resolve()),
        'train': 'images/train',
        'val': 'images/val',
    }
    if classes:
        data['nc'] = len(classes)
        data['names'] = classes
    data_yaml.write_text(yaml.dump(data, allow_unicode=True, default_flow_style=False), encoding='utf-8')

    return {
        'workdir': str(workdir),
        'yaml': str(data_yaml),
        'train_dir': str(images_train),
        'val_dir': str(images_val),
        'train_count': total_copied_train,
        'val_count': total_copied_val,
        'skipped': total_skipped,
        'considered': total_considered,
        'dirs_processed': len(dirs),
    }
