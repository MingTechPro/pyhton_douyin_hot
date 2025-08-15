"""
数据格式化工具模块

@author: MingTechPro
@version: 1.0.0
@date: 2025-08-15
@description: 该模块提供了各种数据格式化工具函数，用于处理和转换不同格式的数据。

主要功能:
- 文本清理和格式化
- 数据验证
- URL处理
- 时间格式化
- 数字格式化

依赖模块:
- re: 正则表达式
- urllib.parse: URL解析和编码
- datetime: 时间处理
"""
import re
import hashlib
import base64
from urllib.parse import quote, urlencode, urlparse, urlunparse
from typing import Optional, Dict, Any, Union
from datetime import datetime


def clean_text(text: str) -> str:
    """
    清理文本内容
    
    移除多余的空白字符、特殊字符等，确保文本格式规范。
    
    @param {str} text - 需要清理的文本
    @return {str} - 清理后的文本
    
    @example
        clean_text("  测试文本  \n\t  ")  # 返回: "测试文本"
        clean_text("特殊字符@#$%")  # 返回: "特殊字符"
    """
    if not text:
        return ""
    
    # 移除多余的空白字符
    text = re.sub(r'\s+', ' ', text.strip())
    
    # 移除特殊字符（保留中文、英文、数字、常用标点）
    text = re.sub(r'[^\w\s\u4e00-\u9fff.,!?;:()（）【】""''、。，！？；：]', '', text)
    
    return text


def format_number(num: Union[int, float]) -> str:
    """
    格式化数字显示
    
    将大数字转换为带逗号的易读格式。
    
    @param {Union[int, float]} num - 需要格式化的数字
    @return {str} - 格式化后的数字字符串
    
    @example
        format_number(12345)  # 返回: "12,345"
        format_number(123456789)  # 返回: "123,456,789"
    """
    return f"{num:,}"


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    格式化日期时间
    
    将datetime对象格式化为指定格式的字符串。
    
    @param {datetime} dt - 日期时间对象
    @param {str} format_str - 格式化字符串
    @return {str} - 格式化后的日期时间字符串
    
    @example
        format_datetime(datetime.now())  # 返回: "2025-08-15 17:30:00"
        format_datetime(datetime.now(), "%Y年%m月%d日")  # 返回: "2025年08月15日"
    """
    return dt.strftime(format_str)


def validate_url(url: str) -> bool:
    """
    验证URL格式
    
    检查URL是否符合标准格式。
    
    @param {str} url - 需要验证的URL
    @return {bool} - URL是否有效
    
    @example
        validate_url("https://www.douyin.com/hot")  # 返回: True
        validate_url("invalid-url")  # 返回: False
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def encode_url_text(text: str, encoding: str = 'utf-8') -> str:
    """
    对URL中的文本进行编码
    
    将包含中文字符的文本编码为URL安全的格式，防止浏览器解析问题。
    
    @param {str} text - 需要编码的文本
    @param {str} encoding - 编码格式，默认为utf-8
    @return {str} - 编码后的文本
    
    @example
        encode_url_text("美媒：特朗普将亲自迎接普京")  
        # 返回: "%E7%BE%8E%E5%AA%92%EF%BC%9A%E7%89%B9%E6%9C%97%E6%99%AE%E5%B0%86%E4%BA%B2%E8%87%AA%E8%BF%8E%E6%8E%A5%E6%99%AE%E4%BA%AC"
    """
    if not text:
        return ""
    
    # 使用urllib.parse.quote进行URL编码
    return quote(text, safe='', encoding=encoding)


