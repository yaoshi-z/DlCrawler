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
                  "DlCrawler.spiders.douban"
]
NEWSPIDER_MODULE = "DlCrawler.spiders"#生成新爬虫的默认路径

ADDONS = {}

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

#itempipelines设置及数据库设置
ITEM_PIPELINES = {
    "DlCrawler.pipelines.TextPipeline": None,
    "DlCrawler.pipelines.MongoDBPipeline": 400,
}
MONGODB_CONNECTION_STRING = "mongodb://localhost:27017/"
MONGODB_DATABASE = "douban"
MONGODB_COLLECTION = "movie_chart"


# Set settings whose default value is deprecated to a future-proof value
FEED_EXPORT_ENCODING = "utf-8"
