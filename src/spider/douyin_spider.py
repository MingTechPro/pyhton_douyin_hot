"""
抖音爬虫实现模块

@author: MingTechPro
@version: 1.0.0
@date: 2025-08-15
@description: 该模块实现了抖音热榜数据的爬取功能，继承自BaseSpider基类，
             提供了完整的抖音热榜数据获取、解析和处理功能。

主要功能:
- 抖音热榜数据爬取
- 数据解析和格式化
- 缓存机制支持
- 速率限制控制
- 错误处理和重试机制

依赖模块:
- base_spider: 基础爬虫类
- constants: 常量定义
- models: 数据模型
- config_manager: 配置管理
- performance: 性能监控工具
"""
import time
import json
import traceback
from typing import Optional, Dict, Any, List
from datetime import datetime

from .base_spider import BaseSpider
from ..core.constants import Constants
from ..core.models import HotListResponse, HotListItem, VideoArticle, CrawlResult
from ..core.exceptions import (
    NetworkException, RequestTimeoutException, ConnectionException, RateLimitException,
    DataException, DataParseException, EmptyDataException,
    BrowserException, BrowserInitException, PageLoadException,
    SecurityException, InvalidCookieException,
    handle_exceptions, ExceptionFactory
)
from ..config.config_manager import AppConfig
from ..utils.performance import CacheManager, RateLimiter
from ..utils.video_downloader import VideoDownloader


