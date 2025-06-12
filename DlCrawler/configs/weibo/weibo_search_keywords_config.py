# weibo_search_keywords_config.py


CUSTOM_SETTINGS = {
        #  请求配置
        'CONCURRENT_REQUESTS': 1,
        'DOWNLOAD_DELAY': 5,
        #  MongoDB数据库配置
        'MONGODB_CONNECTION_STRING' : "mongodb://localhost:27017/",
        "MONGODB_DATABASE": "weibo",         
        "MONGODB_COLLECTION": "search_keywords",  
        # 下载处理器配置
        'DOWNLOAD_HANDLERS':  {
        "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler"
        },
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",

        # Playwright配置
        "PLAYWRIGHT_PERSIST_CONTEXT": True,
        'PLAYWRIGHT_BROWSER_TYPE': "chromium",
        'PLAYWRIGHT_LAUNCH_OPTIONS':  {
            "headless": False,  # 关闭无头模式,显示浏览器窗口
            "args": ["--window-size=1920,1080"],  # 设置浏览器窗口大小
            "slow_mo": 1000,    # 将每个操作放慢1秒方便观察
            "devtools": False    # 自动打开开发者工具面板
        },
        'PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT': 60_000,
        'PLAYWRIGHT_CONTEXT_ARGS': {
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "extra_http_headers": {
            "Referer": "https://s.weibo.com/",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
         },
            "viewport": {"width": 1920, "height": 1080}
        },
        # Playwright中间件配置
        'DOWNLOADER_MIDDLEWARES': {},
        # Scrapy管道配置

        'ITEM_PIPELINES': {
            'DlCrawler.pipelines.AsyncMongoDBPipeline': 300
        }
    }

KEYWORDS = "胖东来"  # 关键字列表
MAXSCOUNT = 50 # 最大爬取数量
