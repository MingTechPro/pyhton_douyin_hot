"""
日志管理器模块

@author: MingTechPro
@version: 2.1.0
@date: 2025-08-15
@description: 该模块提供了统一的日志管理功能，采用单例模式确保日志配置的一致性。
             支持控制台和文件双重输出，自动日志轮转，彩色输出等功能。

主要功能:
- 统一的日志配置管理
- 控制台和文件双重输出
- 自动日志文件轮转
- 时间戳命名
- 彩色日志输出
- 不同级别的日志控制

设计模式:
- 单例模式: 确保全局唯一的日志管理器
- 工厂模式: 动态创建日志处理器

@example
    # 获取日志管理器实例
    log_manager = LogManager()
    logger = log_manager.get_logger()
    
    # 记录日志
    logger.info("这是一条信息日志")
    logger.error("这是一条错误日志")
"""
import logging
import logging.handlers
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any


class LogManager:
    """
    日志管理器类
    
    采用单例模式实现的日志管理器，提供统一的日志配置和管理功能。
    支持控制台和文件双重输出，自动日志轮转等特性。
    
    @author: MingTechPro
    @version: 2.1.0
    @date: 2025-08-15
    
    主要特性:
    - 单例模式确保全局唯一
    - 支持控制台和文件输出
    - 自动日志文件轮转
    - 时间戳文件命名
    - 灵活的配置选项
    
    @example
        # 获取日志管理器实例
        log_manager = LogManager()
        
        # 获取日志器
        logger = log_manager.get_logger()
        
        # 记录不同级别的日志
        logger.debug("调试信息")
        logger.info("一般信息")
        logger.warning("警告信息")
        logger.error("错误信息")
    """
    
    _instance = None    # 单例实例
    _logger = None      # 日志器实例
    
    def __new__(cls):
        """
        单例模式实现
        
        确保LogManager类只有一个实例。
        
        @returns {LogManager} 单例实例
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """
        初始化日志管理器
        
        如果日志器未初始化，则进行初始化设置。
        """
        if self._logger is None:
            self._setup_logger()
    
    def _setup_logger(self, config: Optional[Dict[str, Any]] = None) -> None:
        """
        设置日志器配置
        
        根据配置参数设置日志器的各种参数，包括级别、格式、处理器等。
        
        @param {Optional[Dict[str, Any]]} config - 日志配置字典，如果为None则使用默认配置
        @returns {None}
        
        @example
            config = {
                "level": "DEBUG",
                "log_file": "logs/custom.log",
                "max_file_size": "5MB"
            }
            self._setup_logger(config)
        """
        # 默认配置
        default_config = {
            "level": "INFO",                    # 全局日志级别
            "console_level": "INFO",            # 控制台日志级别
            "file_level": "DEBUG",              # 文件日志级别
            "log_file": "logs/spider_{timestamp}.log",  # 日志文件路径
            "max_file_size": "10MB",            # 最大文件大小
            "backup_count": 5,                  # 备份文件数量
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",  # 日志格式
            "date_format": "%Y-%m-%d %H:%M:%S"  # 日期格式
        }
        
        # 合并用户配置
        if config:
            default_config.update(config)
        
        # 创建日志器
        self._logger = logging.getLogger('douyin_spider')
        self._logger.setLevel(getattr(logging, default_config["level"]))
        
        # 清除已有的处理器，避免重复添加
        self._logger.handlers.clear()
        
        # 创建格式器
        formatter = logging.Formatter(
            default_config["format"],
            datefmt=default_config["date_format"]
        )
        
        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, default_config["console_level"]))
        console_handler.setFormatter(formatter)
        self._logger.addHandler(console_handler)
        
        # 创建文件处理器 - 使用时间戳命名
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S_%f")[:-3]
        log_file_path = default_config["log_file"].replace("{timestamp}", timestamp)
        
        # 确保日志目录存在
        log_dir = Path(log_file_path).parent
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # 解析文件大小限制
        size_str = default_config["max_file_size"].upper()
        if size_str.endswith('MB'):
            max_bytes = int(size_str[:-2]) * 1024 * 1024
        elif size_str.endswith('KB'):
            max_bytes = int(size_str[:-2]) * 1024
        else:
            max_bytes = int(size_str)
        
        # 创建轮转文件处理器
        file_handler = logging.handlers.RotatingFileHandler(
            log_file_path,
            maxBytes=max_bytes,
            backupCount=default_config["backup_count"],
            encoding='utf-8'
        )
        file_handler.setLevel(getattr(logging, default_config["file_level"]))
        file_handler.setFormatter(formatter)
        self._logger.addHandler(file_handler)
        
        # 记录初始化信息
        self._logger.info("日志系统初始化完成")
        self._logger.info(f"日志文件路径: {log_file_path}")
    
    @classmethod
    def get_logger(cls) -> logging.Logger:
        """
        获取日志器实例
        
        类方法，用于获取全局唯一的日志器实例。
        如果实例不存在，会自动创建。
        
        @returns {logging.Logger} 日志器实例
        
        @example
            # 获取日志器
            logger = LogManager.get_logger()
            
            # 记录日志
            logger.info("这是一条信息日志")
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance._logger
    
    @classmethod
    def setup_logger(cls, config: Dict[str, Any]) -> None:
        """
        设置日志器配置
        
        类方法，用于动态配置日志器参数。
        如果实例不存在，会自动创建。
        
        @param {Dict[str, Any]} config - 日志配置字典
        @returns {None}
        
        @example
            config = {
                "level": "DEBUG",
                "log_file": "logs/debug.log",
                "max_file_size": "5MB"
            }
            LogManager.setup_logger(config)
        """
        if cls._instance is None:
            cls._instance = cls()
        cls._instance._setup_logger(config)
    
    @classmethod
    def set_level(cls, level: str) -> None:
        """
        设置日志级别
        
        动态设置日志器的全局级别。
        
        @param {str} level - 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        @returns {None}
        
        @example
            # 设置为调试级别
            LogManager.set_level("DEBUG")
            
            # 设置为错误级别
            LogManager.set_level("ERROR")
        """
        if cls._instance is None:
            cls._instance = cls()
        
        if cls._instance._logger:
            cls._instance._logger.setLevel(getattr(logging, level.upper()))
        
        # 同时更新所有处理器的级别
        for handler in cls._instance._logger.handlers:
            if isinstance(handler, logging.StreamHandler):
                handler.setLevel(getattr(logging, level.upper()))
    
    @classmethod
    def add_file_handler(cls, file_path: str, level: str = "DEBUG") -> None:
        """
        添加文件处理器
        Args:
            file_path: 文件路径
            level: 日志级别
        """
        logger = cls.get_logger()
        
        # 确保目录存在
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        
        # 创建文件处理器
        file_handler = logging.FileHandler(file_path, encoding='utf-8')
        file_handler.setLevel(getattr(logging, level.upper()))
        
        # 使用相同的格式器
        if logger.handlers:
            file_handler.setFormatter(logger.handlers[0].formatter)
        
        logger.addHandler(file_handler)
    
    @classmethod
    def cleanup_old_logs(cls, log_dir: str, days: int = 7) -> None:
        """
        清理旧日志文件
        Args:
            log_dir: 日志目录
            days: 保留天数
        """
        try:
            log_path = Path(log_dir)
            if not log_path.exists():
                return
            
            cutoff_time = datetime.now().timestamp() - (days * 24 * 60 * 60)
            
            for log_file in log_path.glob("*.log"):
                if log_file.stat().st_mtime < cutoff_time:
                    log_file.unlink()
                    cls.get_logger().info(f"已删除旧日志文件: {log_file}")
                    
        except Exception as e:
            cls.get_logger().error(f"清理旧日志文件失败: {e}")


# 便捷函数
def get_logger(name: str = None) -> logging.Logger:
    """
    获取日志器
    Args:
        name: 日志器名称
    Returns:
        logging.Logger: 日志器
    """
    if name:
        return logging.getLogger(name)
    return LogManager.get_logger()


def setup_logging(config: Dict[str, Any]) -> None:
    """
    设置日志系统的便捷函数
    
    提供便捷的日志系统初始化方法，直接调用即可完成日志配置。
    
    @param {Dict[str, Any]} config - 日志配置字典
    @returns {None}
    
    @example
        config = {
            "level": "INFO",
            "log_file": "logs/app.log",
            "max_file_size": "10MB"
        }
        setup_logging(config)
        
        # 获取日志器并记录日志
        logger = LogManager.get_logger()
        logger.info("日志系统已初始化")
    """
    LogManager.setup_logger(config)
