# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions import DropItem
from scrapy import Request

#class BigfiveleaguesPipeline(object):
#    def process_item(self, item, spider):
#        return item

class ImgDownloadPipeline(ImagesPipeline):

        def get_media_requests(self, item, info):
                for img_url in item['img_urls']:
                        print('Start download image', img_url)
                        yield Request(img_url,meta={'item':item,'index':item['img_urls'].index(img_url)})



        def file_path(self, request, response=None, info=None):
                item = request.meta['item']  # 通过上面的meta传递过来item
                index = request.meta['index']
                logo_name = item['name'] + '.jpg'
                print('logo name is', logo_name)
                return logo_name
