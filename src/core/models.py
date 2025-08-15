"""
数据模型定义模块

@author: MingTechPro
@version: 1.0.0
@date: 2025-08-15
@description: 该模块定义了抖音爬虫系统中使用的所有数据模型，
             使用dataclass装饰器提供类型安全和自动生成的方法。

主要数据模型:
- VideoArticle: 视频文章信息
- HotListItem: 热榜项目信息
- HotListResponse: 热榜响应数据
- CrawlResult: 爬取结果
- PerformanceMetrics: 性能指标

特性:
- 类型注解支持
- 自动序列化方法
- 数据验证支持
- 灵活的字段配置

@example
    # 创建视频文章对象
    article = VideoArticle(
        title="热门视频标题",
        short_url="https://short.url/abc123",
        video_url="https://video.url/xyz789"
    )
    
    # 创建热榜项目
    hot_item = HotListItem(
        position=1,
        title="热门话题",
        url="https://douyin.com/hot/123",
        popularity=1000000,
        views=5000000
    )
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime


@dataclass
class VideoArticle:
    """
    视频文章信息数据类
    
    表示抖音平台上的单个视频文章信息，包含标题、链接等基本信息。
    
    @author: MingTechPro
    @version: 1.0.0
    @date: 2025-08-15
    
    字段说明:
    - title: 视频标题
    - short_url: 短链接URL
    - video_url: 视频播放URL
    - created_at: 创建时间
    
    @example
        article = VideoArticle(
            title="有趣的抖音视频",
            short_url="https://v.douyin.com/abc123",
            video_url="https://aweme.snssdk.com/video/xyz789",
            created_at=datetime.now()
        )
        
        # 转换为字典
        article_dict = article.to_dict()
    """
    title: str                    # 视频标题
    short_url: str                # 短链接URL
    video_url: str                # 视频播放URL
    created_at: Optional[datetime] = None  # 创建时间
    
    def to_dict(self) -> Dict[str, str]:
        """
        转换为字典格式
        
        将VideoArticle对象转换为字典格式，便于JSON序列化。
        
        @returns {Dict[str, str]} 包含所有字段的字典对象
        
        @example
            article = VideoArticle(title="测试", short_url="http://test.com")
            article_dict = article.to_dict()
            # 结果: {"article_title": "测试", "article_short_url": "http://test.com", ...}
        """
        return {
            "article_title": self.title,
            "article_short_url": self.short_url,
            "article_video_url": self.video_url,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


@dataclass
class HotListItem:
    """
    热榜项目数据类
    
    表示抖音热榜中的单个热门项目，包含排名、标题、热度等信息。
    
    @author: MingTechPro
    @version: 1.0.0
    @date: 2025-08-15
    
    字段说明:
    - position: 热榜排名位置
    - title: 热榜项目标题
    - url: 热榜项目链接
    - popularity: 热度值
    - views: 浏览量
    - articles: 关联的视频文章列表
    - created_at: 创建时间
    
    @example
        hot_item = HotListItem(
            position=1,
            title="热门话题#测试",
            url="https://douyin.com/hot/123",
            popularity=1000000,
            views=5000000,
            articles=[article1, article2]
        )
    """
    position: int                 # 热榜排名位置
    title: str                    # 热榜项目标题
    url: str                      # 热榜项目链接
    popularity: int               # 热度值
    views: int                    # 浏览量
    articles: List[VideoArticle] = field(default_factory=list)  # 关联的视频文章列表
    created_at: Optional[datetime] = None  # 创建时间
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典格式
        
        将HotListItem对象转换为字典格式，包含所有字段和关联的文章信息。
        
        @returns {Dict[str, Any]} 包含所有字段的字典对象
        
        @example
            hot_item = HotListItem(position=1, title="测试", url="http://test.com")
            hot_item_dict = hot_item.to_dict()
            # 结果: {"location": 1, "list_title": "测试", "list_url": "http://test.com", ...}
        """
        return {
            "location": self.position,
            "list_title": self.title,
            "list_url": self.url,
            "list_popularity": self.popularity,
            "list_views": self.views,
            "article": [article.to_dict() for article in self.articles],
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


@dataclass
class HotListResponse:
    """
    热榜响应数据类
    
    表示抖音热榜的完整响应数据，包含热榜项目列表和元数据信息。
    
    @author: MingTechPro
    @version: 1.0.0
    @date: 2025-08-15
    
    字段说明:
    - items: 热榜项目列表
    - total_count: 总项目数
    - fetch_time: 数据获取时间
    
    @example
        response = HotListResponse(
            items=[hot_item1, hot_item2],
            total_count=50,
            fetch_time=datetime.now()
        )
    """
    items: List[HotListItem] = field(default_factory=list)  # 热榜项目列表
    total_count: int = 0                                    # 总项目数
    fetch_time: Optional[datetime] = None                   # 数据获取时间
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典格式
        
        将HotListResponse对象转换为字典格式，包含所有热榜项目信息。
        
        @returns {Dict[str, Any]} 包含所有字段的字典对象
        
        @example
            response = HotListResponse(items=[], total_count=0)
            response_dict = response.to_dict()
            # 结果: {"list": [], "total_count": 0, "fetch_time": None}
        """
        return {
            "list": [item.to_dict() for item in self.items],
            "total_count": self.total_count,
            "fetch_time": self.fetch_time.isoformat() if self.fetch_time else None
        }


@dataclass
class CrawlResult:
    """
    爬取结果数据类
    
    表示爬虫执行的结果信息，包含成功状态、数据、错误信息等。
    
    @author: MingTechPro
    @version: 1.0.0
    @date: 2025-08-15
    
    字段说明:
    - success: 爬取是否成功
    - data: 爬取到的数据
    - error_message: 错误信息
    - execution_time: 执行时间
    - items_processed: 处理的项目数
    - items_success: 成功的项目数
    
    @example
        result = CrawlResult(
            success=True,
            data=hot_list_response,
            execution_time=10.5,
            items_processed=10,
            items_success=8
        )
    """
    success: bool                                    # 爬取是否成功
    data: Optional[HotListResponse] = None          # 爬取到的数据
    error_message: Optional[str] = None             # 错误信息
    execution_time: float = 0.0                     # 执行时间(秒)
    items_processed: int = 0                        # 处理的项目数
    items_success: int = 0                          # 成功的项目数
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典格式
        
        将CrawlResult对象转换为字典格式，包含执行结果和统计信息。
        
        @returns {Dict[str, Any]} 包含所有字段的字典对象
        
        @example
            result = CrawlResult(success=True, items_processed=10, items_success=8)
            result_dict = result.to_dict()
            # 结果: {"success": True, "success_rate": 80.0, ...}
        """
        return {
            "success": self.success,
            "data": self.data.to_dict() if self.data else None,
            "error_message": self.error_message,
            "execution_time": self.execution_time,
            "items_processed": self.items_processed,
            "items_success": self.items_success,
            "success_rate": round(self.items_success / self.items_processed * 100, 2) if self.items_processed > 0 else 0
        }


@dataclass
class PerformanceMetrics:
    """
    性能指标数据类
    
    表示爬虫执行的性能统计信息，用于监控和优化。
    
    @author: MingTechPro
    @version: 1.0.0
    @date: 2025-08-15
    
    字段说明:
    - total_time: 总执行时间
    - request_count: 请求总数
    - success_count: 成功请求数
    - error_count: 失败请求数
    - avg_request_time: 平均请求时间
    - memory_usage: 内存使用量
    - cpu_usage: CPU使用率
    
    @example
        metrics = PerformanceMetrics(
            total_time=15.5,
            request_count=20,
            success_count=18,
            error_count=2
        )
    """
    total_time: float = 0.0                         # 总执行时间(秒)
    request_count: int = 0                          # 请求总数
    success_count: int = 0                          # 成功请求数
    error_count: int = 0                            # 失败请求数
    avg_request_time: float = 0.0                   # 平均请求时间(秒)
    memory_usage: float = 0.0                       # 内存使用量(MB)
    cpu_usage: float = 0.0                          # CPU使用率(%)
    
    @property
    def success_rate(self) -> float:
        """
        计算成功率
        
        @returns {float} 成功率百分比
        """
        return round(self.success_count / self.request_count * 100, 2) if self.request_count > 0 else 0.0
    
    @property
    def requests_per_second(self) -> float:
        """
        计算每秒请求数
        
        @returns {float} 每秒请求数
        """
        return round(self.request_count / self.total_time, 2) if self.total_time > 0 else 0.0
