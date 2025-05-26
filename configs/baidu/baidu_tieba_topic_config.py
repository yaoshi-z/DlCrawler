# baidu_tieba_topic_config.py

CONFIG = {
        'CONCURRENT_REQUESTS': 1,
        'DOWNLOAD_DELAY': 5,
        'MONGODB_CONNECTION_STRING' : "mongodb://localhost:27017/",
        "MONGODB_DATABASE": "baidu",         # 数据库名
        "MONGODB_COLLECTION": "topic_list",  # 集合名
        'DOWNLOAD_HANDLERS':  {
        "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler"
        },

        'PLAYWRIGHT_BROWSER_TYPE': "chromium",
        'PLAYWRIGHT_LAUNCH_OPTIONS':  {
            "headless": False,  # 关键参数！关闭无头模式显示浏览器窗口
            "slow_mo": 1000,    # 将每个操作放慢1秒方便观察
            "devtools": True    # 自动打开开发者工具面板
        },

        'DOWNLOADER_MIDDLEWARES': {
            'scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler': 543,
        },
        'ITEM_PIPELINES': {
            'DlCrawler.pipelines.AsyncMongoDBPipeline': 300
        }
    }

TOPIC_NAME = "郑州地铁"  # 贴吧主题名称
MAXPAGE = 5  # 最大翻页数
