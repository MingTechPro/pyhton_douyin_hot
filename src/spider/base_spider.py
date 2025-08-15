"""
基础爬虫类模块

@author: MingTechPro
@version: 2.1.0
@date: 2025-08-15
@description: 该模块定义了爬虫系统的基础类，提供通用的爬虫功能和浏览器管理。
             采用抽象基类设计，为具体的爬虫实现提供统一的接口和基础功能。

主要功能:
- 浏览器实例管理
- 请求头配置
- 重试机制
- 错误处理
- 性能统计
- 日志记录

设计模式:
- 模板方法模式: 定义爬虫执行流程
- 策略模式: 支持不同的重试策略
- 工厂模式: 浏览器实例创建

@example
    class MySpider(BaseSpider):
        def crawl(self):
            with self.get_browser() as browser:
                # 执行爬取逻辑
                pass
"""
import time
import logging
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime

from DrissionPage import ChromiumPage

from ..core.constants import Constants
from ..config.config_manager import AppConfig


@dataclass
class RequestResult:
    """
    请求结果数据类
    
    封装HTTP请求的执行结果，包含成功状态、数据、错误信息等。
    
    @author: MingTechPro
    @version: 2.1.0
    @date: 2025-08-15
    
    字段说明:
    - success: 请求是否成功
    - data: 响应数据
    - error_message: 错误信息
    - response_time: 响应时间
    - status_code: HTTP状态码
    
    @example
        result = RequestResult(
            success=True,
            data={"key": "value"},
            response_time=1.5,
            status_code=200
        )
    """
    success: bool                                    # 请求是否成功
    data: Optional[Dict[str, Any]] = None          # 响应数据
    error_message: Optional[str] = None             # 错误信息
    response_time: float = 0.0                      # 响应时间(秒)
    status_code: Optional[int] = None               # HTTP状态码


