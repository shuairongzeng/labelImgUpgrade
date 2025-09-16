"""
缓存目录管理工具类
用于管理labelImg项目中的训练数据集缓存和临时文件
"""

import os
import shutil
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class CacheManager:
    """缓存目录管理器"""

    def __init__(self, base_dir: str = "projects"):
        """
        初始化缓存管理器

        Args:
            base_dir: 项目基础目录
        """
        self.base_dir = base_dir
        self.cache_subdir = "cache"
        self.filtered_datasets_subdir = "filtered_datasets"
        self.temp_subdir = "temp"

    def get_project_cache_dir(self, project_name: str) -> str:
        """获取项目缓存目录路径"""
        if not project_name:
            project_name = "default"
        return os.path.join(self.base_dir, project_name, self.cache_subdir)

    def get_filtered_datasets_dir(self, project_name: str) -> str:
        """获取筛选数据集缓存目录"""
        cache_dir = self.get_project_cache_dir(project_name)
        return os.path.join(cache_dir, self.filtered_datasets_subdir)

    def get_temp_dir(self, project_name: str) -> str:
        """获取临时文件目录"""
        cache_dir = self.get_project_cache_dir(project_name)
        return os.path.join(cache_dir, self.temp_subdir)

    def create_filtered_dataset_dir(self, project_name: str, dataset_prefix: str = "filtered") -> str:
        """
        创建筛选数据集目录

        Args:
            project_name: 项目名称
            dataset_prefix: 数据集前缀

        Returns:
            创建的目录路径
        """
        filtered_dir = self.get_filtered_datasets_dir(project_name)

        # 确保父目录存在
        os.makedirs(filtered_dir, exist_ok=True)

        # 创建带时间戳的子目录
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dataset_dir = os.path.join(filtered_dir, f"{dataset_prefix}_{timestamp}")
        os.makedirs(dataset_dir, exist_ok=True)

        logger.info(f"创建筛选数据集目录: {dataset_dir}")
        return dataset_dir

    def create_temp_dir(self, project_name: str, temp_prefix: str = "temp") -> str:
        """
        创建临时目录

        Args:
            project_name: 项目名称
            temp_prefix: 临时目录前缀

        Returns:
            创建的临时目录路径
        """
        temp_base_dir = self.get_temp_dir(project_name)

        # 确保父目录存在
        os.makedirs(temp_base_dir, exist_ok=True)

        # 创建带时间戳的临时目录
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]  # 毫秒精度
        temp_dir = os.path.join(temp_base_dir, f"{temp_prefix}_{timestamp}")
        os.makedirs(temp_dir, exist_ok=True)

        logger.info(f"创建临时目录: {temp_dir}")
        return temp_dir

    def get_cache_statistics(self, project_name: str = None) -> Dict[str, any]:
        """
        获取缓存统计信息

        Args:
            project_name: 项目名称，None表示获取所有项目的统计

        Returns:
            缓存统计信息字典
        """
        stats = {
            'total_size': 0,
            'total_files': 0,
            'total_dirs': 0,
            'projects': {}
        }

        if project_name:
            # 获取单个项目的统计
            project_stats = self._get_project_cache_stats(project_name)
            stats['projects'][project_name] = project_stats
            stats['total_size'] = project_stats['size']
            stats['total_files'] = project_stats['files']
            stats['total_dirs'] = project_stats['dirs']
        else:
            # 获取所有项目的统计
            if os.path.exists(self.base_dir):
                for item in os.listdir(self.base_dir):
                    project_path = os.path.join(self.base_dir, item)
                    if os.path.isdir(project_path):
                        cache_path = os.path.join(project_path, self.cache_subdir)
                        if os.path.exists(cache_path):
                            project_stats = self._get_project_cache_stats(item)
                            stats['projects'][item] = project_stats
                            stats['total_size'] += project_stats['size']
                            stats['total_files'] += project_stats['files']
                            stats['total_dirs'] += project_stats['dirs']

        return stats

    def _get_project_cache_stats(self, project_name: str) -> Dict[str, any]:
        """获取单个项目的缓存统计信息"""
        cache_dir = self.get_project_cache_dir(project_name)

        stats = {
            'size': 0,
            'files': 0,
            'dirs': 0,
            'filtered_datasets': {'count': 0, 'size': 0},
            'temp_files': {'count': 0, 'size': 0},
            'last_modified': None
        }

        if not os.path.exists(cache_dir):
            return stats

        for root, dirs, files in os.walk(cache_dir):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    file_size = os.path.getsize(file_path)
                    stats['size'] += file_size
                    stats['files'] += 1

                    # 按子目录分类统计
                    if self.filtered_datasets_subdir in root:
                        stats['filtered_datasets']['size'] += file_size
                        stats['filtered_datasets']['count'] += 1
                    elif self.temp_subdir in root:
                        stats['temp_files']['size'] += file_size
                        stats['temp_files']['count'] += 1

                    # 更新最后修改时间
                    mtime = os.path.getmtime(file_path)
                    if stats['last_modified'] is None or mtime > stats['last_modified']:
                        stats['last_modified'] = mtime

                except (OSError, IOError):
                    continue

            stats['dirs'] += len(dirs)

        return stats

    def clean_old_cache(self, project_name: str = None, days_old: int = 7) -> Dict[str, any]:
        """
        清理过期缓存

        Args:
            project_name: 项目名称，None表示清理所有项目
            days_old: 清理多少天前的缓存

        Returns:
            清理结果统计
        """
        cutoff_time = time.time() - (days_old * 24 * 3600)

        result = {
            'cleaned_files': 0,
            'cleaned_dirs': 0,
            'freed_size': 0,
            'errors': []
        }

        if project_name:
            projects = [project_name]
        else:
            projects = []
            if os.path.exists(self.base_dir):
                for item in os.listdir(self.base_dir):
                    project_path = os.path.join(self.base_dir, item)
                    if os.path.isdir(project_path):
                        cache_path = os.path.join(project_path, self.cache_subdir)
                        if os.path.exists(cache_path):
                            projects.append(item)

        for proj in projects:
            try:
                proj_result = self._clean_project_cache(proj, cutoff_time)
                result['cleaned_files'] += proj_result['cleaned_files']
                result['cleaned_dirs'] += proj_result['cleaned_dirs']
                result['freed_size'] += proj_result['freed_size']
                result['errors'].extend(proj_result['errors'])
            except Exception as e:
                result['errors'].append(f"清理项目 {proj} 失败: {str(e)}")

        return result

    def _clean_project_cache(self, project_name: str, cutoff_time: float) -> Dict[str, any]:
        """清理单个项目的过期缓存"""
        cache_dir = self.get_project_cache_dir(project_name)

        result = {
            'cleaned_files': 0,
            'cleaned_dirs': 0,
            'freed_size': 0,
            'errors': []
        }

        if not os.path.exists(cache_dir):
            return result

        # 遍历缓存目录
        for root, dirs, files in os.walk(cache_dir, topdown=False):
            # 检查文件
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    if os.path.getmtime(file_path) < cutoff_time:
                        file_size = os.path.getsize(file_path)
                        os.remove(file_path)
                        result['cleaned_files'] += 1
                        result['freed_size'] += file_size
                except Exception as e:
                    result['errors'].append(f"删除文件 {file_path} 失败: {str(e)}")

            # 检查空目录
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                try:
                    if os.path.getmtime(dir_path) < cutoff_time and not os.listdir(dir_path):
                        os.rmdir(dir_path)
                        result['cleaned_dirs'] += 1
                except Exception as e:
                    result['errors'].append(f"删除目录 {dir_path} 失败: {str(e)}")

        return result

    def clean_all_cache(self, project_name: str = None) -> Dict[str, any]:
        """
        清理所有缓存

        Args:
            project_name: 项目名称，None表示清理所有项目

        Returns:
            清理结果统计
        """
        result = {
            'cleaned_files': 0,
            'cleaned_dirs': 0,
            'freed_size': 0,
            'errors': []
        }

        if project_name:
            cache_dir = self.get_project_cache_dir(project_name)
            if os.path.exists(cache_dir):
                try:
                    # 计算清理前的大小
                    stats = self._get_project_cache_stats(project_name)
                    result['freed_size'] = stats['size']
                    result['cleaned_files'] = stats['files']
                    result['cleaned_dirs'] = stats['dirs']

                    # 删除整个缓存目录
                    shutil.rmtree(cache_dir)
                    logger.info(f"已清理项目 {project_name} 的所有缓存")
                except Exception as e:
                    result['errors'].append(f"清理项目 {project_name} 缓存失败: {str(e)}")
        else:
            # 清理所有项目的缓存
            if os.path.exists(self.base_dir):
                for item in os.listdir(self.base_dir):
                    project_path = os.path.join(self.base_dir, item)
                    if os.path.isdir(project_path):
                        cache_path = os.path.join(project_path, self.cache_subdir)
                        if os.path.exists(cache_path):
                            try:
                                stats = self._get_project_cache_stats(item)
                                result['freed_size'] += stats['size']
                                result['cleaned_files'] += stats['files']
                                result['cleaned_dirs'] += stats['dirs']

                                shutil.rmtree(cache_path)
                                logger.info(f"已清理项目 {item} 的所有缓存")
                            except Exception as e:
                                result['errors'].append(f"清理项目 {item} 缓存失败: {str(e)}")

        return result

    def clean_specific_directory(self, dir_path: str) -> Dict[str, any]:
        """
        清理指定目录

        Args:
            dir_path: 要清理的目录路径

        Returns:
            清理结果统计
        """
        result = {
            'cleaned_files': 0,
            'cleaned_dirs': 0,
            'freed_size': 0,
            'errors': []
        }

        if not os.path.exists(dir_path):
            return result

        try:
            # 计算清理前的大小
            for root, dirs, files in os.walk(dir_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        result['freed_size'] += os.path.getsize(file_path)
                        result['cleaned_files'] += 1
                    except:
                        pass
                result['cleaned_dirs'] += len(dirs)

            # 删除目录
            shutil.rmtree(dir_path)
            logger.info(f"已清理目录: {dir_path}")

        except Exception as e:
            result['errors'].append(f"清理目录 {dir_path} 失败: {str(e)}")

        return result

    def format_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
        if size_bytes == 0:
            return "0 B"

        size_names = ["B", "KB", "MB", "GB", "TB"]
        import math
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_names[i]}"

    def get_cache_directories(self, project_name: str = None) -> List[Dict[str, any]]:
        """
        获取缓存目录列表

        Args:
            project_name: 项目名称，None表示获取所有项目

        Returns:
            缓存目录信息列表
        """
        directories = []

        if project_name:
            projects = [project_name]
        else:
            projects = []
            if os.path.exists(self.base_dir):
                for item in os.listdir(self.base_dir):
                    project_path = os.path.join(self.base_dir, item)
                    if os.path.isdir(project_path):
                        cache_path = os.path.join(project_path, self.cache_subdir)
                        if os.path.exists(cache_path):
                            projects.append(item)

        for proj in projects:
            cache_dir = self.get_project_cache_dir(proj)
            if os.path.exists(cache_dir):
                # 获取子目录
                for subdir in [self.filtered_datasets_subdir, self.temp_subdir]:
                    subdir_path = os.path.join(cache_dir, subdir)
                    if os.path.exists(subdir_path):
                        for item in os.listdir(subdir_path):
                            item_path = os.path.join(subdir_path, item)
                            if os.path.isdir(item_path):
                                try:
                                    size = sum(
                                        os.path.getsize(os.path.join(dirpath, filename))
                                        for dirpath, dirnames, filenames in os.walk(item_path)
                                        for filename in filenames
                                    )
                                    mtime = os.path.getmtime(item_path)

                                    directories.append({
                                        'project': proj,
                                        'type': subdir,
                                        'name': item,
                                        'path': item_path,
                                        'size': size,
                                        'formatted_size': self.format_size(size),
                                        'modified_time': datetime.fromtimestamp(mtime),
                                        'age_days': (time.time() - mtime) / (24 * 3600)
                                    })
                                except Exception as e:
                                    logger.warning(f"获取目录信息失败 {item_path}: {str(e)}")

        # 按修改时间排序
        directories.sort(key=lambda x: x['modified_time'], reverse=True)
        return directories


# 全局缓存管理器实例
cache_manager = CacheManager()