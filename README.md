# 抖音热点爬虫项目 (Douyin Hot Spider)

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)](https://opensource.org/licenses/Apache-2.0)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)]()
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

一个功能强大、高性能的抖音热点数据爬虫项目，采用模块化架构设计，支持多种数据格式输出、智能缓存机制、性能监控等特性。

[📚 开发文档](./DEVELOPMENT.md) &nbsp;&nbsp;&nbsp;&nbsp; [❓ 常见问题](#-常见问题) &nbsp;&nbsp;&nbsp;&nbsp; [📝 更新日志](#-更新日志)

## 📋 目录

- [✨ 功能特性](#-功能特性)
- [🚀 快速开始](#-快速开始)
- [💻 使用说明](#-使用说明)
- [📁 项目结构](#-项目结构)
- [⚙️ 配置说明](#-配置说明)
- [📄 许可证](#-许可证)

## ✨ 功能特性

### 🔥 核心功能
- **智能数据爬取**: 自动获取抖音热榜数据，支持实时更新
- **多格式输出**: 支持 JSON、CSV、TXT、Markdown 等多种输出格式
- **智能视频下载**: 支持视频自动下载，智能跳过已存在文件，避免重复下载
- **无头浏览器**: 支持后台运行模式，不显示浏览器窗口
- **防盗链绕过**: 智能设置请求头，绕过视频防盗链保护
- **并发下载**: 支持多线程并发下载，大幅提升下载效率
- **智能缓存**: 内置缓存机制，避免重复请求，提高响应速度
- **错误重试**: 自动重试机制，确保数据获取的可靠性

### 🛠️ 技术特性
- **模块化设计**: 清晰的代码结构，易于维护和扩展
- **配置管理**: 多层级配置系统（命令行 > environment.py > config.json）
- **日志系统**: 完善的日志记录，支持多级别日志输出和自动清理
- **性能监控**: 实时性能统计和监控功能
- **速率限制**: 智能请求频率控制，避免被反爬虫机制检测
- **数据模型**: 使用dataclass进行类型安全的数据建模

## 🚀 快速开始

### 环境要求

- **Python**: 3.8 或更高版本
- **操作系统**: Windows 10+, macOS 10.14+, Ubuntu 18.04+
- **内存**: 建议 4GB 以上
- **网络**: 稳定的互联网连接

### 快速安装

1. **克隆项目**
   ```bash
   git clone https://github.com/MingTechPro/pyhton_douyin_hot.git
   cd pyhton_douyin_hot
   copy environment.example.py environment.py
   ```

2. **安装依赖**
   ```bash
   pip install -e .
   ```

3. **配置环境**
   ```bash
   # 编辑 environment.py 文件，配置你的抖音Cookie
   # 从浏览器开发者工具中复制完整的cookie值
   ```

4. **运行程序**
   ```bash
   python main.py
   ```

## 💻 使用说明

### 环境配置

首先需要配置 `environment.py` 文件：

```python
"""
环境配置文件
用于存储敏感信息和用户自定义配置
"""

# 抖音请求Cookie配置
# 从浏览器开发者工具中复制完整的cookie值
DOUYIN_COOKIE = "your_cookie_here"

# 可选配置覆盖（会覆盖config.json中的对应值）
REQUEST_INTERVAL = None  # None表示使用config.json中的默认值
MAX_ITEMS = None  # None表示使用config.json中的默认值

# 浏览器配置
BROWSER_HEADLESS = False  # 是否启用无头模式（后台运行）

# 视频下载配置
VIDEO_DOWNLOAD_ENABLED = False  # 是否启用视频下载功能
VIDEO_DOWNLOAD_DIR = "douyin_video"  # 视频下载目录
```

### 基本使用

```bash
# 使用默认配置运行
python main.py

# 获取指定数量的热点数据
python main.py -m 20

# 设置请求间隔
python main.py -i 2.0

# 输出到文件
python main.py -o hot_data.json

# 指定输出格式
python main.py -f csv -o hot_data.csv

# 启用无头浏览器模式（后台运行）
python main.py --headless

# 启用视频下载功能
python main.py --download-videos

# 指定视频下载目录
python main.py --download-videos --download-dir "./my_videos"

# 试运行模式（检查配置）
python main.py --dry-run

# 显示详细性能信息
python main.py -p -m 10

# 组合使用多个功能
python main.py -m 15 --headless --download-videos --download-dir "./videos"
```

### 命令行参数

| 参数 | 简写 | 类型 | 默认值 | 说明 |
|------|------|------|--------|------|
| `--max-items` | `-m` | int | config.json | 最大获取项目数 |
| `--interval` | `-i` | float | config.json | 请求间隔时间(秒) |
| `--output` | `-o` | str | - | 输出文件路径 |
| `--format` | `-f` | str | json | 输出格式(json/csv/txt/markdown) |
| `--no-skip-top` | - | flag | False | 不跳过热榜置顶项目 |
| `--headless` | - | flag | False | 在后台模式运行浏览器 |
| `--download-videos` | - | flag | False | 启用视频下载功能 |
| `--download-dir` | - | str | downloads | 指定视频下载目录 |
| `--debug` | `-d` | flag | False | 开启调试模式 |
| `--performance` | `-p` | flag | False | 显示详细性能信息 |
| `--dry-run` | - | flag | False | 试运行模式 |
| `--version` | `-v` | flag | - | 显示版本信息 |
| `--help` | `-h` | flag | - | 显示帮助信息 |

### 使用示例

#### 示例 1：获取前 10 条热点数据
```bash
python main.py -m 10
```

#### 示例 2：获取数据并保存为 CSV 格式
```bash
python main.py -m 20 -f csv -o douyin_hot.csv
```

#### 示例 3：设置较长的请求间隔避免被限制
```bash
python main.py -m 50 -i 3.0 -p
```

#### 示例 4：调试模式运行
```bash
python main.py -d -m 5
```

#### 示例 5：无头模式运行（后台运行）
```bash
python main.py --headless -m 10
```

#### 示例 6：启用视频下载功能
```bash
python main.py --download-videos --download-dir "./my_videos" -m 5
```

#### 示例 7：试运行模式（检查配置）
```bash
python main.py --dry-run
```

#### 示例 8：输出Markdown格式
```bash
python main.py -m 10 -f markdown -o report.md
```

#### 示例 9：组合使用多个参数
```bash
python main.py -m 20 -i 2.0 --headless -p -f json -o results.json
```

## 📁 项目结构

```
Pyhton_douyin_hot/
├── src/                          # 源代码目录
│   ├── config/                   # 配置管理模块
│   │   ├── __init__.py
│   │   └── config_manager.py     # 配置管理器
│   ├── core/                     # 核心模块
│   │   ├── __init__.py
│   │   ├── constants.py          # 常量定义
│   │   └── models.py             # 数据模型
│   ├── spider/                   # 爬虫模块
│   │   ├── __init__.py
│   │   ├── base_spider.py        # 基础爬虫类
│   │   └── douyin_spider.py      # 抖音爬虫实现
│   └── utils/                    # 工具模块
│       ├── __init__.py
│       ├── formatters.py         # 数据格式化工具
│       ├── logger.py             # 日志管理
│       ├── log_cleaner.py        # 日志清理工具
│       └── performance.py        # 性能监控工具
├── douyin_data/                  # 数据输出目录
├── logs/                         # 日志文件目录
├── main.py                       # 主程序入口
├── manage_logs.py                # 日志管理脚本
├── config.json                   # 配置文件
├── environment.py                # 环境变量配置
├── pyproject.toml                # 项目配置和依赖管理
├── .gitignore                    # Git忽略文件
├── README.md                     # 项目说明文档
├── DEVELOPMENT.md                # 开发文档
└── LICENSE                       # 许可证文件
```

## ⚙️ 配置说明

### 配置文件结构

项目使用 `config.json` 作为主要配置文件，支持以下配置项：

```json
{
  "urls": {
    "hot_list": "https://www.douyin.com/hot",
    "video": "https://www.douyin.com/video"
  },
  "request": {
    "headers": {
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    },
    "timeouts": {
      "hot_list": 30,
      "video_detail": 10
    },
    "retry": {
      "hot_list_max_retries": 3,
      "hot_list_delay": 2
    }
  },
  "crawler": {
    "max_items": 10,
    "request_interval": 1,
    "skip_top_item": true,
    "enable_cache": true,
    "cache_duration": 300
  },
  "output": {
    "format": "json",
    "indent": 2,
    "ensure_ascii": false,
    "default_path": "douyin_data"
  },
  "logging": {
    "level": "INFO",
    "console_level": "INFO",
    "file_level": "DEBUG",
    "log_file": "logs/spider_{timestamp}.log"
  }
}
```

### 环境变量配置

项目支持通过环境变量进行配置，优先级高于配置文件：

```bash
# 设置最大获取数量
export DOUYIN_MAX_ITEMS=20

# 设置请求间隔
export DOUYIN_REQUEST_INTERVAL=2.0

# 设置输出格式
export DOUYIN_OUTPUT_FORMAT=csv

# 设置日志级别
export DOUYIN_LOG_LEVEL=DEBUG
```

## ❓ 常见问题

### Q1: 程序运行时报网络错误怎么办？

**A**: 请检查以下几点：
- 确保网络连接正常
- 检查防火墙设置
- 尝试使用代理服务器
- 调整请求间隔时间
- 确认Cookie配置是否正确

### Q2: 如何避免被反爬虫机制检测？

**A**: 建议采取以下措施：
- 增加请求间隔时间 (`-i` 参数)
- 减少获取数量 (`-m` 参数)
- 使用随机 User-Agent
- 启用代理轮换
- 限制并发请求数量
- 定期更新Cookie

### Q3: 数据输出格式有哪些？

**A**: 目前支持以下格式：
- **JSON**: 结构化数据，便于程序处理
- **CSV**: 表格格式，便于 Excel 打开
- **TXT**: 纯文本格式，便于阅读
- **Markdown**: 富文本格式，便于文档化

### Q4: 如何获取抖音Cookie？

**A**: 获取Cookie的步骤：
1. 打开浏览器，访问抖音网站
2. 登录你的抖音账号
3. 按F12打开开发者工具
4. 切换到Network标签页
5. 刷新页面，找到任意请求
6. 在请求头中找到Cookie字段并复制完整值
7. 粘贴到 `environment.py` 文件的 `DOUYIN_COOKIE` 变量中

### Q5: 什么是试运行模式？

**A**: 试运行模式（`--dry-run`）的作用：
- 检查配置文件是否正确加载
- 验证命令行参数是否有效
- 显示当前运行配置信息
- 不实际执行爬取操作
- 适用于配置验证和故障排查

## 📝 更新日志

### v1.2.0 (2025-08-17)
- 🎉 重大功能更新
- ✨ 新增智能视频下载功能
- ✨ 实现防盗链绕过技术
- ✨ 添加文件存在检查，避免重复下载
- ✨ 支持多线程并发下载
- ✨ 优化数据输出格式，移除冗余字段
- 🐛 修复缓存系统兼容性问题
- 🐛 修复数据模型序列化问题
- ⚡ 大幅提升下载性能和稳定性
- 📝 完善开发文档和使用指南

### v1.0.0 (2025-01-15)
- 🎉 初始版本发布
- ✨ 基础爬虫功能
- ✨ 模块化架构设计
- ✨ 支持多种输出格式 (JSON/CSV/TXT/Markdown)
- ✨ 添加性能监控和统计功能
- ✨ 实现智能缓存机制
- ✨ 完善错误处理和重试机制
- ✨ 配置管理系统
- ✨ 日志记录功能
- ✨ 命令行参数支持
- 📚 完善文档和示例

## 📄 许可证

本项目采用 [Apache License 2.0](https://opensource.org/licenses/Apache-2.0) 许可证。

## 📞 联系我

- **项目主页**: [https://github.com/MingTechPro/pyhton_douyin_hot.git](https://github.com/MingTechPro/Pyhton_douyin_hot.git)
- **问题反馈**: [https://github.com/MingTechPro/pyhton_douyin_hot/issues](https://github.com/MingTechPro/pyhton_douyin_hot/issues)
- **邮箱**: chenpeiming52001@163.com

## 🙏 致谢

感谢所有为这个项目做出贡献的开发者！

---

⭐ 如果这个项目对你有帮助，请给我们一个星标！