def create_encrypted_url(base_url: str, item_id: str, title: str, encryption_method: str = 'url_encode') -> str:
    """
    创建加密的URL
    
    将包含中文字符的标题进行加密处理，生成浏览器友好的URL。
    
    @param {str} base_url - 基础URL
    @param {str} item_id - 项目ID
    @param {str} title - 标题文本
    @param {str} encryption_method - 加密方法，支持'url_encode'、'base64'、'hash'
    @return {str} - 加密后的完整URL
    
    @example
        create_encrypted_url(
            "https://www.douyin.com/hot",
            "2204535", 
            "美媒：特朗普将亲自迎接普京"
        )
        # 返回: "https://www.douyin.com/hot/2204535/%E7%BE%8E%E5%AA%92%EF%BC%9A%E7%89%B9%E6%9C%97%E6%99%AE%E5%B0%86%E4%BA%B2%E8%87%AA%E8%BF%8E%E6%8E%A5%E6%99%AE%E4%BA%AC"
    """
    if not all([base_url, item_id, title]):
        return base_url
    
    # 清理标题文本
    clean_title = clean_text(title)
    
    if encryption_method == 'url_encode':
        # URL编码方式（推荐）
        encoded_title = encode_url_text(clean_title)
        return f"{base_url}/{item_id}/{encoded_title}"
    
    elif encryption_method == 'base64':
        # Base64编码方式
        import base64
        encoded_title = base64.b64encode(clean_title.encode('utf-8')).decode('utf-8')
        # 替换URL不安全的字符
        encoded_title = encoded_title.replace('+', '-').replace('/', '_').replace('=', '')
        return f"{base_url}/{item_id}/{encoded_title}"
    
    elif encryption_method == 'hash':
        # 哈希编码方式
        title_hash = hashlib.md5(clean_title.encode('utf-8')).hexdigest()
        return f"{base_url}/{item_id}/{title_hash}"
    
    else:
        # 默认使用URL编码
        encoded_title = encode_url_text(clean_title)
        return f"{base_url}/{item_id}/{encoded_title}"


def decode_url_text(encoded_text: str, encoding: str = 'utf-8') -> str:
    """
    解码URL中的文本
    
    将URL编码的文本解码为原始文本。
    
    @param {str} encoded_text - 编码后的文本
    @param {str} encoding - 编码格式，默认为utf-8
    @return {str} - 解码后的原始文本
    
    @example
        decode_url_text("%E7%BE%8E%E5%AA%92%EF%BC%9A%E7%89%B9%E6%9C%97%E6%99%AE%E5%B0%86%E4%BA%B2%E8%87%AA%E8%BF%8E%E6%8E%A5%E6%99%AE%E4%BA%AC")
        # 返回: "美媒：特朗普将亲自迎接普京"
    """
    if not encoded_text:
        return ""
    
    try:
        from urllib.parse import unquote
        return unquote(encoded_text, encoding=encoding)
    except Exception:
        return encoded_text


def extract_url_components(url: str) -> Dict[str, str]:
    """
    提取URL组件
    
    解析URL并提取各个组件部分。
    
    @param {str} url - 需要解析的URL
    @return {Dict[str, str]} - URL组件字典
    
    @example
        extract_url_components("https://www.douyin.com/hot/2204535/美媒：特朗普将亲自迎接普京")
        # 返回: {
        #     'scheme': 'https',
        #     'netloc': 'www.douyin.com',
        #     'path': '/hot/2204535/美媒：特朗普将亲自迎接普京',
        #     'params': '',
        #     'query': '',
        #     'fragment': ''
        # }
    """
    try:
        parsed = urlparse(url)
        return {
            'scheme': parsed.scheme,
            'netloc': parsed.netloc,
            'path': parsed.path,
            'params': parsed.params,
            'query': parsed.query,
            'fragment': parsed.fragment
        }
    except Exception:
        return {}


def is_chinese_text(text: str) -> bool:
    """
    检查文本是否包含中文字符
    
    @param {str} text - 需要检查的文本
    @return {bool} - 是否包含中文字符
    
    @example
        is_chinese_text("Hello World")  # 返回: False
        is_chinese_text("你好世界")  # 返回: True
        is_chinese_text("Hello 世界")  # 返回: True
    """
    if not text:
        return False
    
    # 检查是否包含中文字符（Unicode范围：\u4e00-\u9fff）
    return bool(re.search(r'[\u4e00-\u9fff]', text))


