#-*- coding:utf-8 -*-
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import scrapy
from ..items import LeagueItem,ClubItem,PlayerItem
import proxy
import datetime
import logging

class leaguesSpider(scrapy.Spider):
	logger = logging.getLogger(__name__)
	logger.info('start generate proxy ip')
	proxy.get_proxy()
	name = 'leagues'
	allowed_domains = ['sodasoccer.com']
	start_urls = [
		'http://www.sodasoccer.com/dasai/index.html',
		]

	#获取五大联赛页面url
	def parse(self, response):
		#只获取欧洲五大联赛对应的列表元素
		leagues = response.xpath('//div[@class="league_box1"][2]/ul/li')[0:5]
		#获取五大联赛各自的详情页相对地址
		leagues_urls = leagues.xpath('div[@class="l_box"]/a/@href').extract()
		#拼接得到联赛的详情页绝对url
		for league_url in leagues_urls:		
			url = 'http://www.sodasoccer.com' + league_url	
			self.logger.info(url)
			#调用爬取联赛信息的函数
			yield scrapy.Request(url,callback=self.parse_league)

	#爬取联赛详情
	def parse_league(self, response):
		clubs = []
		league = LeagueItem()
		#联赛logo
                league['img_urls'] = [response.xpath('//div[@class="limg"]/img/@src').extract()[0].split('?')[0]]
		#联赛中文名称
		league['name'] = response.xpath('//h1[@class="lh1"]/text()').extract()[0]
		#联赛英文名称
		league['league_uname'] = response.xpath('//h2[@class="lh2"]/text()').extract()[0]
		#联赛下的俱乐部列表
		league_clubs = response.xpath('//div[@class="l_zwq"]/ul/li/p/a/text()').extract()
		#将列表转化为字符串，避免存入MySQL后中文显示为unicode
		for club in league_clubs:
			tmp = club.strip('\r\n\t\t\t').strip()
			clubs.append(tmp)
		league['league_clubs'] = clubs
		#获取各当前联赛下各俱乐部的详情页
		clubs_details = response.xpath('//div[@class="l_zwq"]/ul/li/div[@class="qiuduitu_wb"]/a/@href').extract()
		#递归调用俱乐部信息爬虫函数
		for club_details in clubs_details:
			yield scrapy.Request('http://www.sodasoccer.com' + club_details,callback=self.parse_club)
		self.logger.info(league)
		yield league

	#俱乐部信息爬取
	def parse_club(self, response):
	    if response.status==200:
                club = ClubItem()
		#俱乐部所在联赛中文名
                club['club_league'] = response.xpath('//div[@class="leida"]/ul/li[@class="world_fu1_li world_fu1_li_frist"]/span/a/text()').extract()[0]
                #俱乐部logo
		club['img_urls'] = [response.xpath('//div[@class="photo"]/img/@src').extract()[0].split('?')[0]]
                #俱乐部详情父元素
		club_info = response.xpath('//div[@class="jiben"]/ul[@class="xin"]')
                #俱乐部中文名称
		club['name'] = club_info.xpath('li/text()').extract()[0]
                #俱乐部英文名称
		club['club_uname'] = club_info.xpath('li/text()').extract()[1]
                #俱乐部主教练
		club_manager = club_info.xpath('li/a/text()').extract()[0]
                if club_manager:
			club['club_manager'] = club_manager
		else:
			club['club_manager'] = '-'
		#俱乐部球场
                soccerfield = club_info.xpath('li/text()').extract()[2]
                if soccerfield:
			club['club_soccerfield'] = soccerfield
		else:
			club['club_soccerfield'] = '-'
		try:	
			new_info = response.xpath('//div[@id="lineup_0"]/table')
                	old_info = response.xpath('//div[@id="lineup_1"]/table')
			#新赛季引进球员
			new_players = new_info.xpath('tr/td/a/text()').extract()[::2]
			#上个赛季阵容
			old_players = old_info.xpath('tr/td/a/text()').extract()[::2]
			#得到所有球员
			club['club_players'] = new_players + old_players
			new_players_details = new_info.xpath('tr/td/a/@href').extract()[::2]
                	old_players_details = old_info.xpath('tr/td/@href').extract()[::2]
			players_details = new_players_details + old_players_details
			self.logger.info('All players of club %s is %s',club['club_uname'],players_details)
		except:
			club['club_players'] = '-'
		if players_details:
			#递归调用球员信息爬虫
			for player_details in players_details:
                		yield scrapy.Request('http://www.sodasoccer.com' + player_details,callback=self.parse_player)
		self.logger.info(club)
		yield club
	    else:
		self.logger.info('get league failed, Try again')
		yield scrapy.Request(request.url, callback=self.parse_club)

	#球员信息爬取
	def parse_player(self, response):
                player = PlayerItem()
		#球员中文名
		player['name'] = response.xpath('//div[@class="detailhead"]/h1/text()').extract()[0]
		info = response.xpath('//div[@class="jiben"]/ul[@class="xin"]')
		#球员英文名
		player['player_uname'] = info.xpath('li/text()').extract()[0].strip(':').strip()
		try:
			birth_tmp = info.xpath('li/text()').extract()[1].strip().split('-')[0]
			#球员生日信息
			birth = int(birth_tmp.strip())
			this_year = int(datetime.datetime.now().year)
			#球员年龄
			player['player_age'] = this_year - birth
		except Exception as error:
			self.logger.info(error)
			player['player_age'] = 'unknow'
		#场上位置
		player['player_position'] = info.xpath('li/span/strong/text()').extract()[0].strip()		
		#国籍
		player['player_nationality'] = info.xpath('li/span/strong/text()').extract()[3].strip()	
		#身高
		player['player_high'] = info.xpath('li/text()').extract()[3].strip()	
		#体重
		player['player_weight'] = info.xpath('li/span/strong/text()').extract()[2].strip()
		#身价
		player['player_networth'] = info.xpath('li/text()').extract()[2].strip()
		#当前俱乐部
		player['player_club'] = response.xpath('//div[@class="leida"]/ul/li[@class="world_fu1_li world_fu1_li_frist"]/span/a/text()').extract()[0].strip()
		#球衣号码
		player_number = response.xpath('//div[@class="leida"]/ul/li[@class="world_fu1_li world_fu1_li_sec"]/span[@class="world_hao_con world_hao_con1"]/text()').extract()
		if not player_number:
			player['player_number'] = 'unknow'
		else:
			player['player_number'] = player_number[0].strip()
		#照片
		player['img_urls'] = [response.xpath('//div[@class="photo"]/img/@src').extract()[0].strip().split('?')[0]]
		#联赛
		player['player_league'] = response.xpath('//div[@id="career_stat_0"]/table/tr/td/text()').extract()[0].strip()
		
		self.logger.info(player)
		yield player
