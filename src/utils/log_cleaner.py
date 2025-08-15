"""
日志清理工具模块

@author: MingTechPro
@version: 1.0.0
@date: 2025-08-15
@description: 该模块提供了日志文件清理功能，可以手动清理旧的日志文件，
             释放磁盘空间，保持日志目录的整洁。

主要功能:
- 清理指定天数之前的日志文件
- 按文件大小清理日志文件
- 统计日志文件信息
- 安全的日志清理操作

@example
    # 清理7天前的日志文件
    from src.utils.log_cleaner import LogCleaner
    cleaner = LogCleaner("logs")
    cleaner.cleanup_by_age(days=7)
    
    # 清理超过100MB的日志文件
    cleaner.cleanup_by_size(max_size_mb=100)
    
    # 获取日志文件统计信息
    stats = cleaner.get_log_stats()
    print(f"总文件数: {stats['total_files']}, 总大小: {stats['total_size_mb']:.2f}MB")
"""

import os
import glob
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import logging


class LogCleaner:
    """
    日志清理器类
    
    提供多种日志清理策略，包括按时间、按大小等。
    支持安全的清理操作，避免误删重要文件。
    
    @author: MingTechPro
    @version: 1.0.0
    @date: 2025-08-15
    
    主要特性:
    - 按时间清理旧日志文件
    - 按大小清理日志文件
    - 统计日志文件信息
    - 安全的清理操作
    - 详细的清理报告
    
    @example
        cleaner = LogCleaner("logs")
        
        # 清理7天前的日志
        result = cleaner.cleanup_by_age(days=7)
        print(f"清理了 {result['deleted_count']} 个文件")
        
        # 获取统计信息
        stats = cleaner.get_log_stats()
        print(f"剩余文件: {stats['total_files']} 个")
    """
    
    def __init__(self, log_dir: str = "logs"):
        """
        初始化日志清理器
        
        @param {str} log_dir - 日志目录路径
        """
        self.log_dir = Path(log_dir)
        self.logger = logging.getLogger(__name__)
        
        # 确保日志目录存在
        self.log_dir.mkdir(parents=True, exist_ok=True)
    
    def get_log_files(self, pattern: str = "spider_*.log") -> List[Path]:
        """
        获取日志文件列表
        
        @param {str} pattern - 文件匹配模式
        @returns {List[Path]} 日志文件路径列表
        
        @example
            files = cleaner.get_log_files("spider_*.log")
            print(f"找到 {len(files)} 个日志文件")
        """
        pattern_path = self.log_dir / pattern
        return [Path(f) for f in glob.glob(str(pattern_path)) if Path(f).is_file()]
    
    def get_log_stats(self) -> Dict:
        """
        获取日志文件统计信息
        
        @returns {Dict} 统计信息字典
        
        @example
            stats = cleaner.get_log_stats()
            print(f"总文件数: {stats['total_files']}")
            print(f"总大小: {stats['total_size_mb']:.2f}MB")
        """
        files = self.get_log_files()
        total_size = sum(f.stat().st_size for f in files)
        
        # 按时间分组统计
        now = datetime.now()
        today_files = []
        week_files = []
        month_files = []
        older_files = []
        
        for file in files:
            file_mtime = datetime.fromtimestamp(file.stat().st_mtime)
            age_days = (now - file_mtime).days
            
            if age_days == 0:
                today_files.append(file)
            elif age_days <= 7:
                week_files.append(file)
            elif age_days <= 30:
                month_files.append(file)
            else:
                older_files.append(file)
        
        return {
            "total_files": len(files),
            "total_size_mb": total_size / (1024 * 1024),
            "today_files": len(today_files),
            "week_files": len(week_files),
            "month_files": len(month_files),
            "older_files": len(older_files),
            "files": files
        }
    
    def cleanup_by_age(self, days: int = 7, dry_run: bool = False) -> Dict:
        """
        按时间清理日志文件
        
        @param {int} days - 保留天数
        @param {bool} dry_run - 试运行模式，不实际删除文件
        @returns {Dict} 清理结果
        
        @example
            # 试运行，查看会删除哪些文件
            result = cleaner.cleanup_by_age(days=7, dry_run=True)
            print(f"将删除 {result['to_delete_count']} 个文件")
            
            # 实际执行清理
            result = cleaner.cleanup_by_age(days=7, dry_run=False)
            print(f"已删除 {result['deleted_count']} 个文件")
        """
        cutoff_time = datetime.now() - timedelta(days=days)
        files = self.get_log_files()
        
        to_delete = []
        for file in files:
            file_mtime = datetime.fromtimestamp(file.stat().st_mtime)
            if file_mtime < cutoff_time:
                to_delete.append(file)
        
        deleted_count = 0
        deleted_files = []
        errors = []
        
        if not dry_run:
            for file in to_delete:
                try:
                    file.unlink()
                    deleted_count += 1
                    deleted_files.append(str(file))
                    self.logger.info(f"已删除旧日志文件: {file}")
                except Exception as e:
                    error_msg = f"删除文件失败: {file}, 错误: {e}"
                    errors.append(error_msg)
                    self.logger.error(error_msg)
        
        return {
            "to_delete_count": len(to_delete),
            "deleted_count": deleted_count,
            "deleted_files": deleted_files,
            "errors": errors,
            "cutoff_time": cutoff_time,
            "dry_run": dry_run
        }
    
    def cleanup_by_size(self, max_size_mb: float = 100, dry_run: bool = False) -> Dict:
        """
        按大小清理日志文件
        
        @param {float} max_size_mb - 最大总大小(MB)
        @param {bool} dry_run - 试运行模式
        @returns {Dict} 清理结果
        
        @example
            # 清理超过100MB的日志文件
            result = cleaner.cleanup_by_size(max_size_mb=100)
            print(f"已删除 {result['deleted_count']} 个文件")
        """
        files = self.get_log_files()
        
        # 按修改时间排序，优先删除旧文件
        files.sort(key=lambda f: f.stat().st_mtime)
        
        total_size = sum(f.stat().st_size for f in files)
        max_size_bytes = max_size_mb * 1024 * 1024
        
        to_delete = []
        current_size = total_size
        
        for file in files:
            if current_size <= max_size_bytes:
                break
            
            file_size = file.stat().st_size
            to_delete.append(file)
            current_size -= file_size
        
        deleted_count = 0
        deleted_files = []
        errors = []
        
        if not dry_run:
            for file in to_delete:
                try:
                    file.unlink()
                    deleted_count += 1
                    deleted_files.append(str(file))
                    self.logger.info(f"已删除大日志文件: {file}")
                except Exception as e:
                    error_msg = f"删除文件失败: {file}, 错误: {e}"
                    errors.append(error_msg)
                    self.logger.error(error_msg)
        
        return {
            "original_size_mb": total_size / (1024 * 1024),
            "target_size_mb": max_size_mb,
            "to_delete_count": len(to_delete),
            "deleted_count": deleted_count,
            "deleted_files": deleted_files,
            "errors": errors,
            "dry_run": dry_run
        }
    
    def cleanup_duplicates(self, dry_run: bool = False) -> Dict:
        """
        清理重复的日志文件（基于文件名模式）
        
        @param {bool} dry_run - 试运行模式
        @returns {Dict} 清理结果
        
        @example
            # 清理重复的日志文件
            result = cleaner.cleanup_duplicates()
            print(f"已删除 {result['deleted_count']} 个重复文件")
        """
        files = self.get_log_files()
        
        # 按文件名分组
        file_groups = {}
        for file in files:
            # 提取基础文件名（去掉时间戳）
            base_name = file.stem.split('_')[0]  # 取spider部分
            if base_name not in file_groups:
                file_groups[base_name] = []
            file_groups[base_name].append(file)
        
        to_delete = []
        for base_name, group_files in file_groups.items():
            if len(group_files) > 1:
                # 保留最新的文件，删除其他文件
                group_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
                to_delete.extend(group_files[1:])  # 删除除最新文件外的所有文件
        
        deleted_count = 0
        deleted_files = []
        errors = []
        
        if not dry_run:
            for file in to_delete:
                try:
                    file.unlink()
                    deleted_count += 1
                    deleted_files.append(str(file))
                    self.logger.info(f"已删除重复日志文件: {file}")
                except Exception as e:
                    error_msg = f"删除文件失败: {file}, 错误: {e}"
                    errors.append(error_msg)
                    self.logger.error(error_msg)
        
        return {
            "to_delete_count": len(to_delete),
            "deleted_count": deleted_count,
            "deleted_files": deleted_files,
            "errors": errors,
            "dry_run": dry_run
        }
    
    def print_stats(self) -> None:
        """
        打印日志文件统计信息
        
        @returns {None}
        
        @example
            cleaner.print_stats()
            # 输出: 总文件数: 25, 总大小: 45.67MB
        """
        stats = self.get_log_stats()
        
        print(f"📊 日志文件统计信息:")
        print(f"   总文件数: {stats['total_files']}")
        print(f"   总大小: {stats['total_size_mb']:.2f}MB")
        print(f"   今日文件: {stats['today_files']}")
        print(f"   本周文件: {stats['week_files']}")
        print(f"   本月文件: {stats['month_files']}")
        print(f"   更早文件: {stats['older_files']}")