class BaseSpider(ABC):
    """
    基础爬虫抽象类
    
    提供爬虫系统的核心功能和通用方法，采用模板方法模式定义爬虫执行流程。
    具体的爬虫实现类需要继承此类并实现抽象方法。
    
    @author: MingTechPro
    @version: 2.1.0
    @date: 2025-08-15
    
    主要功能:
    - 浏览器实例管理
    - 请求头配置
    - 重试机制
    - 错误处理
    - 性能统计
    - 日志记录
    
    抽象方法:
    - crawl(): 执行爬取操作
    
    @example
        class DouyinSpider(BaseSpider):
            def crawl(self):
                with self.get_browser() as browser:
                    # 实现具体的爬取逻辑
                    pass
    """
    
    def __init__(self, config: AppConfig, logger: Optional[logging.Logger] = None):
        """
        初始化基础爬虫
        
        设置配置、日志器和性能统计计数器。
        
        @param {AppConfig} config - 应用配置对象
        @param {Optional[logging.Logger]} logger - 日志器对象，如果为None则使用默认日志器
        @returns {None}
        
        @example
            config = AppConfig()
            logger = logging.getLogger(__name__)
            spider = BaseSpider(config, logger)
        """
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        self._browser: Optional[ChromiumPage] = None
        self._request_count = 0      # 请求总数
        self._success_count = 0      # 成功请求数
        self._error_count = 0        # 失败请求数
        
    @contextmanager
    def get_browser(self):
        """
        获取浏览器实例的上下文管理器
        
        提供浏览器实例的自动创建和清理，确保资源正确释放。
        使用上下文管理器模式，支持with语句。
        
        @yields {ChromiumPage} 浏览器实例
        
        @throws {Exception} 当浏览器创建失败时抛出
        
        @example
            with self.get_browser() as browser:
                # 使用浏览器进行页面操作
                page = browser.get_page()
                # 浏览器会在退出with块时自动关闭
        """
        browser = None
        try:
            self.logger.info("正在初始化浏览器...")
            browser = ChromiumPage()
            self.logger.info("浏览器初始化成功")
            yield browser
        except Exception as e:
            self.logger.error(f"浏览器创建失败：{str(e)}")
            raise
        finally:
            if browser:
                try:
                    browser.quit()
                    self.logger.info("浏览器已正确关闭")
                except Exception as e:
                    self.logger.error(f"关闭浏览器时出现错误：{str(e)}")
    
    def get_request_headers(self, referer: Optional[str] = None) -> Dict[str, str]:
        """
        获取请求头配置
        
        根据配置生成标准的HTTP请求头，包含Cookie、User-Agent等必要信息。
        
        @param {Optional[str]} referer - 引用页面URL，用于设置Referer头
        @returns {Dict[str, str]} 请求头字典
        
        @example
            headers = self.get_request_headers("https://www.douyin.com")
            # 结果: {"cookie": "...", "User-Agent": "...", "referer": "..."}
        """
        headers = {
            "cookie": self.config.cookie,
            "User-Agent": self.config.user_agent,
        }
        
        if referer:
            headers["referer"] = referer
            
        return headers
    
    def retry_on_failure(self, max_retries: int = None, delay: int = None):
        """
        重试装饰器
        
        为方法提供自动重试功能，当方法执行失败时自动重试指定次数。
        支持指数退避策略。
        
        @param {int} max_retries - 最大重试次数，如果为None则使用配置中的值
        @param {int} delay - 重试间隔时间（秒），如果为None则使用配置中的值
        @returns {function} 装饰器函数
        
        @example
            @self.retry_on_failure(max_retries=3, delay=2)
            def fetch_data(self):
                # 这个方法会在失败时自动重试3次
                pass
        """
        if max_retries is None:
            max_retries = self.config.hot_list_max_retries
        if delay is None:
            delay = self.config.hot_list_delay
            
        def decorator(func):
            def wrapper(*args, **kwargs):
                last_exception = None
                for attempt in range(max_retries):
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        last_exception = e
                        if attempt < max_retries - 1:
                            self.logger.warning(f"{func.__name__} 第{attempt + 1}次尝试失败，{delay}秒后重试... 错误：{str(e)}")
                            time.sleep(delay)
                        else:
                            self.logger.error(f"{func.__name__} 经过{max_retries}次尝试后仍然失败")
                raise last_exception
            return wrapper
        return decorator
    
    def safe_get_nested_value(self, data: Dict[str, Any], keys: List[Any], default: Any = None) -> Any:
        """
        安全地获取嵌套字典的值
        
        从嵌套的字典结构中安全地获取值，避免KeyError异常。
        支持多层嵌套的字典和列表访问。
        
        @param {Dict[str, Any]} data - 源数据字典
        @param {List[Any]} keys - 键的路径列表，支持字符串和数字索引
        @param {Any} default - 默认值，当路径不存在时返回
        @returns {Any} 获取到的值或默认值
        
        @example
            data = {"a": {"b": {"c": 123}}}
            value = self.safe_get_nested_value(data, ["a", "b", "c"], 0)
            # 结果: 123
            
            value = self.safe_get_nested_value(data, ["a", "b", "d"], 0)
            # 结果: 0 (默认值)
        """
        try:
            result = data
            for key in keys:
                result = result[key]
            return result
        except (KeyError, IndexError, TypeError):
            return default
    
    def clean_text(self, text: str) -> str:
        """
        清洗文本数据
        
        对原始文本进行清洗处理，去除特殊字符、多余空白等。
        确保文本数据的质量和一致性。
        
        @param {str} text - 原始文本
        @returns {str} 清洗后的文本
        
        @example
            dirty_text = "  Hello\n\tWorld  \u200b"
            clean_text = self.clean_text(dirty_text)
            # 结果: "Hello World"
        """
        if not isinstance(text, str):
            text = str(text)
        
        # 去除首尾空白
        text = text.strip()
        
        # 替换特殊字符
        replacements = {
            '\n': ' ',      # 换行符
            '\r': ' ',      # 回车符
            '\t': ' ',      # 制表符
            '\u200b': '',   # 零宽度空格
            '\ufeff': '',   # BOM字符
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        # 压缩连续空格
        import re
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def sanitize_url(self, url: str) -> str:
        """
        清理和验证URL
        
        对URL进行清理和基本验证，确保URL的安全性和有效性。
        移除潜在的恶意字符和无效格式。
        
        @param {str} url - 原始URL
        @returns {str} 清理后的URL，如果无效则返回空字符串
        
        @example
            dirty_url = "https://example.com/path<script>alert('xss')</script>"
            clean_url = self.sanitize_url(dirty_url)
            # 结果: "https://example.com/path"
        """
        if not isinstance(url, str):
            url = str(url)
        
        url = url.strip()
        
        # 基本URL验证
        if not url.startswith(('http://', 'https://')):
            return ""
            
        # 移除潜在的恶意字符
        dangerous_chars = ['"', "'", '<', '>', '`', '\n', '\r', '\t']
        for char in dangerous_chars:
            url = url.replace(char, '')
        
        return url
    
    def record_request(self, success: bool = True) -> None:
        """
        记录请求统计信息
        
        更新请求计数器，用于性能监控和统计。
        
        @param {bool} success - 请求是否成功，默认为True
        @returns {None}
        
        @example
            try:
                # 执行请求
                response = self.make_request()
                self.record_request(success=True)
            except Exception:
                self.record_request(success=False)
        """
        self._request_count += 1
        if success:
            self._success_count += 1
        else:
            self._error_count += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取请求统计信息
        
        返回当前爬虫实例的请求统计信息，包括总数、成功数、失败数和成功率。
        
        @returns {Dict[str, Any]} 统计信息字典
        
        @example
            stats = self.get_stats()
            print(f"请求总数: {stats['request_count']}")
            print(f"成功率: {stats['success_rate']}%")
        """
        return {
            "request_count": self._request_count,
            "success_count": self._success_count,
            "error_count": self._error_count,
            "success_rate": round(self._success_count / self._request_count * 100, 2) if self._request_count > 0 else 0
        }
    
    @abstractmethod
    def crawl(self) -> Any:
        """
        执行爬取操作（抽象方法）
        
        子类必须实现此方法来定义具体的爬取逻辑。
        这是模板方法模式的核心方法。
        
        @returns {Any} 爬取结果，具体类型由子类定义
        
        @example
            class MySpider(BaseSpider):
                def crawl(self):
                    with self.get_browser() as browser:
                        # 实现具体的爬取逻辑
                        return result
        """
        pass
