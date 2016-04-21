from scrapy import Spider, Item, Field

class Post(Item):
    title = Field()

class BlogSpider(Spider):
    name, start_urls = 'geosmart', ['http://geosmart.github.io/']

    def parse(self, response):
        return [Post(title=e.extract()) for e in response.css("header")]

#run
# scrapy runspider myspider.py