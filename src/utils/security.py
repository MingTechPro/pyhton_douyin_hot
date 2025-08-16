"""
安全验证工具模块
用于验证Cookie、URL等敏感信息的安全性

@author AI Assistant
@date 2025-01-15
"""

import re
import warnings
from typing import Dict, Any
from urllib.parse import urlparse


class SecurityValidator:
    """
    安全验证器类
    提供Cookie、URL等安全验证功能
    """
    
    @staticmethod
    def validate_cookie(cookie_str: str) -> Dict[str, Any]:
        """
        验证Cookie格式和有效性
        
        @param {str} cookie_str - Cookie字符串
        @returns {Dict[str, Any]} 验证结果
        
        @example
            result = SecurityValidator.validate_cookie(cookie)
            if result['is_valid']:
                print("Cookie验证通过")
            else:
                print(f"Cookie验证失败: {result['error']}")
        """
        result = {
            'is_valid': False,
            'error': None,
            'warning': [],
            'info': {}
        }
        
        if not cookie_str:
            result['error'] = "Cookie不能为空"
            return result
        
        if len(cookie_str) < 50:
            result['error'] = "Cookie长度过短，可能无效"
            return result
        
        # 检查必要的Cookie字段
        required_fields = ['sessionid', 'sid_tt', 'uid_tt']
        missing_fields = []
        
        for field in required_fields:
            if field not in cookie_str:
                missing_fields.append(field)
        
        if missing_fields:
            result['warning'].append(f"缺少重要Cookie字段: {', '.join(missing_fields)}")
        
        # 检查Cookie格式
        cookie_pairs = cookie_str.split(';')
        valid_pairs = 0
        
        for pair in cookie_pairs:
            pair = pair.strip()
            if '=' in pair:
                valid_pairs += 1
            elif pair:  # 非空但格式错误
                result['warning'].append(f"格式错误的Cookie片段: {pair[:20]}...")
        
        if valid_pairs == 0:
            result['error'] = "Cookie格式完全无效"
            return result
        
        # 检查是否包含可疑字符
        suspicious_patterns = [
            r'<script',
            r'javascript:',
            r'eval\(',
            r'document\.',
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, cookie_str, re.IGNORECASE):
                result['error'] = f"Cookie包含可疑内容: {pattern}"
                return result
        
        # 检查过期时间相关字段
        if 'expires=' in cookie_str.lower() or 'max-age=' in cookie_str.lower():
            result['warning'].append("Cookie包含过期时间设置，请注意及时更新")
        
        # 基本验证通过
        result['is_valid'] = True
        result['info'] = {
            'cookie_pairs_count': valid_pairs,
            'total_length': len(cookie_str),
            'has_session_info': any(field in cookie_str for field in required_fields)
        }
        
        return result
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """
        验证URL安全性
        
        @param {str} url - URL字符串
        @returns {bool} 是否安全
        """
        if not url:
            return False
        
        # 检查协议
        if not url.startswith(('http://', 'https://')):
            return False
        
        # 检查是否包含恶意字符
        dangerous_chars = ['<', '>', '"', "'", '`', '\n', '\r', '\t']
        for char in dangerous_chars:
            if char in url:
                return False
        
        # 检查是否是抖音域名
        douyin_domains = ['douyin.com', 'snssdk.com', 'bytedance.com']
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # 移除端口号
        if ':' in domain:
            domain = domain.split(':')[0]
        
        # 检查是否是可信域名
        is_trusted = False
        for trusted_domain in douyin_domains:
            if domain == trusted_domain or domain.endswith('.' + trusted_domain):
                is_trusted = True
                break
        
        return is_trusted
    
    @staticmethod
    def sanitize_input(input_str: str) -> str:
        """
        清理输入字符串，移除潜在危险字符
        
        @param {str} input_str - 输入字符串
        @returns {str} 清理后的字符串
        """
        if not isinstance(input_str, str):
            input_str = str(input_str)
        
        # 移除或转义危险字符
        dangerous_chars = {
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#x27;',
            '&': '&amp;',
            '\x00': '',  # 空字符
        }
        
        for char, replacement in dangerous_chars.items():
            input_str = input_str.replace(char, replacement)
        
        # 移除控制字符
        input_str = ''.join(char for char in input_str if ord(char) >= 32 or char in '\t\n\r')
        
        return input_str

    @staticmethod
    def validate_cookie_safe(cookie_str: str, show_warnings: bool = True) -> bool:
        """
        安全的Cookie验证方法，只返回布尔值
        可选择是否显示警告信息
        
        @param {str} cookie_str - Cookie字符串
        @param {bool} show_warnings - 是否显示警告信息
        @returns {bool} Cookie是否有效
        """
        try:
            result = SecurityValidator.validate_cookie(cookie_str)
            
            # 显示警告信息
            if show_warnings and result['warning']:
                for warning in result['warning']:
                    warnings.warn(f"Cookie警告: {warning}", UserWarning)
            
            # 如果验证失败，显示错误
            if not result['is_valid'] and show_warnings:
                warnings.warn(f"Cookie验证失败: {result['error']}", UserWarning)
            
            return result['is_valid']
        except Exception as e:
            if show_warnings:
                warnings.warn(f"Cookie验证异常: {str(e)}", UserWarning)
            return False
