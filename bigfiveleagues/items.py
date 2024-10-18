# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class LeagueItem(scrapy.Item):
    # define the fields for your item here like:
    id = scrapy.Field()
    name = scrapy.Field()
    file_urls = scrapy.Field()

class ClubItem(scrapy.Item):
    # define the fields for your item here like:
    id = scrapy.Field()
    club_league = scrapy.Field()
    name = scrapy.Field()
    file_urls = scrapy.Field()
#        club_describe = scrapy.Field()
    club_manager = scrapy.Field()
    club_players = scrapy.Field()
    club_ceo = scrapy.Field()
    club_soccerfield = scrapy.Field()

class PlayerItem(scrapy.Item):
    id = scrapy.Field()
    # define the fields for your item here like:
    player_league = scrapy.Field()
    player_club = scrapy.Field()
    name = scrapy.Field()
    file_urls = scrapy.Field()
    player_number = scrapy.Field()
    player_position = scrapy.Field()
    player_nationality = scrapy.Field()
    player_high = scrapy.Field()
    player_weight = scrapy.Field()
    player_age = scrapy.Field()
    player_networth = scrapy.Field()
