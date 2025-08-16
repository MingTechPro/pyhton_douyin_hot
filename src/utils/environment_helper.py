"""
环境配置辅助工具
用于处理environment.py配置文件的加载和验证

@author AI Assistant  
@date 2025-01-15
"""

import importlib.util
import warnings
from pathlib import Path
from typing import Dict, Any, Optional
from .security import SecurityValidator


class EnvironmentHelper:
    """
    环境配置辅助类
    负责加载和验证environment.py配置文件
    """
    
    @staticmethod
    def load_environment_config(config_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        加载环境配置文件
        
        @param {Optional[str]} config_dir - 配置文件目录，None表示使用默认目录
        @returns {Dict[str, Any]} 环境配置字典
        
        @example
            config = EnvironmentHelper.load_environment_config()
            cookie = config.get('DOUYIN_COOKIE', '')
        """
        env_config = {}
        
        # 确定配置文件路径
        if config_dir:
            env_file = Path(config_dir) / "environment.py"
        else:
            # 默认在项目根目录查找
            current_file = Path(__file__)
            project_root = current_file.parent.parent.parent
            env_file = project_root / "environment.py"
        
        if env_file.exists():
            try:
                # 动态导入环境配置文件
                spec = importlib.util.spec_from_file_location("environment", env_file)
                env_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(env_module)
                
                # 获取所有非私有配置项
                for attr_name in dir(env_module):
                    if not attr_name.startswith('_') and not callable(getattr(env_module, attr_name)):
                        env_config[attr_name] = getattr(env_module, attr_name)
                        
            except Exception as e:
                warnings.warn(f"环境配置加载失败: {e}", UserWarning)
        
        return env_config
    
    @staticmethod
    def validate_environment_config(env_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证环境配置
        
        @param {Dict[str, Any]} env_config - 环境配置字典
        @returns {Dict[str, Any]} 验证结果
        
        @example
            config = EnvironmentHelper.load_environment_config()
            result = EnvironmentHelper.validate_environment_config(config)
            if result['is_valid']:
                print("配置验证通过")
        """
        result = {
            'is_valid': True,
            'errors': [],
            'warnings': []
        }
        
        # 检查Cookie配置
        cookie = env_config.get('DOUYIN_COOKIE', '')
        if cookie and env_config.get('ENABLE_COOKIE_VALIDATION', True):
            try:
                cookie_result = SecurityValidator.validate_cookie(cookie)
                if not cookie_result['is_valid']:
                    result['errors'].append(f"Cookie验证失败: {cookie_result['error']}")
                    result['is_valid'] = False
                
                if cookie_result['warning']:
                    result['warnings'].extend([f"Cookie警告: {w}" for w in cookie_result['warning']])
                    
            except Exception as e:
                result['errors'].append(f"Cookie验证异常: {str(e)}")
                result['is_valid'] = False
        
        # 检查其他配置项
        if 'REQUEST_INTERVAL' in env_config:
            interval = env_config['REQUEST_INTERVAL']
            if interval is not None and interval < 0:
                result['errors'].append("REQUEST_INTERVAL不能为负数")
                result['is_valid'] = False
            elif interval is not None and interval < 0.5:
                result['warnings'].append("REQUEST_INTERVAL过短可能被反爬虫检测")
        
        if 'MAX_ITEMS' in env_config:
            max_items = env_config['MAX_ITEMS']
            if max_items is not None and max_items <= 0:
                result['errors'].append("MAX_ITEMS必须大于0")
                result['is_valid'] = False
            elif max_items is not None and max_items > 1000:
                result['warnings'].append("MAX_ITEMS过大可能被限流")
        
        return result
    
    @staticmethod
    def auto_validate_on_import(config_dir: Optional[str] = None, show_warnings: bool = True) -> bool:
        """
        自动验证环境配置（在模块导入时调用）
        
        @param {Optional[str]} config_dir - 配置文件目录  
        @param {bool} show_warnings - 是否显示警告信息
        @returns {bool} 验证是否通过
        
        @example
            # 在模块初始化时调用
            if not EnvironmentHelper.auto_validate_on_import():
                print("环境配置验证失败")
        """
        try:
            env_config = EnvironmentHelper.load_environment_config(config_dir)
            
            # 如果没有环境配置文件，跳过验证
            if not env_config:
                return True
            
            result = EnvironmentHelper.validate_environment_config(env_config)
            
            # 显示警告
            if show_warnings and result['warnings']:
                for warning in result['warnings']:
                    warnings.warn(warning, UserWarning)
            
            # 显示错误
            if show_warnings and result['errors']:
                for error in result['errors']:
                    warnings.warn(f"配置错误: {error}", UserWarning)
            
            return result['is_valid']
            
        except Exception as e:
            if show_warnings:
                warnings.warn(f"环境配置验证异常: {str(e)}", UserWarning)
            return False
