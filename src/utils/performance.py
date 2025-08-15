"""
性能监控工具模块

@author: MingTechPro
@version: 1.0.0
@date: 2025-08-15
@description: 该模块提供了完整的性能监控功能，包括系统资源监控、请求统计、
             缓存管理、速率限制等。帮助开发者分析和优化爬虫性能。

主要功能:
- 系统资源监控 (CPU、内存)
- 请求性能统计
- 智能缓存管理
- 速率限制控制
- 性能指标计算
- 实时监控报告

监控指标:
- 执行时间统计
- 请求成功率
- 平均响应时间
- 系统资源使用
- 缓存命中率
- 速率限制状态

@example
    # 创建性能监控器
    monitor = PerformanceMonitor()
    monitor.start()
    
    # 执行爬取操作
    spider.crawl()
    
    # 结束监控并获取统计
    monitor.end()
    stats = monitor.get_stats()
    print(f"执行时间: {stats['total_time']}秒")
"""
import time
import psutil
import threading
import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from contextlib import contextmanager


@dataclass
class PerformanceMetrics:
    """
    性能指标数据类
    
    存储和管理爬虫执行过程中的各种性能指标数据。
    
    @author: MingTechPro
    @version: 1.0.0
    @date: 2025-08-15
    
    字段说明:
    - total_time: 总执行时间
    - request_count: 请求总数
    - success_count: 成功请求数
    - error_count: 失败请求数
    - avg_request_time: 平均请求时间
    - requests_per_second: 每秒请求数
    - memory_usage: 内存使用量
    - cpu_usage: CPU使用率
    - request_times: 请求时间历史
    - memory_history: 内存使用历史
    - cpu_history: CPU使用历史
    
    @example
        metrics = PerformanceMetrics()
        metrics.request_count = 100
        metrics.success_count = 95
        metrics.calculate_metrics()
        print(f"成功率: {metrics.success_rate}%")
    """
    total_time: float = 0.0                    # 总执行时间(秒)
    request_count: int = 0                     # 请求总数
    success_count: int = 0                     # 成功请求数
    error_count: int = 0                       # 失败请求数
    avg_request_time: float = 0.0              # 平均请求时间(秒)
    requests_per_second: float = 0.0           # 每秒请求数
    memory_usage: float = 0.0                  # 内存使用量(MB)
    cpu_usage: float = 0.0                     # CPU使用率(%)
    request_times: List[float] = field(default_factory=list)      # 请求时间历史
    memory_history: List[float] = field(default_factory=list)     # 内存使用历史
    cpu_history: List[float] = field(default_factory=list)        # CPU使用历史
    
    def calculate_metrics(self) -> None:
        """
        计算性能指标
        
        根据收集的原始数据计算各种性能指标，包括成功率、QPS等。
        
        @returns {None}
        
        @example
            metrics = PerformanceMetrics()
            metrics.request_count = 100
            metrics.success_count = 95
            metrics.total_time = 10.0
            metrics.calculate_metrics()
            # 现在可以访问 metrics.success_rate 和 metrics.requests_per_second
        """
        # 计算成功率
        if self.request_count > 0:
            self.success_rate = round(self.success_count / self.request_count * 100, 2)
        else:
            self.success_rate = 0.0
            
        # 计算每秒请求数
        if self.total_time > 0:
            self.requests_per_second = round(self.request_count / self.total_time, 2)
        else:
            self.requests_per_second = 0.0
            
        # 计算平均请求时间
        if self.request_times:
            self.avg_request_time = sum(self.request_times) / len(self.request_times)
        else:
            self.avg_request_time = 0.0


