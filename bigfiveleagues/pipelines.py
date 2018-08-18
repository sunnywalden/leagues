# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions import DropItem
from scrapy import Request
import pymysql
from .items import LeagueItem,ClubItem,PlayerItem
from scrapy.utils.project import get_project_settings  #导入seetings配置

#class BigfiveleaguesPipeline(object):
#    def process_item(self, item, spider):
#        return item

def dbHandle():
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
		print('Connect to mysql success!')
	return conn

class ImgDownloadPipeline(ImagesPipeline):

        def get_media_requests(self, item, info):
                for img_url in item['img_urls']:
                        print('Start download image', img_url)
                        yield Request(img_url,meta={'item':item,'index':item['img_urls'].index(img_url)})



        def file_path(self, request, response=None, info=None):
                item = request.meta['item']  # 通过上面的meta传递过来item
                index = request.meta['index']
		if item.get('player_club'):
			print('player',item['player_uname'],'info scrapy now')
                	logo_name = item['player_club'] + '_'  + item['name']  + '.jpg'
		else:
			logo_name = item['name'] + '.jpg'
                print('logo name is', logo_name)
                return logo_name

class LeaguesItemPipeline(object):
    '''保存到数据库中对应的class
       1、在settings.py文件中配置
       2、在自己实现的爬虫类中yield item,会自动执行'''


    # pipeline默认调用
    def process_item(self, item, spider):

# 写入数据库中
    # SQL语句在这里
	conn = dbHandle()
	cursor = conn.cursor()
	if isinstance(item, LeagueItem):
		print('Handle league item now',item['league_uname'])
		sql = "insert ignore into leagues values(%s,%s,%s,%s)"
		clubs = ''
		for club in item['league_clubs']:
#			tmp = club.encode('UTF-8')
			club += club + ','
		print(clubs)
		params = (item['league_uname'], item['name'], item['img_urls'], clubs)
#		params = (item['league_uname'], item['name'], item['img_urls'], str(item['league_clubs']))
	elif isinstance(item, ClubItem):
		print('Handle club item now',item['club_uname'])
 		sql = "insert ignore into clubs values(%s,%s,%s,%s,%s,%s,%s,%s)"
		players = ''
		for player in item['club_players']:
#			tmp = player.encode('UTF-8')
			players += player + ','
		print(players)
 		params = (
			item['club_league']+'-'+item['name'],
			item['club_league'],
			item['name'],
			item['club_uname'],
			item['img_urls'],
			item['club_manager'],
			players,
			item['club_soccerfield']
			)
	elif isinstance(item, PlayerItem):
		print('Handle player item now',item['player_uname'])
		sql = "insert ignore into players values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
		params = (
			item['player_club']+'-'+item['name'],
			item['player_league'],
			item['player_club'],
			item['name'],
			item['player_uname'],
			item['img_urls'],
			item['player_number'],
			item['player_position'],
			item['player_nationality'],
			item['player_high'],
			item['player_weight'],
			item['player_age'],
			item['player_networth']
			)
 	try:
		cursor.execute(sql, params)
		conn.commit()
            # 关闭连接
	except Exception as error:
            # 出现错误时打印错误日志
		print(error)
		conn.rollback()
	return item

