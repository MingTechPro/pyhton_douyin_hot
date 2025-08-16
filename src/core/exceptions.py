"""
自定义异常类模块

@author: MingTechPro
@version: 1.0.0
@date: 2025-08-15
@description: 该模块定义了抖音爬虫系统的所有自定义异常类，
             提供更精确的错误分类和处理机制。

异常层次结构:
- DouyinSpiderException (基础异常)
  ├── ConfigurationException (配置相关异常)
  ├── NetworkException (网络相关异常)
  ├── DataException (数据相关异常)
  ├── SecurityException (安全相关异常)
  ├── BrowserException (浏览器相关异常)
  └── ValidationException (验证相关异常)

使用场景:
- 精确的错误分类和处理
- 异常恢复策略
- 错误日志和监控
- 用户友好的错误消息

@example
    try:
        spider.crawl()
    except NetworkException as e:
        logger.error(f"网络错误: {e}")
        # 网络重试逻辑
    except DataParseException as e:
        logger.error(f"数据解析错误: {e}")
        # 数据恢复逻辑
    except DouyinSpiderException as e:
        logger.error(f"爬虫错误: {e}")
        # 通用错误处理
"""

from typing import Optional, Dict, Any
from datetime import datetime


class DouyinSpiderException(Exception):
    """
    抖音爬虫基础异常类
    
    所有自定义异常的基类，提供统一的异常接口和属性。
    
    @author: MingTechPro
    @version: 1.0.0
    @date: 2025-08-15
    
    属性:
    - message: 错误消息
    - error_code: 错误代码
    - timestamp: 异常发生时间
    - context: 异常上下文信息
    - suggestion: 解决建议
    
    @example
        raise DouyinSpiderException(
            "爬虫执行失败",
            error_code="SPIDER_001",
            context={"url": "https://example.com"},
            suggestion="检查网络连接和配置"
        )
    """
    
    def __init__(
        self, 
        message: str, 
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        suggestion: Optional[str] = None
    ):
        """
        初始化异常
        
        @param {str} message - 错误消息
        @param {Optional[str]} error_code - 错误代码
        @param {Optional[Dict[str, Any]]} context - 异常上下文信息
        @param {Optional[str]} suggestion - 解决建议
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "UNKNOWN"
        self.timestamp = datetime.now()
        self.context = context or {}
        self.suggestion = suggestion
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典格式
        
        @returns {Dict[str, Any]} 异常信息字典
        """
        return {
            "exception_type": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code,
            "timestamp": self.timestamp.isoformat(),
            "context": self.context,
            "suggestion": self.suggestion
        }
    
    def __str__(self) -> str:
        """返回格式化的错误消息"""
        base_msg = f"[{self.error_code}] {self.message}"
        if self.suggestion:
            base_msg += f" | 建议: {self.suggestion}"
        return base_msg


class ConfigurationException(DouyinSpiderException):
    """
    配置相关异常
    
    当配置文件缺失、格式错误或配置参数无效时抛出。
    
    @example
        raise ConfigurationException(
            "配置文件不存在",
            error_code="CONFIG_001",
            context={"config_file": "config.json"},
            suggestion="检查配置文件路径是否正确"
        )
    """
    
    def __init__(self, message: str, **kwargs):
        kwargs.setdefault('error_code', 'CONFIG_001')
        super().__init__(message, **kwargs)


class NetworkException(DouyinSpiderException):
    """
    网络相关异常
    
    当网络请求失败、超时或连接错误时抛出。
    
    @example
        raise NetworkException(
            "请求超时",
            error_code="NETWORK_001",
            context={"url": "https://api.douyin.com", "timeout": 30},
            suggestion="检查网络连接或增加超时时间"
        )
    """
    
    def __init__(self, message: str, **kwargs):
        kwargs.setdefault('error_code', 'NETWORK_001')
        super().__init__(message, **kwargs)


