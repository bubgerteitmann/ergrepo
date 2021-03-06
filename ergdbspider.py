import scrapy
import json
import re

class ErgDBSpider(scrapy.Spider):
    name = 'ergdbspider'
    start_urls = ['http://ergdb.org/search']
    image_urls = scrapy.Field()
    def parse(self, response):
        for row in response.css('div.row'):
            contentArea = row.css('div.contentArea')
            rowData = {}
            if contentArea.css('div.titleDiv>a::text').get():
                rowData['title'] = contentArea.css('div.titleDiv>a::text').get()
            for creator in contentArea.css('strong>a'):
                if '?creator=' in creator.css('a::attr("href")').get():
                    rowData['creator'] = creator.css('a::text').get()
            if row.css('span.downloadMrc::attr("onclick")').get():
                s = row.css('span.downloadMrc::attr("onclick")').get()
                s = s[s.find('[[') : s.find(']]')+2]
                if s:
                    rowData['MRC'] = json.loads(s)
            if len(rowData) == 3:
                if rowData['title']:
                    rowData['title'] = re.sub(r'\W+', '', rowData['title'], flags=re.UNICODE)
                if rowData['creator']:
                    rowData['creator'] = re.sub(r'\W+', '', rowData['creator'], flags=re.UNICODE)
                else:
                    rowData['creator'] = 'generic'
                yield rowData
        for next_page in response.css('a.wpv-filter-next-link::attr("href")'):
            yield response.follow(next_page, self.parse)
