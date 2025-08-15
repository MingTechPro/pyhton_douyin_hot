"""
配置管理器模块

@author: MingTechPro
@version: 2.1.0
@date: 2025-08-15
@description: 该模块负责管理抖音爬虫的所有配置信息，包括从配置文件加载、
             环境变量覆盖、配置验证等功能。采用单例模式确保配置的一致性。

主要功能:
- 配置文件加载和解析
- 环境变量配置覆盖
- 配置参数验证
- 动态配置更新
- 配置热重载支持

配置层次:
1. 默认配置 (硬编码)
2. 配置文件 (config.json)
3. 环境变量 (env_config.py)
4. 命令行参数 (运行时)

@example
    # 创建配置管理器
    config_manager = ConfigManager()
    
    # 获取配置
    config = config_manager.get_config()
    
    # 更新配置
    config_manager.update_config(max_items=10, request_interval=2)
"""
import json
import os
import importlib.util
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime


@dataclass
class AppConfig:
    """
    应用配置数据类
    
    使用dataclass装饰器自动生成初始化方法、字符串表示等。
    包含抖音爬虫运行所需的所有配置参数。
    
    @author: MingTechPro
    @version: 2.1.0
    @date: 2025-08-15
    
    配置分类:
    - URLs: 目标网站地址
    - 请求配置: HTTP请求相关参数
    - 重试配置: 失败重试策略
    - 爬虫配置: 爬取行为控制
    - 输出配置: 数据输出格式
    - 日志配置: 日志记录设置
    - 高级配置: 代理、限流、并发等
    
    @example
        config = AppConfig(
            hot_list_url="https://www.douyin.com/hot",
            video_url="https://www.douyin.com/video",
            user_agent="Mozilla/5.0...",
            max_items=10,
            request_interval=2
        )
        
        # 验证配置
        config.validate()
    """
    
    # URLs配置组 - 目标网站地址
    hot_list_url: str          # 热榜页面URL
    video_url: str             # 视频详情页面URL
    
    # 请求配置组 - HTTP请求相关参数
    user_agent: str            # 浏览器User-Agent
    cookie: str                # 请求Cookie
    hot_list_timeout: int      # 热榜请求超时时间(秒)
    video_detail_timeout: int  # 视频详情请求超时时间(秒)
    
    # 重试配置组 - 失败重试策略
    hot_list_max_retries: int      # 热榜请求最大重试次数
    hot_list_delay: int            # 热榜请求重试延迟(秒)
    video_detail_max_retries: int  # 视频详情请求最大重试次数
    video_detail_delay: int        # 视频详情请求重试延迟(秒)
    
    # 爬虫配置组 - 爬取行为控制
    max_items: int             # 最大获取项目数
    request_interval: int      # 请求间隔时间(秒)
    skip_top_item: bool        # 是否跳过热榜置顶项目
    enable_cache: bool         # 是否启用缓存
    cache_duration: int        # 缓存持续时间(秒)
    concurrent_requests: bool  # 是否启用并发请求
    
    # 输出配置组 - 数据输出格式
    output_format: str         # 输出格式 (json/csv/txt/markdown)
    output_indent: int         # JSON输出缩进
    ensure_ascii: bool         # 是否确保ASCII编码
    output_default_path: str   # 默认输出路径
    output_filename_template: str  # 输出文件名模板
    
    # 日志配置组 - 日志记录设置
    log_level: str             # 日志级别
    console_log_level: str     # 控制台日志级别
    file_log_level: str        # 文件日志级别
    log_file_path: str         # 日志文件路径
    log_max_file_size: str     # 日志文件最大大小
    log_backup_count: int      # 日志文件备份数量
    log_format: str            # 日志格式
    log_date_format: str       # 日志日期格式
    
    # URL编码配置组 - URL编码相关设置
    url_encoding_enabled: bool = True              # 是否启用URL编码
    url_encoding_method: str = "url_encode"        # URL编码方法 (url_encode/base64/hash)
    url_encoding_encoding: str = "utf-8"           # URL编码字符集
    url_encoding_safe_chars: str = ""              # URL编码安全字符
    
    # 高级配置组 - 代理、限流、并发等
    enable_proxy: bool = False                     # 是否启用代理
    proxy_config: Dict[str, str] = field(default_factory=dict)  # 代理配置
    enable_rate_limit: bool = True                 # 是否启用速率限制
    rate_limit_requests: int = 10                  # 速率限制请求数
    rate_limit_period: int = 60                    # 速率限制时间窗口(秒)
    enable_retry_backoff: bool = True              # 是否启用重试退避
    max_concurrent_workers: int = 3                # 最大并发工作线程数
    
    def validate(self) -> None:
        """
        验证配置参数的有效性
        
        检查所有配置参数是否符合业务逻辑要求，确保配置的正确性。
        如果发现无效配置，将抛出ValueError异常。
        
        @returns {None}
        @throws {ValueError} 当配置参数无效时抛出
        
        @example
            config = AppConfig(...)
            try:
                config.validate()
                print("配置验证通过")
            except ValueError as e:
                print(f"配置验证失败: {e}")
        """
        # 验证URL配置
        if not self.hot_list_url or not self.hot_list_url.startswith('http'):
            raise ValueError("热榜URL不能为空且必须是有效的HTTP(S)地址")
        
        if not self.video_url or not self.video_url.startswith('http'):
            raise ValueError("视频URL不能为空且必须是有效的HTTP(S)地址")
            
        # 验证请求配置
        if not self.user_agent:
            raise ValueError("User-Agent不能为空")
            
        if self.hot_list_timeout is None or self.hot_list_timeout <= 0 or self.video_detail_timeout is None or self.video_detail_timeout <= 0:
            raise ValueError("超时时间必须大于0")
            
        # 验证重试配置
        if self.hot_list_max_retries is None or self.hot_list_max_retries < 0 or self.video_detail_max_retries is None or self.video_detail_max_retries < 0:
            raise ValueError("重试次数不能为负数")
            
        if self.hot_list_delay is None or self.hot_list_delay < 0 or self.video_detail_delay is None or self.video_detail_delay < 0:
            raise ValueError("重试延迟不能为负数")
            
        # 验证爬虫配置
        if self.max_items is None or self.max_items <= 0:
            raise ValueError("最大项目数必须大于0")
            
        if self.request_interval is None or self.request_interval < 0:
            raise ValueError("请求间隔不能为负数")
            
        # 验证输出配置
        if self.output_indent is None or self.output_indent < 0:
            raise ValueError("输出缩进不能为负数")
            
        # 验证高级配置
        if self.rate_limit_requests is None or self.rate_limit_requests <= 0 or self.rate_limit_period is None or self.rate_limit_period <= 0:
            raise ValueError("限流配置必须大于0")
            
        if self.max_concurrent_workers is None or self.max_concurrent_workers <= 0:
            raise ValueError("并发工作线程数必须大于0")


