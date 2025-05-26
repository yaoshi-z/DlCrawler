# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class DlcrawlerItem(scrapy.Item):
    #字段声明
    text = scrapy.Field()
    author = scrapy.Field()
    tags = scrapy.Field()
class DoubanMovieItem(scrapy.Item):
    # 电影条目字段声明
    url = scrapy.Field()
    title = scrapy.Field()
    director = scrapy.Field()
    screenwriter = scrapy.Field()
    actors = scrapy.Field()
    genres = scrapy.Field()
    country = scrapy.Field()
    language = scrapy.Field()
    release_dates = scrapy.Field()
    runtime = scrapy.Field()
    aka = scrapy.Field()
    imdb = scrapy.Field()
    douban_rating = scrapy.Field()
    star_distribution = scrapy.Field()
    synopsis = scrapy.Field()

class BaiduTiebaTopicItem(scrapy.Item):
    bar_name = scrapy.Field()      # 吧名
    title = scrapy.Field()         # 帖子标题  
    content = scrapy.Field()       # 帖子内容
    author = scrapy.Field()        # 发帖人
    reply_count = scrapy.Field()   # 回复数