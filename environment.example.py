"""
环境配置文件模板

复制此文件为 environment.py 并根据需要修改配置。
environment.py 文件包含敏感信息，不应提交到版本控制系统。

配置优先级: 命令行参数 > environment.py > config.json
"""

# =============================================================================
# 基础配置 - 覆盖 config.json 中的默认配置
# =============================================================================

# 爬虫基本配置
MAX_ITEMS = None               # 最大爬取项目数 (None = 使用默认值)
REQUEST_INTERVAL = None        # 请求间隔秒数 (None = 使用默认值)
SKIP_TOP_ITEM = None          # 是否跳过置顶项 (None = 使用默认值)

# 输出配置
OUTPUT_FORMAT = None          # 输出格式: json/csv/txt/markdown
OUTPUT_ENCODING = None        # 输出编码 (None = 使用默认值)

# =============================================================================
# 浏览器配置
# =============================================================================

# 浏览器运行模式
BROWSER_HEADLESS = False        # 是否启用无头模式（后台运行，不显示浏览器窗口）
BROWSER_DISABLE_DEV_SHM_USAGE = True   # 是否禁用/dev/shm使用
BROWSER_NO_SANDBOX = False      # 是否禁用沙盒模式

# =============================================================================
# 视频下载配置
# =============================================================================

# 视频下载功能
VIDEO_DOWNLOAD_ENABLED = False  # 是否启用视频下载功能
VIDEO_DOWNLOAD_DIR = "douyin_video"  # 视频下载目录
VIDEO_DOWNLOAD_MAX_FILE_SIZE = 209715200  # 最大文件大小（200MB）
VIDEO_DOWNLOAD_MAX_CONCURRENT = 3     # 最大并发下载数
VIDEO_DOWNLOAD_TIMEOUT = 30          # 下载超时时间（秒）
VIDEO_DOWNLOAD_CHUNK_SIZE = 8192     # 分块下载大小（字节）
VIDEO_DOWNLOAD_MAX_RETRIES = 3       # 最大重试次数
VIDEO_DOWNLOAD_RETRY_DELAY = 1.0     # 重试延迟时间（秒）
VIDEO_DOWNLOAD_AUTO_DOWNLOAD = False # 是否自动下载视频

# =============================================================================
# 缓存配置
# =============================================================================

ENABLE_CACHE = None           # 是否启用缓存 (None = 使用默认值)
CACHE_DURATION = None         # 缓存持续时间秒数 (None = 使用默认值)

# =============================================================================
# 日志配置
# =============================================================================

LOG_LEVEL = None              # 日志级别: DEBUG/INFO/WARNING/ERROR
LOG_FILE_ENABLED = None       # 是否启用日志文件 (None = 使用默认值)

# =============================================================================
# 高级配置
# =============================================================================

# 调试配置
DEBUG = False                 # 是否启用调试模式
PERFORMANCE_MONITORING = False # 是否启用性能监控

# 网络配置  
PROXY_HTTP = None            # HTTP代理 "http://proxy:port"
PROXY_HTTPS = None           # HTTPS代理 "https://proxy:port"

# =============================================================================
# 示例配置
# =============================================================================

# 以下是一些常用的配置示例，取消注释并修改值即可使用：

# # 快速模式配置
# MAX_ITEMS = 5
# REQUEST_INTERVAL = 0.5
# BROWSER_HEADLESS = True

# # 下载模式配置
# VIDEO_DOWNLOAD_ENABLED = True
# VIDEO_DOWNLOAD_MAX_CONCURRENT = 5
# BROWSER_HEADLESS = True

# # 调试模式配置
# DEBUG = True
# LOG_LEVEL = "DEBUG"
# PERFORMANCE_MONITORING = True

# # 生产环境配置
# MAX_ITEMS = 50
# REQUEST_INTERVAL = 2.0
# BROWSER_HEADLESS = True
# VIDEO_DOWNLOAD_ENABLED = True
# ENABLE_CACHE = True
