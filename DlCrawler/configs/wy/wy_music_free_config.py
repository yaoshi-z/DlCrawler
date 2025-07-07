# 0801 wy_music_free_config.py

CUSTOM_SETTINGS = {
        #  请求配置
        'CONCURRENT_REQUESTS': 1,
        'DOWNLOAD_DELAY': 3,
        #  MongoDB数据库配置
        'MONGODB_CONNECTION_STRING' : "mongodb://localhost:27017/",
        "MONGODB_DATABASE": "wy",         
        "MONGODB_COLLECTION": "music_free",  
       
        # 用户代理
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
       
        # Scrapy管道配置
        'ITEM_PIPELINES': {
            'DlCrawler.pipelines.MongoDBPipeline': 300,
            'DlCrawler.pipelines.CustomExporterPipeline': 900

        },
        # 🔺以上配置非必要不修改

        # 🔻以下配置根据实际需求修改
        'TEMPLATE_NO': '0801', # 模版编号
        'EXPORT_FILE_FORMAT': "csv", # 导出文件格式

        'MAXCOUNT': 2000 , # 歌曲ID最大获取数量
        'IS_DOWNLOAD_MUSIC': True # 是否下载歌曲
    }


