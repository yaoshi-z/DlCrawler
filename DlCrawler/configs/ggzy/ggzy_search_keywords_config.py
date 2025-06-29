# 7001 ggzy_search_keywords_config.py


from scrapy_playwright.page import PageMethod

CUSTOM_SETTINGS = {
        #  请求配置
        'CONCURRENT_REQUESTS': 1,
        'DOWNLOAD_DELAY': 3,

        #  MongoDB数据库配置
        'MONGODB_CONNECTION_STRING' : "mongodb://localhost:27017/", 
        "MONGODB_DATABASE": "ggzy",         
        "MONGODB_COLLECTION": "search_keywords", 

        # 下载处理器配置
        'DOWNLOAD_HANDLERS':  {
        "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler"
        },
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",

        # Playwright基础配置
        "PLAYWRIGHT_MAX_CONTEXTS":1, # 最大上下文数,默认1
        "PLAYWRIGHT_PERSISTENT_CONTEXT": True, # 持久化上下文,默认True
        "PLAYWRIGHT_MAX_PAGES_PER_CONTEXT":6,  # 单上下文最多5个标签页
        'PLAYWRIGHT_BROWSER_TYPE': "chromium", # 浏览器类型,默认chromium

        # Playwright浏览器级启动参数
        'PLAYWRIGHT_LAUNCH_OPTIONS':  {
            "headless": False,  # 关闭无头模式,显示浏览器窗口
            "args": ["--window-size=1920,1080"],  # 设置浏览器窗口大小
            "slow_mo": 1000,    # 将每个操作放慢1秒方便观察
            "devtools": False    # 自动打开开发者工具面板
        },
        'PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT': 60_000, # 设置超时时间,默认60s

        # Playwright上下文级参数
        'PLAYWRIGHT_CONTEXT_ARGS': {
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "extra_http_headers": {
             # 依据域名设置合适的浏览器Referer头   
            "Referer": "https://www.ggzy.gov.cn", 
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
            "Sec-Ch-Ua": '"Chromium";v="136", "Google Chrome";v="136", "Not;A=Brand";v="24"',
            "Sec-Ch-Ua-Mobile": "?0"
         },
            # 资源拦截配置, 依网站环境而定
            "block_patterns": [
                "*://*.doubleclick.net/*",
                "*://*.googleadservices.com/*",
                "*://*.cnzz.com/*",
                "*://*.baidu.com/*tongji*",
                "*.jpg", 
                "*.png"
         ],
            "viewport": {"width": 1920, "height": 1080},
          "playwright_page_methods": [] # page级参数默认为空, 由爬虫文件进行设置
        },

        # 中间件配置
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy.downloadermiddlewares.retry.RetryMiddleware': 90,
        },

        # Scrapy管道配置
        'ITEM_PIPELINES': {
            'DlCrawler.pipelines.AsyncMongoDBPipeline': 300,
            'DlCrawler.pipelines.CustomExporterPipeline': 900

        },

        # 🔺以上配置为开发级参数, 非必要不修改
        # 🔻以下配置为用户级参数, 根据实际需求修改
           
        'EXPORT_FILE_FORMAT': "csv",# 导出文件格式,默认csv, 支持json,csv
        'KEYWORDS': "河南", # 关键词参数, 由实际需求填写
        'MAXCOUNT': 80,  # 最大获取数量
        # 开始/结束日期的配置必须是有效的可用日期,成对填写. 否则报错,采集终止
        # 格式为: YYYY-MM-DD, 若全部为空,则按网站默认"近3天"时间段内爬取
        'START_DATE':'2025-06-17', # 开始日期
        'END_DATE':'2025-06-17' # 结束日期
    }