class RequestTimeoutException(NetworkException):
    """请求超时异常"""
    
    def __init__(self, message: str = "请求超时", **kwargs):
        kwargs.setdefault('error_code', 'NETWORK_002')
        kwargs.setdefault('suggestion', '检查网络连接或增加超时时间')
        super().__init__(message, **kwargs)


class ConnectionException(NetworkException):
    """连接异常"""
    
    def __init__(self, message: str = "连接失败", **kwargs):
        kwargs.setdefault('error_code', 'NETWORK_003')
        kwargs.setdefault('suggestion', '检查网络连接和目标服务器状态')
        super().__init__(message, **kwargs)


class RateLimitException(NetworkException):
    """速率限制异常"""
    
    def __init__(self, message: str = "请求频率过高", **kwargs):
        kwargs.setdefault('error_code', 'NETWORK_004')
        kwargs.setdefault('suggestion', '降低请求频率或使用代理')
        super().__init__(message, **kwargs)


class DataException(DouyinSpiderException):
    """
    数据相关异常
    
    当数据解析失败、格式错误或数据无效时抛出。
    
    @example
        raise DataParseException(
            "JSON解析失败",
            error_code="DATA_001",
            context={"raw_data": "invalid json"},
            suggestion="检查API响应格式"
        )
    """
    
    def __init__(self, message: str, **kwargs):
        kwargs.setdefault('error_code', 'DATA_001')
        super().__init__(message, **kwargs)


class DataParseException(DataException):
    """数据解析异常"""
    
    def __init__(self, message: str = "数据解析失败", **kwargs):
        kwargs.setdefault('error_code', 'DATA_002')
        kwargs.setdefault('suggestion', '检查数据格式和解析逻辑')
        super().__init__(message, **kwargs)


class DataValidationException(DataException):
    """数据验证异常"""
    
    def __init__(self, message: str = "数据验证失败", **kwargs):
        kwargs.setdefault('error_code', 'DATA_003')
        kwargs.setdefault('suggestion', '检查数据完整性和有效性')
        super().__init__(message, **kwargs)


class EmptyDataException(DataException):
    """数据为空异常"""
    
    def __init__(self, message: str = "获取到的数据为空", **kwargs):
        kwargs.setdefault('error_code', 'DATA_004')
        kwargs.setdefault('suggestion', '检查API接口或调整查询参数')
        super().__init__(message, **kwargs)


class SecurityException(DouyinSpiderException):
    """
    安全相关异常
    
    当检测到安全威胁、Cookie无效或权限不足时抛出。
    
    @example
        raise SecurityException(
            "Cookie已过期",
            error_code="SECURITY_001",
            context={"cookie_age": "7 days"},
            suggestion="重新获取有效的Cookie"
        )
    """
    
    def __init__(self, message: str, **kwargs):
        kwargs.setdefault('error_code', 'SECURITY_001')
        super().__init__(message, **kwargs)


class InvalidCookieException(SecurityException):
    """无效Cookie异常"""
    
    def __init__(self, message: str = "Cookie无效或已过期", **kwargs):
        kwargs.setdefault('error_code', 'SECURITY_002')
        kwargs.setdefault('suggestion', '重新获取有效的Cookie')
        super().__init__(message, **kwargs)


class PermissionDeniedException(SecurityException):
    """权限拒绝异常"""
    
    def __init__(self, message: str = "访问权限不足", **kwargs):
        kwargs.setdefault('error_code', 'SECURITY_003')
        kwargs.setdefault('suggestion', '检查账号权限或使用管理员权限')
        super().__init__(message, **kwargs)


class SuspiciousActivityException(SecurityException):
    """可疑活动异常"""
    
    def __init__(self, message: str = "检测到可疑活动", **kwargs):
        kwargs.setdefault('error_code', 'SECURITY_004')
        kwargs.setdefault('suggestion', '暂停操作，检查安全设置')
        super().__init__(message, **kwargs)


