from scrapy.exceptions import DropItem
import pymongo 

class TextPipeline(object):
    def __init__(self):
        self.limit = 50
    def process_item(self, item, spider):
        if item.get('text'):
            if len(item['text']) > self.limit:
                item['text'] = item['text'][:self.limit].rstrip() + '...'
            return item
        else:
            raise DropItem(f"Missing text in {item}")
        
class MongoDBPipeline(object):
    def __init__(self,connection_string):
        self.connection_string = connection_string
    
    @classmethod
    def from_crawler(cls,crawler):
        return cls(
            connection_string=crawler.settings.get('MONGODB_CONNECTION_STRING')
        )
    
    def open_spider(self,spider):
        self.database = spider.settings.get('MONGODB_DATABASE')
        self.collection = spider.settings.get('MONGODB_COLLECTION')
        self.client = pymongo.MongoClient(self.connection_string)
        self.db = self.client[self.database]
    
    def process_item(self,item,spider):
        collection = self.collection
        self.db[collection].insert_one(dict(item))
        return item
    def close_spider(self,spider):
        self.client.close()