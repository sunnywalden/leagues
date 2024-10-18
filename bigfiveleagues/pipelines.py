# -*- coding: utf-8 -*-
import os

from scrapy.pipelines.files import FilesPipeline
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions import DropItem
from scrapy import Request
import pymysql
from .items import LeagueItem,ClubItem,PlayerItem
from scrapy.utils.project import get_project_settings  #导入settings配置
import logging


logger = logging.getLogger(__name__)

class FileDownloadPipeline(FilesPipeline):
    def __init__(self, store_uri,  download_func=None, settings=None):
        if settings is None:
            settings = get_project_settings()
        super().__init__(store_uri, download_func, settings)
        self.logger = logging.getLogger(__name__)
        # self.img_store = settings.get('FILES_STORE')

    @classmethod
    def from_settings(cls, settings):
        store_uri = settings.get('FILES_STORE')
        return cls(store_uri, settings=settings)


    def get_media_requests(self, item, info):
                for img_url in item['file_urls']:
                        self.logger.info('Start download image %s', img_url)
                        yield Request(img_url,meta={'item':item,'index':item['file_urls'].index(img_url)})

    def media_failed(self, failure, request, info):
        self.logger.error(f"File (unknown-error): Error downloading file from {request.url} referred in {info.spider.name}: {failure}")
        return super().media_failed(failure, request, info)

    def file_path(self, request, response=None, info=None, *, item=None):
        item = request.meta['item']  # 通过上面的meta传递过来item
        index = request.meta['index']
        if item.get('player_number'):
            self.logger.info('player %s info scrapy now',
                             item['name'])
            logo_name = item['name']  + '.jpg'
            img_path = "%s/" % 'players'
        elif item.get('club_manager'):
            self.logger.info('club %s info scrapy now',item['name'])
            logo_name = item['name'] + '.jpg'
            img_path = "%s/" % 'clubs'
        else:
            self.logger.info('league %s info scrapy now',item['name'])
            logo_name = item['name'] + '.jpg'
            img_path = "%s/" % 'leagues'
        if not os.path.exists(img_path):
            os.mkdir(img_path)
            self.logger.info('the path item picture to save is %s', img_path + logo_name)
#		return logo_name
        final_file = img_path + logo_name
        return final_file

class LeaguesItemPipeline(object):
    """保存到数据库中对应的class
       1、在settings.py文件中配置
       2、在自己实现的爬虫类中yield item,会自动执行"""
    logger = logging.getLogger(__name__)

    def dbHandle(self):
        '''1、@classmethod声明一个类方法，而对于平常我们见到的叫做实例方法。
        2、类方法的第一个参数cls（class的缩写，指这个类本身），而实例方法的第一个参数是self，表示该类的一个实例
        3、可以通过类来调用，就像C.f()，相当于java中的静态方法'''
        #读取settings中配置的数据库参数
        settings = get_project_settings()
        conn = pymysql.connect(
            host=settings['MYSQL_HOST'],
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            passwd=settings['MYSQL_PASSWD'],
            charset='utf8',  # 编码要加上，否则可能出现中文乱码问题
            cursorclass=pymysql.cursors.DictCursor,
            )
        if conn:
            logger.info('Connect to mysql success!')
        return conn
    # pipeline默认调用
    def process_item(self, item, spider):
       # 写入数据库中
       # SQL语句在这里
       global sql, params
       conn = self.dbHandle()
       cursor = conn.cursor()
       if isinstance(item, LeagueItem):
          self.logger.info('Handle league %s item now',item['name'])
          sql = "insert ignore into leagues values(%s,%s,%s)"
          final_logo_url = ''
          for logo_url in item['file_urls']:
              final_logo_url = logo_url
          params = (item['id'], item['name'], final_logo_url)
          self.logger.info(sql,item['id'], item['name'], final_logo_url)
       elif isinstance(item, ClubItem):
          self.logger.info('Handle club %s item now',item['name'])
#		self.logger.info(clubs)
          sql = "insert ignore into clubs values(%s,%s,%s,%s,%s,%s,%s,%s)"
          players = ''
          for player in item['club_players']:
              players += player + ','
          final_club_logo_url = ''
          for club_logo_url in item['file_urls']:
              final_club_logo_url = club_logo_url
          params = (
            item['id'],
            item['name'],
            final_club_logo_url,
            item['club_manager'],
            item['club_soccerfield']
            )
          self.logger.info(sql,
                           item['id'],
                           item['name'],
                           final_club_logo_url,
                           item['club_manager'],
                           item['club_soccerfield'])
       elif isinstance(item, PlayerItem):
           self.logger.info('Handle player %s item now',item['name'])
           player_portrait_url = ''
           for portrait_url in item['file_urls']:
                        player_portrait_url = portrait_url
           sql = "insert ignore into players values(%s,%s,%s,%s,%s)"
           params = (
            item['id'],
            item['name'],
            player_portrait_url,
            item['player_number'],
            item['player_position'],
            item['player_nationality'],
            item['player_high'],
            item['player_weight'],
            item['player_age'],
            item['player_networth']
            )
           self.logger.info(sql,
                            item['id'],
                            item['name'],
                            player_portrait_url,
                            item['player_number'],
                            item['player_position'],
                            item['player_nationality'],
                            item['player_high'],
                            item['player_weight'],
                            item['player_age'],
                            item['player_networth'])
       try:
           cursor.execute(sql, params)
           conn.commit()
           # 关闭连接
       except Exception as error:
           # 出现错误时打印错误日志
           self.logger.info(error)
           conn.rollback()
       return item
