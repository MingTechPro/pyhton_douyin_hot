#!/usr/bin/env python3
"""
抖音热榜爬虫 - 优化版本
使用模块化架构，提供更好的可维护性和扩展性

@author: MingTechPro
@version: 1.0.0
@date: 2025-08-15
@description: 这是一个经过优化的抖音热榜爬虫程序，采用模块化设计，
             支持多种输出格式、性能监控、缓存机制等功能。

主要特性:
- 模块化架构设计
- 多格式输出支持 (JSON/CSV/TXT/Markdown)
- 性能监控和统计
- 智能缓存机制
- 灵活的配置管理
- 完善的错误处理
- 命令行参数支持

使用示例:
    python main_optimized.py                    # 使用默认配置
    python main_optimized.py -n 5               # 获取前5条数据
    python main_optimized.py -i 2               # 请求间隔2秒
    python main_optimized.py --performance      # 显示详细性能信息
    python main_optimized.py --format csv -o result.csv  # CSV格式输出
"""

import sys
import argparse
import traceback
from pathlib import Path
from datetime import datetime

# 添加src目录到Python路径，确保能够导入自定义模块
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.config.config_manager import ConfigManager
from src.utils.logger import LogManager, setup_logging
from src.utils.performance import PerformanceMonitor, CacheManager, RateLimiter
from src.core.models import HotListResponse, CrawlResult
from src.spider.douyin_spider import DouyinSpider