class BrowserException(DouyinSpiderException):
    """
    浏览器相关异常
    
    当浏览器初始化失败、页面加载错误或元素定位失败时抛出。
    
    @example
        raise BrowserException(
            "浏览器启动失败",
            error_code="BROWSER_001",
            context={"browser_type": "Chrome"},
            suggestion="检查浏览器安装和配置"
        )
    """
    
    def __init__(self, message: str, **kwargs):
        kwargs.setdefault('error_code', 'BROWSER_001')
        super().__init__(message, **kwargs)


class BrowserInitException(BrowserException):
    """浏览器初始化异常"""
    
    def __init__(self, message: str = "浏览器初始化失败", **kwargs):
        kwargs.setdefault('error_code', 'BROWSER_002')
        kwargs.setdefault('suggestion', '检查浏览器安装和驱动程序')
        super().__init__(message, **kwargs)


class PageLoadException(BrowserException):
    """页面加载异常"""
    
    def __init__(self, message: str = "页面加载失败", **kwargs):
        kwargs.setdefault('error_code', 'BROWSER_003')
        kwargs.setdefault('suggestion', '检查网络连接和页面URL')
        super().__init__(message, **kwargs)


class ElementNotFoundException(BrowserException):
    """元素未找到异常"""
    
    def __init__(self, message: str = "页面元素未找到", **kwargs):
        kwargs.setdefault('error_code', 'BROWSER_004')
        kwargs.setdefault('suggestion', '检查页面结构变化或选择器')
        super().__init__(message, **kwargs)


class ValidationException(DouyinSpiderException):
    """
    验证相关异常
    
    当参数验证失败、格式错误或约束违反时抛出。
    
    @example
        raise ValidationException(
            "参数值超出范围",
            error_code="VALIDATION_001",
            context={"param": "max_items", "value": 1000, "max_allowed": 100},
            suggestion="调整参数值到允许范围内"
        )
    """
    
    def __init__(self, message: str, **kwargs):
        kwargs.setdefault('error_code', 'VALIDATION_001')
        super().__init__(message, **kwargs)


class ParameterValidationException(ValidationException):
    """参数验证异常"""
    
    def __init__(self, message: str = "参数验证失败", **kwargs):
        kwargs.setdefault('error_code', 'VALIDATION_002')
        kwargs.setdefault('suggestion', '检查参数值和类型')
        super().__init__(message, **kwargs)


class FormatValidationException(ValidationException):
    """格式验证异常"""
    
    def __init__(self, message: str = "格式验证失败", **kwargs):
        kwargs.setdefault('error_code', 'VALIDATION_003')
        kwargs.setdefault('suggestion', '检查数据格式是否符合要求')
        super().__init__(message, **kwargs)


class ConstraintViolationException(ValidationException):
    """约束违反异常"""
    
    def __init__(self, message: str = "约束条件违反", **kwargs):
        kwargs.setdefault('error_code', 'VALIDATION_004')
        kwargs.setdefault('suggestion', '检查业务规则和约束条件')
        super().__init__(message, **kwargs)


# 异常工厂类
class ExceptionFactory:
    """
    异常工厂类
    
    提供便捷的异常创建方法和异常处理策略。
    
    @example
        factory = ExceptionFactory()
        exception = factory.create_network_exception("超时", timeout=30)
        raise exception
    """
    
    @staticmethod
    def create_network_exception(
        message: str, 
        error_type: str = "general",
        **context
    ) -> NetworkException:
        """
        创建网络异常
        
        @param {str} message - 错误消息
        @param {str} error_type - 错误类型 (timeout, connection, rate_limit)
        @param {**context} context - 上下文信息
        @returns {NetworkException} 网络异常实例
        """
        if error_type == "timeout":
            return RequestTimeoutException(message, context=context)
        elif error_type == "connection":
            return ConnectionException(message, context=context)
        elif error_type == "rate_limit":
            return RateLimitException(message, context=context)
        else:
            return NetworkException(message, context=context)
    
    @staticmethod
    def create_data_exception(
        message: str,
        error_type: str = "general",
        **context
    ) -> DataException:
        """
        创建数据异常
        
        @param {str} message - 错误消息
        @param {str} error_type - 错误类型 (parse, validation, empty)
        @param {**context} context - 上下文信息
        @returns {DataException} 数据异常实例
        """
        if error_type == "parse":
            return DataParseException(message, context=context)
        elif error_type == "validation":
            return DataValidationException(message, context=context)
        elif error_type == "empty":
            return EmptyDataException(message, context=context)
        else:
            return DataException(message, context=context)
    
    @staticmethod
    def create_security_exception(
        message: str,
        error_type: str = "general",
        **context
    ) -> SecurityException:
        """
        创建安全异常
        
        @param {str} message - 错误消息
        @param {str} error_type - 错误类型 (cookie, permission, suspicious)
        @param {**context} context - 上下文信息
        @returns {SecurityException} 安全异常实例
        """
        if error_type == "cookie":
            return InvalidCookieException(message, context=context)
        elif error_type == "permission":
            return PermissionDeniedException(message, context=context)
        elif error_type == "suspicious":
            return SuspiciousActivityException(message, context=context)
        else:
            return SecurityException(message, context=context)


