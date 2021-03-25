import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from evansbank.items import Article


class EvansbankSpider(scrapy.Spider):
    name = 'evansbank'
    start_urls = ['https://evansbank.com/about/news-media/']

    def parse(self, response):
        links = response.xpath('//a[@rel="nofollow"]/@href').getall()
        dates = response.xpath('//p[@class="date"]')
        for i, link in enumerate(links):
            yield response.follow(link, self.parse_article, cb_kwargs=dict(date=dates[i].xpath('./text()').get()))

    def parse_article(self, response, date):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//title/text()').get()
        if title:
            title = title.strip()

        content = response.xpath('//article//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
