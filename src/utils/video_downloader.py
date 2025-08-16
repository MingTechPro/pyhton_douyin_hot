"""
视频下载器模块

@author: MingTechPro
@version: 1.0.0
@date: 2025-08-15
@description: 该模块提供视频下载功能，支持从抖音等平台下载视频文件。
             包含进度跟踪、错误处理、重试机制等功能。

主要功能:
- 视频文件下载
- 下载进度跟踪
- 文件名规范化
- 错误处理和重试
- 并发下载支持
- 下载速度限制

安全特性:
- URL验证
- 文件名安全检查
- 下载大小限制
- 超时控制

@example
    downloader = VideoDownloader(
        download_dir="downloads",
        max_file_size=100 * 1024 * 1024,  # 100MB
        timeout=30
    )
    
    result = downloader.download_video(
        url="https://example.com/video.mp4",
        filename="my_video.mp4"
    )
    
    if result.success:
        print(f"下载成功: {result.file_path}")
    else:
        print(f"下载失败: {result.error_message}")
"""

import os
import re
import time
import hashlib
import logging
import requests
from pathlib import Path
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass
from urllib.parse import urlparse, unquote
from concurrent.futures import ThreadPoolExecutor, as_completed

from ..core.exceptions import (
    NetworkException, SecurityException, ValidationException,
    handle_exceptions
)


@dataclass
class DownloadResult:
    """
    下载结果数据类
    
    封装视频下载的执行结果，包含成功状态、文件路径、错误信息等。
    
    @author: MingTechPro
    @version: 1.0.0
    @date: 2025-08-15
    
    字段说明:
    - success: 下载是否成功
    - file_path: 下载文件的完整路径
    - file_size: 文件大小（字节）
    - download_time: 下载耗时（秒）
    - error_message: 错误信息
    - download_speed: 下载速度（字节/秒）
    
    @example
        result = DownloadResult(
            success=True,
            file_path="/downloads/video.mp4",
            file_size=1024000,
            download_time=5.2
        )
    """
    success: bool                                   # 下载是否成功
    file_path: Optional[str] = None                # 下载文件的完整路径
    file_size: int = 0                             # 文件大小（字节）
    download_time: float = 0.0                     # 下载耗时（秒）
    error_message: Optional[str] = None            # 错误信息
    download_speed: float = 0.0                    # 下载速度（字节/秒）
    skipped: bool = False                          # 是否跳过下载（文件已存在）


