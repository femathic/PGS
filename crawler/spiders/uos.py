import os
import json

import scrapy
from datetime import datetime
from urllib.parse import urlparse

from .thread import worker
from .utils import save_json



class Sterling(scrapy.Spider):
    """
        Create a spider class for University of Sterling
    """
    name = 'uos'
    static_url = 'https://www.stir.ac.uk/research/hub/person/'


    def start_requests(self):
        # Send request to static_url to download website content
        yield scrapy.Request(self.static_url, self.parse)


    def parse(self, response):
        # format response data
        try:
            result_urls = response.xpath('//*[@id="content"]/section[2]/div/div/div[1]/div/div/a/@href').getall()
            next_page = response.xpath('//*[@id="content"]/section[3]/div/div/div/ul/li[last()]/a/@href').get()

            for href in result_urls:
                yield scrapy.Request(response.urljoin(href), callback=self.extract)
        except Exception as e:
            print(e)

        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield response.follow(next_page, callback=self.parse)

    def extract(self, response):
        date = datetime.now().strftime("%B %d %Y")

        top = response.xpath('//*[@id="content"]/section[1]/div')

        name = top.css('div h1.u-heritage-green::text').get()
        id_ = '-'.join(name.lower().split(' '))
        job = top.css('div p.role span::text').get()
        address = top.css('div p.department').xpath('//span/following-sibling::span/text()').get()
        department = top.css('div p.department span a::text').get().strip()
        url = response.url
        phone = ''
        email = ''

        mid = response.xpath('//*[@id="content"]/section[2]/div/div')
        if mid:
            try:
                email = mid.css('div.c-facts ul li a::text').getall()[0]
                phone = mid.css('div.c-facts ul li a::text').getall()[1]
            except Exception as e:
                print('No email or phone number')

        try:
            bio = response.xpath('//*[@id="aboutme"]/div/p[1]/text()').get()[:250].rstrip() + '...'
        except Exception as e:
            bio = ''
            print('No personal profile (bio)')
        img = response.urljoin(top.css('div.small-4 img::attr(src)').get()) \
              if top.css('div.small-4 img::attr(src)').get() else ""

        bottom = response.xpath('//*[@id="content"]/section[4]/div')
        courses_taught = []
        expertise = []
        try:
            tabs = bottom.css('div.cell ul')
            courses_taught = tabs[0].css('li a::text').getall()
            expertise = tabs[1].css('li a::text').getall()
        except Exception as e:
            pass

        data = [{
            "id": id_,
            "name": name,
            "job": job,
            "school": "University of Sterling",
            "department": department,
            "bio": bio,
            "image": img,
            "email": email,
            "url": url,
            "address": address,
            "phone": phone,
            "expertise": expertise,
            "courses_taught": courses_taught,
            "date_modified": date
        }]

        worker(save_json(data))


    def closed(self, reason):
        parsed_uri = urlparse(self.static_url)
        print('closing...', parsed_uri)
