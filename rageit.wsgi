# -*- coding: utf-8 -*-
import sys, os
sys.path.append(os.path.dirname(__file__)) 
sys.path.append("/home/joink/public_html/rageit/irclog")
#sys.path.append(os.path.abspath("./irclog"))
sys.stdout = sys.stderr

#from postvarsel import *
from pysqlite2 import dbapi2 as sqlite
from math import *
import irclog.archive
import random
import string
#connection = sqlite.connect('/usr/local/wsgi-scripts/post.db')
#cursor = connection.cursor()


rage = [ "clean.png", "EWBTE2.png", "FemaleHappy.png", "french.png", "Happy.png", "Hehehe.png", "loool.png", "redeyes.png", "Smile.png", "Stoned.png", "whyyyyyy.png",
"dude-come-on.png", "EWBTE.png", "FemaleRetarded.png", "grin.png", "hehehe.png", "herp.png", "pfftch.png", "Smile2.png", "SoMuchWin.png", "suspicious.png"]

pub_path = "~joink/rageit/avatars/rage"

def get_avatar():
	place = random.randint(0, len(rage)-1)
	return pub_path + "/" + rage[place]
##


class Analyze:
	"""Speak Analyzer"""
	def __init__(self):
		self.angry = 0
		self.happy = 0
		self.suspicious = 0.0
		self.shout = 0.0
		self.wordcount = 0
		self.sentence_length = 0	
		self.debug_out = ""

	def parse(self, speak):
		self.debug_out += "Analyzing: <br/>\n"
		for sentence in speak:
			#self.debug_out += "<br/>Sent: %s\n" % (sentence)
			#self.debug_out += "Len: %d<br/>\n" % (len(sentence))
			self.ana_shout(sentence)
			self.ana_wordcount(sentence)
			self.ana_length(sentence)
			self.ana_keywords(sentence)

		self.debug_out += "WordCount: %d<br/>\n" % (self.wordcount)
		self.debug_out += "Len: %d<br/>\n" % (self.sentence_length)
		self.debug_out += "Shout: %f<br/>\n" % (self.shout)
		self.debug_out += "Suspicious: %f<br/>\n" % (self.suspicious)

	def ana_keywords(self,sentence):
		if u"konspirasjon" in sentence:
			self.suspicious += 2

	def ana_length(self, sentence):
		self.sentence_length += len(sentence)

	def ana_wordcount(self, sentence):
		words = 0
		for word in sentence.split(" "):
			words += 1
		self.wordcount += words

	def ana_shout(self, sentence):
		upper = 0
		words_len = 0
		for word in sentence.split(" "):
			for c in word:
				words_len += 1
				if c in string.uppercase or c in u"ÆØÅ!":
					upper += 1
				if c in u"!":
					upper += 2
		if upper != 0:
			self.shout += float(upper) / words_len

	
def application(environ, start_response):
	status = '200 OK'
	output = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"> 
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
<meta http-equiv="Content-Type" content="text/html;charset=utf-8" /> 
<title>RageIt</title>
</head>
<body>
"""
#<link rel="stylesheet" type="text/css" media="screen" href=""http://toppe.no/~joink/rageit/style-screen.css">
	print >> environ['wsgi.errors'], "application debug #1"
	#trackIDs=["RB084737486HK"]
	#print "The ID is %s" % trackID


	story_raw = u"""10:01 <@DrSlem> hmmm, internettet mitt er usigelig treigt i dag
10:02 <@DrSlem> kanskje et forsiktig hint fra NGT om at regningen skal betales i morgen...
10:02 <@DrSlem> eller mest sannsynlig; en konspirasjon!
10:03 <@_neon_> DE ER DI RØDGRØNNE SOMM HAR SKYLLA
10:04 <@runehol> NÅ MÅ JENS Å CO GÅ
10:04 < vrakrav_> NISSELUER!
10:05 < Skuggen> JULEKALENDER!
10:11 < daven> POSTKASSE!"""

	story_raw = story_raw.encode("utf8")
	story_irc = irclog.parser.parse(story_raw.splitlines())

	story = []
	nick = ""
	for message in story_irc:
		if isinstance(message, irclog.messages.PublicMessage):
			message.__class__ = irclog.messages.PublicMessage
			if (nick != message.nick):
				story.append([message.nick, [], Analyze()])
				nick = message.nick
			story[len(story)-1][1].append(message.line)
	
	for cell in story:
		cell[2].parse(cell[1])

	grid_max_width = 4
	strip_length = len(story)
	
	if strip_length <= grid_max_width:
		grid_width = strip_length
		grid_length = 1
	else:
		grid_width = int(grid_max_width)
		grid_length = int(ceil(float(strip_length) / grid_max_width))

	output += "<p>strip_length = %d, grid_width = %d, grid_length = %d</p>\n" % (strip_length, grid_width, grid_length)
	output += "<table border=\"1\">\n"

	current_cell = 0
	for row in range(0, grid_length):
		output +="<tr>\n"
		for column in range(0, grid_width):
			speak = ""
			nick = ""
			output += "<td>\n"
			if current_cell < strip_length:
				speak = "<br/>\n".join(story[current_cell][1])
				nick = story[current_cell][0]
				ana = story[current_cell][2]	
				current_cell += 1

				output += "<p>%s</p>\n" % (speak)
				output += "<img src=\"%s\">\n" % (get_avatar())
				output += "<p>%s</p>\n" % (nick)
				output += "<p>%s</p>\n" % (ana.debug_out) 
			output += "</td>\n"
		output +="</tr>\n"
	output += "</table>\n"


	output += "</body>\n</html>\n"
	output = output.encode("utf-8")
	response_headers = [	('Content-type', 'text/html'),
				('charset','utf-8'),
				('Content-Length', str(len(output)))]
	
	start_response(status, response_headers)

	return [output]

#from paste.evalexception.middleware import EvalException
#application = EvalException(application)

#from wsgiref import simple_server
#httpd = simple_server.WSGIServer(
#	('',8000),
#	simple_server.WSGIRequestHandler,
#	)
#httpd.set_app(application)
#httpd.serve_forever()
