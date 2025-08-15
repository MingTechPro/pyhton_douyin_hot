# 抖音热点爬虫项目

一个用于爬取抖音热点数据的Python项目，支持数据采集、处理和格式化输出。

## 功能特性

- 🔥 抖音热点数据爬取
- 📊 数据格式化和处理
- 🚀 高性能爬虫架构
- 📝 详细的日志记录
- ⚙️ 灵活的配置管理

## 项目结构

```
Pyhton_douyin_hot/
├── src/
│   ├── config/          # 配置管理
│   ├── core/            # 核心模块
│   ├── spider/          # 爬虫模块
│   └── utils/           # 工具模块
├── main.py              # 主程序入口
├── pyproject.toml       # 项目配置
└── README.md           # 项目说明
```

## 安装依赖

```bash
pip install -e .
```

## 使用方法

```bash
python main.py
```

## 配置说明

项目使用 `pyproject.toml` 进行依赖管理，主要配置文件包括：

- `config.json`: 爬虫配置
- `environment.py`: 环境变量配置

## 开发环境

- Python 3.8+
- 支持Windows/Linux/macOS

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！
