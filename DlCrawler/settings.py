import datetime
import pathlib

BOT_NAME = "DlCrawler"

SPIDER_MODULES = ["DlCrawler.spiders.toscape",
                  "DlCrawler.spiders.douban",
                  "DlCrawler.spiders.baidu",
]
NEWSPIDER_MODULE = "DlCrawler.spiders"#生成新爬虫的默认路径

ADDONS = {}

# Obey robots.txt rules
ROBOTSTXT_OBEY = False


# TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"

#  MONGODB数据库地址
MONGODB_CONNECTION_STRING = "mongodb://localhost:27017/"

# 日志配置
# logs_dir = pathlib.Path(__file__).parent / "logs"
# logs_dir.mkdir(parents=True, exist_ok=True)  # 确保日志目录存在
# LOG_ENABLED = True #
# LOG_STDOUT = True 
# LOG_FILE = logs_dir / f"Log_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
# LOG_LEVEL = "DEBUG"
# LOG_ENCODING = "utf-8"
# LOG_FORMAT = '%(asctime)s [%(name)s] %(levelname)s: %(message)s'
# LOG_DATEFORMAT = '%Y-%m-%d %H:%M:%S'

FEED_EXPORT_ENCODING = "utf-8"
