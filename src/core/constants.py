"""
常量定义模块

@author: MingTechPro
@version: 1.0.0
@date: 2025-08-15
@description: 该模块定义了抖音爬虫系统中使用的所有常量，
             包括API端点、数据字段名、默认值、状态码等。

主要常量分类:
- API端点: 抖音API接口地址
- 数据字段: JSON响应中的字段名
- 文件扩展名: 支持的文件格式
- 默认值: 系统默认配置参数
- 状态码: HTTP响应状态码
- 错误消息: 预定义的错误信息

使用场景:
- 数据解析和提取
- API请求构建
- 错误处理和消息
- 文件操作
- 配置管理

@example
    # 使用API端点常量
    api_url = f"https://api.douyin.com/{Constants.API_SEARCH_LIST}"
    
    # 使用数据字段常量
    data = response.get(Constants.DATA_FIELD, {})
    
    # 使用错误消息常量
    error_msg = Constants.ERROR_MESSAGES['request_failed']
"""


class Constants:
    """
    应用常量类
    
    定义抖音爬虫系统中使用的所有常量值，提供统一的常量管理。
    
    @author: MingTechPro
    @version: 1.0.0
    @date: 2025-08-15
    
    常量分类:
    - API端点: 抖音API接口地址
    - 数据字段: JSON响应中的字段名
    - 文件扩展名: 支持的文件格式
    - 默认值: 系统默认配置参数
    - 状态码: HTTP响应状态码
    - 错误消息: 预定义的错误信息
    
    @example
        # 获取API端点
        search_api = Constants.API_SEARCH_LIST
        
        # 获取数据字段
        data_field = Constants.DATA_FIELD
        
        # 获取错误消息
        error_msg = Constants.ERROR_MESSAGES['request_failed']
    """
    
    # API端点常量 - 抖音API接口地址
    API_SEARCH_LIST = "search/list"        # 搜索列表API
    API_AWEME_DETAIL = "aweme/detail"      # 视频详情API
    
    # 数据字段名常量 - JSON响应中的字段名
    DATA_FIELD = "data"                    # 数据主字段
    WORD_LIST_FIELD = "word_list"          # 热词列表字段
    AWEME_DETAIL_FIELD = "aweme_detail"    # 视频详情字段
    ACTIVE_TIME_FIELD = "active_time"      # 活跃时间字段
    
    # 热榜项目字段常量 - 热榜数据结构中的字段名
    SENTENCE_ID_FIELD = "sentence_id"      # 句子ID字段
    WORD_FIELD = "word"                    # 热词字段
    POSITION_FIELD = "position"            # 位置字段
    HOT_VALUE_FIELD = "hot_value"          # 热度值字段
    VIEW_COUNT_FIELD = "view_count"        # 浏览量字段
    
    # 视频字段常量 - 视频数据结构中的字段名
    AWEME_ID_FIELD = "aweme_id"            # 视频ID字段
    DESC_FIELD = "desc"                    # 描述字段
    VIDEO_FIELD = "video"                  # 视频字段
    BIT_RATE_FIELD = "bit_rate"            # 比特率字段
    PLAY_ADDR_FIELD = "play_addr"          # 播放地址字段
    URL_LIST_FIELD = "url_list"            # URL列表字段
    
    # 文件扩展名常量 - 支持的文件格式
    JSON_EXT = ".json"                     # JSON文件扩展名
    CSV_EXT = ".csv"                       # CSV文件扩展名
    LOG_EXT = ".log"                       # 日志文件扩展名
    
    # 默认值常量 - 系统默认配置参数
    DEFAULT_TIMEOUT = 30                   # 默认超时时间(秒)
    DEFAULT_MAX_RETRIES = 3                # 默认最大重试次数
    DEFAULT_DELAY = 2                      # 默认延迟时间(秒)
    DEFAULT_MAX_ITEMS = 10                 # 默认最大项目数
    
    # 状态码常量 - HTTP响应状态码
    SUCCESS = 200                          # 成功状态码
    TIMEOUT = 408                          # 超时状态码
    RATE_LIMIT = 429                       # 限流状态码
    
    # 错误消息常量 - 预定义的错误信息
    ERROR_MESSAGES = {
        'config_not_found': '配置文件不存在',           # 配置文件不存在错误
        'invalid_url': 'URL格式无效',                  # URL格式错误
        'request_failed': '请求失败',                  # 请求失败错误
        'data_parse_error': '数据解析错误',            # 数据解析错误
        'browser_init_failed': '浏览器初始化失败'      # 浏览器初始化错误
    }
