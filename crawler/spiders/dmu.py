import os
import json

import scrapy
from datetime import datetime
from urllib.parse import urlparse

from .thread import worker
from .utils import save_json



class DeMontfort(scrapy.Spider):
    """
        Create a spider class for De Montfort University
    """
    name = 'dmu'
    static_url = 'https://www.dmu.ac.uk/About-DMU/Academic-staff/Full-listing-of-dmu-academic-staff.aspx'
    next_page = ''


    def start_requests(self):
        # Send request to static_url to download website content
        yield scrapy.Request(self.static_url, self.parse)


    def parse(self, response):
        # format response data
        try:
            result_urls = response.css('tbody tr.sys_subitem a::attr(href)').getall()
            next_page = response.css('span.sys_navigationnext a::attr(href)').get()

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

        name = response.xpath('//*[@id="whosWhoRecord"]/h1/text()').get()
        id_ = '-'.join(name.lower().split(' '))
        job = response.xpath('//*[@id="UserJobLabel"]/text()').get()
        address = response.xpath('//*[@id="UserAddressLabel"]/span/text()').get()
        phone = response.xpath('//*[@id="UserTelLabel"]/text()').get()
        department = response.xpath('//*[@id="UserSchoolLabel"]/text()').get()
        email = response.xpath('//*[@id="UserEmailLabel"]/a/text()').get()
        url = response.url

        try:
            bio = response.xpath('//*[@id="acc"]/div[1]/div/p/text()').get()[:250].rstrip() + '...'
        except Exception as e:
            bio = ''
            print('No personal profile (bio)')
        img = response.urljoin(response.css('div.sys_userimage img::attr(src)').get()) \
              if response.css('div.sys_userimage img::attr(src)').get() else ""

        tabs = response.xpath('//*[@id="acc"]/div')
        courses_taught = []
        expertise = []
        for tab in tabs:
            try:
                if tab.css('div.acc-item h3::text').get() == 'Courses taught':
                    courses_taught = tab.css('div p a::text').getall() or tab.css('div p::text').getall()
                if tab.css('div.acc-item h3::text').get() == 'Research interests/expertise':
                    expertise = tab.css('div p::text').get().split(', ') or tab.css('div ul li::text').getall()
            except Exception as e:
                pass

        data = [{
            "id": id_,
            "name": name,
            "job": job,
            "school": "De Montfort University",
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