class DouyinSpider(BaseSpider):
    """
    抖音热榜爬虫实现类
    
    继承自BaseSpider基类，专门用于爬取抖音热榜数据。
    支持缓存机制、速率限制、错误重试等功能。
    
    @extends {BaseSpider} 基础爬虫类
    @implements {crawl} 爬取方法
    @implements {_fetch_hot_list_data} 获取热榜数据
    @implements {_process_hot_list_item} 处理热榜项目
    @implements {_process_video_detail} 提取视频文章信息
    
    @example
        config = AppConfig()
        logger = LogManager.get_logger()
        cache_manager = CacheManager()
        rate_limiter = RateLimiter()
        
        spider = DouyinSpider(
            config=config,
            logger=logger,
            cache_manager=cache_manager,
            rate_limiter=rate_limiter
        )
        
        result = spider.crawl()
        if result.success:
            print(f"爬取成功，获取到 {len(result.data.items)} 条数据")
    """
    
    def __init__(self, config: AppConfig, logger=None, cache_manager: Optional[CacheManager] = None, rate_limiter: Optional[RateLimiter] = None):
        """
        初始化抖音爬虫实例
        
        创建抖音爬虫对象，设置配置、日志器、缓存管理器和速率限制器。
        
        @param {AppConfig} config - 应用配置对象，包含爬虫运行所需的所有配置参数
        @param {object} logger - 日志器对象，用于记录爬虫运行日志
        @param {CacheManager} cache_manager - 缓存管理器，用于缓存爬取结果，避免重复请求
        @param {RateLimiter} rate_limiter - 速率限制器，用于控制请求频率，避免被反爬虫机制检测
        
        @example
            config = AppConfig()
            logger = LogManager.get_logger()
            cache_manager = CacheManager(max_size=100, ttl=3600)
            rate_limiter = RateLimiter(max_requests=10, time_window=60)
            
            spider = DouyinSpider(
                config=config,
                logger=logger,
                cache_manager=cache_manager,
                rate_limiter=rate_limiter
            )
        """
        super().__init__(config, logger)
        self.cache_manager = cache_manager
        self.rate_limiter = rate_limiter
        
        # 初始化视频下载器（如果启用）
        self.video_downloader = None
        if getattr(config, 'video_download_enabled', False):
            self.video_downloader = VideoDownloader(
                download_dir=getattr(config, 'video_download_dir', 'downloads'),
                max_file_size=getattr(config, 'video_download_max_file_size', 209715200),
                max_concurrent=getattr(config, 'video_download_max_concurrent', 3),
                timeout=getattr(config, 'video_download_timeout', 30),
                chunk_size=getattr(config, 'video_download_chunk_size', 8192),
                max_retries=getattr(config, 'video_download_max_retries', 3),
                retry_delay=getattr(config, 'video_download_retry_delay', 1.0),
                logger=logger
            )
            self.logger.info("📥 视频下载器已启用")
        
    def crawl(self) -> CrawlResult:
        """
        执行爬取操作
        
        主要的爬取方法，负责：
        - 检查缓存中是否有可用数据
        - 使用浏览器获取抖音热榜数据
        - 解析和格式化数据
        - 处理热榜项目
        - 返回爬取结果
        
        @returns {CrawlResult} 爬取结果对象，包含成功状态、数据、执行时间等信息
        
        @throws {Exception} 当爬取过程中出现错误时抛出
        
        @example
            result = spider.crawl()
            if result.success:
                print(f"爬取成功，处理了 {result.items_processed} 条数据")
            else:
                print(f"爬取失败: {result.error_message}")
        """
        start_time = time.time()
        items_processed = 0
        items_success = 0
        
        try:
            # 检查缓存中是否有可用数据
            if self.cache_manager and self.config.enable_cache:
                cache_key = f"hot_list_{datetime.now().strftime('%Y%m%d_%H')}_{self.config.max_items}"
                cached_data = self.cache_manager.get(cache_key)
                if cached_data:
                    self.logger.info(f"💾 使用缓存数据")
                    return CrawlResult(
                        success=True,
                        data=cached_data,
                        execution_time=time.time() - start_time,
                        items_processed=len(cached_data.items),
                        items_success=len(cached_data.items)
                    )
            
            # 使用浏览器获取数据
            with self.get_browser() as browser:
                # 获取热榜数据
                hot_list_json = self._fetch_hot_list_data(browser)
                if not hot_list_json:
                    return CrawlResult(
                        success=False,
                        error_message="获取热榜数据失败",
                        execution_time=time.time() - start_time
                    )
                
                # 提取热榜数据
                hot_list_data = hot_list_json.get(Constants.DATA_FIELD)
                if not hot_list_data:
                    return CrawlResult(
                        success=False,
                        error_message=f"热榜数据格式异常：缺少{Constants.DATA_FIELD}字段",
                        execution_time=time.time() - start_time
                    )
                
                # 创建响应对象
                hot_list_response = HotListResponse(
                    fetch_time=datetime.now()
                )
                
                # 处理热榜项目
                hot_items_list = hot_list_data.get(Constants.WORD_LIST_FIELD, [])
                if not hot_items_list:
                    return CrawlResult(
                        success=False,
                        error_message="热榜数据为空",
                        execution_time=time.time() - start_time
                    )
                
                # 根据配置决定是否跳过第一条（置顶）数据
                if self.config.skip_top_item and len(hot_items_list) > 1:
                    hot_items_list = hot_items_list[1:]
                    self.logger.info("⏭️  跳过置顶数据")
                
                # 处理每个热榜项目
                for i, hot_item_data in enumerate(hot_items_list):
                    # 检查是否达到最大项目数限制
                    if i >= self.config.max_items:
                        break
                    
                    items_processed += 1
                    
                    try:
                        # 处理单个热榜项目
                        hot_item = self._process_hot_list_item(hot_item_data, browser)
                        if hot_item:
                            hot_list_response.items.append(hot_item)
                            items_success += 1
                            self.logger.info(f"✅ [{i+1}] {hot_item.title}")
                        else:
                            self.logger.warning(f"❌ [{i+1}] 处理失败")
                    except Exception as e:
                        self.logger.error(f"❌ [{i+1}] 处理出错: {str(e)}")
                        continue
                    
                    # 请求间隔控制
                    if i < len(hot_items_list) - 1 and self.config.request_interval > 0:
                        time.sleep(self.config.request_interval)
                
                # 如果启用了视频下载功能，执行批量下载
                if self.video_downloader and hot_list_response.items:
                    self._download_videos_from_items(hot_list_response.items)
                
                # 缓存结果
                if self.cache_manager and self.config.enable_cache:
                    cache_key = f"hot_list_{datetime.now().strftime('%Y%m%d_%H')}_{self.config.max_items}"
                    self.cache_manager.set(cache_key, hot_list_response)
                    self.logger.info("💾 数据已缓存")
                
                return CrawlResult(
                    success=True,
                    data=hot_list_response,
                    execution_time=time.time() - start_time,
                    items_processed=items_processed,
                    items_success=items_success
                )
                
        except Exception as e:
            self.logger.error(f"❌ 爬取过程出错: {str(e)}")
            if self.config.debug:
                self.logger.error(f"🔍 错误详情: {traceback.format_exc()}")
            return CrawlResult(
                success=False,
                error_message=str(e),
                execution_time=time.time() - start_time,
                items_processed=items_processed,
                items_success=items_success
            )
    
    @handle_exceptions(default_return=None, log_exceptions=True, reraise=True)
    def _fetch_hot_list_data(self, browser) -> Optional[Dict[str, Any]]:
        """
        获取热榜数据
        Args:
            browser: 浏览器实例
        Returns:
            Dict[str, Any]: 热榜数据
        """
        @self.retry_on_failure(
            max_retries=self.config.hot_list_max_retries,
            delay=self.config.hot_list_delay
        )
        def _fetch():
            request_start = time.time()
            try:
                browser.listen.start(Constants.API_SEARCH_LIST)
                browser.get(self.config.hot_list_url)
                response = browser.listen.wait(timeout=self.config.hot_list_timeout)
                
                if response is None:
                    raise RequestTimeoutException(
                        "热榜请求超时",
                        context={
                            "url": self.config.hot_list_url,
                            "timeout": self.config.hot_list_timeout
                        }
                    )
                    
                data = response.response.body
                if data is None:
                    raise EmptyDataException(
                        "热榜响应体为空",
                        context={"url": self.config.hot_list_url}
                    )
                    
                request_duration = time.time() - request_start
                self.logger.info(f"✅ 热榜数据获取成功 ({request_duration:.2f}秒)")
                
                # 记录请求统计
                self.record_request(True, request_duration)
                
                return data
            except (RequestTimeoutException, EmptyDataException):
                # 重新抛出自定义异常
                request_duration = time.time() - request_start
                self.record_request(False, request_duration)
                raise
            except Exception as e:
                request_duration = time.time() - request_start
                self.logger.error(f"❌ 获取热榜数据失败 ({request_duration:.2f}秒): {str(e)}")
                self.record_request(False, request_duration)
                
                # 根据错误类型创建相应的异常
                if "timeout" in str(e).lower():
                    raise RequestTimeoutException(
                        f"网络请求超时: {str(e)}",
                        context={"url": self.config.hot_list_url, "original_error": str(e)}
                    )
                elif "connection" in str(e).lower():
                    raise ConnectionException(
                        f"连接失败: {str(e)}",
                        context={"url": self.config.hot_list_url, "original_error": str(e)}
                    )
                else:
                    raise NetworkException(
                        f"网络请求失败: {str(e)}",
                        context={"url": self.config.hot_list_url, "original_error": str(e)}
                    )
        
        return _fetch()
    
    def _fetch_video_detail(self, browser, url: str) -> Optional[Dict[str, Any]]:
        """
        获取视频详情数据
        Args:
            browser: 浏览器实例
            url: 视频URL
        Returns:
            Dict[str, Any]: 视频详情数据
        """
        @self.retry_on_failure(
            max_retries=self.config.video_detail_max_retries,
            delay=self.config.video_detail_delay
        )
        def _fetch():
            request_start = time.time()
            try:
                # 简化视频详情获取日志
                browser.listen.start(Constants.API_AWEME_DETAIL)
                browser.get(url)
                response = browser.listen.wait(timeout=self.config.video_detail_timeout)
                
                if response is None:
                    self.logger.warning("获取视频详情超时")
                    request_duration = time.time() - request_start
                    self.record_request(False, request_duration)
                    return None
                    
                data = response.response.body
                if data is None:
                    self.logger.warning("视频详情响应体为空")
                    request_duration = time.time() - request_start
                    self.record_request(False, request_duration)
                    return None
                    
                request_duration = time.time() - request_start
                # 记录成功请求
                self.record_request(True, request_duration)
                return data
            except Exception as e:
                request_duration = time.time() - request_start
                self.logger.error(f"❌ 获取视频详情失败: {str(e)}")
                self.record_request(False, request_duration)
                return None
        
        return _fetch()
    
    def _process_hot_list_item(self, item_data: Dict[str, Any], browser) -> Optional[HotListItem]:
        """
        处理热榜项目
        Args:
            item_data: 热榜项目数据
            browser: 浏览器实例
        Returns:
            HotListItem: 处理后的热榜项目
        """
        try:
            # 验证数据完整性
            if not self._validate_hot_list_item(item_data):
                self.logger.warning("热榜项目数据验证失败，跳过...")
                return None
            
            # 提取基本信息
            item_id = item_data.get(Constants.SENTENCE_ID_FIELD)
            item_title = self.clean_text(item_data.get(Constants.WORD_FIELD))
            item_position = int(item_data.get(Constants.POSITION_FIELD))
            item_popularity = int(item_data.get(Constants.HOT_VALUE_FIELD))
            item_views = int(item_data.get(Constants.VIEW_COUNT_FIELD))
            
            # 先构建热榜页面URL用于获取视频详情
            from ..utils.formatters import create_encrypted_url
            if self.config.url_encoding_enabled:
                hot_list_page_url = create_encrypted_url(
                    base_url=self.config.hot_list_url,
                    item_id=item_id,
                    title=item_title,
                    encryption_method=self.config.url_encoding_method
                )
            else:
                # 如果禁用URL编码，使用原始方式（不推荐）
                hot_list_page_url = f"{self.config.hot_list_url}/{item_id}/{item_title}"
            
            # 记录调试信息
            self.logger.debug(f"位置：{item_position}, 热度：{item_popularity}, 浏览量：{item_views}")
            
            # 获取视频详情以获得视频短链接
            video_detail_json = self._fetch_video_detail(browser, hot_list_page_url)
            
            # 获取视频短链接
            video_short_url = None
            if video_detail_json is not None:
                # 从视频详情中提取视频ID来构建短链接
                video_detail_data = video_detail_json.get(Constants.AWEME_DETAIL_FIELD)
                if video_detail_data:
                    video_id = str(video_detail_data.get(Constants.AWEME_ID_FIELD, "")).strip()
                    if video_id:
                        video_short_url = f"{self.config.video_url}/{video_id}"
            
            # 如果没有获取到视频短链接，使用热榜页面URL作为备选
            item_url = video_short_url if video_short_url else hot_list_page_url
            
            # 创建热榜项目
            hot_list_item = HotListItem(
                position=item_position,
                title=item_title,
                url=item_url,  # 现在这里存储的是视频短链接
                popularity=item_popularity,
                views=item_views,
                created_at=datetime.now()
            )
            
            # 重用已获取的视频详情数据
            if video_detail_json is not None:
                # 处理视频详情数据
                video_article = self._process_video_detail(video_detail_json)
                if video_article:
                    hot_list_item.articles.append(video_article)
            
            return hot_list_item
            
        except Exception as e:
            self.logger.error(f"处理热榜项目时发生异常：{str(e)}")
            return None
    
    def _process_video_detail(self, video_detail_json: Dict[str, Any]) -> Optional[VideoArticle]:
        """
        处理视频详情数据
        Args:
            video_detail_json: 视频详情JSON数据
        Returns:
            VideoArticle: 视频文章对象
        """
        try:
            # 处理返回数据格式问题
            if isinstance(video_detail_json, str):
                if not video_detail_json.strip():
                    return None
                try:
                    video_detail_json = json.loads(video_detail_json)
                except json.JSONDecodeError:
                    return None
            
            # 检查并提取视频详情数据
            video_detail_data = video_detail_json.get(Constants.AWEME_DETAIL_FIELD)
            if not video_detail_data:
                return None
            
            # 验证视频数据
            if not self._validate_video_data(video_detail_data):
                return None
            
            # 提取视频信息
            video_id = str(video_detail_data.get(Constants.AWEME_ID_FIELD)).strip()
            video_title = self.clean_text(video_detail_data.get(Constants.DESC_FIELD, ""))
            
            if not video_id:
                return None
            
            video_short_url = f"{self.config.video_url}/{video_id}"
            
            # 安全地获取视频URL
            raw_video_url = self.safe_get_nested_value(
                video_detail_data, 
                [Constants.VIDEO_FIELD, Constants.BIT_RATE_FIELD, 0, Constants.PLAY_ADDR_FIELD, Constants.URL_LIST_FIELD, 0],
                ""
            )
            
            # 清洗视频URL
            video_play_url = self.sanitize_url(raw_video_url) if raw_video_url else ""
            
            # 创建视频文章对象
            return VideoArticle(
                title=video_title,
                short_url=video_short_url,
                video_url=video_play_url,
                created_at=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"处理视频详情时发生异常：{str(e)}")
            return None
    
    def _validate_hot_list_item(self, item: Dict[str, Any]) -> bool:
        """
        验证热榜项目数据完整性
        Args:
            item: 热榜项目数据
        Returns:
            bool: 数据是否有效
        """
        required_fields = [
            Constants.SENTENCE_ID_FIELD,
            Constants.WORD_FIELD,
            Constants.POSITION_FIELD,
            Constants.HOT_VALUE_FIELD,
            Constants.VIEW_COUNT_FIELD
        ]
        
        for field in required_fields:
            if field not in item or item[field] is None:
                return False
        
        # 验证数据类型
        try:
            position = int(item[Constants.POSITION_FIELD])
            hot_value = int(item[Constants.HOT_VALUE_FIELD])
            view_count = int(item[Constants.VIEW_COUNT_FIELD])
            
            if position <= 0 or hot_value < 0 or view_count < 0:
                return False
                
        except (ValueError, TypeError):
            return False
        
        # 验证标题长度
        title = str(item[Constants.WORD_FIELD]).strip()
        if len(title) == 0 or len(title) > 200:
            return False
            
        return True
    
    def _validate_video_data(self, video_data: Dict[str, Any]) -> bool:
        """
        验证视频数据完整性
        Args:
            video_data: 视频数据
        Returns:
            bool: 数据是否有效
        """
        if not isinstance(video_data, dict):
            return False
            
        # 检查必要字段
        if Constants.AWEME_ID_FIELD not in video_data:
            return False
            
        aweme_id = video_data.get(Constants.AWEME_ID_FIELD)
        if not aweme_id or not str(aweme_id).strip():
            return False
            
        return True
    
    def _download_videos_from_items(self, hot_items: List[HotListItem]) -> None:
        """
        从热榜项目中下载视频
        
        @param {List[HotListItem]} hot_items - 热榜项目列表
        @returns {None}
        """
        if not self.video_downloader:
            return
        
        # 收集需要下载的视频信息
        video_download_list = []
        for item in hot_items:
            for article in item.articles:
                if article.video_url:
                    # 生成文件名（基于标题和位置）
                    safe_title = self._sanitize_video_filename(item.title)
                    filename = f"[{item.position}]_{safe_title}.mp4"
                    
                    video_download_list.append({
                        'url': article.video_url,
                        'filename': filename,
                        'referer': item.url  # 使用 list_url 作为 referer
                    })
        
        if not video_download_list:
            self.logger.warning("⚠️  没有找到可下载的视频URL")
            return
        
        self.logger.info(f"📥 开始下载 {len(video_download_list)} 个视频...")
        
        # 定义批量下载进度回调
        def batch_progress(completed: int, total: int):
            progress_percent = (completed / total) * 100
            self.logger.info(f"📊 视频下载进度: {completed}/{total} ({progress_percent:.1f}%)")
        
        # 执行批量下载
        try:
            download_results = self.video_downloader.download_videos(
                video_download_list,
                progress_callback=batch_progress
            )
            
            # 统计下载结果
            success_count = sum(1 for result in download_results if result.success and not getattr(result, 'skipped', False))
            skipped_count = sum(1 for result in download_results if result.success and getattr(result, 'skipped', False))
            failed_count = sum(1 for result in download_results if not result.success)
            total_count = len(download_results)
            
            # 构建简洁的结果消息
            result_parts = []
            if success_count > 0:
                result_parts.append(f"下载 {success_count}")
            if skipped_count > 0:
                result_parts.append(f"跳过 {skipped_count}")
            if failed_count > 0:
                result_parts.append(f"失败 {failed_count}")
            
            result_message = f"📊 视频处理完成: {', '.join(result_parts)} (共 {total_count} 个)"
            self.logger.info(result_message)
            
            # 只有在有实际下载时才显示详细统计
            if success_count > 0:
                # 计算实际下载的统计（排除跳过的文件）
                downloaded_results = [r for r in download_results if r.success and not getattr(r, 'skipped', False)]
                if downloaded_results:
                    total_size = sum(r.file_size for r in downloaded_results)
                    total_time = sum(r.download_time for r in downloaded_results)
                    avg_speed = total_size / total_time if total_time > 0 else 0
                    
                    self.logger.info(
                        f"📈 下载统计: {self._format_size(total_size)}, "
                        f"{total_time:.1f}秒, {self._format_speed(avg_speed)}"
                    )
            
            # 只显示失败的下载详情（如果有）
            failed_downloads = [result for result in download_results if not result.success]
            if failed_downloads:
                self.logger.warning(f"❌ {failed_count} 个视频下载失败")
                for i, result in enumerate(failed_downloads[:2]):  # 只显示前2个失败的
                    error_msg = result.error_message or "未知错误"
                    # 简化错误消息，只显示关键部分
                    if "403 Client Error: Forbidden" in error_msg:
                        error_msg = "403 访问被拒绝"
                    elif "Network" in error_msg:
                        error_msg = "网络连接错误"
                    self.logger.warning(f"  [{i+1}] {error_msg}")
                if len(failed_downloads) > 2:
                    self.logger.warning(f"  ... 还有 {len(failed_downloads) - 2} 个失败")
                    
        except Exception as e:
            self.logger.error(f"❌ 批量下载视频时发生异常: {str(e)}")
    
    def _sanitize_video_filename(self, title: str) -> str:
        """
        清理视频文件名
        
        @param {str} title - 原始标题
        @returns {str} 清理后的文件名
        """
        import re
        
        if not title:
            return "video"
        
        # 移除或替换不安全的字符
        title = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', title)
        
        # 限制长度
        if len(title) > 50:
            title = title[:50]
        
        # 移除首尾空白和点号
        title = title.strip('. ')
        
        return title or "video"
    
    def _format_size(self, size: int) -> str:
        """
        格式化文件大小显示
        
        @param {int} size - 字节数
        @returns {str} 格式化的大小字符串
        """
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f}{unit}"
            size /= 1024
        return f"{size:.1f}TB"
    
    def _format_speed(self, speed: float) -> str:
        """
        格式化下载速度显示
        
        @param {float} speed - 字节/秒
        @returns {str} 格式化的速度字符串
        """
        return f"{self._format_size(int(speed))}/s"