class ConfigManager:
    """
    配置管理器
    
    该类负责管理抖音爬虫的所有配置信息，包括从配置文件加载、
    环境变量覆盖、配置验证等功能。采用单例模式确保配置的一致性。
    
    @author: MingTechPro
    @version: 2.1.0
    @date: 2025-08-15
    
    主要功能:
    - 配置文件加载和解析
    - 环境变量配置覆盖
    - 配置参数验证
    - 动态配置更新
    - 配置热重载支持
    
    配置层次:
    1. 默认配置 (硬编码)
    2. 配置文件 (config.json)
    3. 环境变量 (env_config.py)
    4. 命令行参数 (运行时)
    
    @example
        # 创建配置管理器
        config_manager = ConfigManager()
        
        # 获取配置
        config = config_manager.get_config()
        
        # 更新配置
        config_manager.update_config(max_items=10, request_interval=2)
    """
    
    def __init__(self, config_dir: Optional[str] = None):
        """
        初始化配置管理器
        
        创建配置管理器实例，设置配置文件目录路径。
        
        @param {Optional[str]} config_dir - 配置文件目录路径，如果为None则使用默认路径
        @returns {None}
        
        @example
            # 使用默认配置目录
            config_manager = ConfigManager()
            
            # 指定配置目录
            config_manager = ConfigManager("/path/to/config")
        """
        self.config_dir = Path(config_dir) if config_dir else Path(__file__).parent.parent.parent
        self._config: Optional[AppConfig] = None
        self._env_config: Dict[str, Any] = {}
        
    def load_config(self) -> AppConfig:
        """
        加载配置文件
        
        从配置文件和环境变量中加载所有配置信息，创建AppConfig对象。
        采用懒加载模式，只在首次调用时加载配置。
        
        @returns {AppConfig} 配置对象，包含所有配置参数
        
        @throws {FileNotFoundError} 当配置文件不存在时抛出
        @throws {RuntimeError} 当配置加载失败时抛出
        @throws {ValueError} 当配置验证失败时抛出
        
        @example
            config_manager = ConfigManager()
            config = config_manager.load_config()
            print(f"最大项目数: {config.max_items}")
        """
        if self._config is not None:
            return self._config
            
        try:
            # 加载基础配置文件
            config_file = self.config_dir / "config.json"
            if not config_file.exists():
                raise FileNotFoundError(f"配置文件不存在: {config_file}")
            
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # 加载环境配置
            self._load_env_config()
            
            # 创建配置对象，环境配置优先
            self._config = AppConfig(
                # URLs配置
                hot_list_url=config_data["urls"]["hot_list"],
                video_url=config_data["urls"]["video"],
                
                # 请求配置
                user_agent=config_data["request"]["headers"]["User-Agent"],
                cookie=self._env_config.get('DOUYIN_COOKIE', ''),
                hot_list_timeout=config_data["request"]["timeouts"]["hot_list"],
                video_detail_timeout=config_data["request"]["timeouts"]["video_detail"],
                
                # 重试配置
                hot_list_max_retries=config_data["request"]["retry"]["hot_list_max_retries"],
                hot_list_delay=config_data["request"]["retry"]["hot_list_delay"],
                video_detail_max_retries=config_data["request"]["retry"]["video_detail_max_retries"],
                video_detail_delay=config_data["request"]["retry"]["video_detail_delay"],
                
                # 爬虫配置（环境配置优先）
                max_items=self._env_config.get('MAX_ITEMS') if self._env_config.get('MAX_ITEMS') is not None else config_data["crawler"]["max_items"],
                request_interval=self._env_config.get('REQUEST_INTERVAL') if self._env_config.get('REQUEST_INTERVAL') is not None else config_data["crawler"]["request_interval"],
                skip_top_item=config_data["crawler"]["skip_top_item"],
                enable_cache=config_data["crawler"]["enable_cache"],
                cache_duration=config_data["crawler"]["cache_duration"],
                concurrent_requests=config_data["crawler"]["concurrent_requests"],
                
                # 输出配置
                output_format=config_data["output"]["format"],
                output_indent=config_data["output"]["indent"],
                ensure_ascii=config_data["output"]["ensure_ascii"],
                output_default_path=config_data["output"].get("default_path", "data"),
                output_filename_template=config_data["output"].get("filename_template", "douyin_hotlist_{timestamp}"),
                
                # 日志配置
                log_level=config_data["logging"]["level"],
                console_log_level=config_data["logging"]["console_level"],
                file_log_level=config_data["logging"]["file_level"],
                log_file_path=config_data["logging"]["log_file"],
                log_max_file_size=config_data["logging"]["max_file_size"],
                log_backup_count=config_data["logging"]["backup_count"],
                log_format=config_data["logging"]["format"],
                log_date_format=config_data["logging"]["date_format"],
                
                # URL编码配置
                url_encoding_enabled=config_data.get("url_encoding", {}).get("enabled", True),
                url_encoding_method=config_data.get("url_encoding", {}).get("method", "url_encode"),
                url_encoding_encoding=config_data.get("url_encoding", {}).get("encoding", "utf-8"),
                url_encoding_safe_chars=config_data.get("url_encoding", {}).get("safe_chars", ""),
                
                # 高级配置项
                enable_proxy=self._env_config.get('ENABLE_PROXY', False),
                proxy_config=self._env_config.get('PROXY_CONFIG', {}),
                enable_rate_limit=self._env_config.get('ENABLE_RATE_LIMIT', True),
                rate_limit_requests=self._env_config.get('RATE_LIMIT_REQUESTS', 10),
                rate_limit_period=self._env_config.get('RATE_LIMIT_PERIOD', 60),
                enable_retry_backoff=self._env_config.get('ENABLE_RETRY_BACKOFF', True),
                max_concurrent_workers=self._env_config.get('MAX_CONCURRENT_WORKERS', 3),
            )
            
            # 验证配置有效性
            self._config.validate()
            
            return self._config
            
        except Exception as e:
            raise RuntimeError(f"配置加载失败: {e}")
    
    def _load_env_config(self) -> None:
        """
        加载环境配置
        
        从env_config.py文件中动态加载环境变量配置。
        环境配置会覆盖默认配置，提供更灵活的配置管理。
        
        @returns {None}
        
        @example
            # env_config.py 示例
            DOUYIN_COOKIE = "your_cookie_here"
            MAX_ITEMS = 20
            REQUEST_INTERVAL = 3
            ENABLE_PROXY = True
        """
        env_config_file = self.config_dir / "env_config.py"
        
        if env_config_file.exists():
            try:
                # 动态导入环境配置文件
                spec = importlib.util.spec_from_file_location("env_config", env_config_file)
                env_config = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(env_config)
                
                # 获取所有非私有配置项
                for attr_name in dir(env_config):
                    if not attr_name.startswith('_'):
                        attr_value = getattr(env_config, attr_name)
                        if not callable(attr_value):
                            self._env_config[attr_name] = attr_value
                            
            except Exception as e:
                print(f"警告：环境配置加载失败，使用默认配置: {e}")
        else:
            print("警告：未找到env_config.py文件，请复制并配置该文件")
    
    def reload_config(self) -> AppConfig:
        """
        重新加载配置
        
        清除当前配置缓存，重新从配置文件和环境变量加载配置。
        适用于配置更新后需要立即生效的场景。
        
        @returns {AppConfig} 重新加载后的配置对象
        
        @throws {FileNotFoundError} 当配置文件不存在时抛出
        @throws {RuntimeError} 当配置加载失败时抛出
        @throws {ValueError} 当配置验证失败时抛出
        
        @example
            config_manager = ConfigManager()
            
            # 修改配置文件后重新加载
            config = config_manager.reload_config()
            print("配置已重新加载")
        """
        self._config = None
        self._env_config = {}
        return self.load_config()
    
    def get_config(self) -> AppConfig:
        """
        获取当前配置
        
        获取当前配置对象，如果配置未加载则自动加载。
        这是获取配置的推荐方法。
        
        @returns {AppConfig} 当前配置对象
        
        @example
            config_manager = ConfigManager()
            config = config_manager.get_config()
            print(f"当前最大项目数: {config.max_items}")
        """
        if self._config is None:
            return self.load_config()
        return self._config
    
    def update_config(self, **kwargs) -> None:
        """
        动态更新配置项
        
        在运行时动态更新配置参数，支持部分配置更新。
        更新后会自动验证配置的有效性。
        
        @param {**kwargs} kwargs - 要更新的配置项，支持任意数量的配置参数
        @returns {None}
        
        @throws {ValueError} 当配置项不存在或验证失败时抛出
        
        @example
            config_manager = ConfigManager()
            
            # 更新单个配置项
            config_manager.update_config(max_items=15)
            
            # 更新多个配置项
            config_manager.update_config(
                max_items=20,
                request_interval=3,
                enable_cache=True
            )
        """
        if self._config is None:
            self.load_config()
            
        # 逐个更新配置项
        for key, value in kwargs.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)
            else:
                raise ValueError(f"未知的配置项: {key}")
        
        # 重新验证配置有效性
        self._config.validate()
