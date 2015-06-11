#
# Author: Jay Vaughan
#
# Pipelines for processing items returned from a scrape.
# Dont forget to add pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html
#
from scrapy import log
from pysqlite2 import dbapi2 as sqlite

# This pipeline takes the Item and stuffs it into scrapedata.db
class scrapeDatasqLitePipeline(object):
    def __init__(self):
        # Possible we should be doing this in spider_open instead, but okay
        self.connection = sqlite.connect('./scrapedata.db')
        self.cursor = self.connection.cursor()
        self.cursor.execute('CREATE TABLE IF NOT EXISTS myscrapedata ' \
                    '(id INTEGER PRIMARY KEY, url VARCHAR(80), desc VARCHAR(80))')

    # Take the item and put it in database - do not allow duplicates
    def process_item(self, item, spider):
        self.cursor.execute("select * from myscrapedata where url=?", item['url'])
        result = self.cursor.fetchone()
        if result:
            log.msg("Item already in database: %s" % item, level=log.DEBUG)
        else:
            self.cursor.execute(
                "insert into myscrapedata (url, desc) values (?, ?)",
                    (item['url'][0], item['desc'][0])

            self.connection.commit()

            log.msg("Item stored : " % item, level=log.DEBUG)
        return item

    def handle_error(self, e):
        log.err(e)