from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


import scrapy
from ..items import LeagueItem,ClubItem,PlayerItem
import proxy
import datetime


class leaguesSpider(scrapy.Spider):
	print('start generate proxy ip')
	proxy.get_proxy()

	name = 'leagues'
	allowed_domains = ['sodasoccer.com']
	start_urls = [
		'http://www.sodasoccer.com/dasai/index.html',
		]

	def parse(self, response):
		for league in response.xpath('//div[@class="league_box1"]/ul'):
 			print(league)
 			details = league.xpath('li/div[@class="l_box"]/a/@href').extract()[0]
		
			url = 'http://www.sodasoccer.com' + details	
			print(url)
			yield scrapy.Request(url,callback=self.parse_league)

	def parse_league(self, response):
		clubs = []
		league = LeagueItem()
                league['img_urls'] = [response.xpath('//div[@class="limg"]/img/@src').extract()[0].split('?')[0]]
		league['name'] = response.xpath('//h1[@class="lh1"]/text()').extract()[0]
		league['league_uname'] = response.xpath('//h2[@class="lh2"]/text()').extract()[0]
		league_clubs = response.xpath('//div[@class="l_zwq"]/ul/li/p/a/text()').extract()
		for club in league_clubs:
			tmp = club.strip('\r\n\t\t\t').strip()
			clubs.append(tmp)
		league['league_clubs'] = clubs
		clubs_details = response.xpath('//div[@class="l_zwq"]/ul/li/div[@class="qiuduitu_wb"]/a/@href').extract()
                        
		for club_details in clubs_details:
			yield scrapy.Request('http://www.sodasoccer.com' + club_details,callback=self.parse_club)

		print(league)
		yield league

	def parse_club(self, response):
	    if response.status==200:
                club = ClubItem()
                club['club_league'] = response.xpath('//div[@class="leida"]/ul/li[@class="world_fu1_li world_fu1_li_frist"]/span/a/text()').extract()[0]
                club['img_urls'] = [response.xpath('//div[@class="photo"]/img/@src').extract()[0].split('?')[0]]
                club_info = response.xpath('//div[@class="jiben"]/ul[@class="xin"]')

                club['name'] = club_info.xpath('li/text()').extract()[0]
                club['club_uname'] = club_info.xpath('li/text()').extract()[1]
                club_manager = club_info.xpath('li/a/text()').extract()[0]
                if club_manager:
			club['club_manager'] = club_manager
		else:
			club['club_manager'] = '-'
                soccerfield = club_info.xpath('li/text()').extract()[2]
                if soccerfield:
			club['club_soccerfield'] = soccerfield
		else:
			club['club_soccerfield'] = '-'
	
		try:	
			new_info = response.xpath('//div[@id="lineup_0"]/table')
                	old_info = response.xpath('//div[@id="lineup_1"]/table')

			new_players = new_info.xpath('tr/td/a/text()').extract()[::2]
			old_players = old_info.xpath('tr/td/a/text()').extract()[::2]
			club['club_players'] = new_players + old_players
			new_players_details = new_info.xpath('tr/td/a/@href').extract()[::2]
                	old_players_details = old_info.xpath('tr/td/@href').extract()[::2]
			players_details = new_players_details + old_players_details
			print('All players of club',club['club_uname'],'is',players_details)
		except:
			club['club_players'] = '-'
		
		if players_details:
			for player_details in players_details:
                		yield scrapy.Request('http://www.sodasoccer.com' + player_details,callback=self.parse_player)
		
		print(club)
		yield club
	    else:
		print('get league failed, Try again')
		yield scrapy.Request(request.url, callback=self.parse_club)

	def parse_player(self, response):
                player = PlayerItem()
		
		player['name'] = response.xpath('//div[@class="detailhead"]/h1/text()').extract()[0]
		info = response.xpath('//div[@class="jiben"]/ul[@class="xin"]')
		player['player_uname'] = info.xpath('li/text()').extract()[0].strip(':').strip()
		try:
			birth_tmp = info.xpath('li/text()').extract()[1].strip().split('-')[0]
		
			birth = int(birth_tmp.strip())
			this_year = int(datetime.datetime.now().year)
			player['player_age'] = this_year - birth
		except Exception as error:
			print(error)
			player['player_age'] = 0

		player['player_position'] = info.xpath('li/span/strong/text()').extract()[0].strip()		
		player['player_nationality'] = info.xpath('li/span/strong/text()').extract()[3].strip()	
		player['player_high'] = info.xpath('li/text()').extract()[3].strip()	
		player['player_weight'] = info.xpath('li/span/strong/text()').extract()[2].strip()
		player['player_networth'] = info.xpath('li/text()').extract()[2].strip()
		player['player_club'] = response.xpath('//div[@class="leida"]/ul/li[@class="world_fu1_li world_fu1_li_frist"]/span/a/text()').extract()[0].strip()
		player_number = response.xpath('//div[@class="leida"]/ul/li[@class="world_fu1_li world_fu1_li_sec"]/span[@class="world_hao_con world_hao_con1"]/text()').extract()
		if not player_number:
			player['player_number'] = 'unknow'
		else:
			player['player_number'] = player_number[0].strip()
		player['img_urls'] = [response.xpath('//div[@class="photo"]/img/@src').extract()[0].strip().split('?')[0]]
		player['player_league'] = response.xpath('//div[@id="career_stat_0"]/table/tr/td/text()').extract()[0].strip()
		
		print(player)
		yield player
		
