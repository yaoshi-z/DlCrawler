### **DlCrawler（大龙爬虫）**  
> 基于 Scrapy + Playwright 的模块化爬虫项目，支持多平台公开数据采集  

---

### **项目简介**  
本项目是一个**学习型爬虫框架**，作者**钥匙**旨在通过模块化设计整合爬虫技术知识体系，适用于网站公开数据采集场景。项目遵循合法合规原则，**不强行突破反爬机制、不获取敏感数据、不干扰网站运营**，以模拟人类行为为主,低速安全自动化爬取, 不适用于专业分布式等大型爬虫场景。仅供技术学习与交流。  

- **技术栈**：  
  - **Scrapy**（爬虫框架）  
  - **Scrapy-Playwright**（异步浏览器渲染）  
  - **MongoDB/Pandas**（数据存储与导出）  

- **核心特点**：  
  - 模块化设计：每个模板为独立爬虫，支持快速扩展  
  - 配置驱动：通过 [CUSTOM_SETTINGS](file://d:\mydoc\G04SE\python\projects\021crawler\DlCrawler\configs\baidu\baidu_tieba_topic_config.py#L2-L39) 实现参数化配置  
  - 数据导出：支持 JSON/CSV 格式一键导出  
  - 反爬友好：模拟用户行为与随机延迟，降低封禁风险  

---

### **目录结构**  
```bash
DlCrawler/
├── scrapy.cfg                  # Scrapy配置文件  
├── requirements.txt            # 依赖库列表  
├── README.md                   # 项目说明  
├── 模板列表.csv                # 模板元信息（含字段说明）  
├── DlCrawler/                 # 项目源码目录  
│   ├── items.py                # 数据模型定义  
│   ├── pipelines.py            # 数据处理管道（MongoDB/Pandas导出）  
│   ├── settings.py             # 全局配置 
    └── utils/  			   # 额外的自定义工具包
│   └── spiders/                # 爬虫模板目录  
│       ├── baidu/              # 百度系模板  
│       │   └── baidu_tieba_topic.py  # 贴吧主题帖采集  
│       └── weibo/              # 微博模板  
│           └── weibo_search_keywords.py # 微博关键词搜索  
└── configs/                    # 配置文件目录  
    ├── baidu/  
    └── weibo/  
```

---

### **安装与使用**  
#### **1. 环境要求**  
- Python 3.9+  
- MongoDB（可选，用于存储）  
- Playwright 浏览器依赖：  
  ```bash
  playwright install chromium
  ```

#### **2. 安装依赖**  
```bash
# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

#### **3. 启动爬虫**  
```bash
# 以百度贴吧模板为例
scrapy crawl baidu_tieba_topic
```

#### **4. 自定义配置**  
- 修改对应模板的 `configs/` 目录下的 `*.py` 文件（如 `baidu_tieba_topic_config.py`）  
- 支持字段：  
  - `KEYWORDS`：目标关键词（如贴吧名称）  
  - `MAXPAGE`：最大翻页数  
  - `EXPORT_FILE_FORMAT`：导出格式（json/csv）  

---

### **模板管理**  

模板列表.csv

| 编号 | 模板位置 | 模板名称 | 字段说明 |
|------|----------|----------|----------|
| [1001](file:///D:/mydoc/G04SE/python/projects/021crawler/DlCrawler/spiders/baidu/baidu_tieba_topic.py) | `baidu/baidu_tieba_topic.py` | 百度贴吧指定吧主题帖爬虫模板 | 吧名/主贴标题/内容/作者/回复数 |
| ... | ... | ... | ... |

---

### **分支说明**  
| 分支 | 状态 | 特点 |
|------|------|------|
| `main` | 稳定分支 | 基础框架 + 少量稳定模板 |
| `feat/xxx` | 开发分支 | 持续新增模板，可能存在不稳定功能，暂未同步到github |

---

### **数据导出**  
- **默认路径**：Dlcawler / exports/ 目录  
- **支持格式**：  
  - JSON（默认，保留原始结构）  
  - CSV（兼容 Excel 打开）  
- **配置方式**：  对应模板配置文件的'EXPORT_FILE_FORMAT'参数

---

### **开发规范**  

**1. 字段设计**  

- **设计规范**：`items.py` 新增模板名+Item类，创建必要字段

​	**样例**：

```python
class BaiduTiebaTopicItem(scrapy.Item):
    bar_name = scrapy.Field()      # 吧名
    title = scrapy.Field()         # 帖子标题  
    content = scrapy.Field()       # 帖子内容
    author = scrapy.Field()        # 发帖人
    reply_count = scrapy.Field()   # 回复数
```

#### **2. 模板设计**  
- **命名规范**：`平台_功能.py`（如 baidu_tieba_topic.py）  
- **头部注释**：  
  
  ```python
  """
  - 模板名称
      模板编号: 1001
      模板名称: 百度贴吧指定吧主题帖爬虫模板
  --------------------
  功能：提取指定贴吧的帖子列表信息（标题、内容、作者、回复数等）
  使用：爬取前需在baidu_tieba_topic_config.py中设置推荐的配置参数
  """
  ```
- **类属性**：  
  
  ```python
  class BaiduTiebaTopicSpider(scrapy.Spider):
      name = "baidu_tieba_topic"
      allowed_domains = ["tieba.baidu.com"]
      topic_name = CUSTOM_SETTINGS['KEYWORDS']  # 贴吧主题名称
      encode_topic_name = quote(topic_name)
      start_urls = [f"https://tieba.baidu.com/f?kw={encode_topic_name}&ie=utf-8"]
  
      # 最大翻页数
      max_page = CUSTOM_SETTINGS['MAXPAGE']
      current_page = 1
  
      custom_settings = CUSTOM_SETTINGS
      cookies_dir = pathlib.Path(__file__).parent.parent.parent / "data" / "cookies"
      cookies_dir.mkdir(parents=True, exist_ok=True)  # 自动创建目录
      cookies_file = cookies_dir / f"{name}_cookies.json"
  ```

**3. 配置文件**  

- **命名规范** `DlCralwer/configs/目标网站名/模板名+config.py`

- **示例配置**

  ```python
  # baidu_tieba_topic_config.py
  from scrapy_playwright.page import PageMethod
  
  CUSTOM_SETTINGS = {
          #  请求配置
          
          #  MongoDB数据库配置
        
          # 下载处理器配置
         
          # Playwright配置
         
          # Playwright中间件配置
          
          # 🔺以上配置非必要不修改
  
          # 🔻以下配置根据实际需求修改
          'EXPORT_FILE_FORMAT': "json",
  
          # 该模板要求KEYWORDS参数值必须完全匹配贴吧主题名称,否则可能无法正确获取数据!
          # 贴吧主题名称,使用keywords参数名是为了与其他爬虫保持一致性
          'KEYWORDS': "老天下",  
          'MAXPAGE': 2  # 最大翻页数
      }
  ```

  

#### **4. 其它事项**  

- `pipelines.py,middlewares.py`等全局相关的配置，原则上无需过多修改， 仅需启用/禁用组件即可， 确有需要，可根据实际需求修改。

- **Issue 规范**：  
  - 标题：`[BUG] 模板编号 + 问题描述` 或 `[需求] 模板编号 + 功能建议`  
- **Pull Request**：  
  - 分支选择：`feat` 分支提交新模板，`main` 分支仅合并稳定功能  
  - 代码风格：遵循 PEP8，添加 docstring 注释  

---

### ⚠  **注意事项**  
1. **合法性**：  
   
   - 仅采集网站公开数据，遵守 `robots.txt` 协议  
   - 不得用于非法数据采集或商业用途  
   
2. **反爬策略**：  
   - 模拟用户行为（滚动/随机延迟）  
   - 未使用破解验证码或模拟登录  

3. **数据存储**：  
   - 默认路径：`exports/`（CSV/JSON）  
   - MongoDB 配置：`MONGODB_CONNECTION_STRING`（需本地 MongoDB 服务）  

4. **免责声明**：  
   
   > 本项目仅用于技术学习，使用者需自行承担法律责任。开发者不保证数据准确性，不对因数据采集引发的后果负责。  

---

### **贡献与反馈**  
- **文档完善**：欢迎补充模板说明或修复已知问题  
- **模板扩展**：新增模板时请同步更新 `模板列表.csv`  
- **提交 Issue**：报告 Bug 或提出功能建议  
- **联系作者**：402203271@qq.com

---

### **许可证**  
MIT License  
> 可自由使用/修改/分发，但必须保留版权声明和许可声明  

---

### **常见问题**  
**Q1: 如何查看已导出的数据？**  
A: 数据默认保存在 `exports/` 目录下，文件名格式为 `[spider.name]_[关键词]_时间戳.[json/csv]`  

**Q2: 爬虫被封禁怎么办？**  
A: 项目未突破强反爬机制，若触发验证请调整 [DOWNLOAD_DELAY](file://d:\mydoc\G04SE\python\projects\021crawler\DlCrawler\settings.py#L15-L15) 或切换 IP  

**Q3: 如何调试模板？**  
A: 取消 [parse()](file://d:\mydoc\G04SE\python\projects\021crawler\DlCrawler\DlCrawler\spiders\weibo\weibo_search_keywords.py#L34-L159) 中的调试注释，保存 HTML 到 `debug_files/` 目录  

---

### **结语**  
本项目为个人学习工具集，难免存在疏漏，欢迎提出改进意见！  

> 🚀 学习不息，爬虫不止 —— 以技术驱动数据价值