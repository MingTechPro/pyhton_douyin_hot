#!/usr/bin/env python3
"""
日志管理脚本

@author: MingTechPro
@version: 1.0.0
@date: 2025-08-15
@description: 这是一个便捷的日志管理脚本，提供日志文件查看、清理、统计等功能。

使用示例:
    python manage_logs.py --stats                    # 查看日志统计信息
    python manage_logs.py --cleanup --days 7         # 清理7天前的日志
    python manage_logs.py --cleanup --max-size 50    # 清理超过50MB的日志
    python manage_logs.py --cleanup --duplicates     # 清理重复日志文件
    python manage_logs.py --view --recent 5          # 查看最近5个日志文件
"""

import sys
import argparse
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.utils.log_cleaner import LogCleaner


def view_recent_logs(log_dir: str = "logs", count: int = 10):
    """
    查看最近的日志文件
    
    @param {str} log_dir - 日志目录
    @param {int} count - 显示数量
    @returns {None}
    """
    cleaner = LogCleaner(log_dir)
    files = cleaner.get_log_files()
    
    # 按修改时间排序
    files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    
    print(f"📋 最近 {min(count, len(files))} 个日志文件:")
    print("-" * 80)
    
    for i, file in enumerate(files[:count]):
        stat = file.stat()
        size_mb = stat.st_size / (1024 * 1024)
        mtime = Path(file).stat().st_mtime
        from datetime import datetime
        mtime_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"{i+1:2d}. {file.name}")
        print(f"    大小: {size_mb:.2f}MB | 修改时间: {mtime_str}")
        
        # 显示文件前几行内容
        try:
            with open(file, 'r', encoding='utf-8') as f:
                lines = f.readlines()[:3]  # 只显示前3行
                for line in lines:
                    print(f"    {line.rstrip()}")
        except Exception as e:
            print(f"    读取文件失败: {e}")
        print()


def main():
    """
    主函数
    
    @returns {None}
    """
    parser = argparse.ArgumentParser(
        description="日志管理工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python manage_logs.py --stats                    # 查看日志统计信息
  python manage_logs.py --cleanup --days 7         # 清理7天前的日志
  python manage_logs.py --cleanup --max-size 50    # 清理超过50MB的日志
  python manage_logs.py --cleanup --duplicates     # 清理重复日志文件
  python manage_logs.py --view --recent 5          # 查看最近5个日志文件
  python manage_logs.py --cleanup --dry-run        # 试运行清理操作
        """
    )
    
    parser.add_argument("--log-dir", default="logs", help="日志目录路径")
    
    # 子命令
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # 统计命令
    stats_parser = subparsers.add_parser("stats", help="查看日志统计信息")
    
    # 查看命令
    view_parser = subparsers.add_parser("view", help="查看日志文件")
    view_parser.add_argument("--recent", type=int, default=10, help="显示最近的文件数量")
    
    # 清理命令
    cleanup_parser = subparsers.add_parser("cleanup", help="清理日志文件")
    cleanup_parser.add_argument("--days", type=int, help="保留天数")
    cleanup_parser.add_argument("--max-size", type=float, help="最大总大小(MB)")
    cleanup_parser.add_argument("--duplicates", action="store_true", help="清理重复文件")
    cleanup_parser.add_argument("--dry-run", action="store_true", help="试运行模式")
    
    args = parser.parse_args()
    
    if not args.command:
        # 默认显示统计信息
        cleaner = LogCleaner(args.log_dir)
        cleaner.print_stats()
        return
    
    if args.command == "stats":
        cleaner = LogCleaner(args.log_dir)
        cleaner.print_stats()
        
    elif args.command == "view":
        view_recent_logs(args.log_dir, args.recent)
        
    elif args.command == "cleanup":
        cleaner = LogCleaner(args.log_dir)
        
        if args.duplicates:
            result = cleaner.cleanup_duplicates(dry_run=args.dry_run)
            print(f"重复文件清理结果: {result['deleted_count']} 个文件已删除")
            
        elif args.max_size:
            result = cleaner.cleanup_by_size(max_size_mb=args.max_size, dry_run=args.dry_run)
            print(f"大小清理结果: {result['deleted_count']} 个文件已删除")
            print(f"原始大小: {result['original_size_mb']:.2f}MB")
            print(f"目标大小: {result['target_size_mb']:.2f}MB")
            
        elif args.days:
            result = cleaner.cleanup_by_age(days=args.days, dry_run=args.dry_run)
            print(f"时间清理结果: {result['deleted_count']} 个文件已删除")
            print(f"清理时间点: {result['cutoff_time']}")
            
        else:
            # 默认清理7天前的文件
            result = cleaner.cleanup_by_age(days=7, dry_run=args.dry_run)
            print(f"时间清理结果: {result['deleted_count']} 个文件已删除")
            print(f"清理时间点: {result['cutoff_time']}")


if __name__ == "__main__":
    main()
