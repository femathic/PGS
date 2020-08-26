import os
import json

import scrapy
from datetime import datetime
from urllib.parse import urlparse

from .thread import worker
from .utils import save_json


class AngliaRuskin(scrapy.Spider):
    """
        Create a spider class for Anglia Ruskin University
    """
    name = 'aru'
    static_url = 'https://aru.ac.uk/about-us/find-an-expert'
    # next_page = ''

    def start_requests(self):
        # Send request to static_url to download website content
        yield scrapy.Request(self.static_url, self.parse)


    def parse(self, response):
        # format response data
        try:
            result_urls = response.xpath('/html/body/section[5]/ul/li/div/h3/a/@href').getall()
            next_page = response.xpath('/html/body/div[2]/section/a/@href').get()

            for href in result_urls:
                yield scrapy.Request(response.urljoin(href), callback=self.extract)
        except Exception as e:
            print(e)
            pass

        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield response.follow(next_page, callback=self.parse)


    def extract(self, response):
        date = datetime.now().strftime("%B %d %Y")

        name = response.css('div.staff-profile h1::text').get()
        id_ = '-'.join(name.strip().lower().split(' '))
        phone = 'N/A'
        department = ''
        address = ''
        expertise = []
        courses_taught = []

        info = response.css('div.staff-profile p.staff-profile__summary')
        for dt in info:
            try:
                if dt.css('p span::text').get() == 'School:':
                    department = dt.css('p a::text').get()
                if dt.css('p span::text').get() == 'Location:':
                    address = dt.css('p a::text').get()
                if dt.css('p span::text').get() == 'Areas of Expertise:':
                    expertise = dt.css('p a::text').get().split(', ')
                
            except Exception as e:
                pass

        sections = response.css('div.rte h4')
        for s in sections:
            if s.css('h4::text').get() == 'Teaching':
                courses_taught = [s.xpath('//ul/following-sibling::ul/li/text()').get()]

        job = response.css('div.staff-profile h2.staff-profile__role::text').get().strip()
        email = response.css('div.rte p a::text').get()
        url = response.url

        try:
            bio = response.css('div.rte p.intro::text').get()[:250].rstrip() + '...'
        except Exception as e:
            bio = ''
            print('No personal profile (bio)')
        img = response.urljoin(response.css('div.image--float-right img::attr(src)').get()) \
              if response.css('div.image--float-right img::attr(src)').get() else ""

        data = [{
            "id": id_,
            "name": name,
            "job": job,
            "school": "Anglia Ruskin University",
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