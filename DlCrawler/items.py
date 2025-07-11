# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

# 编号0101 百度贴吧指定吧主题帖爬虫模板
class BaiduTiebaTopicItem(scrapy.Item):
    batch_id = scrapy.Field()      # 批次ID
    bar_name = scrapy.Field()      # 吧名
    title = scrapy.Field()         # 帖子标题  
    title_url = scrapy.Field()     # 帖子链接
    content = scrapy.Field()       # 帖子内容
    author = scrapy.Field()        # 发帖人
    reply_count = scrapy.Field()   # 回复数
    page_num = scrapy.Field()       # 页码

# 编号0102 百度搜索关键词爬虫模板
class BaiduSearchKeywordsItem(scrapy.Item):
    keyword = scrapy.Field()
    batch_id = scrapy.Field()
    title = scrapy.Field()
    bd_url = scrapy.Field()
    raw_url = scrapy.Field()
    is_ad = scrapy.Field()  
    summary = scrapy.Field()

# 编号0103 百度图片关键词爬虫模板
class BaiduImgKeywordsItem(scrapy.Item):
    keyword = scrapy.Field()
    batch_id = scrapy.Field()
    title = scrapy.Field()
    bd_url = scrapy.Field()
    raw_url = scrapy.Field()
    is_ad = scrapy.Field()

# 编号0104 百度贴吧帖子详情爬虫模板
class BaiduTiebaDetailsItem(scrapy.Item):
    batch_id = scrapy.Field()
    bar_name = scrapy.Field()
    title = scrapy.Field()
    title_url = scrapy.Field()
    floor = scrapy.Field()
    author = scrapy.Field()
    bar_level = scrapy.Field()
    main_comment_id = scrapy.Field()
    main_comment = scrapy.Field()
    main_comment_time = scrapy.Field()
    device_source = scrapy.Field()
    sub_comments = scrapy.Field()


# 编号0201 豆瓣电影榜单爬虫模板   
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

#编号0301 ToScape名言模板
class DlcrawlerItem(scrapy.Item):
    text = scrapy.Field() 
    author = scrapy.Field()
    tags = scrapy.Field()



# 编号0401 微博首页爬虫模板
class WeiboHomepageItem(scrapy.Item):
    user_name = scrapy.Field()     # 用户名
    verified_type = scrapy.Field() # 认证类型（如：超话主持人）
    content = scrapy.Field()       # 正文内容
    content_link = scrapy.Field()  # 正文链接
    post_time = scrapy.Field()     # 发布时间
    reposts = scrapy.Field()       # 转发数
    comments = scrapy.Field()      # 评论数
    likes = scrapy.Field()         # 点赞数

# 编号0402 微博搜索关键词爬虫模板
class WeiboSearchKeywordsItem(scrapy.Item):
    keyword = scrapy.Field()       # 关键词
    mid  = scrapy.Field()          # MID
    user_name = scrapy.Field()     # 用户名
    verified_type = scrapy.Field() # 认证类型（如：超话主持人）
    content = scrapy.Field()       # 正文内容
    content_link = scrapy.Field()  # 正文链接
    post_time = scrapy.Field()     # 发布时间
    device_source = scrapy.Field() # 设备来源
    reposts = scrapy.Field()       # 转发数
    comments = scrapy.Field()      # 评论数
    likes = scrapy.Field()         # 点赞数

# 编号0501 Boss直聘指定职位_列表信息爬虫模板
class BossJobsListItem(scrapy.Item):
    batch_id = scrapy.Field()
    city = scrapy.Field()
    position_name = scrapy.Field()
    position_url = scrapy.Field()
    salary = scrapy.Field()
    experience = scrapy.Field()
    education = scrapy.Field()
    company_name = scrapy.Field()
    company_url = scrapy.Field()
    work_area = scrapy.Field()
    
# 编号0601 淘宝_搜索_关键字商品信息爬虫模板
class TaobaoSearchKeywordsItem(scrapy.Item):
    batch_id = scrapy.Field()
    keywords = scrapy.Field()
    shop_name = scrapy.Field()
    shop_url = scrapy.Field()
    location = scrapy.Field()
    product_id = scrapy.Field()
    product_title = scrapy.Field()
    product_price = scrapy.Field()
    product_url = scrapy.Field()
    product_img = scrapy.Field()
    paid_count = scrapy.Field()
    page_num = scrapy.Field()
   
# 编号0701：全国公共资源_搜索_关键字公示信息爬虫模板
class GgzySearchKeywordsItem(scrapy.Item):
    batch_id = scrapy.Field()
    keywords = scrapy.Field()
    title = scrapy.Field()
    title_url = scrapy.Field()
    post_time = scrapy.Field()
    province = scrapy.Field()
    source_platform = scrapy.Field()
    business_category = scrapy.Field()
    announcement_type = scrapy.Field()
    industry = scrapy.Field()
    
# 编号0801: 网易云音乐免费歌单模板
class WyMusicFreeItem(scrapy.Item):
    batch_id = scrapy.Field()
    playlist_id = scrapy.Field()
    playlist_title = scrapy.Field()
    song_id = scrapy.Field()
    song_title = scrapy.Field()
    song_url = scrapy.Field()
