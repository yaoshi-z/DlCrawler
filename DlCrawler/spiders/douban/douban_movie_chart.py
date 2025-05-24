import scrapy
from DlCrawler.items import DoubanMovieItem
import re


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

        # with open("douban_movie_chart.html", "w", encoding="utf-8") as f:
        #     f.write(response.text)

         # 提取所有电影条目
        movies = response.css("tr.item")
        
        for movie in movies:
            item = DoubanMovieItem()
            
            # 电影名称（必填）
            title = movie.css("a.nbg::attr(title)").get()
            if not title:  # 跳过无名称的条目
                continue
            item["title"] = title.strip()
            
            # 电影简介（可选）
            intro = movie.css("div.pl2 p::text").get()
            item["intro"] = intro.strip() if intro else ""
            
            # 评分信息（可选）
            rating = movie.css(".star .rating_nums::text").get()
            item["rating"] = rating.strip() if rating else ""
            
            # 评价人数（可选）
            votes_text = movie.css(".star .pl::text").get()
            
            if votes_text:  
                # 匹配中文括号和"人评价"格式
                votes_match = re.search(r'\((\d+)人评价\)', votes_text)
                if votes_match:
                    item["votes"] = votes_match.group(1)
                else:
                    # 处理其他情况（如"暂无评分"）
                    item["votes"] = ""
                
            yield item

