import datetime
import pathlib
import logging
from scrapy.utils.log import configure_logging

BOT_NAME = "DlCrawler"

SPIDER_MODULES = ["DlCrawler.spiders.toscape",
                  "DlCrawler.spiders.douban",
                  "DlCrawler.spiders.baidu",
                  "DlCrawler.spiders.weibo",
                  "DlCrawler.spiders.boss",
                  "DlCrawler.spiders.taobao",
                  "DlCrawler.spiders.ggzy",
                  "DlCrawler.spiders.wy",
]
NEWSPIDER_MODULE = "DlCrawler.spiders"#生成新爬虫的默认路径

ADDONS = {}

# Obey robots.txt rules
ROBOTSTXT_OBEY = False


# '''日志配置,实现终端和文件双重输出'''
# logs_dir = pathlib.Path(__file__).parent / "logs"
# logs_dir.mkdir(parents=True, exist_ok=True)  # 确保日志目录存在
# configure_logging({
#     'LOG_FORMAT': '%(asctime)s [%(name)s] %(levelname)s: %(message)s',
#     'LOG_DATEFORMAT': '%Y-%m-%d %H:%M:%S',
#     'LOG_LEVEL': 'DEBUG'
# })

# # 获取根日志记录器
# logger = logging.getLogger()

# # 创建一个文件日志处理器
# file_handler = logging.FileHandler(logs_dir / f"Log_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt", encoding='utf-8')
# file_formatter = logging.Formatter('%(asctime)s [%(name)s] %(levelname)s: %(message)s')
# file_handler.setFormatter(file_formatter)
# logger.addHandler(file_handler)

# # 创建一个终端输出处理器
# console_handler = logging.StreamHandler()
# console_formatter = logging.Formatter('%(asctime)s [%(name)s] %(levelname)s: %(message)s')
# console_handler.setFormatter(console_formatter)
# logger.addHandler(console_handler)

# FEED_EXPORT_ENCODING = "utf-8"


'''自定义日志配置 - 分离终端与文件'''
LOG_ENABLED = False # 禁用scrapy日志
logs_dir = pathlib.Path(__file__).parent / "logs"
logs_dir.mkdir(parents=True, exist_ok=True)

# 获取根日志记录器
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)  

# 创建文件处理器（保留DEBUG）
file_handler = logging.FileHandler(
    logs_dir / f"Log_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
    encoding='utf-8'
)
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter('%(asctime)s [%(name)s] %(levelname)s: %(message)s')
file_handler.setFormatter(file_formatter)

# 创建终端处理器（仅显示INFO+）
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.addFilter(lambda record: record.levelno >= logging.INFO)
console_formatter = logging.Formatter('%(asctime)s [%(name)s] %(levelname)s: %(message)s')
console_handler.setFormatter(console_formatter)

# 添加处理器
logger.addHandler(file_handler)
logger.addHandler(console_handler)

FEED_EXPORT_ENCODING = "utf-8"
