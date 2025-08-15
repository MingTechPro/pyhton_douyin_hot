# 抖音热点爬虫项目 - 开发文档

本文档包含抖音热点爬虫项目的详细开发信息，包括API文档、开发指南、测试指南等。

## 📋 目录

- [📦 安装指南](#-安装指南)
- [📚 API文档](#-api文档)
- [🛠️ 开发指南](#-开发指南)
- [🧪 测试指南](#-测试指南)
- [📝 日志管理](#-日志管理)
- [🤝 贡献指南](#-贡献指南)

## 📦 安装指南

### 完整安装步骤

```bash
# 克隆仓库
git clone https://github.com/MingTechPro/pyhton_douyin_hot.git
cd pyhton_douyin_hot

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate     # Windows

# 安装项目
pip install -e .

# 安装开发依赖（可选）
pip install -e ".[dev,test]"
```

### 依赖说明

#### 核心依赖
- **DrissionPage**: 网页自动化工具
- **requests**: HTTP 请求库
- **pandas**: 数据处理库
- **numpy**: 数值计算库
- **aiohttp**: 异步 HTTP 客户端
- **redis**: 缓存数据库
- **pydantic**: 数据验证库
- **psutil**: 系统监控库
- **asyncio-throttle**: 异步限流库
- **pyyaml**: YAML配置文件支持
- **python-dotenv**: 环境变量管理
- **colorlog**: 彩色日志输出

#### 可选依赖
- **测试工具**: pytest, pytest-asyncio, pytest-cov
- **代码质量**: black, flake8, mypy
- **文档生成**: sphinx, sphinx-rtd-theme

### 配置项详解

#### URLs 配置
- `hot_list`: 抖音热榜页面 URL
- `video`: 视频详情页面 URL

#### Request 配置
- `headers`: HTTP 请求头配置
- `timeouts`: 请求超时时间设置
- `retry`: 重试机制配置

#### Crawler 配置
- `max_items`: 最大获取项目数
- `request_interval`: 请求间隔时间
- `skip_top_item`: 是否跳过热榜置顶
- `enable_cache`: 是否启用缓存
- `cache_duration`: 缓存持续时间

#### Output 配置
- `format`: 输出格式 (json/csv/txt/md)
- `indent`: JSON 格式化缩进
- `ensure_ascii`: 是否确保 ASCII 编码
- `default_path`: 默认输出路径

#### Logging 配置
- `level`: 日志级别
- `console_level`: 控制台日志级别
- `file_level`: 文件日志级别
- `log_file`: 日志文件路径

## 📚 API 文档

### 核心类

#### DouyinSpider

主要的爬虫类，负责数据爬取和处理。

```python
from src.spider.douyin_spider import DouyinSpider

# 创建爬虫实例
spider = DouyinSpider()

# 获取热榜数据
hot_data = await spider.get_hot_list(max_items=10)
```

**方法说明：**

- `get_hot_list(max_items: int = 10)`: 获取热榜数据
- `get_video_detail(video_id: str)`: 获取视频详情
- `process_data(raw_data: dict)`: 处理原始数据

#### ConfigManager

配置管理类，负责加载和管理配置。

```python
from src.config.config_manager import ConfigManager

# 创建配置管理器
config = ConfigManager()

# 获取配置项
max_items = config.get('crawler.max_items')
```

**方法说明：**

- `get(key: str, default=None)`: 获取配置项
- `set(key: str, value)`: 设置配置项
- `load_config()`: 加载配置文件
- `save_config()`: 保存配置文件

#### LogManager

日志管理类，提供统一的日志记录功能。

```python
from src.utils.logger import LogManager

# 创建日志管理器
logger = LogManager.get_logger(__name__)

# 记录日志
logger.info("开始爬取数据")
logger.error("发生错误", exc_info=True)
```

### 数据模型

#### HotListResponse

热榜数据响应模型。

```python
from src.core.models import HotListResponse

# 创建响应对象
response = HotListResponse(
    success=True,
    data=hot_data,
    timestamp=datetime.now(),
    total_count=len(hot_data)
)
```

#### CrawlResult

爬取结果模型。

```python
from src.core.models import CrawlResult

# 创建结果对象
result = CrawlResult(
    items=hot_items,
    performance_stats=stats,
    errors=errors
)
```

### 工具类

#### Formatters

数据格式化工具类。

```python
from src.utils.formatters import Formatters

# 格式化数据为JSON
json_data = Formatters.to_json(data)

# 格式化数据为CSV
csv_data = Formatters.to_csv(data)

# 格式化数据为Markdown
md_data = Formatters.to_markdown(data)
```

#### Performance

性能监控工具类。

```python
from src.utils.performance import Performance

# 开始性能监控
perf = Performance()
perf.start()

# 执行操作
# ...

# 结束监控并获取统计信息
stats = perf.end()
print(f"执行时间: {stats['duration']}秒")
print(f"内存使用: {stats['memory_usage']}MB")
```

## 🛠️ 开发指南

### 开发环境设置

1. **克隆项目并安装开发依赖**
   ```bash
   git clone https://github.com/MingTechPro/pyhton_douyin_hot.git
   cd pyhton_douyin_hot
   pip install -e ".[dev,test]"
   ```

2. **安装 pre-commit 钩子**
   ```bash
   pre-commit install
   ```

3. **运行测试**
   ```bash
   pytest
   ```

### 代码规范

项目使用以下工具确保代码质量：

- **Black**: 代码格式化
- **Flake8**: 代码风格检查
- **MyPy**: 类型检查
- **Pre-commit**: Git 钩子

### 添加新功能

1. **创建功能分支**
   ```bash
   git checkout -b feature/new-feature
   ```

2. **编写代码和测试**
   ```python
   # 在 src/ 目录下添加新模块
   # 在 tests/ 目录下添加对应测试
   ```

3. **运行测试和检查**
   ```bash
   pytest
   black src/ tests/
   flake8 src/ tests/
   mypy src/
   ```

4. **提交代码**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```

### 模块开发指南

#### 添加新的爬虫模块

1. **继承基础爬虫类**
   ```python
   from src.spider.base_spider import BaseSpider
   
   class NewSpider(BaseSpider):
       def __init__(self):
           super().__init__()
       
       async def crawl(self):
           # 实现爬取逻辑
           pass
   ```

2. **实现必要的方法**
   - `crawl()`: 主要爬取方法
   - `parse_data()`: 数据解析方法
   - `validate_data()`: 数据验证方法

#### 添加新的格式化器

1. **在 formatters.py 中添加新方法**
   ```python
   @staticmethod
   def to_custom_format(data: List[Dict]) -> str:
       # 实现自定义格式化逻辑
       pass
   ```

2. **在配置文件中注册新格式**
   ```json
   {
     "output": {
       "formats": ["json", "csv", "custom"]
     }
   }
   ```

### 错误处理

#### 自定义异常类

```python
class SpiderException(Exception):
    """爬虫基础异常类"""
    pass

class NetworkException(SpiderException):
    """网络相关异常"""
    pass

class DataParseException(SpiderException):
    """数据解析异常"""
    pass
```

#### 异常处理最佳实践

```python
try:
    data = await spider.get_hot_list()
except NetworkException as e:
    logger.error(f"网络错误: {e}")
    # 重试逻辑
except DataParseException as e:
    logger.error(f"数据解析错误: {e}")
    # 降级处理
except Exception as e:
    logger.error(f"未知错误: {e}")
    # 通用错误处理
```

## 🧪 测试指南

### 运行所有测试
```bash
pytest
```

### 运行特定测试
```bash
pytest tests/test_spider.py
```

### 运行性能测试
```bash
pytest -m "slow"
```

### 生成测试覆盖率报告
```bash
pytest --cov=src --cov-report=html
```

### 测试文件结构

```
tests/
├── __init__.py
├── conftest.py              # 测试配置和fixture
├── test_spider.py           # 爬虫测试
├── test_config.py           # 配置管理测试
├── test_formatters.py       # 格式化工具测试
├── test_logger.py           # 日志系统测试
└── integration/             # 集成测试
    ├── __init__.py
    └── test_end_to_end.py   # 端到端测试
```

### 编写测试用例

#### 单元测试示例

```python
import pytest
from src.spider.douyin_spider import DouyinSpider

class TestDouyinSpider:
    @pytest.fixture
    def spider(self):
        return DouyinSpider()
    
    def test_spider_initialization(self, spider):
        assert spider is not None
        assert hasattr(spider, 'config')
    
    @pytest.mark.asyncio
    async def test_get_hot_list(self, spider):
        data = await spider.get_hot_list(max_items=5)
        assert isinstance(data, list)
        assert len(data) <= 5
```

#### 集成测试示例

```python
import pytest
from src.main import main

class TestIntegration:
    @pytest.mark.asyncio
    async def test_full_workflow(self):
        # 测试完整的工作流程
        result = await main(max_items=3)
        assert result.success
        assert len(result.data) <= 3
```

### Mock 和 Stub

#### 使用 Mock 测试网络请求

```python
from unittest.mock import patch, AsyncMock

class TestNetworkRequests:
    @patch('src.spider.douyin_spider.requests.get')
    def test_network_request(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"data": []}
        
        # 测试代码
        result = spider.make_request()
        assert result is not None
```

## 📝 日志管理

项目提供了完善的日志管理系统，包括自动日志轮转、清理和查看功能。

### 日志配置

在 `config.json` 中可以配置日志相关参数：

```json
{
  "logging": {
    "level": "INFO",
    "console_level": "INFO", 
    "file_level": "DEBUG",
    "log_file": "logs/spider_{timestamp}.log",
    "max_file_size": "10MB",
    "backup_count": 5,
    "cleanup_old_logs": true,
    "log_retention_days": 7
  }
}
```

### 日志管理工具

项目提供了便捷的日志管理脚本 `manage_logs.py`：

#### 查看日志统计信息
```bash
python manage_logs.py stats
```

#### 查看最近的日志文件
```bash
python manage_logs.py view --recent 5
```

#### 清理旧日志文件
```bash
# 清理7天前的日志文件
python manage_logs.py cleanup --days 7

# 清理超过50MB的日志文件
python manage_logs.py cleanup --max-size 50

# 清理重复的日志文件
python manage_logs.py cleanup --duplicates

# 试运行清理操作（不实际删除）
python manage_logs.py cleanup --dry-run --days 7
```

### 日志文件说明

- **日志位置**: `logs/` 目录
- **文件命名**: `spider_YYYY-MM-DD_HH-MM-SS_mmm.log`
- **自动清理**: 程序启动时自动清理7天前的日志文件
- **文件轮转**: 单个日志文件超过10MB时自动轮转

### 日志级别

- **DEBUG**: 详细的调试信息
- **INFO**: 一般信息（默认）
- **WARNING**: 警告信息
- **ERROR**: 错误信息
- **CRITICAL**: 严重错误

### 自定义日志格式

```python
import logging
from src.utils.logger import LogManager

# 创建自定义日志格式
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 获取日志器并设置格式
logger = LogManager.get_logger(__name__)
handler = logger.handlers[0]
handler.setFormatter(formatter)
```

## 🤝 贡献指南

我们欢迎所有形式的贡献！请阅读以下指南：

### 贡献方式

1. **报告 Bug**: 在 GitHub Issues 中报告问题
2. **功能建议**: 提出新功能建议
3. **代码贡献**: 提交 Pull Request
4. **文档改进**: 完善文档和示例
5. **测试贡献**: 添加测试用例

### 提交规范

我们使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

- `feat`: 新功能
- `fix`: 修复 Bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

### Pull Request 流程

1. Fork 项目到你的 GitHub 账户
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

### 开发环境

确保你的开发环境满足以下要求：

- Python 3.8+
- 所有开发依赖已安装
- 代码通过所有测试
- 符合代码规范要求

### 代码审查清单

提交 Pull Request 前，请确保：

- [ ] 代码符合项目规范
- [ ] 所有测试通过
- [ ] 添加了必要的文档
- [ ] 更新了相关测试用例
- [ ] 提交信息符合规范
- [ ] 没有引入新的警告或错误

## 📄 许可证

本项目采用 [Apache License 2.0](https://opensource.org/licenses/Apache-2.0) 许可证。

```
Copyright 2025 Douyin Spider Contributors

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```

---

📖 更多信息请查看 [README.md](./README.md)

