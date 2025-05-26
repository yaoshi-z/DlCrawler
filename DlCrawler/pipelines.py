from scrapy.exceptions import DropItem
import pymongo 
from motor.motor_asyncio import AsyncIOMotorClient
from twisted.internet.defer import Deferred
        
# class MongoDBPipeline(object):
#     def __init__(self,connection_string):
#         self.connection_string = connection_string
    
#     @classmethod
#     def from_crawler(cls,crawler):
#         return cls(
#             connection_string=crawler.settings.get('MONGODB_CONNECTION_STRING')
#         )
    
#     def open_spider(self,spider):
#         self.database = spider.settings.get('MONGODB_DATABASE')
#         self.collection = spider.settings.get('MONGODB_COLLECTION')
#         self.client = pymongo.MongoClient(self.connection_string)
#         self.db = self.client[self.database]
    
#     def process_item(self,item,spider):
#         collection = self.collection
#         self.db[collection].insert_one(dict(item))
#         return item
#     def close_spider(self,spider):
#         self.client.close()

class MongoDBPipeline:
    def __init__(self):
        self.connection_string  = None
        self.database = None
        self.collection = None
        self.client = None

    def open_spider(self, spider):
        # 从爬虫设置中获取MongoDB连接字符串、数据库名和集合名. 
        # 注意open_spider方法不能使用异步方法,因为可能无法正确加载mongoDB参数
        self.connection_string = spider.settings.get('MONGODB_CONNECTION_STRING')
        self.database = spider.settings.get('MONGODB_DATABASE')
        self.collection = spider.settings.get('MONGODB_COLLECTION')
        self.client = AsyncIOMotorClient(self.connection_string)
        self.db = self.client[self.database]

    async def process_item(self, item, spider):
        
        if not self.collection:
            raise DropItem("MongoDB集合未初始化")
        
        await self.db[self.collection].insert_one(dict(item))
        print("==================》Item已正确存储到MongoDB")
        return item