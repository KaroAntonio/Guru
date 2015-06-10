import scrapy

class IpSpider(scrapy.Spider):
    name = 'ip'
    allowed_domains = ['checkip.dyndns.org']
    start_urls = [
        'http://checkip.dyndns.org/',
    ]

    def parse(self, response):
        pub_ip = response.xpath('//body/text()').re('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')[0]
        print "My public IP is: " + pub_ip