def main():
    """
    命令行入口函数
    
    提供命令行界面来使用日志清理功能。
    
    @returns {None}
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="日志文件清理工具")
    parser.add_argument("--log-dir", default="logs", help="日志目录路径")
    parser.add_argument("--days", type=int, default=7, help="保留天数")
    parser.add_argument("--max-size", type=float, help="最大总大小(MB)")
    parser.add_argument("--duplicates", action="store_true", help="清理重复文件")
    parser.add_argument("--dry-run", action="store_true", help="试运行模式")
    parser.add_argument("--stats", action="store_true", help="显示统计信息")
    
    args = parser.parse_args()
    
    cleaner = LogCleaner(args.log_dir)
    
    if args.stats:
        cleaner.print_stats()
        return
    
    if args.duplicates:
        result = cleaner.cleanup_duplicates(dry_run=args.dry_run)
        print(f"重复文件清理结果: {result['deleted_count']} 个文件已删除")
        return
    
    if args.max_size:
        result = cleaner.cleanup_by_size(max_size_mb=args.max_size, dry_run=args.dry_run)
        print(f"大小清理结果: {result['deleted_count']} 个文件已删除")
        return
    
    # 默认按时间清理
    result = cleaner.cleanup_by_age(days=args.days, dry_run=args.dry_run)
    print(f"时间清理结果: {result['deleted_count']} 个文件已删除")


if __name__ == "__main__":
    main()