def parse_arguments() -> argparse.Namespace:
    """
    解析命令行参数
    
    创建并配置命令行参数解析器，支持多种参数选项：
    - 数据获取参数：控制爬取的数量和间隔
    - 输出参数：指定输出格式和文件路径
    - 调试参数：控制日志级别和性能监控
    - 其他参数：版本信息等
    
    @returns {argparse.Namespace} 解析后的命令行参数对象
    @example
        args = parse_arguments()
        print(args.max_items)  # 获取最大项目数参数
    """
    parser = argparse.ArgumentParser(
        description="抖音热榜爬虫 - 优化版本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python main_optimized.py                    # 使用默认配置
  python main_optimized.py -n 5               # 获取前5条数据
  python main_optimized.py -i 2               # 请求间隔2秒
  python main_optimized.py -n 10 -i 1.5      # 获取10条，间隔1.5秒
  python main_optimized.py --no-skip-top     # 不跳过热榜置顶
  python main_optimized.py --debug            # 开启调试模式
  python main_optimized.py --performance      # 显示详细性能信息
  python main_optimized.py -h                 # 显示帮助信息
        """
    )
    
    # 数据获取参数组
    parser.add_argument(
        '-n', '--max-items',
        type=int,
        help='最大获取项目数 (默认: 使用配置文件中的值)'
    )
    
    parser.add_argument(
        '-i', '--interval',
        type=float,
        help='请求间隔时间(秒) (默认: 使用配置文件中的值)'
    )
    
    parser.add_argument(
        '--no-skip-top',
        action='store_true',
        help='不跳过热榜置顶项目 (默认: 跳过)'
    )
    
    # 输出参数组
    parser.add_argument(
        '-o', '--output',
        type=str,
        help='输出文件路径 (默认: 输出到控制台)'
    )
    
    parser.add_argument(
        '--format',
        choices=['json', 'csv', 'txt', 'markdown'],
        default='json',
        help='输出格式 (默认: json)'
    )
    
    # 调试和性能参数组
    parser.add_argument(
        '--debug',
        action='store_true',
        help='开启调试模式 (更详细的日志输出)'
    )
    
    parser.add_argument(
        '--performance',
        action='store_true',
        help='显示详细性能信息'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='试运行模式 (不实际获取数据，只显示配置)'
    )
    
    # 其他参数组
    parser.add_argument(
        '--version',
        action='version',
        version='抖音热榜爬虫 v1.0.0 (优化版本)'
    )
    
    return parser.parse_args()


def apply_command_line_args(config_manager: ConfigManager, args: argparse.Namespace) -> None:
    """
    应用命令行参数到配置管理器
    
    将命令行参数转换为配置更新，并应用到配置管理器中。
    只有非None的参数才会被更新，确保不会覆盖有效的默认值。
    
    @param {ConfigManager} config_manager - 配置管理器实例
    @param {argparse.Namespace} args - 解析后的命令行参数
    @returns {None}
    
    @example
        config_manager = ConfigManager()
        args = parse_arguments()
        apply_command_line_args(config_manager, args)
    """
    config_updates = {}
    
    # 更新最大项目数配置
    if args.max_items is not None:
        config_updates['max_items'] = args.max_items
        
    # 更新请求间隔配置
    if args.interval is not None:
        config_updates['request_interval'] = args.interval
        
    # 更新是否跳过置顶配置
    if args.no_skip_top:
        config_updates['skip_top_item'] = False
    
    # 批量更新配置
    if config_updates:
        config_manager.update_config(**config_updates)


def setup_environment(config_manager: ConfigManager, args: argparse.Namespace) -> tuple:
    """
    设置运行环境
    
    初始化程序运行所需的环境，包括：
    - 加载和应用配置
    - 设置日志系统
    - 应用命令行参数覆盖
    
    @param {ConfigManager} config_manager - 配置管理器实例
    @param {argparse.Namespace} args - 命令行参数
    @returns {tuple} 返回(配置对象, 日志器)的元组
    
    @example
        config_manager = ConfigManager()
        args = parse_arguments()
        config, logger = setup_environment(config_manager, args)
    """
    # 加载配置
    config = config_manager.get_config()
    
    # 应用命令行参数覆盖
    apply_command_line_args(config_manager, args)
    
    # 设置日志配置
    log_config = {
        "level": "DEBUG" if args.debug else config.log_level,
        "console_level": "DEBUG" if args.debug else config.console_log_level,
        "file_level": config.file_log_level,
        "log_file": config.log_file_path,
        "max_file_size": config.log_max_file_size,
        "backup_count": config.log_backup_count,
        "format": config.log_format,
        "date_format": config.log_date_format
    }
    
    # 初始化日志系统
    setup_logging(log_config)
    logger = LogManager.get_logger()
    
    return config, logger


def output_result(result: CrawlResult, args: argparse.Namespace, config) -> None:
    """
    输出爬取结果
    
    根据指定的格式将爬取结果输出到文件或控制台。
    支持多种输出格式：JSON、CSV、TXT、Markdown。
    如果未指定输出文件，将使用默认路径和文件名模板。
    
    @param {CrawlResult} result - 爬取结果对象
    @param {argparse.Namespace} args - 命令行参数
    @param {object} config - 配置对象
    @returns {None}
    
    @example
        result = spider.crawl()
        output_result(result, args, config)
    """
    # 检查是否有有效数据
    if not result.success or not result.data:
        print("未获取到有效数据")
        return
    
    # 根据输出格式生成结果数据
    if args.format == 'json':
        import json
        result_data = json.dumps(
            result.data.to_dict(), 
            ensure_ascii=config.ensure_ascii, 
            indent=config.output_indent
        )
    elif args.format == 'csv':
        from src.utils.formatters import convert_to_csv
        result_data = convert_to_csv(result.data)
    elif args.format == 'txt':
        from src.utils.formatters import convert_to_txt
        result_data = convert_to_txt(result.data)
    elif args.format == 'markdown':
        from src.utils.formatters import convert_to_markdown
        result_data = convert_to_markdown(result.data)
    else:
        # 默认使用JSON格式
        import json
        result_data = json.dumps(
            result.data.to_dict(), 
            ensure_ascii=config.ensure_ascii, 
            indent=config.output_indent
        )
    
    # 确定输出文件路径
    output_path = args.output
    if not output_path:
        # 使用默认输出路径和文件名模板
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = config.output_filename_template.replace("{timestamp}", timestamp)
        filename = f"{filename}.{args.format}"
        
        # 确保输出目录存在
        output_dir = Path(config.output_default_path)
        output_dir.mkdir(exist_ok=True)
        
        output_path = output_dir / filename
    
    # 输出到文件或控制台
    try:
        # 确保输出目录存在
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result_data)
        print(f"结果已保存到文件: {output_file}")
    except Exception as e:
        print(f"保存文件失败: {e}")
        print(result_data)  # 回退到控制台输出


def main():
    """
    主执行函数
    
    程序的主入口点，负责：
    - 解析命令行参数
    - 初始化配置和日志
    - 创建爬虫实例
    - 执行爬取操作
    - 输出结果和性能统计
    
    @returns {None}
    
    @throws {KeyboardInterrupt} 当用户按Ctrl+C时抛出
    @throws {Exception} 当程序执行出现严重错误时抛出
    
    @example
        if __name__ == "__main__":
            main()
    """
    # 解析命令行参数
    args = parse_arguments()
    
    try:
        # 初始化配置管理器
        config_manager = ConfigManager()
        
        # 设置运行环境
        config, logger = setup_environment(config_manager, args)
        
        # 试运行模式检查
        if args.dry_run:
            logger.info("=== 试运行模式 ===")
            logger.info(f"配置信息 - 最大项目数: {config.max_items}, 请求间隔: {config.request_interval}秒")
            logger.info(f"跳过置顶: {config.skip_top_item}, 输出格式: {args.format}")
            if args.output:
                logger.info(f"输出文件: {args.output}")
            logger.info("试运行完成，退出程序")
            return
        
        # 开始执行爬虫
        logger.info("=== 抖音热榜爬虫开始执行 (优化版本) ===")
        logger.info(f"配置信息 - 最大项目数: {config.max_items}, 请求间隔: {config.request_interval}秒")
        
        # 创建性能监控器
        perf_monitor = PerformanceMonitor()
        perf_monitor.start()
        
        # 创建缓存管理器
        cache_manager = CacheManager(
            max_size=100,
            ttl=config.cache_duration
        )
        
        # 创建速率限制器
        rate_limiter = RateLimiter(
            max_requests=config.rate_limit_requests,
            time_window=config.rate_limit_period
        )
        
        # 创建爬虫实例
        spider = DouyinSpider(
            config=config,
            logger=logger,
            cache_manager=cache_manager,
            rate_limiter=rate_limiter
        )
        
        # 执行爬取操作
        result = spider.crawl()
        
        # 结束性能监控
        perf_monitor.end()
        
        # 输出性能统计信息
        if args.performance:
            # 详细性能统计
            stats = perf_monitor.get_stats()
            logger.info("=== 详细性能统计 ===")
            logger.info(f"总执行时间: {stats['total_time']}秒")
            logger.info(f"请求总数: {stats['request_count']}")
            logger.info(f"成功请求: {stats['success_count']}")
            logger.info(f"失败请求: {stats['error_count']}")
            logger.info(f"成功率: {stats['success_rate']}%")
            logger.info(f"平均请求时间: {stats['avg_request_time']}秒")
            logger.info(f"每秒请求数: {stats['requests_per_second']}")
            logger.info(f"内存使用: {stats['memory_usage']}MB")
            logger.info(f"CPU使用: {stats['cpu_usage']}%")
            logger.info(f"最大内存: {stats['max_memory']}MB")
            logger.info(f"最大CPU: {stats['max_cpu']}%")
            logger.info(f"最快请求: {stats['min_request_time']}秒")
            logger.info(f"最慢请求: {stats['max_request_time']}秒")
        else:
            # 简要性能统计
            stats = perf_monitor.get_stats()
            logger.info("=== 性能统计 ===")
            logger.info(f"总执行时间: {stats['total_time']}秒")
            logger.info(f"成功率: {stats['success_rate']}%")
            logger.info(f"平均请求时间: {stats['avg_request_time']}秒")
        
        # 输出爬取结果
        if result.success:
            logger.info(f"=== 爬取成功：处理 {result.items_processed} 条，成功 {result.items_success} 条 ===")
            output_result(result, args, config)
        else:
            logger.error(f"爬取失败: {result.error_message}")
            
    except KeyboardInterrupt:
        # 处理用户中断
        print("\n程序被用户中断")
    except Exception as e:
        # 处理严重错误
        print(f"程序执行出现严重错误：{str(e)}")
        if args.debug:
            print(f"异常详情：{traceback.format_exc()}")


if __name__ == "__main__":
    main()