class PerformanceMonitor:
    """
    性能监控类
    
    提供完整的性能监控功能，包括系统资源监控、请求统计等。
    支持实时监控和多线程安全。
    
    @author: MingTechPro
    @version: 1.0.0
    @date: 2025-08-15
    
    主要功能:
    - 系统资源实时监控
    - 请求性能统计
    - 性能指标计算
    - 监控报告生成
    
    @example
        monitor = PerformanceMonitor()
        monitor.start()
        
        # 执行爬取操作
        spider.crawl()
        
        # 结束监控
        monitor.end()
        stats = monitor.get_stats()
    """
    
    def __init__(self):
        """
        初始化性能监控器
        
        设置监控状态和性能指标收集器。
        """
        self.start_time: Optional[float] = None      # 开始时间
        self.end_time: Optional[float] = None        # 结束时间
        self.metrics = PerformanceMetrics()          # 性能指标
        self._monitoring = False                     # 监控状态
        self._monitor_thread: Optional[threading.Thread] = None  # 监控线程
        
    def start(self) -> None:
        """
        开始性能监控
        
        启动性能监控，开始收集系统资源和请求性能数据。
        
        @returns {None}
        
        @example
            monitor = PerformanceMonitor()
            monitor.start()
            # 现在开始监控系统资源和请求性能
        """
        self.start_time = time.time()
        self.metrics = PerformanceMetrics()
        self._monitoring = True
        
        # 启动系统资源监控线程
        self._start_system_monitoring()
        
    def end(self) -> None:
        """
        结束性能监控
        
        停止性能监控，计算最终的性能指标。
        
        @returns {None}
        
        @example
            monitor.end()
            # 监控结束，可以获取统计信息
            stats = monitor.get_stats()
        """
        self.end_time = time.time()
        self._monitoring = False
        
        # 计算总执行时间
        if self.start_time:
            self.metrics.total_time = self.end_time - self.start_time
            
        # 停止系统资源监控
        self._stop_system_monitoring()
        
        # 计算最终指标
        self.metrics.calculate_metrics()
        
    def record_request(self, duration: float, success: bool = True) -> None:
        """
        记录请求性能数据
        
        记录单个请求的执行时间和成功状态。
        
        @param {float} duration - 请求执行时间(秒)
        @param {bool} success - 请求是否成功，默认为True
        @returns {None}
        
        @example
            start_time = time.time()
            try:
                response = make_request()
                duration = time.time() - start_time
                monitor.record_request(duration, success=True)
            except Exception:
                duration = time.time() - start_time
                monitor.record_request(duration, success=False)
        """
        self.metrics.request_count += 1
        self.metrics.request_times.append(duration)
        
        if success:
            self.metrics.success_count += 1
        else:
            self.metrics.error_count += 1
            
    def get_stats(self) -> Dict[str, Any]:
        """
        获取性能统计信息
        
        返回完整的性能统计报告，包含所有监控指标。
        
        @returns {Dict[str, Any]} 性能统计字典
        
        @example
            stats = monitor.get_stats()
            print(f"总执行时间: {stats['total_time']}秒")
            print(f"成功率: {stats['success_rate']}%")
            print(f"平均请求时间: {stats['avg_request_time']}秒")
        """
        self.metrics.calculate_metrics()
        
        return {
            "total_time": round(self.metrics.total_time, 2),
            "request_count": self.metrics.request_count,
            "success_count": self.metrics.success_count,
            "error_count": self.metrics.error_count,
            "success_rate": self.metrics.success_rate,
            "avg_request_time": round(self.metrics.avg_request_time, 2),
            "requests_per_second": self.metrics.requests_per_second,
            "memory_usage": round(self.metrics.memory_usage, 2),
            "cpu_usage": round(self.metrics.cpu_usage, 2),
            "max_memory": round(max(self.metrics.memory_history) if self.metrics.memory_history else 0, 2),
            "max_cpu": round(max(self.metrics.cpu_history) if self.metrics.cpu_history else 0, 2),
            "min_request_time": round(min(self.metrics.request_times) if self.metrics.request_times else 0, 2),
            "max_request_time": round(max(self.metrics.request_times) if self.metrics.request_times else 0, 2)
        }
    
    def _start_system_monitoring(self) -> None:
        """启动系统资源监控"""
        def monitor_system():
            process = psutil.Process()
            # 初始化CPU监控，第一次调用总是返回0
            process.cpu_percent()
            
            while self._monitoring:
                try:
                    # 监控内存使用
                    memory_info = process.memory_info()
                    memory_mb = memory_info.rss / 1024 / 1024
                    self.metrics.memory_usage = memory_mb
                    self.metrics.memory_history.append(memory_mb)
                    
                    # 监控CPU使用（需要间隔来计算）
                    time.sleep(0.1)  # 短暂间隔以确保CPU计算准确
                    cpu_percent = process.cpu_percent()
                    self.metrics.cpu_usage = cpu_percent
                    self.metrics.cpu_history.append(cpu_percent)
                    
                    time.sleep(0.9)  # 剩余时间，总共1秒
                except Exception:
                    break
        
        self._monitor_thread = threading.Thread(target=monitor_system, daemon=True)
        self._monitor_thread.start()
    
    def _stop_system_monitoring(self) -> None:
        """停止系统资源监控"""
        self._monitoring = False
        if self._monitor_thread and self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=2)


