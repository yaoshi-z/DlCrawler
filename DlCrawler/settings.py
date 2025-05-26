# Scrapy settings for DlCrawler project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = "DlCrawler"

SPIDER_MODULES = ["DlCrawler.spiders.toscape",
                  "DlCrawler.spiders.douban",
                  "DlCrawler.spiders.baidu",
]
NEWSPIDER_MODULE = "DlCrawler.spiders"#生成新爬虫的默认路径

ADDONS = {}

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

#itempipelines设置及数据库设置
# ITEM_PIPELINES = {
#     "DlCrawler.pipelines.TextPipeline": None,
#     "DlCrawler.pipelines.MongoDBPipeline": 400,
# }
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"

#  MONGODB数据库地址
MONGODB_CONNECTION_STRING = "mongodb://localhost:27017/"
# MONGODB_DATABASE = "douban"
# MONGODB_COLLECTION = "movie_chart"

# DOWNLOAD_HANDLERS = {
#     "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
#     "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
# }
# TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"

# PLAYWRIGHT_BROWSER_TYPE = "chromium"
# PLAYWRIGHT_LAUNCH_OPTIONS = {
#     "headless": False,  # 关键参数！关闭无头模式显示浏览器窗口
#     "slow_mo": 1000,    # 将每个操作放慢1秒方便观察
#     "devtools": True    # 自动打开开发者工具面板
# }

# DOWNLOADER_MIDDLEWARES = {
#     'scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler': 543,
# }

# Set settings whose default value is deprecated to a future-proof value
FEED_EXPORT_ENCODING = "utf-8"