# 异常处理装饰器
def handle_exceptions(
    default_return=None,
    log_exceptions: bool = True,
    reraise: bool = True
):
    """
    异常处理装饰器
    
    为函数提供统一的异常处理机制。
    
    @param {Any} default_return - 异常时的默认返回值
    @param {bool} log_exceptions - 是否记录异常日志
    @param {bool} reraise - 是否重新抛出异常
    @returns {function} 装饰器函数
    
    @example
        @handle_exceptions(default_return=[], log_exceptions=True)
        def risky_function():
            # 可能抛出异常的代码
            pass
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except DouyinSpiderException as e:
                if log_exceptions:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"{func.__name__} 发生异常: {e}")
                    logger.debug(f"异常详情: {e.to_dict()}")
                
                if reraise:
                    raise
                else:
                    return default_return
            except Exception as e:
                if log_exceptions:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"{func.__name__} 发生未知异常: {e}")
                
                if reraise:
                    # 将未知异常包装为自定义异常
                    raise DouyinSpiderException(
                        f"未知错误: {str(e)}",
                        error_code="UNKNOWN_ERROR",
                        context={"original_exception": str(e)}
                    ) from e
                else:
                    return default_return
        
        return wrapper
    return decorator


# 异常恢复策略
class RecoveryStrategy:
    """
    异常恢复策略类
    
    提供不同类型异常的恢复策略和处理建议。
    """
    
    @staticmethod
    def get_recovery_strategy(exception: DouyinSpiderException) -> Dict[str, Any]:
        """
        获取异常恢复策略
        
        @param {DouyinSpiderException} exception - 异常实例
        @returns {Dict[str, Any]} 恢复策略信息
        """
        strategies = {
            NetworkException: {
                "retry": True,
                "max_retries": 3,
                "backoff_factor": 2.0,
                "recovery_actions": [
                    "检查网络连接",
                    "尝试使用代理",
                    "增加超时时间",
                    "降低请求频率"
                ]
            },
            DataException: {
                "retry": False,
                "fallback_data": None,
                "recovery_actions": [
                    "检查API响应格式",
                    "验证数据解析逻辑",
                    "使用备用数据源",
                    "忽略无效数据项"
                ]
            },
            SecurityException: {
                "retry": False,
                "require_manual_intervention": True,
                "recovery_actions": [
                    "更新Cookie",
                    "检查账号状态",
                    "联系管理员",
                    "暂停操作"
                ]
            },
            BrowserException: {
                "retry": True,
                "max_retries": 2,
                "recovery_actions": [
                    "重启浏览器",
                    "更新浏览器驱动",
                    "检查页面结构变化",
                    "使用备用选择器"
                ]
            }
        }
        
        exception_type = type(exception)
        
        # 查找最匹配的策略
        for exc_class, strategy in strategies.items():
            if issubclass(exception_type, exc_class):
                return strategy
        
        # 默认策略
        return {
            "retry": False,
            "recovery_actions": ["查看日志获取更多信息", "联系技术支持"]
        }
