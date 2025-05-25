# Name: 豆瓣网电影排行榜爬虫
# Description: 由豆瓣网电影排行榜Url进入，获取页面所有电影URL，逐个进入详情页并获取详细信息

import scrapy
from DlCrawler.items import DoubanMovieItem
import re
import time

class DoubanMovieSpider(scrapy.Spider):
    name = "douban_movie_chart"
    allowed_domains = ["douban.com"]
    start_urls = ["https://movie.douban.com/chart"]

    def start_requests(self):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }
        for url in self.start_urls:
            yield scrapy.Request(url=url, headers=headers)
    def parse(self, response):

        # 临时调试代码
        # with open("temp_files/douban_movie_chart.html", "w", encoding="utf-8") as f:
        #     f.write(response.text)

         # 提取所有电影条目的Url
        movies = response.css("tr.item")
        movie_links = []
        for movie in movies:
            movie_link = movie.css("a::attr(href)").get()
            movie_links.append(movie_link)

        
        

        for link in movie_links:
            yield scrapy.Request(link, 
                                 callback=self.parse_movie_detail,
                                 headers={
                                     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
                                 })
            
    def parse_movie_detail(self, response):

        # 临时调试代码
        # with open("temp_files/douban_movie_detail.html", "w", encoding="utf-8") as f:
        #     f.write(response.text)

        item = DoubanMovieItem()
        
        # 基础信息
        item['url'] = response.url
        item['title'] = response.css('h1 span[property="v:itemreviewed"]::text').get()
        
        # 主要演职人员
        item['director'] = response.xpath('//span[contains(text(), "导演")]/following-sibling::span/a/text()').getall()
        item['screenwriter'] = response.xpath('//span[contains(text(), "编剧")]/following-sibling::span/a/text()').getall()
        item['actors'] = response.css('a[rel="v:starring"]::text').getall()
        
        # 电影资料
        item['genres'] = response.css('span[property="v:genre"]::text').getall()
        item['country'] = response.xpath('//span[contains(text(), "制片国家/地区")]/following-sibling::text()').get().strip()
        item['language'] = response.xpath('//span[contains(text(), "语言")]/following-sibling::text()').get().strip()
        
        # 上映信息
        item['release_dates'] = response.css('span[property="v:initialReleaseDate"]::text').getall()
        item['runtime'] = response.css('span[property="v:runtime"]::attr(content)').get()
        
        # 其他信息
        item['aka'] = response.xpath('//span[contains(text(), "又名")]/following-sibling::text()').get().split(' / ')
        
        # IMDb及豆瓣评分
        item['imdb'] = response.xpath('//span[contains(text(), "IMDb:")]/following-sibling::text()').get().strip()
        item['douban_rating'] = response.css('strong.ll.rating_num::text').get() or '暂无评分'
        
        
        # 豆瓣评分分布
        item['star_distribution'] = None
        if item['douban_rating'] != '暂无评分':
            ratings = response.css('div.ratings-on-weight > div.item')
            item['star_distribution'] = {
                '5': ratings[0].css('span.rating_per::text').get(),
                '4': ratings[1].css('span.rating_per::text').get(),
                '3': ratings[2].css('span.rating_per::text').get(),
                '2': ratings[3].css('span.rating_per::text').get(),
                '1': ratings[4].css('span.rating_per::text').get()
            }
        
        # 剧情简介
        item['synopsis'] = response.css('span[property="v:summary"]::text').getall()
        item['synopsis'] = ''.join([text.strip() for text in item['synopsis']])
        
        yield item
