# baidu_img_keywords_config.py


from scrapy_playwright.page import PageMethod

CUSTOM_SETTINGS = {
        #  请求配置
        'CONCURRENT_REQUESTS': 1,
        'DOWNLOAD_DELAY': 5,
        #  MongoDB数据库配置
        'MONGODB_CONNECTION_STRING' : "mongodb://localhost:27017/",
        "MONGODB_DATABASE": "baidu",         
        "MONGODB_COLLECTION": "img_keywords", 
        # 下载处理器配置
        'DOWNLOAD_HANDLERS':  {
        "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler"
        },
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",

        # Playwright配置
        "PLAYWRIGHT_PERSISTENT_CONTEXT": True,
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
             # 依据域名设置合适的浏览器Referer头   
            "Referer": "https://image.baidu.com/", 
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
         },
            "viewport": {"width": 1920, "height": 1080},
          "playwright_page_methods": [
        
    ]
        },
        # Playwright中间件配置
        'DOWNLOADER_MIDDLEWARES': {},
        # Scrapy管道配置
        'ITEM_PIPELINES': {
            'DlCrawler.pipelines.AsyncMongoDBPipeline': 300,
            'DlCrawler.pipelines.CustomExporterPipeline': 900

        },
        # 🔺以上配置非必要不修改

        # 🔻以下配置根据实际需求修改
        'EXPORT_FILE_FORMAT': "json",

        # 该模板要求KEYWORDS参数值必须完全匹配贴吧主题名称,否则可能无法正确获取数据!
        # 贴吧主题名称,使用keywords参数名是为了与其他爬虫保持一致性
        'KEYWORDS': "郑州地铁",  
        'MAXCOUNT': 50  # 最大获取数量
    }


