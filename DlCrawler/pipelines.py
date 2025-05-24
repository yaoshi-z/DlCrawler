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
    def __init__(self,connection_string,database,collection):
        self.connection_string = connection_string
        self.database = database
        self.collection = collection
    
    @classmethod
    def from_crawler(cls,crawler):
        return cls(
            connection_string=crawler.settings.get('MONGODB_CONNECTION_STRING'),
            database=crawler.settings.get('MONGODB_DATABASE'),
            collection=crawler.settings.get('MONGODB_COLLECTION')
        )
    
    def open_spider(self,spider):
        self.client = pymongo.MongoClient(self.connection_string)
        self.db = self.client[self.database]
    
    def process_item(self,item,spider):
        collection = self.collection
        self.db[collection].insert_one(dict(item))
        return item
    def close_spider(self,spider):
        self.client.close()