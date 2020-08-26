import scrapy


class Crawler(scrapy.Spider):
    name = ""
    static_url = ""
    search_result_urls = ""

    def __init__(self, **kwargs):
        super(Crawler, self).__init__(**kwargs)