def needs_url_encoding(text: str) -> bool:
    """
    检查文本是否需要URL编码
    
    判断文本是否包含需要编码的特殊字符。
    
    @param {str} text - 需要检查的文本
    @return {bool} - 是否需要URL编码
    
    @example
        needs_url_encoding("Hello World")  # 返回: False
        needs_url_encoding("你好世界")  # 返回: True
        needs_url_encoding("Hello World!")  # 返回: True
    """
    if not text:
        return False
    
    # 检查是否包含非ASCII字符或URL不安全字符
    unsafe_chars = [' ', ':', ';', '=', '&', '?', '#', '%', '+', '"', "'", '<', '>', '|', '\\', '^', '`', '{', '}', '[', ']']
    
    # 检查中文字符
    if is_chinese_text(text):
        return True
    
    # 检查URL不安全字符
    for char in unsafe_chars:
        if char in text:
            return True
    
    return False


def convert_to_markdown(hot_list_response) -> str:
    """
    将热榜数据转换为Markdown格式
    
    @param {object} hot_list_response - 热榜响应数据对象
    @return {str} - Markdown格式的字符串
    
    @example
        markdown_content = convert_to_markdown(hot_list_response)
        with open('output.md', 'w', encoding='utf-8') as f:
            f.write(markdown_content)
    """
    lines = []
    lines.append("# 抖音热榜数据")
    lines.append("")
    lines.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    
    for item in hot_list_response.items:
        lines.append(f"## {item.position}. {item.title}")
        lines.append("")
        lines.append(f"- **热度**: {format_number(item.popularity)}")
        lines.append(f"- **浏览量**: {format_number(item.views)}")
        lines.append(f"- **链接**: [{item.url}]({item.url})")
        lines.append("")
        
        if item.articles:
            lines.append("### 相关视频")
            lines.append("")
            for i, article in enumerate(item.articles, 1):
                lines.append(f"#### {i}. {article.title}")
                lines.append("")
                lines.append(f"- **链接**: [{article.short_url}]({article.short_url})")
                if article.video_url:
                    lines.append(f"- **视频**: [点击播放]({article.video_url})")
                lines.append("")
        else:
            lines.append("### 相关视频")
            lines.append("")
            lines.append("*暂无相关视频*")
            lines.append("")
        
        lines.append("---")
        lines.append("")
    
    return "\n".join(lines)


def convert_to_csv(hot_list_response) -> str:
    """
    将热榜数据转换为CSV格式
    
    @param {object} hot_list_response - 热榜响应数据对象
    @return {str} - CSV格式的字符串
    
    @example
        csv_content = convert_to_csv(hot_list_response)
        with open('output.csv', 'w', encoding='utf-8') as f:
            f.write(csv_content)
    """
    lines = []
    # CSV头部
    lines.append("排名,标题,热度,浏览量,链接")
    
    for item in hot_list_response.items:
        # 处理CSV中的特殊字符（逗号、引号等）
        title = item.title.replace('"', '""')  # 转义双引号
        if ',' in title or '"' in title:
            title = f'"{title}"'
        
        lines.append(f"{item.position},{title},{item.popularity},{item.views},{item.url}")
    
    return "\n".join(lines)


def convert_to_txt(hot_list_response) -> str:
    """
    将热榜数据转换为纯文本格式
    
    @param {object} hot_list_response - 热榜响应数据对象
    @return {str} - 纯文本格式的字符串
    
    @example
        txt_content = convert_to_txt(hot_list_response)
        with open('output.txt', 'w', encoding='utf-8') as f:
            f.write(txt_content)
    """
    lines = []
    lines.append("抖音热榜数据")
    lines.append("=" * 50)
    lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    
    for item in hot_list_response.items:
        lines.append(f"{item.position}. {item.title}")
        lines.append(f"   热度: {format_number(item.popularity)}")
        lines.append(f"   浏览量: {format_number(item.views)}")
        lines.append(f"   链接: {item.url}")
        lines.append("")
        
        if item.articles:
            lines.append("   相关视频:")
            for i, article in enumerate(item.articles, 1):
                lines.append(f"   {i}. {article.title}")
                lines.append(f"      链接: {article.short_url}")
                if article.video_url:
                    lines.append(f"      视频: {article.video_url}")
                lines.append("")
        else:
            lines.append("   相关视频: 暂无")
            lines.append("")
        
        lines.append("-" * 30)
        lines.append("")
    
    return "\n".join(lines)
