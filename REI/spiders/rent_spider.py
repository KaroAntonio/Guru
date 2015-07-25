from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import FormRequest, Request

class RentSpider(BaseSpider):

    name = "rent"
    allowed_domains = ["rentometer.com"] # i fixed this
    start_urls = ["https://www.rentometer.com"] # i added this

    def parse(self, response):
        yield FormRequest.from_response(response, formname='commit', formdata={'address':'Denver CO', 'beds':'1'}, callback=self.parseRentAssessment)

    def parseRentAssessment(self, response):
        print(response.xpath('//*[contains(concat(" ", normalize-space(@class), " "), " col-md-12 ")]/ul/li/strong/text()').extract())
        return 
        