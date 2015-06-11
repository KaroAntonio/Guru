# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher
import sqlite3
from scrapy.contrib.exporter import XmlItemExporter

class SQLPipeline(object):
    def __init__(self):
        self.filename = 'properties.db'
        self.conn = sqlite3.connect(self.filename)
        self.conn.text_factory = str
        self.cursor = self.conn.cursor()
    	self.created_tables = []
        dispatcher.connect(self.finalize, signals.engine_stopped)
    
    def process_item(self, item, spider):
        item_class_name = type(item).__name__
    	
    	if item_class_name not in self.created_tables:
            keys = None
            if hasattr(item.__class__, 'keys'):
                sqlite_keys = item.__class__.sqlite_keys
    		self._create_table(item_class_name, item.fields.iterkeys(), sqlite_keys)
    		self.created_tables.append(item_class_name)
    	
        field_list = []
        value_list = []
        for field_name in item.iterkeys():
            field_list.append('[%s]' % field_name)
            field = item.fields[field_name]
            value_list.append(item[field_name])
    	
        #DELETE any Existing Items with the new item's ID
        self.cursor.execute("select * from HouseItem where id=?", (item['id'],))
        result = self.cursor.fetchone()
        if result:
            self.cursor.execute("DELETE FROM HouseItem WHERE id=?",(item['id'],))
        sql = 'insert or ignore into [%s] (%s) values (%s)' % (item_class_name, ', '.join(field_list), ', '.join(['?' for f in field_list]))
            
    	self.conn.execute(sql, value_list)
    	self.conn.commit()
        return item
    
    def _create_table(self, table_name, columns, keys = None):
        sql = 'create table if not exists [%s] ' % table_name
        column_define = ['[%s] text' % column for column in columns]
        if keys:
            if len(keys) > 0:
                primary_key = 'primary key (%s)' % ', '.join(keys[0])
                column_define.append(primary_key)
			
            for key in keys[1:]:
                column_define.append('unique (%s)' % ', '.join(key))
        sql += '(%s)' % ', '.join(column_define)
        self.conn.execute(sql)
        self.conn.commit()
        
    
    def finalize(self):
        if self.conn is not None:
            self.conn.commit()
            self.conn.close()
            self.conn = None
    
    
