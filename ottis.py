# -*- coding: utf-8 -*-
"""

Ottis — A simple bot for Telegram groups that does web and wiki searches.
Author — @karthikeyankc

"""

import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from bs4 import BeautifulSoup
import logging
import requests
import itertools
import json
import os
import urlparse

updater = Updater(token='YOUR TOKEN HERE')
dispatcher = updater.dispatcher

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)

# Scraper header
headers = {'Accept': 'text/html', 'User-Agent': 'Ottis Telegram Bot 0.0.1'}

''' Start '''
def start(bot, update):
	bot.send_message(chat_id=update.message.chat_id, text="I'm Ottis! What menial task can I do for you? For now, I can do two tasks! Type /help to know more!")

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

''' Web search '''
# Search scrapper
def websearch(query):
	url = "https://www.google.com/search?q="
	search_query = query.replace('/search ', '').replace(' ', '%20') # Is there a MessageEntity filter to remove /search?
	result_page = requests.get(url+search_query, headers=headers)
	soup = BeautifulSoup(result_page.content, 'html.parser')

	titles = soup.find_all('h3', {'class':'r'})
	links = []
	counter = 1
	results = {}

	for title in titles:
		links.append(title.find('a'))

	for title, link in itertools.izip_longest(titles, links):
		counter += 1
		title_data = title.text
		if link != None:
			link_data = link.get('href')[7:]
			results[title_data] = urlparse.unquote(link_data[:link_data.find('&')]) # I hope luck works in favor of Ottis!
		if counter == 4:
			break

	return results

# Search handler
def search(bot, update):
	if update.message.text == "/search":
		results = "Search what? You need to add a parameter to the command! Example - '/search the meaning of life'."
	else:
		search_results = websearch(update.message.text)
		results = ""
		for title, link in search_results.iteritems():
			results += "<b>%s</b> - <a href=\"%s\">View Page</a>\n\n" %(title, link)

	bot.send_message(chat_id=update.message.chat_id, text=results, parse_mode=telegram.ParseMode.HTML, disable_web_page_preview=True)

search_handler = CommandHandler('search', search)
dispatcher.add_handler(search_handler)

''' Wiki Summary '''
# MW API
def wikisummary(query):
	try:
		url = "https://en.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&exintro=True&explaintext=True&titles="
		search_query = query.replace('/wiki ', '').replace(' ', '%20') # Any filters to remove the command part in a better way?
		result_page = requests.get(url+search_query, headers=headers)
		j = json.loads(result_page.text)
		page_ids = j['query']['pages']
		
		for key, value in page_ids.iteritems():
			if len(value['extract']) < 50:
				return "Seems there are a lot of Wikis with the same name, try a specific query or visit the disambiguation page for the query here - https://en.wikipedia.org/wiki/%s." %search_query.capitalize()	
			else:
				return value['extract']
	except:
		return "I'm sorry! There is some problem with your query! Try using the /search command!"

# Wiki handler
def wiki(bot, update):
	summary = wikisummary(update.message.text)
	bot.send_message(chat_id=update.message.chat_id, text=summary, disable_web_page_preview=True)

wiki_handler = CommandHandler('wiki', wiki)
dispatcher.add_handler(wiki_handler)

''' Help '''
def help(bot, update):
	bot.send_message(chat_id=update.message.chat_id, text="To search the web use /search.\nTo get a summary from Wikis (Only Wikipedia is supported now) use /wiki.")

help_handler = CommandHandler('help', help)
dispatcher.add_handler(help_handler)

''' Start the bot! '''
PORT = int(os.environ.get('PORT', '5000'))
updater.start_webhook(listen='0.0.0.0', port=PORT, url_path='YOUR TOKEN HERE')
updater.bot.setWebhook("https://YOUR APP NAME.herokuapp.com/" + 'YOUR TOKEN HERE')
updater.idle()