@contextmanager
def performance_monitor():
    """
    性能监控上下文管理器
    Yields:
        PerformanceMonitor: 性能监控器
    """
    monitor = PerformanceMonitor()
    monitor.start()
    try:
        yield monitor
    finally:
        monitor.end()


class CacheManager:
    """
    缓存管理器
    
    提供内存缓存和文件持久化缓存功能，支持TTL过期机制。
    
    @author: MingTechPro
    @version: 1.0.0
    @date: 2025-08-15
    
    主要功能:
    - 内存缓存管理
    - 文件持久化缓存
    - TTL过期机制
    - 缓存大小限制
    - 线程安全操作
    
    @example
        cache = CacheManager(max_size=100, ttl=3600, enable_persistence=True)
        cache.set("key", "value")
        value = cache.get("key")
    """
    
    def __init__(self, max_size: int = 100, ttl: int = 300, enable_persistence: bool = True, cache_dir: str = "cache"):
        """
        初始化缓存管理器
        Args:
            max_size: 最大缓存条目数
            ttl: 缓存生存时间（秒）
            enable_persistence: 是否启用文件持久化
            cache_dir: 缓存文件目录
        """
        self.max_size = max_size
        self.ttl = ttl
        self.enable_persistence = enable_persistence
        self.cache_dir = Path(cache_dir)
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
        
        # 创建缓存目录
        if self.enable_persistence:
            self.cache_dir.mkdir(exist_ok=True)
            self._load_from_file()
        
    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存值
        Args:
            key: 缓存键
        Returns:
            缓存值或None
        """
        with self._lock:
            if key in self._cache:
                item = self._cache[key]
                if time.time() - item['timestamp'] < self.ttl:
                    return item['value']
                else:
                    # 过期，删除
                    del self._cache[key]
            return None
    
    def set(self, key: str, value: Any) -> None:
        """
        设置缓存值
        Args:
            key: 缓存键
            value: 缓存值
        """
        with self._lock:
            # 如果缓存已满，删除最旧的条目
            if len(self._cache) >= self.max_size:
                oldest_key = min(self._cache.keys(), 
                               key=lambda k: self._cache[k]['timestamp'])
                del self._cache[oldest_key]
            
            self._cache[key] = {
                'value': value,
                'timestamp': time.time()
            }
            
            # 保存到文件
            if self.enable_persistence:
                self._save_to_file()
    
    def clear(self) -> None:
        """清空缓存"""
        with self._lock:
            self._cache.clear()
            if self.enable_persistence:
                self._save_to_file()
    
    def size(self) -> int:
        """获取缓存大小"""
        with self._lock:
            return len(self._cache)
    
    def cleanup_expired(self) -> int:
        """
        清理过期条目
        Returns:
            清理的条目数
        """
        current_time = time.time()
        expired_keys = []
        
        with self._lock:
            for key, item in self._cache.items():
                if current_time - item['timestamp'] >= self.ttl:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self._cache[key]
            
            # 保存到文件
            if self.enable_persistence and expired_keys:
                self._save_to_file()
        
        return len(expired_keys)
    
    def _save_to_file(self) -> None:
        """保存缓存到文件"""
        try:
            cache_file = self.cache_dir / "cache.json"
            
            # 准备序列化数据
            serializable_cache = {}
            for key, item in self._cache.items():
                # 尝试序列化值
                try:
                    # 如果是自定义对象，尝试转换为字典
                    if hasattr(item['value'], 'to_dict'):
                        serializable_value = item['value'].to_dict()
                    elif hasattr(item['value'], '__dict__'):
                        serializable_value = item['value'].__dict__
                    else:
                        serializable_value = item['value']
                    
                    serializable_cache[key] = {
                        'value': serializable_value,
                        'timestamp': item['timestamp']
                    }
                except Exception:
                    # 如果无法序列化，跳过该项
                    continue
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(serializable_cache, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            # 静默处理文件保存错误
            pass
    
    def _load_from_file(self) -> None:
        """从文件加载缓存"""
        try:
            cache_file = self.cache_dir / "cache.json"
            if not cache_file.exists():
                return
            
            with open(cache_file, 'r', encoding='utf-8') as f:
                file_cache = json.load(f)
            
            current_time = time.time()
            for key, item in file_cache.items():
                # 检查是否过期
                if current_time - item['timestamp'] < self.ttl:
                    # 尝试恢复对象
                    try:
                        restored_value = self._restore_object(item['value'])
                        if restored_value is not None:
                            self._cache[key] = {
                                'value': restored_value,
                                'timestamp': item['timestamp']
                            }
                    except Exception:
                        # 如果恢复失败，跳过该项
                        continue
                    
        except Exception as e:
            # 静默处理文件加载错误
            pass
    
    def _restore_object(self, data: Dict[str, Any]):
        """从字典恢复对象"""
        try:
            # 检查是否是HotListResponse数据
            if 'list' in data and 'total_count' in data and 'fetch_time' in data:
                from ..core.models import HotListResponse, HotListItem, VideoArticle
                from datetime import datetime
                
                # 恢复VideoArticle对象
                def restore_article(article_data):
                    return VideoArticle(
                        title=article_data.get('article_title', ''),
                        short_url=article_data.get('article_short_url', ''),
                        video_url=article_data.get('article_video_url', ''),
                        created_at=datetime.fromisoformat(article_data['created_at']) if article_data.get('created_at') else None
                    )
                
                # 恢复HotListItem对象
                def restore_hot_item(item_data):
                    articles = [restore_article(article) for article in item_data.get('article', [])]
                    return HotListItem(
                        position=item_data.get('location', 0),
                        title=item_data.get('list_title', ''),
                        url=item_data.get('list_url', ''),
                        popularity=item_data.get('list_popularity', 0),
                        views=item_data.get('list_views', 0),
                        articles=articles,
                        created_at=datetime.fromisoformat(item_data['created_at']) if item_data.get('created_at') else None
                    )
                
                # 恢复HotListResponse对象
                items = [restore_hot_item(item_data) for item_data in data.get('list', [])]
                fetch_time = datetime.fromisoformat(data['fetch_time']) if data.get('fetch_time') else None
                
                return HotListResponse(
                    items=items,
                    total_count=data.get('total_count', 0),
                    fetch_time=fetch_time
                )
            
            return data
        except Exception:
            return data


class RateLimiter:
    """速率限制器"""
    
    def __init__(self, max_requests: int, time_window: int):
        """
        初始化速率限制器
        Args:
            max_requests: 最大请求数
            time_window: 时间窗口（秒）
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests: List[float] = []
        self._lock = threading.Lock()
    
    def can_proceed(self) -> bool:
        """
        检查是否可以继续请求
        Returns:
            bool: 是否可以继续
        """
        current_time = time.time()
        
        with self._lock:
            # 清理过期的请求记录
            self.requests = [req_time for req_time in self.requests 
                           if current_time - req_time < self.time_window]
            
            # 检查是否超过限制
            if len(self.requests) < self.max_requests:
                self.requests.append(current_time)
                return True
            else:
                return False
    
    def wait_if_needed(self) -> float:
        """
        如果需要则等待
        Returns:
            float: 等待的时间
        """
        if not self.can_proceed():
            # 计算需要等待的时间
            current_time = time.time()
            oldest_request = min(self.requests)
            wait_time = self.time_window - (current_time - oldest_request)
            
            if wait_time > 0:
                time.sleep(wait_time)
                return wait_time
        
        return 0.0
    
    def get_remaining_requests(self) -> int:
        """
        获取剩余请求数
        Returns:
            int: 剩余请求数
        """
        current_time = time.time()
        
        with self._lock:
            # 清理过期的请求记录
            self.requests = [req_time for req_time in self.requests 
                           if current_time - req_time < self.time_window]
            
            return max(0, self.max_requests - len(self.requests))
