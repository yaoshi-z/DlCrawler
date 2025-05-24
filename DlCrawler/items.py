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
    # 电影名称（必填）
    title = scrapy.Field()
    
    # 电影简介（可选）
    intro = scrapy.Field()
    
    # 评分信息（可选）
    rating = scrapy.Field()
    
    # 评价人数（可选）
    votes = scrapy.Field()