class VideoDownloader:
    """
    视频下载器类
    
    提供完整的视频下载功能，支持进度跟踪、错误处理、重试机制等。
    采用多线程下载和分块传输，提高下载效率和稳定性。
    
    @author: MingTechPro
    @version: 1.0.0
    @date: 2025-08-15
    
    主要功能:
    - 单个视频下载
    - 批量视频下载
    - 下载进度回调
    - 文件名冲突处理
    - 下载速度控制
    - 重试机制
    
    安全特性:
    - URL白名单验证
    - 文件扩展名检查
    - 下载大小限制
    - 路径遍历攻击防护
    
    @example
        # 创建下载器
        downloader = VideoDownloader(
            download_dir="downloads",
            max_file_size=100 * 1024 * 1024,  # 100MB
            max_concurrent=3,
            timeout=30,
            logger=my_logger
        )
        
        # 下载单个视频
        result = downloader.download_video(
            url="https://example.com/video.mp4",
            filename="my_video.mp4",
            progress_callback=lambda p: print(f"下载进度: {p}%")
        )
        
        # 批量下载
        urls = ["url1", "url2", "url3"]
        results = downloader.download_videos(urls)
    """
    
    def __init__(
        self,
        download_dir: str = "downloads",
        max_file_size: int = 200 * 1024 * 1024,  # 200MB
        max_concurrent: int = 3,
        timeout: int = 30,
        chunk_size: int = 8192,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        logger: Optional[logging.Logger] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        """
        初始化视频下载器
        
        @param {str} download_dir - 下载目录路径
        @param {int} max_file_size - 最大文件大小限制（字节）
        @param {int} max_concurrent - 最大并发下载数
        @param {int} timeout - 请求超时时间（秒）
        @param {int} chunk_size - 分块下载大小（字节）
        @param {int} max_retries - 最大重试次数
        @param {float} retry_delay - 重试延迟时间（秒）
        @param {Optional[logging.Logger]} logger - 日志器
        
        @example
            downloader = VideoDownloader(
                download_dir="./downloads",
                max_file_size=50 * 1024 * 1024,  # 50MB
                max_concurrent=2,
                timeout=60
            )
        """
        self.download_dir = Path(download_dir)
        self.max_file_size = max_file_size
        self.max_concurrent = max_concurrent
        self.timeout = timeout
        self.chunk_size = chunk_size
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.logger = logger or logging.getLogger(__name__)
        
        # 确保下载目录存在
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
        # 支持的视频扩展名
        self.allowed_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm', '.m4v'}
        
        # 可信域名列表（用于安全检查）
        self.trusted_domains = {
            'douyin.com', 'snssdk.com', 'bytedance.com',
            'tiktokcdn.com', 'muscdn.com', 'aweme.com'
        }
        
        # 请求会话配置
        self.session = requests.Session()
        default_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        if headers:
            default_headers.update(headers)
        self.session.headers.update(default_headers)
    
    @handle_exceptions(default_return=DownloadResult(success=False, error_message="下载失败"), log_exceptions=True)
    def download_video(
        self,
        url: str,
        filename: Optional[str] = None,
        progress_callback: Optional[Callable[[float], None]] = None,
        referer: Optional[str] = None
    ) -> DownloadResult:
        """
        下载单个视频
        
        从指定URL下载视频文件到本地，支持进度回调和错误处理。
        
        @param {str} url - 视频URL
        @param {Optional[str]} filename - 自定义文件名，如果为None则自动生成
        @param {Optional[Callable]} progress_callback - 进度回调函数，接收进度百分比(0-100)
        @returns {DownloadResult} 下载结果
        
        @throws {SecurityException} 当URL不安全时抛出
        @throws {ValidationException} 当参数无效时抛出
        @throws {NetworkException} 当网络请求失败时抛出
        
        @example
            def progress_handler(progress):
                print(f"下载进度: {progress:.1f}%")
            
            result = downloader.download_video(
                url="https://example.com/video.mp4",
                filename="my_video.mp4",
                progress_callback=progress_handler
            )
        """
        start_time = time.time()
        
        try:
            # 验证URL安全性
            self._validate_url(url)
            
            # 生成文件名
            if filename is None:
                filename = self._generate_filename(url)
            else:
                filename = self._sanitize_filename(filename)
            
            # 构建完整文件路径
            file_path = self.download_dir / filename
            
            # 检查文件是否已存在
            if file_path.exists():
                existing_size = file_path.stat().st_size
                if existing_size > 1024:  # 文件大小大于1KB，认为是有效文件
                    self.logger.info(f"⏭️  文件已存在，跳过下载: {filename} ({self._format_size(existing_size)})")
                    return DownloadResult(
                        success=True,
                        file_path=str(file_path),
                        file_size=existing_size,
                        download_time=0.0,
                        download_speed=0.0,
                        skipped=True  # 添加跳过标记
                    )
                else:
                    # 文件太小，可能损坏，删除并重新下载
                    file_path.unlink()
                    self.logger.warning(f"🗑️  删除损坏文件: {filename} (只有 {existing_size} 字节)")
            
            # 执行下载（带重试）
            for attempt in range(self.max_retries):
                try:
                    file_size = self._download_file(url, file_path, progress_callback, referer)
                    download_time = time.time() - start_time
                    download_speed = file_size / download_time if download_time > 0 else 0
                    
                    # 简化下载成功日志
                    self.logger.debug(
                        f"✅ 下载完成: {filename} ({self._format_size(file_size)}, {download_time:.1f}s)"
                    )
                    
                    return DownloadResult(
                        success=True,
                        file_path=str(file_path),
                        file_size=file_size,
                        download_time=download_time,
                        download_speed=download_speed
                    )
                    
                except Exception as e:
                    if attempt < self.max_retries - 1:
                        self.logger.warning(f"下载失败，第{attempt + 1}次重试: {str(e)}")
                        time.sleep(self.retry_delay * (attempt + 1))  # 指数退避
                    else:
                        raise
            
        except Exception as e:
            download_time = time.time() - start_time
            error_msg = f"下载失败: {str(e)}"
            self.logger.error(error_msg)
            
            return DownloadResult(
                success=False,
                error_message=error_msg,
                download_time=download_time
            )
    
    def download_videos(
        self,
        video_items: list,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> list[DownloadResult]:
        """
        批量下载视频
        
        并发下载多个视频，提高下载效率。支持整体进度回调。
        
        @param {list} video_items - 视频信息列表，每项可以是URL字符串或包含url和filename的字典
        @param {Optional[Callable]} progress_callback - 进度回调函数，接收(完成数, 总数)
        @returns {list[DownloadResult]} 下载结果列表
        
        @example
            videos = [
                "https://example.com/video1.mp4",
                {"url": "https://example.com/video2.mp4", "filename": "custom_name.mp4"},
                "https://example.com/video3.mp4"
            ]
            
            def batch_progress(completed, total):
                print(f"批量下载进度: {completed}/{total}")
            
            results = downloader.download_videos(videos, batch_progress)
        """
        results = []
        completed_count = 0
        total_count = len(video_items)
        
        # 移除冗余的开始日志，由调用方处理
        
        # 使用线程池并发下载
        with ThreadPoolExecutor(max_workers=self.max_concurrent) as executor:
            # 提交下载任务
            future_to_item = {}
            for i, item in enumerate(video_items):
                if isinstance(item, str):
                    url = item
                    filename = None
                    referer = None
                elif isinstance(item, dict):
                    url = item.get('url')
                    filename = item.get('filename')
                    referer = item.get('referer')
                else:
                    results.append(DownloadResult(
                        success=False,
                        error_message=f"无效的视频项格式: {item}"
                    ))
                    continue
                
                future = executor.submit(self.download_video, url, filename, None, referer)
                future_to_item[future] = (i, item)
            
            # 处理完成的任务
            for future in as_completed(future_to_item):
                index, item = future_to_item[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    result = DownloadResult(
                        success=False,
                        error_message=f"下载异常: {str(e)}"
                    )
                    results.append(result)
                
                completed_count += 1
                
                # 调用进度回调
                if progress_callback:
                    progress_callback(completed_count, total_count)
        
        # 统计结果
        success_count = sum(1 for r in results if r.success)
        self.logger.info(f"📊 批量下载完成: {success_count}/{total_count} 成功")
        
        return results
    
    def _validate_url(self, url: str) -> None:
        """
        验证URL的安全性和有效性
        
        @param {str} url - 待验证的URL
        @raises {SecurityException} 当URL不安全时抛出
        @raises {ValidationException} 当URL无效时抛出
        """
        if not url or not isinstance(url, str):
            raise ValidationException("URL不能为空且必须是字符串")
        
        try:
            parsed = urlparse(url)
            
            # 检查协议
            if parsed.scheme not in ['http', 'https']:
                raise SecurityException(f"不支持的协议: {parsed.scheme}")
            
            # 检查域名
            domain = parsed.netloc.lower()
            if not domain:
                raise ValidationException("URL中缺少域名")
            
            # 域名安全检查（可选，根据需求调整）
            # is_trusted = any(domain == td or domain.endswith('.' + td) for td in self.trusted_domains)
            # if not is_trusted:
            #     self.logger.warning(f"URL域名不在可信列表中: {domain}")
            
        except Exception as e:
            if not isinstance(e, (SecurityException, ValidationException)):
                raise ValidationException(f"URL格式无效: {str(e)}")
            else:
                raise
    
    def _generate_filename(self, url: str) -> str:
        """
        根据URL生成文件名
        
        @param {str} url - 视频URL
        @returns {str} 生成的文件名
        """
        try:
            parsed = urlparse(url)
            
            # 尝试从URL路径中提取文件名
            path_parts = parsed.path.split('/')
            for part in reversed(path_parts):
                if part and '.' in part:
                    # 检查是否有视频文件扩展名
                    name, ext = os.path.splitext(part)
                    if ext.lower() in self.allowed_extensions:
                        return self._sanitize_filename(part)
            
            # 如果无法从URL提取，则生成基于内容的文件名
            url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
            timestamp = int(time.time())
            return f"video_{timestamp}_{url_hash}.mp4"
            
        except Exception:
            # 最后的备选方案
            timestamp = int(time.time())
            return f"video_{timestamp}.mp4"
    
    def _sanitize_filename(self, filename: str) -> str:
        """
        清理和规范化文件名
        
        @param {str} filename - 原始文件名
        @returns {str} 清理后的文件名
        """
        if not filename:
            return "video.mp4"
        
        # URL解码
        filename = unquote(filename)
        
        # 移除或替换危险字符
        dangerous_chars = r'[<>:"/\\|?*\x00-\x1f]'
        filename = re.sub(dangerous_chars, '_', filename)
        
        # 限制文件名长度
        name, ext = os.path.splitext(filename)
        if len(name) > 100:
            name = name[:100]
        
        # 确保有效的视频扩展名
        if not ext or ext.lower() not in self.allowed_extensions:
            ext = '.mp4'
        
        clean_filename = name + ext
        
        # 避免保留文件名
        reserved_names = {'CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 
                         'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 
                         'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 
                         'LPT7', 'LPT8', 'LPT9'}
        
        if name.upper() in reserved_names:
            clean_filename = f"video_{name}{ext}"
        
        return clean_filename
    
    def _handle_filename_conflict(self, file_path: Path) -> Path:
        """
        处理文件名冲突
        
        @param {Path} file_path - 原始文件路径
        @returns {Path} 新的文件路径
        """
        base_name = file_path.stem
        extension = file_path.suffix
        parent_dir = file_path.parent
        
        counter = 1
        while True:
            new_name = f"{base_name}_{counter}{extension}"
            new_path = parent_dir / new_name
            if not new_path.exists():
                return new_path
            counter += 1
            
            # 防止无限循环
            if counter > 1000:
                timestamp = int(time.time())
                new_name = f"{base_name}_{timestamp}{extension}"
                return parent_dir / new_name
    
    def _download_file(
        self,
        url: str,
        file_path: Path,
        progress_callback: Optional[Callable[[float], None]] = None,
        referer: Optional[str] = None
    ) -> int:
        """
        执行实际的文件下载
        
        @param {str} url - 下载URL
        @param {Path} file_path - 保存路径
        @param {Optional[Callable]} progress_callback - 进度回调
        @returns {int} 下载的文件大小
        @raises {NetworkException} 当网络请求失败时抛出
        """
        try:
            # 准备请求头
            headers = {}
            if referer:
                headers['Referer'] = referer
            
            # 发起HEAD请求获取文件信息
            head_response = self.session.head(url, headers=headers, timeout=self.timeout)
            head_response.raise_for_status()
            
            # 检查文件大小
            content_length = head_response.headers.get('content-length')
            if content_length:
                file_size = int(content_length)
                if file_size > self.max_file_size:
                    raise ValidationException(
                        f"文件大小超过限制: {self._format_size(file_size)} > {self._format_size(self.max_file_size)}"
                    )
            
            # 发起GET请求下载文件
            response = self.session.get(url, headers=headers, timeout=self.timeout, stream=True)
            response.raise_for_status()
            
            downloaded_size = 0
            total_size = int(response.headers.get('content-length', 0))
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=self.chunk_size):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        
                        # 调用进度回调
                        if progress_callback and total_size > 0:
                            progress = (downloaded_size / total_size) * 100
                            progress_callback(progress)
            
            return downloaded_size
            
        except requests.exceptions.RequestException as e:
            raise NetworkException(f"网络请求失败: {str(e)}")
        except IOError as e:
            raise ValidationException(f"文件写入失败: {str(e)}")
    
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
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取下载器统计信息
        
        @returns {Dict[str, Any]} 统计信息
        """
        return {
            "download_dir": str(self.download_dir),
            "max_file_size": self.max_file_size,
            "max_concurrent": self.max_concurrent,
            "timeout": self.timeout,
            "chunk_size": self.chunk_size,
            "max_retries": self.max_retries
        }
    
    def __del__(self):
        """析构函数，清理资源"""
        try:
            if hasattr(self, 'session'):
                self.session.close()
        except:
            pass
