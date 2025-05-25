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
     # Basic info
    url = scrapy.Field()
    title = scrapy.Field()
    
    # Crew information
    director = scrapy.Field()
    screenwriter = scrapy.Field()
    actors = scrapy.Field()
    
    # Metadata
    genres = scrapy.Field()
    country = scrapy.Field()
    language = scrapy.Field()
    
    # Release info
    release_dates = scrapy.Field()
    runtime = scrapy.Field()
    
    # Alternate info
    aka = scrapy.Field()
    imdb = scrapy.Field()
    
    # Ratings
    douban_rating = scrapy.Field()
    star_distribution = scrapy.Field()
    
    # Synopsis
    synopsis = scrapy.Field()
